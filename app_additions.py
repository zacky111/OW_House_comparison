"""# agregacja opinii i dołączenie metryk do danych mieszkań
    if "reviews" in st.session_state:
        st.write(f"Opinie załadowane: {len(st.session_state['reviews'])} wierszy")
        if st.button("Połącz agregowane metryki opinii z danymi mieszkań"):
            if df.empty:
                st.error("Najpierw załaduj dane mieszkań.")
            else:
                rev = st.session_state["reviews"].copy()
                agg = rev.groupby("HouseId").agg(
                    AvgSatisfaction = ("Satisfaction", "mean"),
                    AvgNoise = ("Noise", "mean"),
                    AvgComment = ("CommentScore", "mean"),
                    ReviewCount = ("ReviewId", "count")
                ).reset_index()
                merged = df.merge(agg, left_on="Id", right_on="HouseId", how="left")
                merged = merged.drop(columns=["HouseId"])
                st.session_state["data"] = merged
                st.success("Dane połączone. Dodano kolumny: AvgSatisfaction, AvgNoise, AvgComment, ReviewCount.")
                st.dataframe(merged.head(), use_container_width=True)

        if st.button("Zapisz dane mieszkań z metrykami opinii (src/data/house_data_with_reviews.csv)"):
            try:
                out = Path(__file__).resolve().parent / "src" / "data" / "house_data_with_reviews.csv"
                st.session_state["data"].to_csv(out, index=False)
                st.success(f"Zapisano: {out}")
            except Exception as e:
                st.error(f"Błąd zapisu: {e}")

"""