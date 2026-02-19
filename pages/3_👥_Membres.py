import streamlit as st
import pandas as pd

st.title("👥 Membres du Club")

try:
    df = pd.read_csv("data/membres.csv")
    st.dataframe(df, use_container_width=True, hide_index=True)
except FileNotFoundError:
    st.error("Fichier membres.csv introuvable.")
