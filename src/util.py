def apply_criteria_directions(df, criteria_meta):
    df_mod = df.copy()

    for col, meta in criteria_meta.items():
        if meta["direction"] == "min":
            # bezpieczne odwrócenie (skala względna)
            max_val = df_mod[col].max()
            min_val = df_mod[col].min()
            df_mod[col] = max_val + min_val - df_mod[col]

    return df_mod