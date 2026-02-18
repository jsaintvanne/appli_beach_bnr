import streamlit as st
import pandas as pd

st.title("🏐 Planning des Entraînements")

try:
    df = pd.read_csv("data/entrainements.csv")
    st.dataframe(df, use_container_width=True)
except FileNotFoundError:
    st.error("Fichier entrainements.csv introuvable.")
