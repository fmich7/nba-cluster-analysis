"""
Skrypt generujacy Jupyter Notebook (.ipynb) z pelna analiza rankingowa
graczy NBA Playoffs 2023/24 — Metody Analizy Danych, Projekt 1a.
"""
import nbformat as nbf

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3"
    },
    "language_info": {
        "name": "python",
        "version": "3.12.0"
    }
}

cells = []

def md(source):
    cells.append(nbf.v4.new_markdown_cell(source))

def code(source):
    cells.append(nbf.v4.new_code_cell(source))

# ==========================================================================
# TYTUL I METADANE
# ==========================================================================
md(r"""# Ranking graczy NBA Playoffs 2023/24
## Metody Analizy Danych — Projekt 1a (Porządkowanie obiektów)

**Autorzy:** Filip Michalski, Bartek Binda

**Data:** Marzec 2026
""")

# ==========================================================================
# ABSTRAKT I SLOWA KLUCZOWE
# ==========================================================================
md(r"""## Abstrakt

Celem niniejszej pracy jest porządkowanie (ranking) graczy NBA Playoffs sezonu 2023/24
przy użyciu trzech metod wielokryterialnej analizy decyzyjnej: SAW (*Simple Additive Weighting*),
TOPSIS (*Technique for Order of Preference by Similarity to Ideal Solution*) oraz metody
syntetycznego miernika rozwoju Hellwiga.
Analizę przeprowadzono na zbiorze 117 graczy (po filtracji: min. 4 mecze, min. 15 minut/mecz),
opisanych 8 zmiennymi diagnostycznymi (6 stymulant i 2 destymulanty).
Wyniki wskazują na wysoką zgodność rankingów SAW i TOPSIS (ρ Spearmana = 0,987),
przy umiarkowanej korelacji obu metod z rankingiem Hellwiga (ρ = 0,84–0,88).
Różnice wynikają z zastosowania wag eksperckich w SAW/TOPSIS vs. równoważenia zmiennych w Hellwigu.
Najlepszymi graczami wg średniej rangi okazali się Nikola Jokić, LeBron James i Shai Gilgeous-Alexander.

**Słowa kluczowe:** ranking wielokryterialny, SAW, TOPSIS, metoda Hellwiga, NBA Playoffs, analiza danych
""")

# ==========================================================================
# 1. WPROWADZENIE
# ==========================================================================
md(r"""## 1. Wprowadzenie

Współczesny sport profesjonalny generuje ogromne ilości danych statystycznych.
W koszykówce NBA każdy mecz dostarcza dziesiątki wskaźników opisujących skuteczność
poszczególnych graczy — od punktów i zbiórek, po zaawansowane miary efektywności rzutowej.

Faza play-off NBA stanowi szczególnie interesujący obiekt analizy, ponieważ
gra staje się wolniejsza, bardziej taktyczna, a stawka poszczególnych meczów
jest znacznie wyższa niż w sezonie regularnym. Każdy punkt, zbiórka czy asysta
ma większą wagę, a gracze o najwyższych umiejętnościach mają szansę wyróżnić się
na tle rywali.

**Cel pracy:** Sporządzenie rankingu graczy NBA Playoffs 2023/24 z wykorzystaniem
trzech metod porządkowania obiektów wielokryterialnych oraz porównanie uzyskanych
wyników.

**Metody:**
1. **SAW** (Simple Additive Weighting) z normalizacją min-max
2. **TOPSIS** (Technique for Order of Preference by Similarity to Ideal Solution) z normalizacją wektorową
3. **Metoda Hellwiga** (syntetyczny miernik rozwoju) ze standaryzacją z-score

Praca jest zrealizowana w ramach projektu z przedmiotu *Metody Analizy Danych* (wariant 1a — porządkowanie obiektów).
""")

# ==========================================================================
# 2. PRZEGLAD LITERATURY
# ==========================================================================
md(r"""## 2. Przegląd literatury

Wielokryterialna analiza decyzyjna (*Multi-Criteria Decision Analysis*, MCDA) jest szeroko
stosowana w porządkowaniu obiektów opisanych wieloma zmiennymi. Trzy metody wybrane
w niniejszej pracy należą do najczęściej cytowanych podejść w literaturze.

**Metoda SAW** (*Simple Additive Weighting*) jest najprostszą techniką MCDA.
Polega na normalizacji wartości kryterialnych i obliczeniu sumy ważonej (Fishburn, 1967).
Jest powszechnie stosowana ze względu na intuicyjność i łatwość interpretacji.

**Metoda TOPSIS** została zaproponowana przez Hwanga i Yoona (1981). Opiera się
na wyznaczeniu odległości każdego obiektu od rozwiązania idealnego (najlepszego)
i anty-idealnego (najgorszego). Obiekt o największym stosunku odległości od anty-ideału
do sumy odległości od obu rozwiązań referencyjnych zajmuje najwyższą pozycję.
Metoda ta uwzględnia jednocześnie bliskość do ideału i oddalenie od anty-ideału,
co stanowi jej przewagę nad prostszymi podejściami (Hwang & Yoon, 1981).

**Metoda Hellwiga** (syntetyczny miernik rozwoju) jest polskim wkładem w taksonomię
numeryczną, zaproponowanym przez Zdzisława Hellwiga (1968). Metoda polega na
standaryzacji zmiennych, wyznaczeniu wzorca rozwoju oraz obliczeniu odległości
euklidesowych obiektów od tego wzorca. Syntetyczny miernik przyjmuje wartości
bliskie 1 dla obiektów najbliższych wzorcowi (Hellwig, 1968).

W kontekście sportu metody MCDA były stosowane m.in. do rankingowania drużyn
piłkarskich (Dadelo et al., 2014) oraz oceny efektywności zawodników NBA
(Sarlis & Tjortjis, 2020).
""")

