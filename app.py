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


st.set_page_config(page_title="Wsparcie wyboru mieszkania - OW", layout="wide", page_icon=":red_circle:")
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
    # Importuj dane (z uploadu) - jawne potwierdzenie
    if st.button("Importuj dane"):
        if uploaded_file is None:
            st.error("Brak wybranego pliku. Proszę wybrać plik CSV lub wczytać domyślny plik danych.")
        else:
            try:
                df = pd.read_csv(uploaded_file)
                df = data_cleansing(df)
                st.session_state["data"] = df
                st.session_state["criteria_count"] = df.shape[1]
                st.session_state["criteria"] = [(col, "Min") for col in df.columns]
                st.success(f"Zaimportowano dane: {df.shape[0]} wierszy x {df.shape[1]} kolumn")
            except Exception as e:
                st.error(f"Błąd podczas wczytywania pliku: {e}")

    # Wczytaj domyślny plik danych
    default_data_path = Path(__file__).resolve().parent / "src" / "data" / "house_data_with_devs.csv"
    if st.button(f"Wczytaj domyślny plik danych ({default_data_path.relative_to(Path().resolve())})"):
        if default_data_path.exists():
            try:
                df = pd.read_csv(default_data_path)
                df = data_cleansing(df)
                st.session_state["data"] = df
                st.session_state["criteria_count"] = df.shape[1]
                st.session_state["criteria"] = [(col, "Min") for col in df.columns]
                st.success(f"Wczytano domyślny plik danych: {df.shape[0]} wierszy")
            except Exception as e:
                st.error(f"Błąd podczas wczytywania domyślnego pliku danych: {e}")
        else:
            st.error(f"Brak domyślnego pliku danych: {default_data_path}")

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

    # Jawne przyciśnięcie: importuj opinie z uploadu
    if st.button("Importuj opinie"):
        if uploaded_reviews is None:
            st.error("Brak wybranego pliku opinii. Proszę wybrać plik CSV lub wczytać domyślny plik opinii.")
        else:
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
    if st.button(f"Wczytaj domyślny plik opinii ({default_reviews_path.relative_to(Path().resolve())})"):
        if default_reviews_path.exists():
            try:
                rev = pd.read_csv(default_reviews_path)
                st.session_state["reviews"] = rev
                st.success(f"Wczytano domyślny plik opinii: {len(rev)} wierszy")
            except Exception as e:
                st.error(f"Błąd podczas wczytywania domyślnego pliku: {e}")
        else:
            st.error(f"Brak domyślnego pliku opinii: {default_reviews_path}")

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
        locator_options = ['Single', 'Couple', 'Family', 'Student', 'Retiree', 'Professional']
        loc_type = st.selectbox("Wybierz typ lokatora, najbardziej zbliżony do twoich oczekiwań:", locator_options)

        # Opisy po polsku
        locator_descriptions = {
            'Single': "Osoba samotna — priorytetem są bliskość rozrywek, dobre połączenia i niższe koszty utrzymania.",
            'Couple': "Para (bez dzieci) — ważna wygoda mieszkania, trochę więcej przestrzeni i dostęp do usług.",
            'Family': "Rodzina z dziećmi — kluczowe bezpieczeństwo, bliskość szkół, placów zabaw i większe mieszkanie.",
            'Student': "Student — preferuje niskie koszty, bliski dojazd na uczelnię i dostęp do życia studenckiego.",
            'Retiree': "Emeryt/Emerytka — ceni spokój, dostęp do opieki zdrowotnej i wygodę lokalną.",
            'Professional': "Osoba zawodowo aktywna — potrzebuje dobrej komunikacji, spokojnego otoczenia i miejsca do pracy.",
        }

        # zapisz wybór i pokaż krótki opis
        st.session_state["locator_type"] = loc_type
        st.session_state["locator_description"] = locator_descriptions.get(loc_type, "")
        st.info(st.session_state["locator_description"])

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
        st.session_state["locator_description"] = locator_descriptions.get(loc_type, "")

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


