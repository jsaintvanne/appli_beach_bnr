import streamlit as st

st.set_page_config(
    page_title="Beach Nantes Rezé",
    page_icon="🏐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Couleurs du club - Jaune et Vert pastel
st.markdown("""
<style>
    /* Sidebar avec dégradé vert-jaune pastel */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #E0F8E0 0%, #FFFACD 100%);
    }
    
    /* Boutons de navigation */
    [data-testid="stSidebarNav"] a {
        color: #2D5016 !important;
    }
    
    /* Hover sur les boutons */
    [data-testid="stSidebarNav"] a:hover {
        background-color: rgba(255, 215, 0, 0.3) !important;
        border-radius: 8px;
    }
    
    /* Titre du menu */
    .css-1v3fvcr {
        color: #4A7C3C;
    }
</style>
""", unsafe_allow_html=True)

# Créer la navigation personnalisée
accueil = st.Page("pages/0_🏠_Accueil.py", title="Accueil", icon="🏠")
calendrier = st.Page("pages/1_📅_Calendrier.py", title="Calendrier", icon="📅")
entrainements = st.Page("pages/2_🏐_Entrainements.py", title="Entrainements", icon="🏐")
membres = st.Page("pages/3_👥_Membres.py", title="Membres", icon="👥")

pg = st.navigation([accueil, calendrier, entrainements, membres])
pg.run()