# ==========================================================================
# 3. ZMIENNE
# ==========================================================================
md(r"""## 3. Opis zmiennych

### 3.1. Wybrane zmienne diagnostyczne (8)

Wybrano 8 zmiennych opisujących kluczowe aspekty gry koszykarza
— ofensywne (punkty, asysty, efektywność rzutowa), defensywne (zbiórki, przechwyty, bloki)
oraz negatywne (straty, faule):

| Nr | Zmienna | Opis | Charakter | Waga |
|----|---------|------|-----------|------|
| 1 | **PTS** | Punkty na mecz | Stymulanta | 0,25 |
| 2 | **TRB** | Zbiórki na mecz | Stymulanta | 0,15 |
| 3 | **AST** | Asysty na mecz | Stymulanta | 0,18 |
| 4 | **STL** | Przechwyty na mecz | Stymulanta | 0,10 |
| 5 | **BLK** | Bloki na mecz | Stymulanta | 0,08 |
| 6 | **eFG%** | Efektywna skuteczność rzutowa | Stymulanta | 0,14 |
| 7 | **TOV** | Straty na mecz | Destymulanta | 0,05 |
| 8 | **PF** | Faule osobiste na mecz | Destymulanta | 0,05 |

**Suma wag = 1,00**

### 3.2. Uzasadnienie wag eksperckich

- **PTS (0,25)** — Punkty są najważniejszym wyznacznikiem skuteczności ofensywnej w play-offach, gdzie każdy kosz ma dużą wagę.
- **AST (0,18)** — Asysty mierzą zdolność kreowania gry; kluczowe dla rozgrywających i liderów drużyn.
- **TRB (0,15)** — Zbiórki dają drugie szanse ataku (ofensywne) i kończą ataki rywala (defensywne).
- **eFG% (0,14)** — Efektywność rzutowa uwzględniająca wartość rzutów za 3 pkt; syntetyczna miara precyzji.
- **STL (0,10)** — Przechwyty generują szybkie ataki i odzwierciedlają aktywność defensywną.
- **BLK (0,08)** — Bloki chronią obręcz; ważne, ale rzadsze niż przechwyty.
- **TOV (0,05)** — Straty są kosztowne, ale nawet najlepsi gracze mają podwyższone TOV z uwagi na dużą rolę w ataku.
- **PF (0,05)** — Faule obniżają wartość gracza (ryzyko wykluczenia), ale są częściowo efektem agresywnej gry obronnej.

### 3.3. Usunięte zmienne (z uzasadnieniem)

- **3P%, FT%** — Procenty z zerową liczbą prób (0/0) dają 0%, co nie oznacza niskiej umiejętności, a jedynie brak prób. Np. Rudy Gobert ma 3P% = 0 (0 z 0 prób za 3 pkt), a Dereck Lively II ma 3P% = 1.0 (1/1). **eFG%** jest lepszą syntetyczną miarą skuteczności rzutowej.
- **MP (minuty na mecz)** — Dane są już średnimi per-game, więc czas gry jest pośrednio wbudowany w wartości bezwzględne (PTS, TRB, AST, ...). Włączenie MP powodowałoby podwójne liczenie i silną korelację z PTS (r > 0,8).
""")

# ==========================================================================
# 4. KOD - IMPORTY I KONFIGURACJA
# ==========================================================================
md(r"""## 4. Wstępna analiza danych

### 4.1. Wczytanie i przygotowanie danych
""")

code(r"""import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from scipy import stats as sp_stats

# Konfiguracja wykresow
plt.rcParams.update({
    "figure.dpi": 120,
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.labelsize": 10,
})
sns.set_style("whitegrid")

# --- Konfiguracja zmiennych i wag ---
STIMULANTS = ["PTS", "TRB", "AST", "STL", "BLK", "eFG%"]
DESTIMULANTS = ["TOV", "PF"]
ALL_VARIABLES = STIMULANTS + DESTIMULANTS

WEIGHTS = {
    "PTS": 0.25, "AST": 0.18, "TRB": 0.15, "eFG%": 0.14,
    "STL": 0.10, "BLK": 0.08, "TOV": 0.05, "PF": 0.05,
}

print(f"Suma wag: {sum(WEIGHTS.values()):.2f}")
print(f"Stymulanty ({len(STIMULANTS)}): {STIMULANTS}")
print(f"Destymulanty ({len(DESTIMULANTS)}): {DESTIMULANTS}")
""")

code(r"""# Wczytanie danych
df_raw = pd.read_csv("Playoffs.csv", sep=";")

if "Rk" in df_raw.columns:
    df_raw = df_raw.drop(columns=["Rk"])

# Konwersja kolumn numerycznych
numeric_cols = [c for c in df_raw.columns if c not in ("Player", "Pos", "Tm")]
for col in numeric_cols:
    df_raw[col] = pd.to_numeric(df_raw[col], errors="coerce")

print(f"Surowy zbior danych: {len(df_raw)} graczy, {len(df_raw.columns)} kolumn")
print(f"\nPrzykladowe dane (5 pierwszych graczy):")
df_raw[["Player", "Pos", "Tm", "G", "MP"] + ALL_VARIABLES].head()
""")

code(r"""# Filtracja: minimum 4 mecze i 15 minut na mecz
MIN_GAMES = 4
MIN_MP = 15.0

n_before = len(df_raw)
df = df_raw[(df_raw["G"] >= MIN_GAMES) & (df_raw["MP"] >= MIN_MP)].copy()
df = df.reset_index(drop=True)

print(f"Przed filtracja: {n_before} graczy")
print(f"Po filtracji (G >= {MIN_GAMES}, MP >= {MIN_MP}): {len(df)} graczy")
print(f"\nRozklad pozycji:")
print(df["Pos"].value_counts().sort_index().to_string())
""")

# ==========================================================================
# 4.2. BRAKI DANYCH
# ==========================================================================
md(r"""### 4.2. Braki danych""")

code(r"""# Sprawdzenie brakow danych w zmiennych diagnostycznych
missing_info = []
for var in ALL_VARIABLES:
    n_miss = df[var].isna().sum()
    missing_info.append({
        "Zmienna": var,
        "Braki": n_miss,
        "% braków": f"{100 * n_miss / len(df):.2f}%"
    })

missing_df = pd.DataFrame(missing_info)
print("Braki danych w zmiennych diagnostycznych:")
print(missing_df.to_string(index=False))

if missing_df["Braki"].sum() == 0:
    print("\n=> Brak braków danych w wybranych zmiennych. Imputacja nie jest wymagana.")
else:
    print("\n=> Braki danych uzupelniono mediana.")
    for var in ALL_VARIABLES:
        if df[var].isna().any():
            df[var] = df[var].fillna(df[var].median())
""")

