import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta

st.title("🏐 Planning des Entraînements et Tournois")

# Chemin des fichiers
ENTRAINEMENTS_FILE = "data/entrainements.csv"
TOURNOIS_FILE = "data/tournois.csv"
RESPONSABLES_FILE = "data/responsables.json"
MEMBRES_FILE = "data/membres.csv"

# Charger la liste des coachs
def get_coachs():
    """Retourne la liste des coachs depuis le fichier membres.csv"""
    try:
        df_membres = pd.read_csv(MEMBRES_FILE)
        coachs_df = df_membres[df_membres["coach"] == "Oui"]
        coachs = coachs_df["prenom"].str.cat(coachs_df["nom"], sep=" ").tolist()
        return coachs
    except FileNotFoundError:
        st.error("Fichier membres.csv introuvable.")
        return []
    except Exception as e:
        st.error(f"Erreur lors du chargement des coachs: {e}")
        return []
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

def appliquer_entrainement_annee(jour_semaine, heure_debut, heure_fin, coach, terrain1, terrain2):
    """Applique un entraînement récurrent sur toute l'année avec vérification de conflits"""
    responsables = load_responsables()
    
    # Mapping des jours en français vers les indices (0=lundi, 6=dimanche)
    jours_mapping = {
        "lundi": 0, "mardi": 1, "mercredi": 2, "jeudi": 3,
        "vendredi": 4, "samedi": 5, "dimanche": 6
    }
    
    jour_idx = jours_mapping.get(jour_semaine.lower())
    if jour_idx is None:
        return False, []
    
    # Calculer les créneaux horaires concernés (commence à 8h)
    heure_debut_int = int(heure_debut.split(":")[0])
    heure_fin_int = int(heure_fin.split(":")[0])
    creneaux = list(range(heure_debut_int - 8, heure_fin_int - 8))
    
    # Vérifier les conflits potentiels
    conflits = []
    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 12, 31)
    current_date = start_date
    
    while current_date <= end_date:
        if current_date.weekday() == jour_idx:
            year = current_date.year
            month = current_date.month
            day = current_date.day
            
            for creneau in creneaux:
                if terrain1:
                    key = f"{year}-{month}-{day}-{creneau}-terrain1"
                    if responsables.get(key):  # Vérifier si terrain1 est déjà occupé
                        conflits.append(f"{day}/{month}/{year} - Terrain 1 - {8+creneau}h")
                if terrain2:
                    key = f"{year}-{month}-{day}-{creneau}-terrain2"
                    if responsables.get(key):  # Vérifier si terrain2 est déjà occupé
                        conflits.append(f"{day}/{month}/{year} - Terrain 2 - {8+creneau}h")
        
        current_date += timedelta(days=1)
    
    # Si des conflits existent, retourner les informations sans appliquer
    if conflits:
        return False, conflits
    
    # Sinon, appliquer l'entraînement
    current_date = start_date
    count = 0
    while current_date <= end_date:
        # Vérifier si c'est le bon jour de la semaine
        if current_date.weekday() == jour_idx:
            year = current_date.year
            month = current_date.month
            day = current_date.day
            
            # Bloquer les créneaux avec le coach
            for creneau in creneaux:
                if terrain1:
                    key = f"{year}-{month}-{day}-{creneau}-terrain1"
                    responsables[key] = coach
                if terrain2:
                    key = f"{year}-{month}-{day}-{creneau}-terrain2"
                    responsables[key] = coach
            
            count += 1
        
        current_date += timedelta(days=1)
    
    save_responsables(responsables)
    return True, []

