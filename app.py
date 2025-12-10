import time
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from math import pi
import pandas as pd
from io import BytesIO
from datetime import datetime
import os
import plotly.express as px


# algorithms
from src.alg.alg1 import alg1
from src.alg.alg2 import alg2

# data operations
from src.alg.data_cleansing import data_cleansing

# visual
from visual import VISUAL_MD

algorithms = {
    "Algorytm 1": alg1,
    "Algorytm 2": alg2,
}


st.set_page_config(page_title="Wsparcie wyboru mieszkania - OW", layout="wide")
st.markdown(VISUAL_MD, unsafe_allow_html=True)

st.title("Wsparcie wyboru mieszkania - OW")

## zakładki
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Import danych", "Dane", "Dostosowanie kryteriów", "", ""])

# --- ZAKŁADKA 1: Import danych CSV ---
with tab1:
    st.subheader("Import danych (CSV)")
    uploaded_file = st.file_uploader("Wybierz plik CSV", type=["csv"], key="file_uploader_tab1")

    # Jeśli plik został wybrany — wczytaj od razu i zapisz do stanu sesji
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)


            ## tutaj do dodania - data cleansing
            df = data_cleansing(df)


            st.session_state["data"] = df
            st.session_state["criteria_count"] = df.shape[1]
            st.session_state["criteria"] = [(col, "Min") for col in df.columns]
            st.success(f"Zaimportowano dane: {df.shape[0]} wierszy x {df.shape[1]} kolumn")
        except Exception as e:
            st.error(f"Błąd podczas wczytywania pliku: {e}")

    # Przyciski pozostawione dla wygody użytkownika
    if st.button("Importuj dane"):
        if uploaded_file is None and "data" not in st.session_state:
            st.error("Brak wybranego pliku. Proszę wybrać plik CSV.")
        else:
            st.info("Dane załadowane do sesji." if "data" in st.session_state else "Plik wybrany — wczytaj ponownie, jeśli to konieczne.")

    df = st.session_state.get("data", pd.DataFrame())

# --- ZAKŁADKA 2: Dane ---
with tab2:
    st.subheader("Dane")
    df = st.session_state.get("data", pd.DataFrame())
    if not df.empty:
        st.write("### Podgląd danych")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Brak danych do wyświetlenia. Przejdź do zakładki 'Import danych', aby załadować plik CSV.")

# --- ZAKŁADKA 3: Dostosowanie kryteriów ---
with tab3:
    pass

# --- ZAKŁADKA 4: ---
with tab4:
    pass

# --- ZAKŁADKA 5: ---
with tab5:
    pass