# ==========================================================================
# 4.3. STATYSTYKI OPISOWE
# ==========================================================================
md(r"""### 4.3. Statystyki opisowe""")

code(r"""# Statystyki opisowe
records = []
for var in ALL_VARIABLES:
    vals = df[var].dropna()
    records.append({
        "Zmienna": var,
        "Średnia": round(vals.mean(), 3),
        "Mediana": round(vals.median(), 3),
        "Minimum": round(vals.min(), 3),
        "Maksimum": round(vals.max(), 3),
        "Odch. std.": round(vals.std(ddof=1), 3),
        "Skośność": round(sp_stats.skew(vals, bias=False), 3),
        "N": len(vals),
    })

stats_df = pd.DataFrame(records)
stats_df
""")

md(r"""**Komentarz do statystyk opisowych:**

- **PTS** (punkty): Średnia 13,7 pkt/mecz, mediana 12,2 — rozkład prawoskośny (skośność 0,77), co oznacza grupę elitarnych zawodników z wyraźnie wyższymi wynikami.
- **TRB** (zbiórki): Średnia 5,3, mediana 4,4 — silna prawoskośność (1,15), dominacja środkowych i silnych skrzydłowych.
- **AST** (asysty): Średnia 2,9, mediana 2,2 — rozkład prawoskośny (0,95); rozgrywający mają znacznie więcej asyst.
- **eFG%**: Średnia 0,530, niska zmienność (std = 0,075), lekko lewoskośny (-0,87) — kilku graczy z wyjątkowo niską skutecznością.
- **TOV** (straty): Średnia 1,49, mediana 1,3 — prawoskośny; najlepsi gracze tracą piłkę częściej (większa odpowiedzialność).
- **PF** (faule): Średnia 2,36, mała skośność (0,20) — najbardziej symetryczny rozkład ze wszystkich zmiennych.
""")

# ==========================================================================
# 4.4. BOXPLOTY
# ==========================================================================
md(r"""### 4.4. Wykresy pudełkowe (boxploty)""")

code(r"""fig, axes = plt.subplots(2, 4, figsize=(16, 8))
axes = axes.flatten()

for i, var in enumerate(ALL_VARIABLES):
    ax = axes[i]
    vals = df[var].dropna()
    bp = ax.boxplot(vals, vert=True, patch_artist=True,
                    boxprops=dict(facecolor="#4C72B0", alpha=0.7),
                    medianprops=dict(color="yellow", linewidth=2))
    ax.set_title(var, fontsize=12, fontweight="bold")
    ax.set_xticks([])

fig.suptitle("Wykresy pudełkowe zmiennych diagnostycznych", fontsize=14, fontweight="bold")
fig.tight_layout()
plt.show()
""")

# ==========================================================================
# 4.5. HISTOGRAMY
# ==========================================================================
md(r"""### 4.5. Histogramy""")

code(r"""fig, axes = plt.subplots(2, 4, figsize=(16, 8))
axes = axes.flatten()

for i, var in enumerate(ALL_VARIABLES):
    ax = axes[i]
    vals = df[var].dropna()
    ax.hist(vals, bins=15, color="#4C72B0", alpha=0.8, edgecolor="white")
    ax.set_title(var, fontsize=12, fontweight="bold")
    ax.set_ylabel("Liczba graczy")
    ax.axvline(vals.mean(), color="red", linestyle="--", linewidth=1, label="Średnia")
    ax.axvline(vals.median(), color="orange", linestyle="-.", linewidth=1, label="Mediana")
    if i == 0:
        ax.legend(fontsize=8)

fig.suptitle("Histogramy zmiennych diagnostycznych", fontsize=14, fontweight="bold")
fig.tight_layout()
plt.show()
""")

# ==========================================================================
# 4.6. OBSERWACJE ODSTAJACE
# ==========================================================================
md(r"""### 4.6. Obserwacje odstające (metoda IQR)""")

code(r"""# Wykrywanie obserwacji odstajacych metoda IQR (1.5 * IQR)
outlier_records = []
for var in ALL_VARIABLES:
    vals = df[var].dropna()
    q1, q3 = vals.quantile(0.25), vals.quantile(0.75)
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    mask = (df[var] < lower) | (df[var] > upper)
    outliers = df.loc[mask, ["Player", "Pos", var]]
    for _, row in outliers.iterrows():
        outlier_records.append({
            "Zmienna": var,
            "Gracz": row["Player"],
            "Pozycja": row["Pos"],
            "Wartość": row[var],
            "Dolna gr.": round(lower, 3),
            "Górna gr.": round(upper, 3),
        })

outliers_df = pd.DataFrame(outlier_records)
print(f"Wykryto {len(outliers_df)} obserwacji odstających:")
outliers_df
""")

md(r"""**Decyzja:** Obserwacje odstające **nie są usuwane**.

**Uzasadnienie:** W kontekście sportu wartości skrajne reprezentują elitarnych graczy
(np. Joel Embiid — 33 pkt/mecz, Anthony Davis — 15,6 zbiórek/mecz). Ich usunięcie
zniekształciłoby ranking, gdyż właśnie ci gracze powinni zajmować czołowe pozycje.
Metody rankingowe (SAW, TOPSIS, Hellwig) są odporne na obserwacje odstające dzięki
mechanizmom normalizacji.
""")

# ==========================================================================
# 4.7. KORELACJE
# ==========================================================================
md(r"""### 4.7. Macierz korelacji""")

