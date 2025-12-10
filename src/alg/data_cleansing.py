def data_cleansing(df):
    """
    Cleanses the input DataFrame by handling missing values and removing duplicates.

    Parameters:
    df (pd.DataFrame): The input DataFrame to be cleansed.

    Returns:
    pd.DataFrame: The cleansed DataFrame.
    """
    # Remove duplicate rows
    df = df.drop_duplicates()

    # Handle missing values by filling them with the mean of the column
    for column in df.select_dtypes(include=['number']).columns:
        mean_value = df[column].mean()
        df[column].fillna(mean_value, inplace=True)

    # Swap categorical values to numerical (location, condition, garage)
    categorical_mappings = {
        "location": {"city_center": 3, "suburbs": 2, "rural": 1},
        "condition": {"new": 3, "good": 2, "needs_renovation": 1},
        "garage": {"yes": 1, "no": 0}
    }

    for column, mapping in categorical_mappings.items():
        if column in df.columns:
            df[column] = df[column].map(mapping)

    # Create criteria "yearbuilt" into "age" (the lower the better)

    return df