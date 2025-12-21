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
from pathlib import Path


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

def safe_rerun():
    try:
        st.experimental_rerun()
    except AttributeError:
        # spróbuj podnieść odpowiedni wyjątek dla starszych/innnth wersji streamlit
        try:
            from streamlit.runtime.scriptrunner import RerunException
        except Exception:
            try:
                from streamlit.script_runner import RerunException
            except Exception:
                RerunException = None
        if RerunException is not None:
            raise RerunException()
        else:
            st.warning("Proszę odświeżyć stronę (F5), aby zastosować zmiany.")

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


    ## Import opinii lokatorów
    st.markdown("#### Import opinii lokatorów (CSV)")
    uploaded_reviews = st.file_uploader("Wybierz plik CSV z opiniami", type=["csv"], key="file_uploader_reviews")

    if uploaded_reviews is not None:
        try:
            reviews_df = pd.read_csv(uploaded_reviews)
            required_cols = ["ReviewId","HouseId","Developer","ReviewerType","Satisfaction","Noise","Neighbors","Maintenance","CommentScore","Date"]
            if not set(required_cols).issubset(set(reviews_df.columns)):
                st.error(f"Plik nie zawiera wymaganych kolumn: {', '.join(required_cols)}")
            else:
                st.session_state["reviews"] = reviews_df
                st.success(f"Zaimportowano opinie: {reviews_df.shape[0]} wierszy x {reviews_df.shape[1]} kolumn")
        except Exception as e:
            st.error(f"Błąd podczas wczytywania opinii: {e}")

    # opcja wczytania domyślnego wygenerowanego pliku opinii
    default_reviews_path = Path(__file__).resolve().parent / "src" / "data" / "house_reviews.csv"
    if st.button("Wczytaj domyślny plik opinii (src/data/house_reviews.csv)"):
        if default_reviews_path.exists():
            try:
                rev = pd.read_csv(default_reviews_path)
                st.session_state["reviews"] = rev
                st.success(f"Wczytano domyślny plik opinii: {len(rev)} wierszy")
            except Exception as e:
                st.error(f"Błąd podczas wczytywania domyślnego pliku: {e}")
        else:
            st.error("Brak domyślnego pliku: src/data/house_reviews.csv")

        df = st.session_state.get("data", pd.DataFrame())

# --- ZAKŁADKA 2: Dane ---
with tab2:
    df = st.session_state.get("data", pd.DataFrame())
    if not df.empty:
        st.write("### Podgląd danych - mieszkania")
        st.dataframe(df, width="stretch")
    else:
        st.info("Brak danych do wyświetlenia. Przejdź do zakładki 'Import danych', aby załadować plik CSV.")

    df_reviews = st.session_state.get("reviews", pd.DataFrame())

    if not df_reviews.empty:
        st.write("### Podgląd danych - opinie lokatorów")
        st.dataframe(df_reviews, width="stretch")
    else:
        st.info("Brak załadowanych opinii lokatorów.")
    

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
        st.write("--------------------------------")
        
        # Wyświetl suwaki dla kryteriów (bez Id)
        for i, name in enumerate(criteria_cols):
            left, right = st.columns([1, 3])
            with left:
                st.markdown(f"**{name}**")
            with right:
                st.slider(
                    label=f"Waga kryterium {name}",
                    min_value=0.0,
                    max_value=1.0,
                    value=st.session_state.get(f"weight_{i}", 0.5),
                    step=0.05,
                    key=f"weight_{i}",
                    label_visibility="collapsed"
                )

        


        ## Wybór preferencji
        st.write("--------------------------------")
        st.write("### Wybór preferencji dla kryteriów")

        # Wybierz swój typ lokatora
        loc_type = st.selectbox("Wybierz typ lokatora, najbardziej zbliżony do twoich oczekiwań:", ['Single', 'Couple', 'Family', 'Student', 'Retiree', 'Professional'])
        st.session_state["locator_type"] = loc_type

        # Wybór developerów na podstawie załadowanych opinii
        reviews_df = st.session_state.get("reviews", pd.DataFrame())
        if not reviews_df.empty and "Developer" in reviews_df.columns:
            devs = sorted(reviews_df["Developer"].dropna().unique().tolist())
            selected_default = st.session_state.get("selected_developers", devs)
            selected_devs = st.multiselect("Wybierz developerów, których opinie mają być brane pod uwagę:", options=devs, default=selected_default)
            st.session_state["selected_developers"] = selected_devs


            st.write("Wybrani developerzy:", ", ".join(selected_devs) if selected_devs else "Brak wybranych")
        else:
            st.info("Brak załadowanych opinii lub brak kolumny 'Developer' — nie można wybrać developerów.")

        

    st.write("--------------------------------")
    st.write("### Zatwierdzenie preferencji")

    if st.button("Zatwierdź wszystkie preferencje"):
        # zapis wag
        weights = {criteria_cols[i]: st.session_state.get(f"weight_{i}", 0.5) for i in range(n)}
        weights["Id"] = None
        st.session_state["criteria_weights"] = weights

        # zapis typu lokatora
        st.session_state["locator_type"] = loc_type

        # zapis developerów (już są w session_state, ale jawnie)
        st.session_state["selected_developers"] = selected_devs if reviews_df is not None else []

        st.success("Preferencje zapisane: wagi, typ lokatora oraz developerzy.")


    # Pokaż aktualne wagi
        st.write("Aktualne wagi:")
        w_dict = st.session_state.get("criteria_weights", {})
        display_data = [
            {"Kryterium": name, "Waga": w_dict.get(name, None)} 
            for name in all_cols if name != "Id"
        ]
        display_df = pd.DataFrame(display_data)
        st.dataframe(display_df, width="stretch")


# --- ZAKŁADKA 4: ---
with tab4:
    pass

# --- ZAKŁADKA 5: ---
with tab5:
    pass