code(r"""corr = df[ALL_VARIABLES].corr(method="pearson")

fig, ax = plt.subplots(figsize=(10, 8))
mask = np.zeros_like(corr, dtype=bool)
sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", center=0,
            square=True, linewidths=0.5, ax=ax,
            xticklabels=ALL_VARIABLES, yticklabels=ALL_VARIABLES,
            vmin=-1, vmax=1)
ax.set_title("Macierz korelacji Pearsona między zmiennymi diagnostycznymi",
             fontsize=13, fontweight="bold")
fig.tight_layout()
plt.show()

print("\nNajsilniejsze korelacje (|r| > 0.5):")
for i in range(len(ALL_VARIABLES)):
    for j in range(i+1, len(ALL_VARIABLES)):
        r = corr.iloc[i, j]
        if abs(r) > 0.5:
            print(f"  {ALL_VARIABLES[i]} ↔ {ALL_VARIABLES[j]}: r = {r:.3f}")
""")

md(r"""**Komentarz do korelacji:**

- **PTS ↔ TOV (r ≈ 0,78):** Gracze z dużą liczbą punktów częściej tracą piłkę — jest to oczekiwane, ponieważ liderzy ofensywni mają piłkę w rękach znacznie częściej.
- **PTS ↔ AST (r ≈ 0,74):** Najlepsi strzelcy jednocześnie kreują grę dla kolegów.
- **PTS ↔ TRB (r ≈ 0,50):** Gracze dominujący na tablicach często też zdobywają dużo punktów (typowe dla centrów i power forwardów).
- **AST ↔ TOV (r ≈ 0,62):** Rozgrywający, którzy dużo asystują, również częściej tracą piłkę.

**Ważne:** Korelacje te są oczekiwane w koszykówce i **nie dyskwalifikują zmiennych** w metodach rankingowych.
W odróżnieniu od regresji, w SAW, TOPSIS i Hellwigu współliniowość nie powoduje niestabilności wyników,
ponieważ każda zmienna mierzy inny aspekt gry (ofensywa, obrona, kreacja, efektywność).
""")

# ==========================================================================
# 5. METODY
# ==========================================================================
md(r"""## 5. Metody rankingowe

### 5.1. SAW — Simple Additive Weighting (Fishburn, 1967)

Metoda SAW (*Simple Additive Weighting*) polega na normalizacji wartości zmiennych
do przedziału $[0, 1]$ metodą min-max, a następnie obliczeniu ważonej sumy znormalizowanych wartości.

**Normalizacja min-max:**

Dla stymulanty:
$$r_{ij} = \frac{x_{ij} - x_{j}^{\min}}{x_{j}^{\max} - x_{j}^{\min}}$$

Dla destymulanty:
$$r_{ij} = \frac{x_{j}^{\max} - x_{ij}}{x_{j}^{\max} - x_{j}^{\min}}$$

**Wskaźnik syntetyczny:**
$$S_i = \sum_{j=1}^{m} w_j \cdot r_{ij}$$

gdzie $w_j$ — waga $j$-tej zmiennej, $\sum w_j = 1$.
""")

code("""def ranking_saw(df, stimulants, destimulants, weights):
    # SAW (Simple Additive Weighting) z normalizacja min-max
    result = df[["Player", "Pos", "Tm"]].copy()
    all_vars = stimulants + destimulants

    for var in all_vars:
        vals = df[var].values.astype(float)
        v_min, v_max = vals.min(), vals.max()
        denom = v_max - v_min
        if denom == 0:
            result[f"{var}_norm"] = 0.0
        elif var in stimulants:
            result[f"{var}_norm"] = (vals - v_min) / denom
        else:
            result[f"{var}_norm"] = (v_max - vals) / denom

    score = np.zeros(len(result))
    for var in all_vars:
        w = weights.get(var, 0.0)
        score += w * result[f"{var}_norm"].values
    result["SAW_score"] = score
    result["SAW_rank"] = result["SAW_score"].rank(ascending=False, method="min").astype(int)
    result = result.sort_values("SAW_rank").reset_index(drop=True)

    norm_cols = [c for c in result.columns if c.endswith("_norm")]
    result = result.drop(columns=norm_cols)
    return result

saw_df = ranking_saw(df, STIMULANTS, DESTIMULANTS, WEIGHTS)
print("=== TOP 15 — SAW ===")
saw_df[["Player", "Pos", "Tm", "SAW_score", "SAW_rank"]].head(15)
""")

# --- TOPSIS ---
md(r"""### 5.2. TOPSIS — Technique for Order of Preference by Similarity to Ideal Solution (Hwang & Yoon, 1981)

Metoda TOPSIS opiera się na wyznaczeniu odległości euklidesowej obiektu od rozwiązania
idealnego (najlepszego) i anty-idealnego (najgorszego).

**Krok 1 — Normalizacja wektorowa:**
$$r_{ij} = \frac{x_{ij}}{\sqrt{\sum_{i=1}^{n} x_{ij}^2}}$$

**Krok 2 — Ważona macierz decyzyjna:**
$$v_{ij} = w_j \cdot r_{ij}$$

**Krok 3 — Rozwiązanie idealne $A^+$ i anty-idealne $A^-$:**
$$A^+ = \{v_1^+, v_2^+, \ldots, v_m^+\}, \quad A^- = \{v_1^-, v_2^-, \ldots, v_m^-\}$$
Dla stymulant: $v_j^+ = \max_i v_{ij}$, $v_j^- = \min_i v_{ij}$;
Dla destymulant: $v_j^+ = \min_i v_{ij}$, $v_j^- = \max_i v_{ij}$.

**Krok 4 — Odległości euklidesowe:**
$$d_i^+ = \sqrt{\sum_{j=1}^{m}(v_{ij} - v_j^+)^2}, \quad d_i^- = \sqrt{\sum_{j=1}^{m}(v_{ij} - v_j^-)^2}$$

**Krok 5 — Wskaźnik syntetyczny:**
$$C_i = \frac{d_i^-}{d_i^+ + d_i^-}, \quad C_i \in [0, 1]$$
""")

