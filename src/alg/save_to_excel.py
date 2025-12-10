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

