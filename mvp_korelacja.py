import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Wczytanie danych z głosowania MVP (z Twojego zrzutu ekranu)
mvp_data = {
    'Player': [
        'Nikola Jokić', 'Shai Gilgeous-Alexander', 'Luka Dončić', 
        'Giannis Antetokounmpo', 'Jalen Brunson', 'Jayson Tatum', 
        'Anthony Edwards', 'Domantas Sabonis', 'Kevin Durant'
    ],
    'MVP_Total_Points': [926, 640, 566, 192, 142, 86, 18, 3, 1]
}
df_mvp = pd.DataFrame(mvp_data)

# 2. Wczytanie Twoich metryk z pliku CSV
try:
    df_metrics = pd.read_csv('ranking_comparison.csv')
except FileNotFoundError:
    print("Błąd: Nie znaleziono pliku 'ranking_comparison.csv'.")
    exit()

kolumna_z_nazwiskami_csv = 'Player' 

# Opcjonalnie: ujednolicenie wielkości liter
df_mvp['Player'] = df_mvp['Player'].str.lower().str.strip()
df_metrics[kolumna_z_nazwiskami_csv] = df_metrics[kolumna_z_nazwiskami_csv].str.lower().str.strip()

# 3. Połączenie obu tabel na podstawie nazwiska gracza
df_merged = pd.merge(df_mvp, df_metrics, left_on='Player', right_on=kolumna_z_nazwiskami_csv, how='inner')

if df_merged.empty:
    print("Uwaga: Nie udało się połączyć tabel. Sprawdź, czy nazwiska się zgadzają w obu plikach.")
else:
    print(f"Udało się połączyć dane dla {len(df_merged)} zawodników.\n")

    # 4. Obliczenie korelacji (Pearsona)
    korelacje = df_merged.corr(numeric_only=True)['MVP_Total_Points'].sort_values(ascending=False)
    
    # Usunięcie samej kolumny MVP_Total_Points z wyników (korelacja 1.0)
    korelacje = korelacje.drop('MVP_Total_Points')

    # 5. Odfiltrowanie metryk kończących się na _rank i _norm
    # Znak tyldy (~) oznacza negację, więc zostawiamy wszystko to, co NIE ma tych końcówek
    korelacje_filtered = korelacje[~korelacje.index.str.endswith(('_rank', '_norm','_ranga','_rang',))]

    print("Korelacja Twoich metryk z punktami w głosowaniu MVP (odfiltrowane):")
    print("-" * 50)
    print(korelacje_filtered)

    # 6. Wizualizacja graficzna wyników
    # Ustawienie stylu wykresu
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 6))

    # Stworzenie wykresu słupkowego poziomego (ładniejszy i czytelniejszy dla długich nazw)
    ax = sns.barplot(
        x=korelacje_filtered.values, 
        y=korelacje_filtered.index, 
        hue=korelacje_filtered.index,
        palette="coolwarm", 
        legend=False
    )

    # Dodanie tytułu i etykiet
    plt.title('Korelacja metryk z wynikami MVP (bez rang i wartości normowanych)', fontsize=14, pad=15)
    plt.xlabel('Współczynnik korelacji', fontsize=12)
    plt.ylabel('Metryka', fontsize=12)

    # Dodanie pionowej linii wyznaczającej zero (dla wartości dodatnich i ujemnych)
    plt.axvline(x=0, color='black', linestyle='-', linewidth=1)

    # Dodanie konkretnych wartości liczbowych na słupkach
    for i in ax.containers:
        ax.bar_label(i, fmt='%.3f', padding=5)

    # Optymalizacja marginesów i wyświetlenie wykresu
    plt.tight_layout()
    plt.show()