code("""def ranking_topsis(df, stimulants, destimulants, weights):
    # TOPSIS (Hwang & Yoon, 1981)
    result = df[["Player", "Pos", "Tm"]].copy()
    all_vars = stimulants + destimulants
    n = len(df)

    # 1. Normalizacja wektorowa
    norm_matrix = np.zeros((n, len(all_vars)))
    for j, var in enumerate(all_vars):
        vals = df[var].values.astype(float)
        denom = np.sqrt(np.sum(vals ** 2))
        norm_matrix[:, j] = vals / denom if denom != 0 else 0.0

    # 2. Wazona macierz decyzyjna
    w_array = np.array([weights.get(var, 0.0) for var in all_vars])
    weighted = norm_matrix * w_array

    # 3. Rozwiazanie idealne i anty-idealne
    a_plus = np.zeros(len(all_vars))
    a_minus = np.zeros(len(all_vars))
    for j, var in enumerate(all_vars):
        if var in stimulants:
            a_plus[j] = weighted[:, j].max()
            a_minus[j] = weighted[:, j].min()
        else:
            a_plus[j] = weighted[:, j].min()
            a_minus[j] = weighted[:, j].max()

    # 4. Odleglosci euklidesowe
    d_plus = np.sqrt(np.sum((weighted - a_plus) ** 2, axis=1))
    d_minus = np.sqrt(np.sum((weighted - a_minus) ** 2, axis=1))

    # 5. Score
    denom = d_plus + d_minus
    denom = np.where(denom == 0, 1e-10, denom)
    score = d_minus / denom

    result["TOPSIS_score"] = score
    result["TOPSIS_rank"] = result["TOPSIS_score"].rank(ascending=False, method="min").astype(int)
    result = result.sort_values("TOPSIS_rank").reset_index(drop=True)
    return result

topsis_df = ranking_topsis(df, STIMULANTS, DESTIMULANTS, WEIGHTS)
print("=== TOP 15 — TOPSIS ===")
topsis_df[["Player", "Pos", "Tm", "TOPSIS_score", "TOPSIS_rank"]].head(15)
""")

# --- HELLWIG ---
md(r"""### 5.3. Metoda Hellwiga — syntetyczny miernik rozwoju (Hellwig, 1968)

Metoda Hellwiga nie wykorzystuje wag eksperckich. Zamiast tego standaryzuje
zmienne (z-score) i wyznacza wzorzec rozwoju na podstawie wartości ekstremalnych.

**Krok 1 — Standaryzacja z-score:**
$$z_{ij} = \frac{x_{ij} - \bar{x}_j}{s_j}$$

**Krok 2 — Wzorzec rozwoju $z_0$:**
$$z_{0j} = \begin{cases} \max_i z_{ij} & \text{dla stymulant} \\ \min_i z_{ij} & \text{dla destymulant} \end{cases}$$

**Krok 3 — Odległość od wzorca:**
$$d_i = \sqrt{\sum_{j=1}^{m}(z_{ij} - z_{0j})^2}$$

**Krok 4 — Wartość graniczna:**
$$d_0 = \bar{d} + 2 \cdot s_d$$

**Krok 5 — Syntetyczny miernik rozwoju:**
$$S_i = 1 - \frac{d_i}{d_0}, \quad S_i \in (-\infty, 1]$$

Im bliżej 1, tym obiekt jest lepszy (bliższy wzorcowi rozwoju).
""")

code("""def ranking_hellwig(df, stimulants, destimulants):
    # Metoda Hellwiga (1968) - syntetyczny miernik rozwoju
    result = df[["Player", "Pos", "Tm"]].copy()
    all_vars = stimulants + destimulants
    n = len(df)

    # 1. Standaryzacja z-score
    z_matrix = np.zeros((n, len(all_vars)))
    for j, var in enumerate(all_vars):
        vals = df[var].values.astype(float)
        std = vals.std(ddof=1)
        z_matrix[:, j] = (vals - vals.mean()) / std if std != 0 else 0.0

    # 2. Wzorzec rozwoju
    z_ideal = np.zeros(len(all_vars))
    for j, var in enumerate(all_vars):
        if var in stimulants:
            z_ideal[j] = z_matrix[:, j].max()
        else:
            z_ideal[j] = z_matrix[:, j].min()

    # 3. Odleglosci od wzorca
    d = np.sqrt(np.sum((z_matrix - z_ideal) ** 2, axis=1))

    # 4. Wartosc graniczna
    d_0 = d.mean() + 2.0 * d.std(ddof=1)
    if d_0 == 0:
        d_0 = 1.0

    # 5. Syntetyczny miernik
    score = 1.0 - d / d_0

    result["Hellwig_score"] = score
    result["Hellwig_rank"] = result["Hellwig_score"].rank(ascending=False, method="min").astype(int)
    result = result.sort_values("Hellwig_rank").reset_index(drop=True)
    return result

hellwig_df = ranking_hellwig(df, STIMULANTS, DESTIMULANTS)
print("=== TOP 15 — HELLWIG ===")
hellwig_df[["Player", "Pos", "Tm", "Hellwig_score", "Hellwig_rank"]].head(15)
""")

# ==========================================================================
# 6. WYNIKI
# ==========================================================================
md(r"""## 6. Wyniki

### 6.1. Porównanie top graczy w trzech rankingach
""")

code(r"""# Laczenie rankingow
rankings = {"SAW": saw_df, "TOPSIS": topsis_df, "Hellwig": hellwig_df}

merged = pd.DataFrame()
for name, rdf in rankings.items():
    sub = rdf[["Player", f"{name}_score", f"{name}_rank"]].copy()
    if merged.empty:
        merged = sub
    else:
        merged = merged.merge(sub, on="Player", how="outer")

# Dodaj info o graczu
player_info = saw_df[["Player", "Pos", "Tm"]]
merged = merged.merge(player_info, on="Player", how="left")

# Srednia ranga
rank_cols = ["SAW_rank", "TOPSIS_rank", "Hellwig_rank"]
merged["Średnia_ranga"] = merged[rank_cols].mean(axis=1)
merged = merged.sort_values("Średnia_ranga").reset_index(drop=True)

# Wyswietl top 20
display_cols = ["Player", "Pos", "Tm",
                "SAW_score", "SAW_rank",
                "TOPSIS_score", "TOPSIS_rank",
                "Hellwig_score", "Hellwig_rank",
                "Średnia_ranga"]

print("=== TOP 20 GRACZY wg średniej rangi ===\n")
merged[display_cols].head(20)
""")