def bloquer_tournoi(date, heure_debut, heure_fin, niveau, genre, terrain1, terrain2):
    """Bloque les créneaux pour un tournoi à une date spécifique avec vérification de conflits"""
    responsables = load_responsables()
    
    # Calculer les créneaux horaires concernés (commence à 8h)
    heure_debut_int = int(heure_debut.split(":")[0])
    heure_fin_int = int(heure_fin.split(":")[0])
    creneaux = list(range(heure_debut_int - 8, heure_fin_int - 8))
    
    year = date.year
    month = date.month
    day = date.day
    
    # Vérifier les conflits
    conflits = []
    for creneau in creneaux:
        if terrain1:
            key = f"{year}-{month}-{day}-{creneau}-terrain1"
            if responsables.get(key):
                conflits.append(f"{day}/{month}/{year} - Terrain 1 - {8+creneau}h")
        if terrain2:
            key = f"{year}-{month}-{day}-{creneau}-terrain2"
            if responsables.get(key):
                conflits.append(f"{day}/{month}/{year} - Terrain 2 - {8+creneau}h")
    
    # Si des conflits existent, retourner sans appliquer
    if conflits:
        return False, conflits
    
    # Créer l'identifiant du tournoi
    tournoi_info = f"TOURNOI|{niveau}|{genre}"
    
    # Bloquer les créneaux
    for creneau in creneaux:
        if terrain1:
            key = f"{year}-{month}-{day}-{creneau}-terrain1"
            responsables[key] = tournoi_info
        if terrain2:
            key = f"{year}-{month}-{day}-{creneau}-terrain2"
            responsables[key] = tournoi_info
    
    save_responsables(responsables)
    return True, []  # Retourner succès


# Afficher les entraînements existants
st.header("📋 Entraînements récurrents")

try:
    df_entrainements = pd.read_csv(ENTRAINEMENTS_FILE)
    
    # Trier par ordre de jour de la semaine puis par heure de début
    jours_ordre = {
        "Lundi": 0, "Mardi": 1, "Mercredi": 2, "Jeudi": 3,
        "Vendredi": 4, "Samedi": 5, "Dimanche": 6
    }
    df_entrainements['_ordre_jour'] = df_entrainements['jour'].map(jours_ordre)
    df_entrainements = df_entrainements.sort_values(by=['_ordre_jour', 'heure_debut'])
    df_entrainements = df_entrainements.drop(columns=['_ordre_jour'])
    
    st.dataframe(df_entrainements, use_container_width=True, hide_index=True)
except FileNotFoundError:
    df_entrainements = pd.DataFrame(columns=["jour", "heure_debut", "heure_fin", "coach", "niveau", "genre", "terrain1", "terrain2"])
    st.info("Aucun entraînement récurrent pour le moment.")

st.divider()

# Afficher les tournois existants
st.header("🏆 Tournois programmés")

try:
    df_tournois = pd.read_csv(TOURNOIS_FILE)
    
    # Trier par date puis par heure de début
    df_tournois = df_tournois.sort_values(by=['date', 'heure_debut'])
    
    st.dataframe(df_tournois, use_container_width=True, hide_index=True)
except FileNotFoundError:
    df_tournois = pd.DataFrame(columns=["date", "heure_debut", "heure_fin", "niveau", "genre", "terrain1", "terrain2"])
    st.info("Aucun tournoi programmé pour le moment.")

st.divider()

