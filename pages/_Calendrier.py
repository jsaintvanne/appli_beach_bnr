import streamlit as st
import calendar
from datetime import datetime, timedelta
import pandas as pd
import json
import os

# ---------------------------
# Fonctions de persistance
# ---------------------------
RESPONSABLES_FILE = "data/responsables.json"

def load_responsables():
    """Charge les responsables depuis le fichier JSON"""
    if os.path.exists(RESPONSABLES_FILE):
        try:
            with open(RESPONSABLES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_responsables(responsables):
    """Sauvegarde les responsables dans le fichier JSON"""
    os.makedirs("data", exist_ok=True)
    with open(RESPONSABLES_FILE, "w", encoding="utf-8") as f:
        json.dump(responsables, f, ensure_ascii=False, indent=2)

# ---------------------------
# Initialisation session
# ---------------------------
if "current_date" not in st.session_state:
    st.session_state.current_date = datetime.today()

if "selected_day" not in st.session_state:
    st.session_state.selected_day = None

if "responsables" not in st.session_state:
    st.session_state.responsables = load_responsables()

# ---------------------------
# Affichage calendrier ou page jour
# ---------------------------
if st.session_state.selected_day is None:

    st.title("📅 Calendrier du club")

    # ---------------------------
    # Navigation mois
    # ---------------------------
    def mois_precedent():
        date = st.session_state.current_date
        year = date.year
        month = date.month - 1
        if month == 0:
            month = 12
            year -= 1
        st.session_state.current_date = date.replace(year=year, month=month)

    def mois_suivant():
        date = st.session_state.current_date
        year = date.year
        month = date.month + 1
        if month == 13:
            month = 1
            year += 1
        st.session_state.current_date = date.replace(year=year, month=month)

    # Header navigation - centré avec 7 colonnes comme le calendrier
    cols_header = st.columns(7)
    with cols_header[0]:
        st.button("⬅️", on_click=mois_precedent, use_container_width=True)
    
    # Mapper les mois en français
    mois_fr = {
        1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril", 5: "Mai", 6: "Juin",
        7: "Juillet", 8: "Août", 9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
    }
    mois_nom = mois_fr[st.session_state.current_date.month]
    annee = st.session_state.current_date.year
    
    with cols_header[1]:
        pass
    with cols_header[2]:
        pass
    with cols_header[3]:
        st.markdown(f"<h4 style='text-align: center; margin: 0'>{mois_nom} {annee}</h4>", unsafe_allow_html=True)
    with cols_header[4]:
        pass
    with cols_header[5]:
        pass
    with cols_header[6]:
        st.button("➡️", on_click=mois_suivant, use_container_width=True)

    st.divider()

    # Génération calendrier
    year = st.session_state.current_date.year
    month = st.session_state.current_date.month
    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdayscalendar(year, month)
    jours = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
    
    # Fonction pour calculer les places restantes pour un jour
    def get_places_info(day):
        places_totales = 0
        places_occupees = 0
        for hour in range(14):
            key_terrain1 = f"{year}-{month}-{day}-{hour}-terrain1"
            key_terrain2 = f"{year}-{month}-{day}-{hour}-terrain2"
            
            responsable1 = st.session_state.responsables.get(key_terrain1, "")
            responsable2 = st.session_state.responsables.get(key_terrain2, "")
            
            terrains_ouverts = 0
            responsables_count = 0
            if responsable1:
                terrains_ouverts += 1
                responsables_count += 1
            if responsable2:
                terrains_ouverts += 1
                if responsable2 != responsable1:
                    responsables_count += 1
            
            if terrains_ouverts > 0:
                places_totales += terrains_ouverts * 4
                key_joueurs = f"{year}-{month}-{day}-{hour}-joueurs"
                joueurs_count = len(st.session_state.responsables.get(key_joueurs, []))
                # Compter les responsables + les joueurs sélectionnés
                places_occupees += responsables_count + joueurs_count
        
        places_restantes = places_totales - places_occupees if places_totales > 0 else 0
        pourcentage = ((places_totales - places_restantes) / places_totales * 100) if places_totales > 0 else 0
        return places_totales, places_restantes, pourcentage

    cols = st.columns(7)
    for i,j in enumerate(jours):
        cols[i].markdown(f"**{j}**")

    # Affichage des jours
    for week in month_days:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day==0:
                cols[i].write("")
            else:
                # Afficher avec les places restantes si le jour a des responsables
                places_totales, places_restantes, pourcentage = get_places_info(day)
                if places_totales > 0:
                    # Déterminer l'emoji selon le pourcentage
                    if pourcentage <= 25:
                        emoji = "🟢"  # Vert
                    elif pourcentage < 50:
                        emoji = "🟡"  # Jaune
                    elif pourcentage < 75:
                        emoji = "🟠"  # Orange
                    else:
                        emoji = "🔴"  # Rouge
                    
                    places_occupees = places_totales - places_restantes
                    if cols[i].button(f"{emoji} {day} ({places_occupees}/{places_totales})", key=f"{year}-{month}-{day}"):
                        st.session_state.selected_day = datetime(year, month, day)
                        save_responsables(st.session_state.responsables)
                        st.rerun()
                else:
                    if cols[i].button(str(day), key=f"{year}-{month}-{day}"):
                        st.session_state.selected_day = datetime(year, month, day)
                        save_responsables(st.session_state.responsables)
                        st.rerun()

else:
    # ---------------------------
    # Page jour
    # ---------------------------
    day = st.session_state.selected_day
    st.title(f"📅 {day.strftime('%A %d %B %Y')}")

    st.write("### Créneaux horaires (1h)")
    
    # Charger les membres
    try:
        df_membres = pd.read_csv("data/membres.csv")
        # Listes de membres
        membres = df_membres["prenom"].str.cat(df_membres["nom"], sep=" ").tolist()
        membres = [""] + membres  # Ajouter option vide
        
        # Filtrer les staffers pour les responsables de terrain
        staffers = df_membres[df_membres["role"] == "Staffer"]["prenom"].str.cat(
            df_membres[df_membres["role"] == "Staffer"]["nom"], sep=" "
        ).tolist()
        staffers = [""] + staffers  # Ajouter option vide
    except FileNotFoundError:
        membres = [""]
        staffers = [""]
        st.error("Fichier membres.csv introuvable.")

    start_time = datetime(day.year, day.month, day.day, 8)
    for i in range(14):
        heure_debut = start_time + timedelta(hours=i)
        heure_fin = heure_debut + timedelta(hours=1)
        
        # Clés pour les terrains
        key_terrain1 = f"{day.year}-{day.month}-{day.day}-{i}-terrain1"
        key_terrain2 = f"{day.year}-{day.month}-{day.day}-{i}-terrain2"
        
        # Calculer le pourcentage de remplissage pour ce créneau
        responsable1 = st.session_state.responsables.get(key_terrain1, "")
        responsable2 = st.session_state.responsables.get(key_terrain2, "")
        
        terrains_ouverts_creneau = 0
        responsables_count_creneau = 0
        if responsable1:
            terrains_ouverts_creneau += 1
            responsables_count_creneau += 1
        if responsable2:
            terrains_ouverts_creneau += 1
            if responsable2 != responsable1:
                responsables_count_creneau += 1
        
        # Déterminer l'emoji selon le remplissage du créneau
        emoji_creneau = ""
        if terrains_ouverts_creneau > 0:
            places_totales_creneau = terrains_ouverts_creneau * 4
            key_joueurs = f"{day.year}-{day.month}-{day.day}-{i}-joueurs"
            joueurs_count = len(st.session_state.responsables.get(key_joueurs, []))
            places_occupees_creneau = responsables_count_creneau + joueurs_count
            pourcentage_creneau = (places_occupees_creneau / places_totales_creneau * 100) if places_totales_creneau > 0 else 0
            
            if pourcentage_creneau <= 25:
                emoji_creneau = "🟢"  # Vert
            elif pourcentage_creneau < 50:
                emoji_creneau = "🟡"  # Jaune
            elif pourcentage_creneau < 75:
                emoji_creneau = "🟠"  # Orange
            else:
                emoji_creneau = "🔴"  # Rouge
        
        st.write(f"🕒 {heure_debut.strftime('%H:%M')} - {heure_fin.strftime('%H:%M')} {emoji_creneau}")
        
        # Terrain 1 et 2 - Responsables
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Terrain 1**")
            current_resp1 = st.session_state.responsables.get(key_terrain1, "")
            responsable1 = st.selectbox(
                "Responsable",
                staffers,
                index=staffers.index(current_resp1) if current_resp1 in staffers else 0,
                key=f"responsable_terrain1_{key_terrain1}",
                label_visibility="collapsed"
            )
            st.session_state.responsables[key_terrain1] = responsable1
        
        with col2:
            st.write("**Terrain 2**")
            current_resp2 = st.session_state.responsables.get(key_terrain2, "")
            responsable2 = st.selectbox(
                "Responsable",
                staffers,
                index=staffers.index(current_resp2) if current_resp2 in staffers else 0,
                key=f"responsable_terrain2_{key_terrain2}",
                label_visibility="collapsed"
            )
            st.session_state.responsables[key_terrain2] = responsable2
        
        # Déterminer si les terrains sont ouverts et le max de joueurs
        terrains_ouverts = 0
        if responsable1:
            terrains_ouverts += 1
        if responsable2:
            terrains_ouverts += 1
        
        max_joueurs = terrains_ouverts * 4 if terrains_ouverts > 0 else 0
        
        # Ajouter les joueurs si au moins un terrain est ouvert
        if terrains_ouverts > 0:
            # Créer la liste des responsables obligatoires
            responsables_joueurs = []
            if responsable1:
                responsables_joueurs.append(responsable1)
            if responsable2 and responsable2 != responsable1:
                responsables_joueurs.append(responsable2)
            
            # Filtrer les membres disponibles (exclure vides, responsables)
            membres_disponibles = []
            for m in membres[1:]:
                if m != responsable1 and m != responsable2:
                    membres_disponibles.append(m)
            
            key_joueurs = f"{day.year}-{day.month}-{day.day}-{i}-joueurs"
            current_joueurs = st.session_state.responsables.get(key_joueurs, [])
            
            # Filtrer les joueurs courants pour enlever les responsables et les doublons
            joueurs_valides = [j for j in current_joueurs if j in membres_disponibles]
            
            joueurs_selectionnes = st.multiselect(
                f"Joueurs inscrits (max {max_joueurs})",
                membres_disponibles,
                default=joueurs_valides,
                max_selections=max_joueurs - len(responsables_joueurs),
                key=f"joueurs_{key_joueurs}",
                label_visibility="collapsed"
            )
            
            # Combiner responsables + joueurs sélectionnés pour la sauvegarde
            tous_les_joueurs = responsables_joueurs + joueurs_selectionnes
            st.session_state.responsables[key_joueurs] = joueurs_selectionnes
            
            st.write(f"**{len(tous_les_joueurs)}/{max_joueurs} places** (dont {len(responsables_joueurs)} responsable{'s' if len(responsables_joueurs) > 1 else ''})")
        
        st.divider()

    # Sauvegarder les données après les modifications
    save_responsables(st.session_state.responsables)
    
    st.divider()
    if st.button("⬅️ Retour au calendrier"):
        st.session_state.selected_day = None
        save_responsables(st.session_state.responsables)
        st.rerun()