# --- BARPLOTY ---
md(r"""### 6.2. Wykresy słupkowe — top 15 graczy w każdym rankingu""")

code(r"""fig, axes = plt.subplots(1, 3, figsize=(20, 10))
colors = ["#4C72B0", "#DD8452", "#55A868"]

for idx, (name, rdf) in enumerate(rankings.items()):
    ax = axes[idx]
    top = rdf.head(15).iloc[::-1]
    score_col = f"{name}_score"
    players = top["Player"].values
    scores = top[score_col].values

    bars = ax.barh(range(len(players)), scores, color=colors[idx], alpha=0.85)
    ax.set_yticks(range(len(players)))
    ax.set_yticklabels(players, fontsize=9)
    ax.set_xlabel("Score", fontsize=11)
    ax.set_title(f"Top 15 — {name}", fontsize=13, fontweight="bold")

fig.suptitle("Rankingi graczy NBA Playoffs 2023/24 — Top 15",
             fontsize=15, fontweight="bold")
fig.tight_layout()
plt.show()
""")

# --- BUMP CHART ---
md(r"""### 6.3. Bump chart — porównanie pozycji graczy między rankingami""")

code(r"""method_names = list(rankings.keys())
TOP_N_BUMP = 15

# Zbierz rangi
all_ranks = {}
for name, rdf in rankings.items():
    for _, row in rdf.iterrows():
        player = row["Player"]
        if player not in all_ranks:
            all_ranks[player] = {}
        all_ranks[player][name] = row[f"{name}_rank"]

# Gracze w top N w przynajmniej jednym rankingu
top_players = set()
for name, rdf in rankings.items():
    top_players.update(rdf.head(TOP_N_BUMP)["Player"].values)

fig, ax = plt.subplots(figsize=(10, 12))
cmap = plt.get_cmap("tab20")
player_list = sorted(top_players)

for i, player in enumerate(player_list):
    if player not in all_ranks:
        continue
    ranks_for_player = all_ranks[player]
    xs, ys = [], []
    for j, method in enumerate(method_names):
        if method in ranks_for_player:
            xs.append(j)
            ys.append(ranks_for_player[method])

    color = cmap(i % 20)
    ax.plot(xs, ys, marker="o", color=color, linewidth=2, markersize=7, alpha=0.85)

    if ys:
        parts = player.split()
        short = parts[0][0] + ". " + " ".join(parts[1:]) if len(parts) >= 2 else player
        ax.annotate(short, (xs[-1] + 0.05, ys[-1]),
                    fontsize=7.5, va="center", color=color, fontweight="bold")

ax.set_xticks(range(len(method_names)))
ax.set_xticklabels(method_names, fontsize=13, fontweight="bold")
ax.set_ylabel("Pozycja w rankingu", fontsize=12)
ax.set_title(f"Bump chart — porównanie rankingów (gracze w top {TOP_N_BUMP})",
             fontsize=14, fontweight="bold")
ax.invert_yaxis()
ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
plt.show()
""")

# ==========================================================================
# 6.4. KORELACJE MIEDZY RANKINGAMI
# ==========================================================================
md(r"""### 6.4. Zgodność rankingów — korelacja Spearmana i tau Kendalla""")

code(r"""# Korelacja Spearmana
method_names = ["SAW", "TOPSIS", "Hellwig"]
rank_cols = [f"{m}_rank" for m in method_names]

spearman_matrix = pd.DataFrame(index=method_names, columns=method_names, dtype=float)
kendall_matrix = pd.DataFrame(index=method_names, columns=method_names, dtype=float)

for m1 in method_names:
    for m2 in method_names:
        r1 = merged[f"{m1}_rank"].values
        r2 = merged[f"{m2}_rank"].values
        rho, _ = sp_stats.spearmanr(r1, r2)
        tau, _ = sp_stats.kendalltau(r1, r2)
        spearman_matrix.loc[m1, m2] = round(rho, 4)
        kendall_matrix.loc[m1, m2] = round(tau, 4)

print("=== Macierz korelacji Spearmana ===")
print(spearman_matrix.to_string())
print()
print("=== Macierz tau Kendalla ===")
print(kendall_matrix.to_string())
""")

code(r"""# Heatmapa korelacji Spearmana
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

for ax, matrix, title, cmap_name in [
    (axes[0], spearman_matrix, "Korelacja Spearmana", "YlGn"),
    (axes[1], kendall_matrix, "Tau Kendalla", "YlOrRd")
]:
    vals = matrix.values.astype(float)
    sns.heatmap(vals, annot=True, fmt=".4f", cmap=cmap_name,
                xticklabels=matrix.columns, yticklabels=matrix.index,
                vmin=0.6, vmax=1.0, square=True, linewidths=1, ax=ax)
    ax.set_title(title, fontsize=13, fontweight="bold")

fig.suptitle("Zgodność między rankingami", fontsize=14, fontweight="bold")
fig.tight_layout()
plt.show()
""")

# --- SCATTER RANG ---
md(r"""### 6.5. Wykresy rozrzutu rang""")

code(r"""pairs = [("SAW", "TOPSIS"), ("SAW", "Hellwig"), ("TOPSIS", "Hellwig")]

fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))

for idx, (m1, m2) in enumerate(pairs):
    ax = axes[idx]
    x = merged[f"{m1}_rank"].values
    y = merged[f"{m2}_rank"].values

    ax.scatter(x, y, alpha=0.5, s=30, c="#4C72B0")
    lim = max(x.max(), y.max()) + 1
    ax.plot([1, lim], [1, lim], "r--", alpha=0.5, linewidth=1, label="y = x")
    ax.set_xlabel(f"Ranga {m1}", fontsize=11)
    ax.set_ylabel(f"Ranga {m2}", fontsize=11)
    ax.set_title(f"{m1} vs {m2}", fontsize=12, fontweight="bold")
    ax.set_aspect("equal")
    ax.legend(fontsize=9)

fig.suptitle("Porównanie rang między metodami", fontsize=14, fontweight="bold")
fig.tight_layout()
plt.show()
""")

