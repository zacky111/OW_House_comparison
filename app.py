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
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Import danych", "Dane", "Dostosowanie kryteriów", "Wybór algorytmu", "Wyniki"])

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
    st.subheader("Nadaj ważność kryteriom")

    df = st.session_state.get("data", pd.DataFrame())
    if df.empty:
        st.info("Brak załadowanych danych. Przejdź do zakładki 'Import danych' i wczytaj plik CSV.")
    else:
        all_cols = list(df.columns)
        criteria_cols = [c for c in all_cols if c != "Id"]
        n = len(criteria_cols)

        # Domyślne wagi = 0.5 jeśli brak w sesji
        if "criteria_weights" not in st.session_state:
            for i, _ in enumerate(criteria_cols):
                st.session_state.setdefault(f"weight_{i}", 0.5)
            # Id ma wagę None
            st.session_state.setdefault("weight_Id", None)
            st.session_state["criteria_weights"] = {criteria_cols[i]: st.session_state[f"weight_{i}"] for i in range(n)}
            st.session_state["criteria_weights"]["Id"] = None

        st.write("Przesuń suwaki, aby nadać ważność (0.0 — 1.0) dla każdego kryterium:")
        
        # Wyświetl suwaki dla kryteriów (bez Id)
        for i, name in enumerate(criteria_cols):
            left, right = st.columns([1, 3])
            with left:
                st.markdown(f"**{name}**")
            with right:
                st.slider("", min_value=0.0, max_value=1.0,
                          value=st.session_state.get(f"weight_{i}", 0.5),
                          step=0.05, key=f"weight_{i}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Zapisz wagi"):
                weights = {criteria_cols[i]: st.session_state.get(f"weight_{i}", 0.5) for i in range(n)}
                weights["Id"] = None
                st.session_state["criteria_weights"] = weights
                st.success("Wagi zapisane do sesji.")
        with col2:
            if st.button("Przywróć domyślne wagi (0.5)"):
                for i in range(n):
                    st.session_state[f"weight_{i}"] = 0.5
                st.session_state["criteria_weights"] = {criteria_cols[i]: 0.5 for i in range(n)}
                st.session_state["criteria_weights"]["Id"] = None
                st.rerun()

        # Pokaż aktualne wagi
        st.write("Aktualne wagi:")
        w_dict = st.session_state.get("criteria_weights", {})
        display_data = [
            {"Kryterium": name, "Waga": w_dict.get(name, None)} 
            for name in all_cols if name != "Id"
        ]
        display_df = pd.DataFrame(display_data)
        st.dataframe(display_df, use_container_width=True)

# --- ZAKŁADKA 4: ---
with tab4:
    pass

# --- ZAKŁADKA 5: ---
with tab5:
    pass
