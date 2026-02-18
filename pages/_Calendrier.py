import streamlit as st
from streamlit_calendar import calendar
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
if "selected_day" not in st.session_state:
    st.session_state.selected_day = None

if "responsables" not in st.session_state:
    st.session_state.responsables = load_responsables()

# ---------------------------
# Configuration du calendrier
# ---------------------------
def get_calendar_events():
    """Génère les événements pour le calendrier"""
    events = []
    responsables = st.session_state.responsables
    
    # Boucler sur toutes les dates des 12 derniers/prochains mois
    now = datetime.now()
    for month_offset in range(-6, 7):
        check_date = now + timedelta(days=30*month_offset)
        year = check_date.year
        month = check_date.month
        
        # Boucler sur chaque jour du mois
        for day in range(1, 32):
            try:
                current_day = datetime(year, month, day)
            except ValueError:
                continue
            
            # Boucler sur chaque créneau horaire
            for hour in range(14):
                key_terrain1 = f"{year}-{month}-{day}-{hour}-terrain1"
                key_terrain2 = f"{year}-{month}-{day}-{hour}-terrain2"
                
                responsable1 = responsables.get(key_terrain1, "")
                responsable2 = responsables.get(key_terrain2, "")
                
                terrains_ouverts = 0
                responsables_count = 0
                if responsable1:
                    terrains_ouverts += 1
                    responsables_count += 1
                if responsable2:
                    terrains_ouverts += 1
                    if responsable2 != responsable1:
                        responsables_count += 1
                
                # Créer un événement si ce créneau est ouvert
                if terrains_ouverts > 0:
                    places_totales_creneau = terrains_ouverts * 4
                    key_joueurs = f"{year}-{month}-{day}-{hour}-joueurs"
                    joueurs_count = len(responsables.get(key_joueurs, []))
                    places_occupees_creneau = responsables_count + joueurs_count
                    pourcentage_creneau = (places_occupees_creneau / places_totales_creneau * 100) if places_totales_creneau > 0 else 0
                    
                    # Horaire du créneau
                    heure_debut = 8 + hour
                    heure_fin = heure_debut + 1
                    title = f"{heure_debut}h-{heure_fin}h ({places_occupees_creneau}/{places_totales_creneau})"
                    
                    # Déterminer la couleur en fonction du remplissage
                    if pourcentage_creneau >= 100:
                        color = "#000000"  # Noir - plein
                    elif pourcentage_creneau <= 25:
                        color = "#00cc96"  # Vert
                    elif pourcentage_creneau < 50:
                        color = "#ffd60a"  # Jaune
                    elif pourcentage_creneau < 75:
                        color = "#ff9016"  # Orange
                    else:
                        color = "#ff4136"  # Rouge
                    
                    # Créer l'heure de début et fin spécifique pour ce créneau
                    start_datetime = datetime(year, month, day, heure_debut, 0)
                    end_datetime = datetime(year, month, day, heure_fin, 0)
                    
                    events.append({
                        "title": title,
                        "start": start_datetime.isoformat(),
                        "end": end_datetime.isoformat(),
                        "color": color
                    })
    
    return events

def get_calendar_options():
    """Retourne les options de configuration pour le calendrier"""
    return {
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek"
        },
        "locale": "fr",
        "editable": False,
        "selectable": True,
        "height": "auto",
    }

# ---------------------------
# Affichage calendrier ou page jour
# ---------------------------
if st.session_state.selected_day is None:
    st.title("📅 Calendrier du club")
    
    # Récupérer les événements
    events = get_calendar_events()
    calendar_options = get_calendar_options()
    
    # Afficher le calendrier
    calendar_events = calendar(
        events=events,
        options=calendar_options,
        key="beach_calendar"
    )
    
    # Gérer la sélection d'une date via eventClick ou dateClick (clic sur un jour)
    if calendar_events:
        if calendar_events.get("callback") == "eventClick":
            event = calendar_events["eventClick"]["event"]
            start_str = event["start"]
            # Parser la date ISO (ex: "2026-02-07T00:00:00+01:00")
            selected_date = datetime.fromisoformat(start_str.replace("Z", "+00:00")).date()
            selected_datetime = datetime(selected_date.year, selected_date.month, selected_date.day)
            st.session_state.selected_day = selected_datetime
            st.rerun()
        elif calendar_events.get("callback") == "dateClick":
            # Clic sur un jour (même sans événement)
            date_str = calendar_events["dateClick"]["date"]
            # Parser la date ISO (ex: "2026-02-13T23:00:00.000Z")
            selected_date = datetime.fromisoformat(date_str.replace("Z", "+00:00")).date()
            selected_datetime = datetime(selected_date.year, selected_date.month, selected_date.day)
            st.session_state.selected_day = selected_datetime
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