md(r"""**Interpretacja zgodności rankingów:**

| Para metod | ρ Spearmana | τ Kendalla | Interpretacja |
|-----------|------------|------------|---------------|
| SAW ↔ TOPSIS | 0,987 | 0,903 | Bardzo wysoka zgodność |
| SAW ↔ Hellwig | 0,884 | 0,714 | Wysoka zgodność |
| TOPSIS ↔ Hellwig | 0,839 | 0,654 | Umiarkowanie wysoka zgodność |

- **SAW i TOPSIS** dają niemal identyczne wyniki (ρ = 0,987). Obie metody stosują te same wagi eksperckie — różnią się jedynie sposobem normalizacji (min-max vs. wektorowa).
- **Hellwig** daje nieco odmienne wyniki, ponieważ **nie stosuje wag eksperckich** — traktuje wszystkie zmienne równoważnie. W efekcie nagradza graczy o **zbalansowanym profilu** (np. Jarrett Allen: wysokie TRB, wysokie eFG%, niskie TOV, niskie PF).
- SAW i TOPSIS preferują graczy dominujących w wysoko ważonych zmiennych (PTS, AST), co tłumaczy dominację Jokića i LeBrona.
""")

# ==========================================================================
# 6.6 ANALIZA ROZNIC - CIEKAWE PRZYPADKI
# ==========================================================================
md(r"""### 6.6. Analiza wybranych graczy — największe różnice między metodami""")

code(r"""# Gracze z najwiekszymi roznami miedzy rankingami
merged["Rozstęp_rang"] = merged[rank_cols].max(axis=1) - merged[rank_cols].min(axis=1)

print("=== Gracze z NAJWIĘKSZYMI różnicami pozycji między rankingami ===\n")
biggest_diff = merged.nlargest(10, "Rozstęp_rang")
biggest_diff[["Player", "Pos", "SAW_rank", "TOPSIS_rank", "Hellwig_rank",
              "Średnia_ranga", "Rozstęp_rang"]]
""")

code(r"""# Analiza profilu kluczowych graczy
key_players = ["Nikola Joki\u0107", "Jarrett Allen", "Luka Don\u010di\u0107",
               "LeBron James", "Shai Gilgeous-Alexander", "Jalen Brunson",
               "Anthony Davis", "Evan Mobley", "Derrick White", "Joel Embiid"]

# Dopasuj nazwy (CSV moze miec inne kodowanie)
available = df["Player"].tolist()
matched = []
for kp in key_players:
    for ap in available:
        # Proste dopasowanie po poczatkowych literach
        if ap.startswith(kp[:5]) or kp.startswith(ap[:5]):
            matched.append(ap)
            break

print("=== Profile statystyczne kluczowych graczy ===\n")
mask = df["Player"].isin(matched)
if mask.sum() > 0:
    profile = df.loc[mask, ["Player", "Pos"] + ALL_VARIABLES].copy()
    profile = profile.set_index("Player")
    display(profile)
else:
    # Fallback: top 10 z merged
    top10_names = merged.head(10)["Player"].tolist()
    profile = df[df["Player"].isin(top10_names)][["Player", "Pos"] + ALL_VARIABLES].copy()
    profile = profile.set_index("Player")
    display(profile)
""")

md(r"""**Analiza wybranych przypadków:**

1. **Jarrett Allen** — #1 w Hellwigu, ale #14 w SAW i #20 w TOPSIS. Hellwig nagradza jego *zbalansowany profil*: wysokie zbiórki (13,8/mecz), wysoka eFG% i bardzo niskie straty. Bez wag, te cechy dają mu przewagę. W SAW/TOPSIS niska waga TOV i PF (po 0,05) minimalizuje jego "czystość" gry, a średnia liczba punktów (14,8) obniża pozycję przy wadze PTS = 0,25.

2. **Luka Dončić** — #3 w SAW, #4 w TOPSIS, ale #17 w Hellwigu. Dončić dominuje w punktach i asystach (zmienne z najwyższymi wagami), co podnosi go w SAW/TOPSIS. Jednak jego **4,6 strat/mecz** (najwyższe w zbiorze) i wysokie faule obniżają go w Hellwigu, który równoważnie traktuje wszystkie zmienne.

3. **Joel Embiid** — #4 w SAW, #3 w TOPSIS, ale #18 w Hellwigu. Podobna sytuacja — 33 pkt/mecz to najwyższy wynik w zbiorze, ale straty (4,3/mecz) i faule (2,5/mecz) silnie obniżają Hellwiga.

4. **Jalen Brunson** — #10 w SAW, #10 w TOPSIS, ale #55 w Hellwigu (rozstęp 45!). Najskrajniejszy przypadek — mocny strzelec i kreator, ale Hellwig karze go za stosunkowo niskie zbiórki, bloki i eFG% przy jednoczesnych stratach.
""")

# ==========================================================================
# 6.7 ROZKLAD POZYCJI
# ==========================================================================
md(r"""### 6.7. Rozkład pozycji w top 20 każdego rankingu""")

code(r"""fig, axes = plt.subplots(1, 3, figsize=(16, 5))
colors_pos = {"PG": "#4C72B0", "SG": "#DD8452", "SF": "#55A868", "PF": "#C44E52", "C": "#8172B3"}

for idx, (name, rdf) in enumerate(rankings.items()):
    ax = axes[idx]
    top20 = rdf.head(20)
    pos_counts = top20["Pos"].value_counts()
    bars = ax.bar(pos_counts.index, pos_counts.values,
                  color=[colors_pos.get(p, "gray") for p in pos_counts.index],
                  alpha=0.85, edgecolor="white", linewidth=1.5)
    ax.set_title(f"{name} — top 20", fontsize=12, fontweight="bold")
    ax.set_ylabel("Liczba graczy")
    ax.set_xlabel("Pozycja")
    for bar, val in zip(bars, pos_counts.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                str(val), ha="center", fontsize=10, fontweight="bold")

fig.suptitle("Rozkład pozycji w top 20 każdego rankingu", fontsize=14, fontweight="bold")
fig.tight_layout()
plt.show()
""")

