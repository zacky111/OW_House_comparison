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

algorithms = {
    "Algorytm 1": alg1,
    "Algorytm 2": alg2,
}


def save_to_excel_local(benchmark_df, criteria, data_df, batch_count, data_distribution, data_count, data_range, 
                        lambda_poisson, sigma_gauss, mu_gauss, lambda_exponential):
    # Ścieżka zapisu
    folder_path = "eksperymenty_excel"
    os.makedirs(folder_path, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(folder_path, f"benchmark_results_{data_distribution}_{batch_count}_{timestamp}.xlsx")
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        # Arkusz "Wyniki Benchmarku i Dane"
        start_row = 0
        
        # Zapis wyników benchmarku
        benchmark_df.to_excel(writer, index=False, startrow=start_row, sheet_name="Wyniki i Dane")
        start_row += len(benchmark_df) + 3  # Dodajemy odstęp po benchmarku
        
        # Zapis kryteriów z informacją o kierunku min/max
        criteria_df = pd.DataFrame({
            "Kryterium": [c[0] for c in criteria],
            "Min/Max": [c[1] for c in criteria]
        })
        criteria_df.to_excel(writer, index=False, startrow=start_row, sheet_name="Wyniki i Dane")
        start_row += len(criteria_df) + 3  # Dodajemy odstęp po kryteriach
        
        # Zapis ustawień benchmarku
        settings_df = pd.DataFrame({
            "Parametr": ["Liczba batchy", "Rozkład danych", "Liczba punktów", "Zakres wartości",
                         "λ Poisson", "σ Gauss", "μ Gauss", "λ Eksponencjalny"],
            "Wartość": [batch_count, data_distribution, data_count, str(data_range),
                        lambda_poisson, sigma_gauss, mu_gauss, lambda_exponential]
        })
        settings_df.to_excel(writer, index=False, startrow=start_row, sheet_name="Wyniki i Dane")
        start_row += len(settings_df) + 3  # Dodajemy odstęp po ustawieniach
        
        # Zapis pełnych danych wejściowych
        data_df.to_excel(writer, index=False, startrow=start_row, sheet_name="Wyniki i Dane")
        
    # Zapis danych do lokalnego pliku
    with open(file_path, "wb") as f:
        f.write(output.getvalue())

    # Przygotowanie pliku do pobrania
    output.seek(0)
    return file_path, output.getvalue()


# === NOWY INTERFEJS ===
st.set_page_config(page_title="Wsparcie wyboru mieszkania - OW", layout="wide")

st.markdown("""
<style>
/* === DARK MODE === */
body {
    background-color: #0E1117;
    color: #EEE;
    font-family: 'Poppins', sans-serif;
}

/* Nagłówki */
h1, h2, h3 {
    color: #F5F5F5;
    font-weight: 600;
}

/* Zakładki */
.stTabs [data-baseweb="tab"] {
    font-size: 16px;
    font-weight: 500;
    color: #B0C4DE;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #66B2FF;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: #66B2FF;
    border-bottom: 3px solid #66B2FF;
}

/* Formularze i kontenery */
div[data-testid="stForm"] {
    background-color: #1E1E26;
    border-radius: 12px;
    padding: 25px;
    box-shadow: 0 0 8px rgba(0,0,0,0.5);
    color: #EEE;
}

/* Pola wejściowe i selecty */
.stNumberInput input, .stTextInput input, .stSelectbox div[data-baseweb="select"] {
    background-color: #2B2B36 !important;
    color: #EEE !important;
    border-radius: 6px;
    border: 1px solid #3C3C4A;
}

/* Etykiety pól */
label {
    color: #B0C4DE !important;
}

/* Przyciski */
.stButton>button {
    background-color: #007ACC;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1.2rem;
    font-weight: 600;
    transition: 0.3s;
}
.stButton>button:hover {
    background-color: #1493FF;
}

/* Tabele */
[data-testid="stDataFrame"] {
    background-color: #1E1E26;
    color: #EEE;
    border-radius: 10px;
    padding: 10px;
}
</style>
""", unsafe_allow_html=True)



st.title("Wsparcie wyboru mieszkania - OW")

## zakładki
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Import danych", "Dane", "Algorytm", "Porównanie","Eksperyment"])

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
    if not df.empty:
        st.write("### Podgląd zaimportowanych danych")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Zaimportuj plik CSV, aby zobaczyć dane.")

# --- ZAKŁADKA 2: Dane ---
with tab2:
    st.subheader("Dane")
    df = st.session_state.get("data", pd.DataFrame())
    if not df.empty:
        st.write("### Podgląd danych")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Brak danych do wyświetlenia. Przejdź do zakładki 'Import danych', aby załadować plik CSV.")