# Formulaire d'ajout d'entraînement dans un expander
with st.expander("➕ Ajouter un entraînement récurrent", expanded=False):
    with st.form("ajout_entrainement"):
        col1, col2 = st.columns(2)
        
        with col1:
            jour = st.selectbox(
                "Jour de la semaine",
                ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
            )
            
            heure_debut = st.time_input(
                "Heure de début",
                value=datetime.strptime("18:00", "%H:%M").time()
            )
            heure_fin = st.time_input(
                "Heure de fin",
                value=datetime.strptime("20:00", "%H:%M").time()
            )
        
        with col2:
            coachs = get_coachs()
            if not coachs:
                st.warning("Aucun coach disponible. Ajoutez des membres avec le rôle 'coach' dans la page Membres.")
                coach = ""
            else:
                coach = st.selectbox("Coach", coachs)
            
            niveau = st.selectbox(
                "Niveau",
                ["Débutant", "Intermédiaire", "Avancé", "Compétition"]
            )
            
            genre = st.selectbox(
                "Genre",
                ["Mixte", "Féminin", "Masculin"]
            )
            
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                terrain1 = st.checkbox("Terrain 1", value=True)
            with col_t2:
                terrain2 = st.checkbox("Terrain 2", value=False)
        
        submitted = st.form_submit_button("Ajouter l'entraînement", use_container_width=True)
        
        if submitted:
            if not coach:
                st.error("Veuillez entrer le nom du coach")
            elif not terrain1 and not terrain2:
                st.error("Veuillez sélectionner au moins un terrain")
            else:
                # Créer l'identifiant d'entraînement
                coach_info = f"ENTRAINEMENT|{coach}|{genre}|{niveau}"
                
                # Vérifier les conflits avant d'ajouter
                success, conflits = appliquer_entrainement_annee(
                    jour,
                    heure_debut.strftime("%H:%M"),
                    heure_fin.strftime("%H:%M"),
                    coach_info,
                    terrain1,
                    terrain2
                )
                
                if not success:
                    st.error("❌ **ATTENTION : Impossible d'ajouter cet entraînement !**")
                    st.error("Les créneaux suivants sont déjà occupés sur le terrain sélectionné :")
                    with st.expander("📋 Voir la liste complète des conflits", expanded=True):
                        for conflit in conflits:
                            st.write(f"• {conflit}")
                    st.info("💡 Veuillez modifier l'heure ou le jour de l'entraînement pour éviter ces conflits.")
                else:
                    # Ajouter au CSV
                    nouvelle_ligne = pd.DataFrame([{
                        "jour": jour,
                        "heure_debut": heure_debut.strftime("%H:%M"),
                        "heure_fin": heure_fin.strftime("%H:%M"),
                        "coach": coach,
                        "niveau": niveau,
                        "genre": genre,
                        "terrain1": "oui" if terrain1 else "non",
                        "terrain2": "oui" if terrain2 else "non"
                    }])
                    
                    df_entrainements = pd.concat([df_entrainements, nouvelle_ligne], ignore_index=True)
                    df_entrainements.to_csv(ENTRAINEMENTS_FILE, index=False)
            
                    st.success(f"✅ Entraînement ajouté avec succès pour tous les {jour}s de l'année 2026 !")
                    st.rerun()