# --- ZAKŁADKA DDDATKOWA: Surowe dane do algorytmów (do usunięcia) ---
with st.expander("Surowe dane do algorytmów (do usunięcia)"):
    df = st.session_state.get("data", pd.DataFrame())
    if df.empty:
        st.info("Brak danych do wyświetlenia.")
    else:
        st.write("### Dane wejściowe do algorytmów (surowe)")
        st.dataframe(df, width="stretch")

        reviews_df = st.session_state.get("reviews", pd.DataFrame())
        selected_devs = st.session_state.get("selected_developers", [])

        df_filtered = df.copy()

        # Usuń zduplikowane nazwy kolumn (zachowaj pierwsze wystąpienia)
        if df_filtered.columns.duplicated().any():
            st.warning("Wykryto zduplikowane nazwy kolumn w danych wejściowych. Usunięto duplikaty (zachowano pierwsze wystąpienia).")
            df_filtered = df_filtered.loc[:, ~df_filtered.columns.duplicated()]

        # Filtruj po developerach (jeśli wybrano)
        if selected_devs:
            if "Developer" in df_filtered.columns:
                df_filtered = df_filtered[df_filtered["Developer"].isin(selected_devs)]
            elif not reviews_df.empty and "Developer" in reviews_df.columns and "HouseId" in reviews_df.columns:
                house_ids = reviews_df[reviews_df["Developer"].isin(selected_devs)]["HouseId"].unique().tolist()
                if "Id" in df_filtered.columns:
                    df_filtered = df_filtered[df_filtered["Id"].isin(house_ids)]

        if df_filtered.empty:
            st.warning("Brak mieszkań po zastosowaniu filtra developerów.")
        else:
            # Przygotowanie wag i kierunków kryteriów
            criteria_cols = [c for c in df_filtered.columns if c != "Id"]
            weights_map = st.session_state.get("criteria_weights", {c: 0.5 for c in criteria_cols})
            criteria_list = st.session_state.get("criteria", [(c, "Max") for c in criteria_cols])
            dir_map = {c: d for c, d in criteria_list}

            # Normalizacja kryteriów (0..1)
            norm_df = df_filtered.copy()
            numeric_cols = [c for c in criteria_cols if c in norm_df.columns and pd.api.types.is_numeric_dtype(norm_df[c])]
            for col in numeric_cols:
                col_min = norm_df[col].min()
                col_max = norm_df[col].max()
                if pd.isna(col_min) or pd.isna(col_max) or col_min == col_max:
                    norm_df[col + "_norm"] = 0.5
                else:
                    vals = (norm_df[col] - col_min) / (col_max - col_min)
                    if dir_map.get(col, "Max") == "Max":
                        norm_df[col + "_norm"] = vals
                    else:
                        norm_df[col + "_norm"] = 1 - vals

            # Skumulowany wynik kryteriów wg wag
            norm_df["criteria_score"] = 0.0
            sum_w = 0.0
            for col in numeric_cols:
                w = float(weights_map.get(col, 0.0))
                sum_w += w
                norm_df["criteria_score"] += norm_df[col + "_norm"] * w
            if sum_w > 0:
                norm_df["criteria_score"] = norm_df["criteria_score"] / sum_w
            else:
                norm_df["criteria_score"] = 0.0

            # Agregacja opinii z uwzględnieniem typu lokatora
            loc_type = st.session_state.get("locator_type", None)
            if not reviews_df.empty and "HouseId" in reviews_df.columns and "Satisfaction" in reviews_df.columns:
                rev = reviews_df.copy()
                rev["rev_w"] = np.where(rev.get("ReviewerType") == loc_type, 0.7, 0.3)
                try:
                    agg = rev.groupby("HouseId").apply(lambda g: np.average(g["Satisfaction"].astype(float), weights=g["rev_w"])).rename("review_score").reset_index()
                    # normalizacja review_score
                    if not agg["review_score"].empty:
                        rmin, rmax = agg["review_score"].min(), agg["review_score"].max()
                        if rmin == rmax:
                            agg["review_score_norm"] = 0.5
                        else:
                            agg["review_score_norm"] = (agg["review_score"] - rmin) / (rmax - rmin)
                    else:
                        agg["review_score_norm"] = np.nan
                    # przygotuj tylko potrzebne kolumny i dołącz
                    agg2 = agg[["HouseId", "review_score_norm"]].rename(columns={"review_score_norm": "review_score"})
                    if "review_score" in norm_df.columns:
                        norm_df = norm_df.drop(columns=["review_score"])
                    if "Id" in norm_df.columns:
                        norm_df = norm_df.merge(agg2.rename(columns={"HouseId": "Id"}), on="Id", how="left")
                except Exception as e:
                    st.error(f"Błąd przy agregacji opinii: {e}")
            if "review_score" not in norm_df.columns:
                norm_df["review_score"] = np.nan

            # Finalny DF - usuń zduplikowane kolumny jeśli jakieś pozostały
            final_df = norm_df.copy()
            if final_df.columns.duplicated().any():
                st.warning("Wykryto zduplikowane nazwy kolumn po przetworzeniu. Usunięto duplikaty (zachowano pierwsze wystąpienia).")
                final_df = final_df.loc[:, ~final_df.columns.duplicated()]

            st.write("### Finalny DF wejściowy do algorytmów (po filtrach i agregacji)")
            st.dataframe(final_df, width="stretch")

            if st.button("Zapisz finalny DF dla algorytmów"):
                st.session_state["alg_input_df"] = final_df
                st.success("Zapisano finalny DataFrame do st.session_state['alg_input_df'].")

# -----------------------------------------------------------------------

# --- ZAKŁADKA 4: ---
with tab4:
    pass

# --- ZAKŁADKA 5: ---
with tab5:
    pass


