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
from src.alg.alg1 import calculate_topsis_score
from src.alg.alg2 import RSM_alg

# data operations
from src.alg.data_cleansing import data_cleansing
from src.util import apply_criteria_directions

# visual
from visual import VISUAL_MD

algorithms = {
    "Algorytm TOPSIS": calculate_topsis_score,
    "Algorytm RSM": RSM_alg,
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


tabs = ["Import danych", "Dane", "Dostosowanie kryteriów", "Wybór algorytmu"]
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = tabs[0]
active_tab = st.radio("", tabs, index=tabs.index(st.session_state["active_tab"]), key="main_tab_radio", horizontal=True)
st.session_state["active_tab"] = active_tab

# mapuj poprzednie bloki 'with tabX' na warunki:
if active_tab == "Import danych":
    # --- ZAKŁADKA 1: Import danych CSV ---
    with st.expander("Import danych (CSV)", expanded=True):
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

elif active_tab == "Dane":
    # --- ZAKŁADKA 2: Dane ---
    with st.expander("Podgląd danych", expanded=True):
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

elif active_tab == "Dostosowanie kryteriów":
    # --- ZAKŁADKA 3: Dostosowanie kryteriów ---
    with st.expander("Nadaj ważność kryteriom", expanded=True):
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

            suggested_directions = {
                "Area": "max",
                "Bedrooms": "max",
                "Bathrooms": "max",
                "Floors": "max",
                "YearBuilt": "max",
                "Location": "max",
                "Condition": "max",
                "Garage": "max",
                "Price": "min",
                "Developer": "max",
            }
            
            suggested_directions_meaning={
                "Area": "Dla max, większy metraż jest lepszy",
                "Bedrooms": "Dla max, więcej sypialni jest lepsze",
                "Bathrooms": "Dla max, więcej łazienek jest lepsze",
                "Floors": "Dla max, więcej pięter jest lepsze",
                "YearBuilt": "Dla max, nowszy rok budowy jest lepszy",
                "Location": "Dla max, lepsza lokalizacja jest lepsza",
                "Condition": "Dla max, lepszy stan techniczny jest lepszy",
                "Garage": "Dla max, więcej miejsc parkingowych jest lepsze",
                "Price": "Dla min, niższa cena jest lepsza",
                "Developer": "Dla max, lepszy deweloper jest lepszy",
            }

            # Wyświetl suwaki dla kryteriów (bez Id) oraz wybór kierunku (min/max)
            for i, name in enumerate(criteria_cols):
                left, middle, right = st.columns([2,2, 0.5])
                with left:
                    st.markdown(f"**{name}**")
                with middle:
                    st.slider(
                        label=f"Waga kryterium {name}",
                        min_value=0.0,
                        max_value=1.0,
                        step=0.05,
                        key=f"weight_{i}",
                        label_visibility="collapsed"
                    )
                with right:
                    direction = st.selectbox(
                        "Kierunek",
                        ["max", "min"],
                        index=0,
                        key=f"dir_{name}",
                        label_visibility="collapsed",
                        help=f"Zaznacz 'max', jeśli wyższe wartości są lepsze dla kryterium '{name}'. Zaznacz 'min', jeśli niższe wartości są lepsze."
        )
                # wytłumaczenie sugerowanego kierunku dla tego kryterium
                suggested = suggested_directions.get(name)
                if suggested:
                    st.caption(f"Sugerowany kierunek dla '{name}': **{suggested}**")
                meaning = suggested_directions_meaning.get(name, "")
                if meaning:
                    st.caption(f"{meaning}.")


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

            # =========================
            # 2. ZAPIS KIERUNKÓW
            # =========================
            criteria_directions = {
                name: st.session_state.get(f"dir_{name}", "max")
                for name in criteria_cols
            }
            st.session_state["criteria_directions"] = criteria_directions

            df_alg = df.copy()

            df_alg[criteria_cols] = apply_criteria_directions(
                df_alg[criteria_cols],
                {
                    c: {"direction": criteria_directions[c]}
                    for c in criteria_cols
                }
            )

            st.session_state["alg_input_df"] = df_alg



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

        # typ lokatora
            loc_type = st.session_state.get("locator_type")
            loc_desc = st.session_state.get("locator_description")
            if loc_type:
                st.markdown("### Typ lokatora")
                st.write(f"**{loc_type}**")
                if loc_desc:
                    st.info(loc_desc)
            else:
                st.warning("Nie wybrano typu lokatora.")

            # Wybrani developerzy
            selected_devs = st.session_state.get("selected_developers", [])

            st.markdown("### Wybrani developerzy")
            if selected_devs:
                st.write(", ".join(selected_devs))
            else:
                st.warning("Nie wybrano żadnych developerów.")


elif active_tab == "Wybór algorytmu":
    # --- ZAKŁADKA 4: Wybór i uruchomienie algorytmu ---
    with st.expander("Wybierz i uruchom algorytm", expanded=True):

        alg_choice = st.selectbox("Algorytm:", options=list(algorithms.keys()))
        alg_func = algorithms[alg_choice]

        alg_df = st.session_state.get(
            "alg_input_df",
            st.session_state.get("data", pd.DataFrame())
        )

        if alg_df.empty:
            st.info("Brak danych wejściowych dla algorytmu.")
            st.stop()

        # kolumny numeryczne
        numeric_cols = [
            c for c in alg_df.columns
            if pd.api.types.is_numeric_dtype(alg_df[c]) and c != "Id"
        ]

        if not numeric_cols:
            st.error("Brak kryteriów numerycznych.")
            st.stop()

        st.write("Kryteria użyte w algorytmie:", ", ".join(numeric_cols))

        top_n = st.number_input(
            "Pokaż top N wyników",
            min_value=1,
            max_value=len(alg_df),
            value=min(10, len(alg_df)),
            step=1
        )

        # =============================
        # PRZYCISK – TYLKO LICZENIE
        # =============================
        if st.button("Uruchom algorytm"):
            try:
                X = alg_df[numeric_cols].copy()
                if X.isna().any().any():
                    X = X.fillna(X.mean())

                weights_map = st.session_state.get("criteria_weights", {})
                weights = [float(weights_map.get(c, 1.0)) for c in numeric_cols]
                if sum(weights) == 0:
                    weights = None

                results = alg_func(X.values, weights=weights)

                res_rows = []
                for idx, score in results[:top_n]:
                    row_id = int(alg_df.iloc[idx]["Id"]) if "Id" in alg_df.columns else idx
                    res_rows.append({
                        "Id": row_id,
                        "df_index": alg_df.index[idx],
                        "score": float(score)
                    })

                st.session_state["alg_results"] = pd.DataFrame(res_rows)
                st.session_state["show_house_id"] = None
                st.success("Algorytm wykonany.")

            except Exception as e:
                st.error(f"Błąd algorytmu: {e}")

        # ==================================
        # WYŚWIETLANIE WYNIKÓW (PERSIST)
        # ==================================
        res_df = st.session_state.get("alg_results", pd.DataFrame())

        if res_df.empty:
            st.info("Brak wyników — uruchom algorytm.")
            st.stop()

        st.write("### Wyniki algorytmu")
        st.dataframe(
            res_df.drop(columns=["df_index"], errors="ignore"),
            width="stretch"
            )

        st.write("### 🏆 Ranking mieszkań (szczegóły)")

        for i, row in res_df.iterrows():
            hid = int(row["Id"])
            score = float(row["score"])

            with st.expander(f"{i+1}. Mieszkanie Id {hid} — score {score:.3f}", expanded=False):

                house_rows = alg_df[alg_df["Id"] == hid]
                if house_rows.empty:
                    st.warning("Brak danych mieszkania.")
                    continue

                house = house_rows.iloc[0]

                show_cols = [
                    "Area","Bedrooms","Bathrooms","Floors","YearBuilt",
                    "Location","Condition","Garage","Price",
                    "criteria_score","review_score","Developer"
                ]
                available = [c for c in show_cols if c in alg_df.columns]

                details_df = (
                    house[available]
                    .astype(str)
                    .to_frame("Wartość")
                    .reset_index()
                    .rename(columns={"index": "Kryterium"})
                )

                st.table(details_df.set_index("Kryterium"))

                # opinie lokatorów
                reviews_df = st.session_state.get("reviews", pd.DataFrame())
                if not reviews_df.empty and "HouseId" in reviews_df.columns:
                    house_reviews = reviews_df[reviews_df["HouseId"] == hid]
                    if not house_reviews.empty:
                        st.write("### Opinie lokatorów")
                        st.dataframe(
                            house_reviews[
                                ["ReviewerType","Satisfaction","Noise",
                                "Neighbors","Maintenance","CommentScore","Date"]
                            ],
                            width="stretch"
                        )
                    else:
                        st.info("Brak opinii dla tego mieszkania.")