# Formulaire d'ajout de tournoi dans un expander
with st.expander("🏆 Ajouter un tournoi", expanded=False):
    with st.form("ajout_tournoi"):
        col1, col2 = st.columns(2)
        
        with col1:
            date_tournoi = st.date_input(
                "Date du tournoi",
                value=datetime.now()
            )
            
            heure_debut_tournoi = st.time_input(
                "Heure de début",
                value=datetime.strptime("09:00", "%H:%M").time()
            )
            
            heure_fin_tournoi = st.time_input(
                "Heure de fin",
                value=datetime.strptime("18:00", "%H:%M").time()
            )
        
        with col2:
            niveau_tournoi = st.selectbox(
                "Niveau",
                ["S1", "S2", "S3", "Loisir"]
            )
            
            genre_tournoi = st.selectbox(
                "Genre",
                ["Mixte", "Féminin", "Masculin"],
                key="genre_tournoi"
            )
            
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                terrain1_tournoi = st.checkbox("Terrain 1", value=True, key="terrain1_tournoi")
            with col_t2:
                terrain2_tournoi = st.checkbox("Terrain 2", value=True, key="terrain2_tournoi")
        
        submitted_tournoi = st.form_submit_button("Ajouter le tournoi", use_container_width=True)
        
        if submitted_tournoi:
            if not terrain1_tournoi and not terrain2_tournoi:
                st.error("Veuillez sélectionner au moins un terrain")
            else:
                # Vérifier les conflits avant d'ajouter
                success, conflits = bloquer_tournoi(
                    date_tournoi,
                    heure_debut_tournoi.strftime("%H:%M"),
                    heure_fin_tournoi.strftime("%H:%M"),
                    niveau_tournoi,
                    genre_tournoi,
                    terrain1_tournoi,
                    terrain2_tournoi
                )
                
                if not success:
                    st.error("❌ **ATTENTION : Impossible d'ajouter ce tournoi !**")
                    st.error("Les créneaux suivants sont déjà occupés sur le terrain sélectionné :")
                    with st.expander("📋 Voir la liste complète des conflits", expanded=True):
                        for conflit in conflits:
                            st.write(f"• {conflit}")
                    st.info("💡 Veuillez modifier l'heure ou la date du tournoi pour éviter ces conflits.")
                else:
                    # Ajouter au CSV
                    nouvelle_ligne_tournoi = pd.DataFrame([{
                        "date": date_tournoi.strftime("%Y-%m-%d"),
                        "heure_debut": heure_debut_tournoi.strftime("%H:%M"),
                        "heure_fin": heure_fin_tournoi.strftime("%H:%M"),
                        "niveau": niveau_tournoi,
                        "genre": genre_tournoi,
                        "terrain1": "oui" if terrain1_tournoi else "non",
                        "terrain2": "oui" if terrain2_tournoi else "non"
                    }])
                    
                    df_tournois = pd.concat([df_tournois, nouvelle_ligne_tournoi], ignore_index=True)
                    os.makedirs("data", exist_ok=True)
                    df_tournois.to_csv(TOURNOIS_FILE, index=False)
                    
                    st.success(f"✅ Tournoi ajouté avec succès pour le {date_tournoi.strftime('%d/%m/%Y')} !")
                    st.rerun()

st.divider()

# Bouton pour réappliquer tous les entraînements
st.header("🔄 Gestion")

col1, col2 = st.columns(2)

with col1:
    if st.button("Réappliquer tous les entraînements sur l'année 2026", use_container_width=True):
        try:
            df_entrainements = pd.read_csv(ENTRAINEMENTS_FILE)
            count = 0
            for _, row in df_entrainements.iterrows():
                terrain1 = row["terrain1"] == "oui"
                terrain2 = row["terrain2"] == "oui"
                # Créer un identifiant d'entraînement au format: "ENTRAINEMENT|coach|genre|niveau"
                coach_info = f"ENTRAINEMENT|{row['coach']}|{row.get('genre', 'Mixte')}|{row['niveau']}"
                success, conflits = appliquer_entrainement_annee(
                    row["jour"],
                    row["heure_debut"],
                    row["heure_fin"],
                    coach_info,
                    terrain1,
                    terrain2
                )
                if success:
                    count += 1
            st.success(f"✅ {count} entraînements réappliqués avec succès !")
            st.info("💡 Retournez sur la page Calendrier pour voir les entraînements apparaître en violet.")
        except Exception as e:
            st.error(f"Erreur : {e}")

with col2:
    if st.button("Réappliquer tous les tournois", use_container_width=True):
        try:
            df_tournois = pd.read_csv(TOURNOIS_FILE)
            count = 0
            for _, row in df_tournois.iterrows():
                terrain1 = row["terrain1"] == "oui"
                terrain2 = row["terrain2"] == "oui"
                date_tournoi = datetime.strptime(row["date"], "%Y-%m-%d")
                success, conflits = bloquer_tournoi(
                    date_tournoi,
                    row["heure_debut"],
                    row["heure_fin"],
                    row["niveau"],
                    row["genre"],
                    terrain1,
                    terrain2
                )
                if success:
                    count += 1
            st.success(f"✅ {count} tournoi(s) reprogrammé(s) !")
            st.info("💡 Retournez sur la page Calendrier pour voir les tournois.")
        except Exception as e:
            st.error(f"Erreur : {e}")
