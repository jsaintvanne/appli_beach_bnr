import streamlit as st

st.set_page_config(
    page_title="Club Beach Volley",
    page_icon="🏐",
    layout="wide"
)

st.title("🏐 Club de Beach Volley")
st.subheader("Bienvenue sur le site officiel du club !")

st.markdown("""
Notre club de beach volley accueille joueurs débutants et confirmés  
dans une ambiance conviviale et sportive 🌞
""")

st.divider()

st.header("📰 Actualités")

col1, col2 = st.columns(2)

with col1:
    st.info("📅 Tournoi interne prévu le 15 juin !")
    st.info("🏖️ Reprise des entraînements le 3 avril")

with col2:
    st.success("🎉 2 nouvelles recrues cette semaine !")
    st.warning("⚠️ Terrain 2 en maintenance vendredi")

st.divider()

st.write("Utilisez le menu à gauche pour naviguer.")