# ==========================================================================
# 7. ZAPIS WYNIKOW
# ==========================================================================
md(r"""### 6.8. Zapis wyników""")

code(r"""from pathlib import Path

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# Zapis rankingów
saw_df.to_csv(OUTPUT_DIR / "ranking_saw.csv", index=False)
topsis_df.to_csv(OUTPUT_DIR / "ranking_topsis.csv", index=False)
hellwig_df.to_csv(OUTPUT_DIR / "ranking_hellwig.csv", index=False)

# Zapis porównania
merged.to_csv(OUTPUT_DIR / "ranking_comparison.csv", index=False)

# Zapis macierzy korelacji
spearman_matrix.to_csv(OUTPUT_DIR / "spearman_matrix.csv")
kendall_matrix.to_csv(OUTPUT_DIR / "kendall_matrix.csv")

# Zapis statystyk opisowych
stats_df.to_csv(OUTPUT_DIR / "descriptive_stats.csv", index=False)

# Zapis outlierow
outliers_df.to_csv(OUTPUT_DIR / "outliers.csv", index=False)

# Zapis przefiltrowanego zbioru danych
dataset_cols = ["Player", "Pos", "Tm", "G", "GS", "MP"] + ALL_VARIABLES
df[dataset_cols].to_csv("nba_playoffs_2024_dataset.csv", index=False)

print("Wyniki zapisane do katalogu output/")
print(f"Zbiór danych zapisany: nba_playoffs_2024_dataset.csv ({len(df)} graczy)")
print(f"\nPliki:")
for f in sorted(OUTPUT_DIR.iterdir()):
    if f.is_file():
        print(f"  {f}")
""")

# ==========================================================================
# 8. PODSUMOWANIE
# ==========================================================================
md(r"""## 7. Podsumowanie

### 7.1. Główne wnioski

1. **Zgodność SAW i TOPSIS:** Metody SAW i TOPSIS, mimo różnych technik normalizacji (min-max vs. wektorowa), dają niemal identyczne rankingi (ρ Spearmana = 0,987). Obie wykorzystują te same wagi eksperckie, co jest dominującym czynnikiem kształtującym wynik.

2. **Odmienność Hellwiga:** Metoda Hellwiga, nie stosując wag eksperckich, nagradza graczy o zbalansowanym profilu statystycznym. Jarrett Allen (#1 w Hellwigu) jest modelowym przykładem — równomiernie wysoki poziom we wszystkich zmiennych, ale brak dominacji w najbardziej „medialnych" statystykach (PTS, AST).

3. **Top 3 wg średniej rangi:**
   - **Nikola Jokić** (DEN, C) — #1 SAW, #1 TOPSIS, #4 Hellwig → średnia ranga 2,0
   - **LeBron James** (LAL, PF) — #2 SAW, #2 TOPSIS, #3 Hellwig → średnia ranga 2,3
   - **Shai Gilgeous-Alexander** (OKC, PG) — #5 SAW, #5 TOPSIS, #2 Hellwig → średnia ranga 4,0

4. **Wpływ wag:** Wagi eksperckie z dominacją PTS (0,25) i AST (0,18) premiują liderów ofensywnych. Obniżenie wagi destymulant (TOV = 0,05, PF = 0,05) oznacza, że gracze z wieloma stratami (Dončić, Embiid) nie są za to surowo karani w SAW/TOPSIS, ale są w Hellwigu.

5. **Obserwacje odstające:** Zidentyfikowano 11 obserwacji odstających (metoda IQR), ale zdecydowano o ich zachowaniu — w sporcie wartości skrajne reprezentują graczy elitarnych, a ich usunięcie zniekształciłoby ranking.

### 7.2. Ograniczenia

- Wagi eksperckie są subiektywne — inny ekspert mógłby przypisać inne wagi, zmieniając ranking SAW/TOPSIS.
- Dane obejmują jedynie statystyki „pudełkowe" (*box score*) — nie uwzględniają zaawansowanych metryk (np. BPM, VORP, WS).
- Filtracja (G ≥ 4, MP ≥ 15) eliminuje graczy z krótkim udziałem w play-offach, co może pominąć wartościowych rezerwowych.

### 7.3. Dalsze kierunki badań

- Zastosowanie metody AHP do obiektywizacji wag zamiast subiektywnych wag eksperckich.
- Dodanie zaawansowanych metryk (BPM, WS/48, Net Rating).
- Analiza wrażliwości rankingu na zmianę wag.
""")

# ==========================================================================
# 9. BIBLIOGRAFIA
# ==========================================================================
md(r"""## 8. Bibliografia

1. Dadelo, S., Turskis, Z., Zavadskas, E. K., & Dadelienė, R. (2014). Multi-criteria assessment and ranking system of sport team formation based on objective-measured values of criteria set. *Expert Systems with Applications*, 41(14), 6106–6113.

2. Fishburn, P. C. (1967). Additive utilities with incomplete product sets: Application to priorities and assignments. *Operations Research*, 15(3), 537–542.

3. Hellwig, Z. (1968). Zastosowanie metody taksonomicznej do typologicznego podziału krajów ze względu na poziom ich rozwoju oraz zasoby i strukturę wykwalifikowanych kadr. *Przegląd Statystyczny*, 15(4), 307–327.

4. Hwang, C. L., & Yoon, K. (1981). *Multiple Attribute Decision Making: Methods and Applications*. Springer-Verlag.

5. Sarlis, V., & Tjortjis, C. (2020). Sports analytics — Evaluation of basketball players and team performance. *Information Systems*, 93, 101562.
""")

# ==========================================================================
# KONIEC
# ==========================================================================
md(r"""---
*Wygenerowano automatycznie — Metody Analizy Danych, Projekt 1a, Marzec 2026*
""")

# Zbuduj notebook
nb.cells = cells

# Zapisz
output_path = "nba_ranking_analysis.ipynb"
with open(output_path, "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print(f"Notebook zapisany: {output_path}")
