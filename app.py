import streamlit as st

st.set_page_config(
    page_title="Beach Nantes Rezé",
    page_icon="🏐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Créer la navigation personnalisée
accueil = st.Page("pages/0_🏠_Accueil.py", title="Accueil", icon="🏠")
calendrier = st.Page("pages/1_📅_Calendrier.py", title="Calendrier", icon="📅")
entrainements = st.Page("pages/2_🏐_Entrainements.py", title="Entrainements", icon="🏐")
membres = st.Page("pages/3_👥_Membres.py", title="Membres", icon="👥")

pg = st.navigation([accueil, calendrier, entrainements, membres])
pg.run()
