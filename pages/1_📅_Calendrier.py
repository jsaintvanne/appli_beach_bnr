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

# Toujours recharger les responsables depuis le fichier pour détecter les changements
# faits depuis d'autres pages (comme les entraînements)
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
            
            # Tracker pour marquer les heures déjà traitées pour chaque terrain
            heures_traitees_terrain1 = set()
            heures_traitees_terrain2 = set()
            
            # Boucler sur chaque créneau horaire
            for hour in range(14):
                key_terrain1 = f"{year}-{month}-{day}-{hour}-terrain1"
                key_terrain2 = f"{year}-{month}-{day}-{hour}-terrain2"
                
                responsable1 = responsables.get(key_terrain1, "")
                responsable2 = responsables.get(key_terrain2, "")
                
                # Vérifier si c'est un entraînement ou un tournoi
                is_entrainement1 = responsable1.startswith("ENTRAINEMENT|") if responsable1 else False
                is_entrainement2 = responsable2.startswith("ENTRAINEMENT|") if responsable2 else False
                is_tournoi1 = responsable1.startswith("TOURNOI|") if responsable1 else False
                is_tournoi2 = responsable2.startswith("TOURNOI|") if responsable2 else False
                
                # Si c'est le même entraînement sur les deux terrains, créer un seul événement
                if is_entrainement1 and is_entrainement2 and responsable1 == responsable2 and hour not in heures_traitees_terrain1:
                    entrainement_info = responsable1
                    
                    # Trouver toutes les heures consécutives avec le même entraînement
                    heure_debut_event = hour
                    heure_fin_event = hour + 1
                    
                    for next_hour in range(hour + 1, 14):
                        next_key1 = f"{year}-{month}-{day}-{next_hour}-terrain1"
                        next_key2 = f"{year}-{month}-{day}-{next_hour}-terrain2"
                        next_resp1 = responsables.get(next_key1, "")
                        next_resp2 = responsables.get(next_key2, "")
                        if next_resp1 == entrainement_info and next_resp2 == entrainement_info:
                            heure_fin_event = next_hour + 1
                            heures_traitees_terrain1.add(next_hour)
                            heures_traitees_terrain2.add(next_hour)
                        else:
                            break
                    
                    # Parser les infos de l'entraînement
                    parts = entrainement_info.split("|")
                    if len(parts) == 4:
                        coach = parts[1]
                        genre = parts[2]
                        niveau = parts[3]
                        title = f"🏐 Entrainement {genre} - {niveau}"
                    else:
                        title = "🏐 Entrainement"
                    
                    # Créer l'événement pour toute la plage
                    start_datetime = datetime(year, month, day, 8 + heure_debut_event, 0)
                    end_datetime = datetime(year, month, day, 8 + heure_fin_event, 0)
                    
                    events.append({
                        "title": title,
                        "start": start_datetime.isoformat(),
                        "end": end_datetime.isoformat(),
                        "color": "#E9D5FF",  # Lavande pastel pour les entraînements
                        "textColor": "#1f2937"  # Texte noir
                    })
                    continue
                
                # Traiter les entraînements du terrain 1
                if is_entrainement1 and hour not in heures_traitees_terrain1:
                    entrainement_info = responsable1
                    
                    # Trouver toutes les heures consécutives avec le même entraînement
                    heure_debut_event = hour
                    heure_fin_event = hour + 1
                    
                    for next_hour in range(hour + 1, 14):
                        next_key = f"{year}-{month}-{day}-{next_hour}-terrain1"
                        next_resp = responsables.get(next_key, "")
                        if next_resp == entrainement_info:
                            heure_fin_event = next_hour + 1
                            heures_traitees_terrain1.add(next_hour)
                        else:
                            break
                    
                    # Parser les infos de l'entraînement
                    parts = entrainement_info.split("|")
                    if len(parts) == 4:
                        coach = parts[1]
                        genre = parts[2]
                        niveau = parts[3]
                        title = f"🏐 T1: {genre} - {niveau}"
                    else:
                        title = "🏐 Terrain 1"
                    
                    # Créer l'événement pour toute la plage
                    start_datetime = datetime(year, month, day, 8 + heure_debut_event, 0)
                    end_datetime = datetime(year, month, day, 8 + heure_fin_event, 0)
                    
                    events.append({
                        "title": title,
                        "start": start_datetime.isoformat(),
                        "end": end_datetime.isoformat(),
                        "color": "#E9D5FF",  # Lavande pastel pour les entraînements
                        "textColor": "#1f2937"  # Texte noir
                    })
                
                # Traiter les entraînements du terrain 2
                if is_entrainement2 and hour not in heures_traitees_terrain2:
                    entrainement_info = responsable2
                    
                    # Trouver toutes les heures consécutives avec le même entraînement
                    heure_debut_event = hour
                    heure_fin_event = hour + 1
                    
                    for next_hour in range(hour + 1, 14):
                        next_key = f"{year}-{month}-{day}-{next_hour}-terrain2"
                        next_resp = responsables.get(next_key, "")
                        if next_resp == entrainement_info:
                            heure_fin_event = next_hour + 1
                            heures_traitees_terrain2.add(next_hour)
                        else:
                            break
                    
                    # Parser les infos de l'entraînement
                    parts = entrainement_info.split("|")
                    if len(parts) == 4:
                        coach = parts[1]
                        genre = parts[2]
                        niveau = parts[3]
                        title = f"🏐 T2: {genre} - {niveau}"
                    else:
                        title = "🏐 Terrain 2"
                    
                    # Créer l'événement pour toute la plage
                    start_datetime = datetime(year, month, day, 8 + heure_debut_event, 0)
                    end_datetime = datetime(year, month, day, 8 + heure_fin_event, 0)
                    
                    events.append({
                        "title": title,
                        "start": start_datetime.isoformat(),
                        "end": end_datetime.isoformat(),
                        "color": "#E9D5FF",  # Lavande pastel pour les entraînements
                        "textColor": "#1f2937"  # Texte noir
                    })
                
                # Si c'est le même tournoi sur les deux terrains, créer un seul événement
                if is_tournoi1 and is_tournoi2 and responsable1 == responsable2 and hour not in heures_traitees_terrain1:
                    tournoi_info = responsable1
                    
                    # Trouver toutes les heures consécutives avec le même tournoi
                    heure_debut_event = hour
                    heure_fin_event = hour + 1
                    
                    for next_hour in range(hour + 1, 14):
                        next_key1 = f"{year}-{month}-{day}-{next_hour}-terrain1"
                        next_key2 = f"{year}-{month}-{day}-{next_hour}-terrain2"
                        next_resp1 = responsables.get(next_key1, "")
                        next_resp2 = responsables.get(next_key2, "")
                        if next_resp1 == tournoi_info and next_resp2 == tournoi_info:
                            heure_fin_event = next_hour + 1
                            heures_traitees_terrain1.add(next_hour)
                            heures_traitees_terrain2.add(next_hour)
                        else:
                            break
                    
                    # Parser les infos du tournoi
                    parts = tournoi_info.split("|")
                    if len(parts) == 3:
                        niveau = parts[1]
                        genre = parts[2]
                        title = f"🏆 Tournoi {niveau} - {genre}"
                    else:
                        title = "🏆 Tournoi"
                    
                    # Créer l'événement pour toute la plage
                    start_datetime = datetime(year, month, day, 8 + heure_debut_event, 0)
                    end_datetime = datetime(year, month, day, 8 + heure_fin_event, 0)
                    
                    events.append({
                        "title": title,
                        "start": start_datetime.isoformat(),
                        "end": end_datetime.isoformat(),
                        "color": "#FED7AA",  # Pêche pastel pour les tournois
                        "textColor": "#1f2937"  # Texte noir
                    })
                    continue
                
                # Traiter les tournois du terrain 1
                if is_tournoi1 and hour not in heures_traitees_terrain1:
                    tournoi_info = responsable1
                    
                    # Trouver toutes les heures consécutives avec le même tournoi
                    heure_debut_event = hour
                    heure_fin_event = hour + 1
                    
                    for next_hour in range(hour + 1, 14):
                        next_key = f"{year}-{month}-{day}-{next_hour}-terrain1"
                        next_resp = responsables.get(next_key, "")
                        if next_resp == tournoi_info:
                            heure_fin_event = next_hour + 1
                            heures_traitees_terrain1.add(next_hour)
                        else:
                            break
                    
                    # Parser les infos du tournoi
                    parts = tournoi_info.split("|")
                    if len(parts) == 3:
                        niveau = parts[1]
                        genre = parts[2]
                        title = f"🏆 T1: {niveau} - {genre}"
                    else:
                        title = "🏆 Terrain 1"
                    
                    # Créer l'événement pour toute la plage
                    start_datetime = datetime(year, month, day, 8 + heure_debut_event, 0)
                    end_datetime = datetime(year, month, day, 8 + heure_fin_event, 0)
                    
                    events.append({
                        "title": title,
                        "start": start_datetime.isoformat(),
                        "end": end_datetime.isoformat(),
                        "color": "#FED7AA",  # Pêche pastel pour les tournois
                        "textColor": "#1f2937"  # Texte noir
                    })
                
                # Traiter les tournois du terrain 2
                if is_tournoi2 and hour not in heures_traitees_terrain2:
                    tournoi_info = responsable2
                    
                    # Trouver toutes les heures consécutives avec le même tournoi
                    heure_debut_event = hour
                    heure_fin_event = hour + 1
                    
                    for next_hour in range(hour + 1, 14):
                        next_key = f"{year}-{month}-{day}-{next_hour}-terrain2"
                        next_resp = responsables.get(next_key, "")
                        if next_resp == tournoi_info:
                            heure_fin_event = next_hour + 1
                            heures_traitees_terrain2.add(next_hour)
                        else:
                            break
                    
                    # Parser les infos du tournoi
                    parts = tournoi_info.split("|")
                    if len(parts) == 3:
                        niveau = parts[1]
                        genre = parts[2]
                        title = f"🏆 T2: {niveau} - {genre}"
                    else:
                        title = "🏆 Terrain 2"
                    
                    # Créer l'événement pour toute la plage
                    start_datetime = datetime(year, month, day, 8 + heure_debut_event, 0)
                    end_datetime = datetime(year, month, day, 8 + heure_fin_event, 0)
                    
                    events.append({
                        "title": title,
                        "start": start_datetime.isoformat(),
                        "end": end_datetime.isoformat(),
                        "color": "#FED7AA",  # Pêche pastel pour les tournois
                        "textColor": "#1f2937"  # Texte noir
                    })
                
                # Si c'est un entraînement ou tournoi, ne pas traiter comme créneau ouvert
                if is_entrainement1 or is_entrainement2 or is_tournoi1 or is_tournoi2:
                    continue
                
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
                    key_max_places = f"{year}-{month}-{day}-{hour}-max_places"
                    capacite_max = terrains_ouverts * 8
                    places_totales_creneau = responsables.get(key_max_places, capacite_max)
                    places_totales_creneau = max(responsables_count, min(places_totales_creneau, capacite_max))
                    key_joueurs = f"{year}-{month}-{day}-{hour}-joueurs"
                    joueurs_count = len(responsables.get(key_joueurs, []))
                    places_occupees_creneau = responsables_count + joueurs_count
                    pourcentage_creneau = (places_occupees_creneau / places_totales_creneau * 100) if places_totales_creneau > 0 else 0
                    
                    # Horaire du créneau
                    heure_debut = 8 + hour
                    heure_fin = heure_debut + 1
                    title = f"({places_occupees_creneau}/{places_totales_creneau})"
                    
                    # Déterminer la couleur en fonction du remplissage
                    if pourcentage_creneau >= 100:
                        color = "#D1D5DB"  # Gris clair - plein
                    elif pourcentage_creneau <= 25:
                        color = "#BBF7D0"  # Vert menthe pastel
                    elif pourcentage_creneau < 50:
                        color = "#FEF3C7"  # Jaune pastel
                    elif pourcentage_creneau < 75:
                        color = "#FDBA74"  # Orange pastel
                    else:
                        color = "#FECACA"  # Rose pastel
                    
                    # Créer l'heure de début et fin spécifique pour ce créneau
                    start_datetime = datetime(year, month, day, heure_debut, 0)
                    end_datetime = datetime(year, month, day, heure_fin, 0)
                    
                    events.append({
                        "title": title,
                        "start": start_datetime.isoformat(),
                        "end": end_datetime.isoformat(),
                        "color": color,
                        "textColor": "#1f2937"  # Texte noir
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
        "timeZone": "Europe/Paris",  # Utiliser le fuseau horaire français
        "firstDay": 1,  # Commence le lundi (0=dimanche, 1=lundi)
        "displayEventEnd": True,  # Afficher l'heure de fin des événements
        "eventTimeFormat": {  # Format court pour les heures (sans minutes si :00)
            "hour": "numeric",
            "minute": "2-digit",
            "meridiem": False,
            "omitZeroMinute": True
        },
        "eventDisplay": "block",  # Affichage en bloc (meilleur pour le responsive)
        "editable": False,
        "selectable": True,
        "height": "auto",
    }

# ---------------------------
# Affichage calendrier ou page jour
# ---------------------------
if st.session_state.selected_day is None:
    st.title("📅 Calendrier du club")
    
    st.markdown("""
    Pour vous ajouter sur une session (hors entrainements/tournois), cliquez sur un créneau horaire vert/jaune/orange/rouge, puis sélectionnez votre nom dans la liste déroulante.\n
    Pour les staffers, pour ajouter une session de jeu, cliquez sur le jour souhaité, puis utilisez les menus déroulants pour assigner un responsable à chaque terrain. Vous pouvez aussi indiquer le nombre de joueurs inscrits pour chaque créneau.""")
    
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
            # Extraire uniquement la partie date (YYYY-MM-DD) sans tenir compte du fuseau horaire
            date_part = start_str.split("T")[0]
            year, month, day = map(int, date_part.split("-"))
            selected_datetime = datetime(year, month, day)
            st.session_state.selected_day = selected_datetime
            st.rerun()
        elif calendar_events.get("callback") == "dateClick":
            # Clic sur un jour (même sans événement)
            date_str = calendar_events["dateClick"]["date"]
            # Extraire uniquement la partie date (YYYY-MM-DD) sans tenir compte du fuseau horaire
            date_part = date_str.split("T")[0]
            year, month, day = map(int, date_part.split("-"))
            selected_datetime = datetime(year, month, day)
            st.session_state.selected_day = selected_datetime
            st.rerun()

else:
    # ---------------------------
    # Page jour
    # ---------------------------
    # Bouton de retour au calendrier en haut
    if st.button("⬅️ Retour au calendrier", key="retour_haut"):
        st.session_state.selected_day = None
        save_responsables(st.session_state.responsables)
        st.rerun()
    
    day = st.session_state.selected_day
    
    # Traduire le jour et le mois en français
    jours_fr = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    mois_fr = ["", "janvier", "février", "mars", "avril", "mai", "juin", 
               "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
    
    jour_semaine = jours_fr[day.weekday()]
    nom_mois = mois_fr[day.month]
    titre_jour = f"{jour_semaine.capitalize()} {day.day} {nom_mois} {day.year}"
    
    st.title(f"📅 {titre_jour}")

    st.write("### Créneaux horaires (1h)")
    
    # Charger les membres
    try:
        df_membres = pd.read_csv("data/membres.csv")
        # Listes de membres
        membres = df_membres["prenom"].str.cat(df_membres["nom"], sep=" ").tolist()
        membres = [""] + membres  # Ajouter option vide
        
        # Filtrer les staffers pour les responsables de terrain
        staffers_df = df_membres[df_membres["staffer"] == "Oui"]
        staffers = staffers_df["prenom"].str.cat(
            staffers_df["nom"], sep=" "
        ).tolist()
        staffers = [""] + staffers  # Ajouter option vide
    except FileNotFoundError:
        membres = [""]
        staffers = [""]
        st.error("Fichier membres.csv introuvable.")

    # Style CSS pour séparer les colonnes
    st.markdown("""
        <style>
        [data-testid="column"]:first-child {
            border-right: 2px solid #e0e0e0;
            padding-right: 1rem;
        }
        [data-testid="column"]:last-child {
            padding-left: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    start_time = datetime(day.year, day.month, day.day, 8)
    
    # Afficher les créneaux par paires (2 par ligne)
    for row in range(7):  # 7 lignes pour 14 créneaux
        cols = st.columns(2)
        
        for col_idx in range(2):
            i = row * 2 + col_idx  # Index du créneau (0 à 13)
            
            with cols[col_idx]:
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
                    key_max_places = f"{day.year}-{day.month}-{day.day}-{i}-max_places"
                    capacite_max = terrains_ouverts_creneau * 8
                    places_totales_creneau = st.session_state.responsables.get(key_max_places, capacite_max)
                    places_totales_creneau = max(responsables_count_creneau, min(places_totales_creneau, capacite_max))
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
                
                # Vérifier si c'est un entraînement ou un tournoi
                current_resp1 = st.session_state.responsables.get(key_terrain1, "")
                current_resp2 = st.session_state.responsables.get(key_terrain2, "")
                
                is_entrainement1 = current_resp1.startswith("ENTRAINEMENT|") if current_resp1 else False
                is_entrainement2 = current_resp2.startswith("ENTRAINEMENT|") if current_resp2 else False
                is_tournoi1 = current_resp1.startswith("TOURNOI|") if current_resp1 else False
                is_tournoi2 = current_resp2.startswith("TOURNOI|") if current_resp2 else False
                
                # Terrain 1
                st.write("**Terrain 1**")
                if is_entrainement1:
                    # Décomposer les infos de l'entraînement
                    parts = current_resp1.split("|")
                    coach = parts[1] if len(parts) > 1 else ""
                    genre = parts[2] if len(parts) > 2 else ""
                    niveau = parts[3] if len(parts) > 3 else ""
                    st.info(f"🏐 Entraînement {genre} - {niveau}\n\nCoach: {coach}")
                    st.caption("⚠️ Créneau bloqué pour entraînement")
                elif is_tournoi1:
                    # Décomposer les infos du tournoi
                    parts = current_resp1.split("|")
                    niveau = parts[1] if len(parts) > 1 else ""
                    genre = parts[2] if len(parts) > 2 else ""
                    st.warning(f"🏆 Tournoi {niveau} - {genre}")
                    st.caption("⚠️ Créneau bloqué pour tournoi")
                else:
                    responsable1 = st.selectbox(
                        "Responsable",
                        staffers,
                        index=staffers.index(current_resp1) if current_resp1 in staffers else 0,
                        key=f"responsable_terrain1_{key_terrain1}",
                        label_visibility="collapsed"
                    )
                    st.session_state.responsables[key_terrain1] = responsable1
                
                # Terrain 2
                st.write("**Terrain 2**")
                if is_entrainement2:
                    # Décomposer les infos de l'entraînement
                    parts = current_resp2.split("|")
                    coach = parts[1] if len(parts) > 1 else ""
                    genre = parts[2] if len(parts) > 2 else ""
                    niveau = parts[3] if len(parts) > 3 else ""
                    st.info(f"🏐 Entraînement {genre} - {niveau}\n\nCoach: {coach}")
                    st.caption("⚠️ Créneau bloqué pour entraînement")
                elif is_tournoi2:
                    # Décomposer les infos du tournoi
                    parts = current_resp2.split("|")
                    niveau = parts[1] if len(parts) > 1 else ""
                    genre = parts[2] if len(parts) > 2 else ""
                    st.warning(f"🏆 Tournoi {niveau} - {genre}")
                    st.caption("⚠️ Créneau bloqué pour tournoi")
                else:
                    responsable2 = st.selectbox(
                        "Responsable",
                        staffers,
                        index=staffers.index(current_resp2) if current_resp2 in staffers else 0,
                        key=f"responsable_terrain2_{key_terrain2}",
                        label_visibility="collapsed"
                    )
                    st.session_state.responsables[key_terrain2] = responsable2
                
                # Déterminer si les terrains sont ouverts et le max de joueurs
                # Ne pas permettre l'ajout de joueurs si c'est un entraînement ou un tournoi
                terrains_ouverts = 0
                responsable1 = st.session_state.responsables.get(key_terrain1, "") if not is_entrainement1 and not is_tournoi1 else ""
                responsable2 = st.session_state.responsables.get(key_terrain2, "") if not is_entrainement2 and not is_tournoi2 else ""
                responsable1 = responsable1.strip() if isinstance(responsable1, str) else ""
                responsable2 = responsable2.strip() if isinstance(responsable2, str) else ""
                
                if responsable1:
                    terrains_ouverts += 1
                if responsable2:
                    terrains_ouverts += 1
                
                # Ajouter les joueurs si au moins un terrain est ouvert
                if terrains_ouverts > 0:
                    # Créer la liste des responsables obligatoires
                    responsables_joueurs = []
                    if responsable1:
                        responsables_joueurs.append(responsable1)
                    if responsable2 and responsable2.strip().lower() != responsable1.strip().lower():
                        responsables_joueurs.append(responsable2)

                    min_capacite = len(responsables_joueurs)
                    capacite_max = terrains_ouverts * 8
                    key_max_places = f"{day.year}-{day.month}-{day.day}-{i}-max_places"
                    capacite_courante = st.session_state.responsables.get(key_max_places, capacite_max)
                    capacite_totale = max(min_capacite, min(capacite_courante, capacite_max))

                    capacite_totale = st.selectbox(
                        "Capacité totale du créneau (staffers inclus)",
                        options=list(range(min_capacite, capacite_max + 1)),
                        index=capacite_totale - min_capacite,
                        key=f"capacite_{key_max_places}"
                    )
                    st.session_state.responsables[key_max_places] = capacite_totale
                    
                    # Tous les membres (hors option vide) pour inclure aussi les responsables dans la sélection
                    membres_disponibles = membres[1:]
                    
                    key_joueurs = f"{day.year}-{day.month}-{day.day}-{i}-joueurs"
                    current_joueurs = st.session_state.responsables.get(key_joueurs, [])
                    
                    # Joueurs courants valides (hors responsables)
                    joueurs_valides = [j for j in current_joueurs if j in membres_disponibles and j not in responsables_joueurs]
                    joueurs_possibles = max(0, capacite_totale - len(responsables_joueurs))
                    if len(joueurs_valides) > joueurs_possibles:
                        joueurs_valides = joueurs_valides[:joueurs_possibles]

                    # Préselectionner les responsables + joueurs
                    selection_par_defaut = responsables_joueurs + [j for j in joueurs_valides if j not in responsables_joueurs]
                    widget_key = f"joueurs_{key_joueurs}"
                    signature_key = f"{widget_key}_staff_signature"
                    staff_signature = "|".join(sorted([r.strip().lower() for r in responsables_joueurs]))

                    # Si les staffers changent (ou 1er affichage), resynchroniser la sélection affichée
                    if st.session_state.get(signature_key) != staff_signature or widget_key not in st.session_state:
                        selection_affichee = [j for j in selection_par_defaut if j in membres_disponibles]
                        selection_affichee = selection_affichee[:capacite_totale]
                        st.session_state[widget_key] = selection_affichee
                        st.session_state[signature_key] = staff_signature
                    
                    selection_complete = st.multiselect(
                        f"Joueurs inscrits (max {joueurs_possibles})",
                        membres_disponibles,
                        default=selection_par_defaut,
                        max_selections=capacite_totale,
                        placeholder="Selection des joueurs",
                        key=widget_key,
                        label_visibility="collapsed"
                    )

                    # Inclure automatiquement les responsables, même si décochés dans la liste
                    joueurs_selectionnes = [j for j in selection_complete if j not in responsables_joueurs]
                    joueurs_selectionnes = joueurs_selectionnes[:joueurs_possibles]
                    
                    # Combiner responsables + joueurs sélectionnés pour la sauvegarde
                    tous_les_joueurs = responsables_joueurs + joueurs_selectionnes
                    st.session_state.responsables[key_joueurs] = joueurs_selectionnes
                    
                    st.write(f"**{len(tous_les_joueurs)}/{capacite_totale} places** (dont {len(responsables_joueurs)} responsable{'s' if len(responsables_joueurs) > 1 else ''} + max {joueurs_possibles} joueur{'s' if joueurs_possibles > 1 else ''})")
                
                st.divider()

    # Sauvegarder les données après les modifications
    save_responsables(st.session_state.responsables)
    
    st.divider()
    if st.button("⬅️ Retour au calendrier"):
        st.session_state.selected_day = None
        save_responsables(st.session_state.responsables)
        st.rerun()
