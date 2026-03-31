"""
Ranking graczy NBA Playoffs 2023/24
====================================
Metody Analizy Danych - Projekt 1a (Porzadkowanie obiektow)

Trzy metody rankingowe:
  1. SAW  (Simple Additive Weighting) z normalizacja min-max
  2. TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution)
  3. Metoda Hellwiga (syntetyczny miernik rozwoju)

Porownanie rankingów: korelacja Spearmana, tau Kendalla, wizualizacje.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats as sp_stats

# ---------------------------------------------------------------------------
# Konfiguracja
# ---------------------------------------------------------------------------

STIMULANTS: list[str] = [
    "PTS",  # Punkty — glowna miara ofensywnej produktywnosci
    "TRB",  # Zbiorki — dominacja na tablicach
    "AST",  # Asysty — kreacja gry dla druzyny
    "STL",  # Przechwyty — aktywnosc defensywna
    "BLK",  # Bloki — obrona przy koszu
    "eFG%",  # Efektywnosc rzutowa (uwzglednia 3-punktowe; syntetyczna miara)
]
# UWAGA: Usunieto 3P% i FT% — procenty z zerowa liczba prob (0 3PA / 0 FTA)
# daja 0%, co nie oznacza niskiej umiejetnosci, a jedynie brak prob.
# Np. Rudy Gobert ma 3P% = 0 (0/0), a Dereck Lively II ma 3P% = 1.0 (1/1).
# eFG% (Effective Field Goal %) jest lepsza syntetyczna miara skutecznosci.
#
# Usunieto rowniez MP (minuty). Dane sa juz per-game averages, wiec czas gry
# jest posrednio wbudowany w wartosci bezwzgledne (PTS, TRB, AST, ...).
# Wlaczenie MP powodowalby podwojne liczenie czasu gry i silna korelacje
# z PTS (r > 0.8).

DESTIMULANTS: list[str] = [
    "TOV",  # Straty — negatywny wplyw na druzyne
    "PF",  # Faule — ryzyko wykluczenia i wolne dla rywala
]

ALL_VARIABLES: list[str] = STIMULANTS + DESTIMULANTS  # 8 zmiennych

# Wagi eksperckie (suma = 1.0)
# Uzasadnienie:
#   PTS  (0.25) — Punkty sa najwazniejszym wyznacznikiem skutecznosci ofensywnej
#                  w playoffach, gdzie kazdy kosz ma duza wage.
#   AST  (0.18) — Asysty mierza zdolnosc kreowania gry; kluczowe dla rozgrywajacych
#                  i liderow druzyn, odzwierciedlaja wspolprace zespolowa.
#   TRB  (0.15) — Zbiorki daja drugie szanse (ofensywne) i koncza ataki rywala
#                  (defensywne); istotne w playoffach przy wolniejszym tempie gry.
#   eFG% (0.14) — Efektywnosc rzutowa uwzgledniajaca wartosc rzutow za 3 pkt;
#                  wazniejsza niz surowa liczba prob (FGA).
#   STL  (0.10) — Przechwyty generuja szybkie ataki i demoralizuja rywala;
#                  wyraz aktywnosci defensywnej.
#   BLK  (0.08) — Bloki chronia obrecz i odstraszaja atakami; wazne, ale rzadsze
#                  niz przechwyty — stad nizsza waga.
#   TOV  (0.05) — Straty sa kosztowne, ale nawet najlepsi gracze (np. Jokic, Doncic)
#                  maja podwyzszone TOV z uwagi na duza role w ataku.
#   PF   (0.05) — Faule obnizaja wartosc gracza (ryzyko wykluczenia, wolne dla
#                  rywala), ale sa czesciowo efektem agresywnej gry obronnej.
WEIGHTS: dict[str, float] = {
    "PTS": 0.25,
    "AST": 0.18,
    "TRB": 0.15,
    "eFG%": 0.14,
    "STL": 0.10,
    "BLK": 0.08,
    "TOV": 0.05,
    "PF": 0.05,
}

OUTPUT_DIR = Path("output")
PLOTS_DIR = OUTPUT_DIR / "plots"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Ranking graczy NBA Playoffs — SAW, TOPSIS, Hellwig"
    )
    p.add_argument(
        "--csv",
        type=str,
        default="Playoffs.csv",
        help="Sciezka do pliku CSV (domyslnie Playoffs.csv)",
    )
    p.add_argument(
        "--min-games", type=int, default=4, help="Minimalna liczba meczow (domyslnie 4)"
    )
    p.add_argument(
        "--min-mp",
        type=float,
        default=15.0,
        help="Minimalna srednia minut na mecz (domyslnie 15)",
    )
    p.add_argument(
        "--top-n",
        type=int,
        default=20,
        help="Ilu graczy pokazac w tabelach top (domyslnie 20)",
    )
    return p.parse_args()


# ---------------------------------------------------------------------------
# Wczytanie i filtrowanie
# ---------------------------------------------------------------------------


def load_and_filter(csv_path: str, min_games: int, min_mp: float) -> pd.DataFrame:
    """Wczytaj CSV, konwertuj numerycznie, odfiltruj graczy z za malym sample size."""
    df = pd.read_csv(csv_path, sep=";")

    if "Rk" in df.columns:
        df = df.drop(columns=["Rk"])

    # Konwersja kolumn numerycznych
    numeric_cols = [c for c in df.columns if c not in ("Player", "Pos", "Tm")]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    n_before = len(df)
    df = df[(df["G"] >= min_games) & (df["MP"] >= min_mp)].copy()
    df = df.reset_index(drop=True)

    print(
        f"Wczytano {n_before} graczy, po filtrach (G>={min_games}, MP>={min_mp}): {len(df)}"
    )
    return df


# ---------------------------------------------------------------------------
# Wstepna analiza danych
# ---------------------------------------------------------------------------


def descriptive_statistics(df: pd.DataFrame, variables: list[str]) -> pd.DataFrame:
    """Statystyki opisowe: srednia, mediana, min, max, std, skosnosc."""
    records = []
    for var in variables:
        vals = df[var].dropna()
        records.append(
            {
                "Zmienna": var,
                "Srednia": round(vals.mean(), 3),
                "Mediana": round(vals.median(), 3),
                "Minimum": round(vals.min(), 3),
                "Maksimum": round(vals.max(), 3),
                "Odch. std.": round(vals.std(ddof=1), 3),
                "Skosnosc": round(sp_stats.skew(vals, bias=False), 3),
                "N": len(vals),
            }
        )
    stats_df = pd.DataFrame(records)
    return stats_df


def detect_outliers_iqr(df: pd.DataFrame, variables: list[str]) -> pd.DataFrame:
    """Wykryj obserwacje odstajace metoda IQR (1.5*IQR)."""
    outlier_records = []
    for var in variables:
        vals = df[var].dropna()
        q1, q3 = vals.quantile(0.25), vals.quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        mask = (df[var] < lower) | (df[var] > upper)
        outliers = df.loc[mask, ["Player", "Pos", var]]
        for _, row in outliers.iterrows():
            outlier_records.append(
                {
                    "Zmienna": var,
                    "Gracz": row["Player"],
                    "Pozycja": row["Pos"],
                    "Wartosc": row[var],
                    "Dolna_granica": round(lower, 3),
                    "Gorna_granica": round(upper, 3),
                }
            )
    return pd.DataFrame(outlier_records)


def check_missing_data(df: pd.DataFrame, variables: list[str]) -> pd.DataFrame:
    """Sprawdz braki danych w wybranych zmiennych."""
    records = []
    for var in variables:
        n_missing = df[var].isna().sum()
        records.append(
            {
                "Zmienna": var,
                "Braki": n_missing,
                "Procent_brakow": round(100 * n_missing / len(df), 2),
            }
        )
    return pd.DataFrame(records)


# ---------------------------------------------------------------------------
# Wizualizacje — wstepna analiza
# ---------------------------------------------------------------------------


def plot_boxplots(df: pd.DataFrame, variables: list[str], out_dir: Path) -> None:
    """Boxploty dla kazdej zmiennej — dwa panele."""
    n_vars = len(variables)
    n_cols = 4
    n_rows = int(np.ceil(n_vars / n_cols))

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(4 * n_cols, 3.5 * n_rows))
    axes = axes.flatten()

    for i, var in enumerate(variables):
        ax = axes[i]
        vals = df[var].dropna()
        bp = ax.boxplot(
            vals,
            vert=True,
            patch_artist=True,
            boxprops=dict(facecolor="#4C72B0", alpha=0.7),
            medianprops=dict(color="yellow", linewidth=2),
        )
        ax.set_title(var, fontsize=11, fontweight="bold")
        ax.set_xticks([])

    # Ukryj puste subploty
    for j in range(n_vars, len(axes)):
        axes[j].set_visible(False)

    fig.suptitle("Boxploty zmiennych", fontsize=14, fontweight="bold", y=1.01)
    fig.tight_layout()
    fig.savefig(out_dir / "boxplots.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Zapisano: {out_dir / 'boxplots.png'}")


def plot_histograms(df: pd.DataFrame, variables: list[str], out_dir: Path) -> None:
    """Histogramy dla kazdej zmiennej."""
    n_vars = len(variables)
    n_cols = 4
    n_rows = int(np.ceil(n_vars / n_cols))

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(4 * n_cols, 3.5 * n_rows))
    axes = axes.flatten()

    for i, var in enumerate(variables):
        ax = axes[i]
        vals = df[var].dropna()
        ax.hist(vals, bins=15, color="#4C72B0", alpha=0.8, edgecolor="white")
        ax.set_title(var, fontsize=11, fontweight="bold")
        ax.set_ylabel("Liczba graczy")

    for j in range(n_vars, len(axes)):
        axes[j].set_visible(False)

    fig.suptitle("Histogramy zmiennych", fontsize=14, fontweight="bold", y=1.01)
    fig.tight_layout()
    fig.savefig(out_dir / "histograms.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Zapisano: {out_dir / 'histograms.png'}")


def plot_correlation_heatmap(
    df: pd.DataFrame, variables: list[str], out_dir: Path
) -> None:
    """Heatmapa korelacji Pearsona miedzy zmiennymi."""
    corr = df[variables].corr(method="pearson")

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap="RdBu_r",
        center=0,
        square=True,
        linewidths=0.5,
        ax=ax,
        xticklabels=variables,
        yticklabels=variables,
    )
    ax.set_title("Macierz korelacji Pearsona", fontsize=14, fontweight="bold")
    fig.tight_layout()
    fig.savefig(out_dir / "correlation_heatmap.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Zapisano: {out_dir / 'correlation_heatmap.png'}")


# ---------------------------------------------------------------------------
# Metody rankingowe
# ---------------------------------------------------------------------------


def ranking_saw(
    df: pd.DataFrame,
    stimulants: list[str],
    destimulants: list[str],
    weights: dict[str, float],
) -> pd.DataFrame:
    """
    SAW (Simple Additive Weighting) z normalizacja min-max.

    Normalizacja:
      - stymulanta:   r_ij = (x_ij - x_min) / (x_max - x_min)
      - destymulanta:  r_ij = (x_max - x_ij) / (x_max - x_min)

    Score: S_i = sum_j (w_j * r_ij)
    """
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
        else:  # destymulanta
            result[f"{var}_norm"] = (v_max - vals) / denom

    # Score = suma wazona
    score = np.zeros(len(result))
    for var in all_vars:
        w = weights.get(var, 0.0)
        score += w * result[f"{var}_norm"].values
    result["SAW_score"] = score
    result["SAW_rank"] = (
        result["SAW_score"].rank(ascending=False, method="min").astype(int)
    )
    result = result.sort_values("SAW_rank").reset_index(drop=True)

    # Wyczysc kolumny pomocnicze
    norm_cols = [c for c in result.columns if c.endswith("_norm")]
    result = result.drop(columns=norm_cols)
    return result


def ranking_topsis(
    df: pd.DataFrame,
    stimulants: list[str],
    destimulants: list[str],
    weights: dict[str, float],
) -> pd.DataFrame:
    """
    TOPSIS (Hwang & Yoon, 1981).

    1. Normalizacja wektorowa: r_ij = x_ij / sqrt(sum_i(x_ij^2))
    2. Wazona macierz: v_ij = w_j * r_ij
    3. Rozwiazanie idealne A+ i anty-idealne A-
    4. Odleglosci euklidesowe: d_i+ i d_i-
    5. Score: C_i = d_i- / (d_i+ + d_i-)
    """
    result = df[["Player", "Pos", "Tm"]].copy()
    all_vars = stimulants + destimulants
    n = len(df)

    # 1. Normalizacja wektorowa
    norm_matrix = np.zeros((n, len(all_vars)))
    for j, var in enumerate(all_vars):
        vals = df[var].values.astype(float)
        denom = np.sqrt(np.sum(vals**2))
        if denom == 0:
            norm_matrix[:, j] = 0.0
        else:
            norm_matrix[:, j] = vals / denom

    # 2. Wazona macierz decyzyjna
    w_array = np.array([weights.get(var, 0.0) for var in all_vars])
    weighted = norm_matrix * w_array  # broadcasting

    # 3. Rozwiazanie idealne (A+) i anty-idealne (A-)
    a_plus = np.zeros(len(all_vars))
    a_minus = np.zeros(len(all_vars))
    for j, var in enumerate(all_vars):
        if var in stimulants:
            a_plus[j] = weighted[:, j].max()
            a_minus[j] = weighted[:, j].min()
        else:  # destymulanta
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
    result["TOPSIS_rank"] = (
        result["TOPSIS_score"].rank(ascending=False, method="min").astype(int)
    )
    result = result.sort_values("TOPSIS_rank").reset_index(drop=True)
    return result


def ranking_hellwig(
    df: pd.DataFrame, stimulants: list[str], destimulants: list[str]
) -> pd.DataFrame:
    """
    Metoda Hellwiga (1968) — syntetyczny miernik rozwoju.

    1. Standaryzacja z-score: z_ij = (x_ij - mean_j) / std_j
    2. Wzorzec rozwoju z_0j: max(z_ij) dla stymulant, min(z_ij) dla destymulant
    3. Odleglosc od wzorca: d_i = sqrt(sum_j (z_ij - z_0j)^2)
    4. d_0 = mean(d) + 2 * std(d)
    5. Miernik: S_i = 1 - d_i / d_0
       (im blizej 1, tym lepiej)
    """
    result = df[["Player", "Pos", "Tm"]].copy()
    all_vars = stimulants + destimulants
    n = len(df)

    # 1. Standaryzacja z-score
    z_matrix = np.zeros((n, len(all_vars)))
    for j, var in enumerate(all_vars):
        vals = df[var].values.astype(float)
        std = vals.std(ddof=1)
        if std == 0:
            z_matrix[:, j] = 0.0
        else:
            z_matrix[:, j] = (vals - vals.mean()) / std

    # 2. Wzorzec rozwoju
    z_ideal = np.zeros(len(all_vars))
    for j, var in enumerate(all_vars):
        if var in stimulants:
            z_ideal[j] = z_matrix[:, j].max()
        else:  # destymulanta
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
    result["Hellwig_rank"] = (
        result["Hellwig_score"].rank(ascending=False, method="min").astype(int)
    )
    result = result.sort_values("Hellwig_rank").reset_index(drop=True)
    return result


# ---------------------------------------------------------------------------
# Porownanie rankingów
# ---------------------------------------------------------------------------


def compare_rankings(
    rankings: dict[str, pd.DataFrame], top_n: int
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Porownaj rankingi: korelacja Spearmana i tau Kendalla + tabela zbiorcza."""

    # Potrzebujemy dopasowac po Player
    merged = pd.DataFrame()
    for name, rdf in rankings.items():
        sub = rdf[["Player", f"{name}_score", f"{name}_rank"]].copy()
        if merged.empty:
            merged = sub
        else:
            merged = merged.merge(sub, on="Player", how="outer")

    # Korelacje
    rank_cols = [c for c in merged.columns if c.endswith("_rank")]
    method_names = [c.replace("_rank", "") for c in rank_cols]

    print("\n=== KORELACJA SPEARMANA MIEDZY RANKINGAMI ===")
    spearman_matrix = pd.DataFrame(
        index=method_names, columns=method_names, dtype=float
    )
    for i, m1 in enumerate(method_names):
        for j, m2 in enumerate(method_names):
            r1 = merged[f"{m1}_rank"].values
            r2 = merged[f"{m2}_rank"].values
            corr, _ = sp_stats.spearmanr(r1, r2)
            spearman_matrix.loc[m1, m2] = round(corr, 4)
    print(spearman_matrix.to_string())

    print("\n=== TAU KENDALLA MIEDZY RANKINGAMI ===")
    kendall_matrix = pd.DataFrame(index=method_names, columns=method_names, dtype=float)
    for i, m1 in enumerate(method_names):
        for j, m2 in enumerate(method_names):
            r1 = merged[f"{m1}_rank"].values
            r2 = merged[f"{m2}_rank"].values
            tau, _ = sp_stats.kendalltau(r1, r2)
            kendall_matrix.loc[m1, m2] = round(tau, 4)
    print(kendall_matrix.to_string())

    # Tabela TOP N
    merged_sorted = merged.sort_values(f"{method_names[0]}_rank").reset_index(drop=True)
    # Dodaj Player info z powrotem
    player_info = rankings[list(rankings.keys())[0]][["Player", "Pos", "Tm"]]
    top_table = merged.merge(player_info, on="Player", how="left")

    # Sortuj po sredniej rang
    rank_vals = top_table[rank_cols].values
    top_table["Srednia_ranga"] = rank_vals.mean(axis=1)
    top_table = top_table.sort_values("Srednia_ranga").reset_index(drop=True)

    display_cols = (
        ["Player", "Pos", "Tm"]
        + [f"{m}_score" for m in method_names]
        + [f"{m}_rank" for m in method_names]
        + ["Srednia_ranga"]
    )
    display_cols = [c for c in display_cols if c in top_table.columns]

    print(f"\n=== TOP {top_n} GRACZY (wg sredniej rangi) ===")
    print(top_table[display_cols].head(top_n).to_string(index=False))

    return top_table, spearman_matrix, kendall_matrix


# ---------------------------------------------------------------------------
# Wizualizacje — wyniki
# ---------------------------------------------------------------------------


def plot_ranking_bars(
    rankings: dict[str, pd.DataFrame], top_n: int, out_dir: Path
) -> None:
    """Barploty top N graczy dla kazdego rankingu."""
    n_methods = len(rankings)
    fig, axes = plt.subplots(1, n_methods, figsize=(7 * n_methods, max(8, top_n * 0.4)))

    if n_methods == 1:
        axes = [axes]

    colors = ["#4C72B0", "#DD8452", "#55A868"]

    for idx, (name, rdf) in enumerate(rankings.items()):
        ax = axes[idx]
        top = rdf.head(top_n).iloc[::-1]  # odwroc dla poziomego wykresu
        score_col = f"{name}_score"
        players = top["Player"].values
        scores = top[score_col].values

        bars = ax.barh(
            range(len(players)), scores, color=colors[idx % len(colors)], alpha=0.85
        )
        ax.set_yticks(range(len(players)))
        ax.set_yticklabels(players, fontsize=9)
        ax.set_xlabel("Score", fontsize=11)
        ax.set_title(f"Top {top_n} — {name}", fontsize=13, fontweight="bold")
        ax.invert_xaxis() if False else None  # score rosnacy w prawo

    fig.suptitle(
        f"Rankingi graczy NBA Playoffs — Top {top_n}",
        fontsize=15,
        fontweight="bold",
        y=1.02,
    )
    fig.tight_layout()
    fig.savefig(out_dir / "ranking_barplots.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Zapisano: {out_dir / 'ranking_barplots.png'}")


def plot_bump_chart(
    rankings: dict[str, pd.DataFrame], top_n: int, out_dir: Path
) -> None:
    """Bump chart — porownanie pozycji gracza miedzy rankingami."""
    method_names = list(rankings.keys())

    # Zbierz rangi
    all_ranks = {}
    for name, rdf in rankings.items():
        for _, row in rdf.iterrows():
            player = row["Player"]
            if player not in all_ranks:
                all_ranks[player] = {}
            all_ranks[player][name] = row[f"{name}_rank"]

    # Filtruj do graczy ktory sa w top_n w przynajmniej jednym rankingu
    top_players = set()
    for name, rdf in rankings.items():
        top_players.update(rdf.head(top_n)["Player"].values)

    fig, ax = plt.subplots(figsize=(8, max(10, top_n * 0.5)))

    cmap = plt.get_cmap("tab20")
    player_list = sorted(top_players)

    for i, player in enumerate(player_list):
        if player not in all_ranks:
            continue
        ranks_for_player = all_ranks[player]
        xs = []
        ys = []
        for j, method in enumerate(method_names):
            if method in ranks_for_player:
                xs.append(j)
                ys.append(ranks_for_player[method])

        color = cmap(i % 20)
        ax.plot(xs, ys, marker="o", color=color, linewidth=1.5, markersize=6, alpha=0.8)

        # Etykieta przy ostatnim punkcie
        if ys:
            # Skroc imie: "Jayson Tatum" -> "J. Tatum"
            parts = player.split()
            if len(parts) >= 2:
                short = parts[0][0] + ". " + " ".join(parts[1:])
            else:
                short = player
            ax.annotate(
                short,
                (xs[-1] + 0.05, ys[-1]),
                fontsize=7,
                va="center",
                color=color,
                fontweight="bold",
            )

    ax.set_xticks(range(len(method_names)))
    ax.set_xticklabels(method_names, fontsize=12, fontweight="bold")
    ax.set_ylabel("Pozycja w rankingu", fontsize=12)
    ax.set_title(
        f"Bump chart — porownanie rankingów (gracze w top {top_n})",
        fontsize=14,
        fontweight="bold",
    )
    ax.invert_yaxis()  # 1. miejsce na gorze
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()
    fig.savefig(out_dir / "bump_chart.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Zapisano: {out_dir / 'bump_chart.png'}")


def plot_spearman_heatmap(spearman_matrix: pd.DataFrame, out_dir: Path) -> None:
    """Heatmapa korelacji Spearmana miedzy rankingami."""
    fig, ax = plt.subplots(figsize=(6, 5))
    vals = spearman_matrix.values.astype(float)
    sns.heatmap(
        vals,
        annot=True,
        fmt=".4f",
        cmap="YlGn",
        xticklabels=spearman_matrix.columns,
        yticklabels=spearman_matrix.index,
        vmin=0.8,
        vmax=1.0,
        square=True,
        linewidths=1,
        ax=ax,
    )
    ax.set_title(
        "Korelacja Spearmana miedzy rankingami", fontsize=13, fontweight="bold"
    )
    fig.tight_layout()
    fig.savefig(out_dir / "spearman_heatmap.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Zapisano: {out_dir / 'spearman_heatmap.png'}")


def plot_rank_scatter(rankings: dict[str, pd.DataFrame], out_dir: Path) -> None:
    """Scatter ploty rang miedzy parami metod."""
    method_names = list(rankings.keys())
    pairs = []
    for i in range(len(method_names)):
        for j in range(i + 1, len(method_names)):
            pairs.append((method_names[i], method_names[j]))

    if not pairs:
        return

    fig, axes = plt.subplots(1, len(pairs), figsize=(6 * len(pairs), 5))
    if len(pairs) == 1:
        axes = [axes]

    for idx, (m1, m2) in enumerate(pairs):
        ax = axes[idx]
        r1_df = rankings[m1].set_index("Player")
        r2_df = rankings[m2].set_index("Player")
        common = r1_df.index.intersection(r2_df.index)

        x = r1_df.loc[common, f"{m1}_rank"].values
        y = r2_df.loc[common, f"{m2}_rank"].values

        ax.scatter(x, y, alpha=0.6, s=25, c="#4C72B0")
        # Linia y=x
        lim = max(x.max(), y.max()) + 1
        ax.plot([1, lim], [1, lim], "r--", alpha=0.5, linewidth=1)
        ax.set_xlabel(f"Ranga {m1}", fontsize=11)
        ax.set_ylabel(f"Ranga {m2}", fontsize=11)
        ax.set_title(f"{m1} vs {m2}", fontsize=12, fontweight="bold")
        ax.set_aspect("equal")

    fig.suptitle(
        "Porownanie rang miedzy metodami", fontsize=14, fontweight="bold", y=1.02
    )
    fig.tight_layout()
    fig.savefig(out_dir / "rank_scatter.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Zapisano: {out_dir / 'rank_scatter.png'}")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------


def main() -> None:
    args = parse_args()

    OUTPUT_DIR.mkdir(exist_ok=True)
    PLOTS_DIR.mkdir(exist_ok=True)

    # ---------------------------------------------------------------
    # 1. Wczytanie i filtrowanie danych
    # ---------------------------------------------------------------
    print("=" * 60)
    print("1. WCZYTANIE I FILTROWANIE DANYCH")
    print("=" * 60)
    df = load_and_filter(args.csv, args.min_games, args.min_mp)
    print(f"   Pozycje w zbiorze: {df['Pos'].value_counts().to_dict()}")

    # ---------------------------------------------------------------
    # 2. Braki danych
    # ---------------------------------------------------------------
    print("\n" + "=" * 60)
    print("2. BRAKI DANYCH")
    print("=" * 60)
    missing_df = check_missing_data(df, ALL_VARIABLES)
    print(missing_df.to_string(index=False))
    if missing_df["Braki"].sum() == 0:
        print("   -> Brak brakow danych w wybranych zmiennych.")
    else:
        print("   -> Braki danych uzupelniono mediana (jesli wystepuja).")
        for var in ALL_VARIABLES:
            if df[var].isna().any():
                df[var] = df[var].fillna(df[var].median())

    # ---------------------------------------------------------------
    # 3. Statystyki opisowe
    # ---------------------------------------------------------------
    print("\n" + "=" * 60)
    print("3. STATYSTYKI OPISOWE")
    print("=" * 60)
    stats_df = descriptive_statistics(df, ALL_VARIABLES)
    print(stats_df.to_string(index=False))
    stats_df.to_csv(OUTPUT_DIR / "descriptive_stats.csv", index=False)
    print(f"   Zapisano: {OUTPUT_DIR / 'descriptive_stats.csv'}")

    # ---------------------------------------------------------------
    # 4. Obserwacje odstajace
    # ---------------------------------------------------------------
    print("\n" + "=" * 60)
    print("4. OBSERWACJE ODSTAJACE (IQR)")
    print("=" * 60)
    outliers_df = detect_outliers_iqr(df, ALL_VARIABLES)
    if outliers_df.empty:
        print("   Nie wykryto obserwacji odstajacych metoda IQR.")
    else:
        print(f"   Wykryto {len(outliers_df)} obserwacji odstajacych:")
        print(outliers_df.to_string(index=False))
        print("\n   Decyzja: Obserwacje odstajace NIE sa usuwane.")
        print("   Uzasadnienie: W sporcie wartosci skrajne reprezentuja")
        print("   elitarnych graczy (np. Jokic, Embiid) — usuwanie ich")
        print("   znieksztalciloby ranking.")
    outliers_df.to_csv(OUTPUT_DIR / "outliers.csv", index=False)

    # ---------------------------------------------------------------
    # 5. Wizualizacje wstepne
    # ---------------------------------------------------------------
    print("\n" + "=" * 60)
    print("5. WIZUALIZACJE WSTEPNE")
    print("=" * 60)
    plot_boxplots(df, ALL_VARIABLES, PLOTS_DIR)
    plot_histograms(df, ALL_VARIABLES, PLOTS_DIR)
    plot_correlation_heatmap(df, ALL_VARIABLES, PLOTS_DIR)

    # Analiza korelacji miedzy zmiennymi
    corr = df[ALL_VARIABLES].corr(method="pearson")
    print("\n   Macierz korelacji Pearsona:")
    print(corr.to_string())
    print("\n   Komentarz: Najsilniejsze korelacje wystepuja miedzy PTS a AST")
    print("   (r~0.6) oraz PTS a TOV (r~0.8) — gracze z duza liczba punktow")
    print("   czesciej tez tracą pilke (wieksza odpowiedzialnosc w ataku).")
    print("   PTS koreluje tez z TRB (r~0.5) — najlepsi gracze zbieraja wiecej.")
    print("   Korelacje te sa oczekiwane i nie dyskwalifikuja zmiennych w rankingu,")
    print(
        "   poniewaz kazda z nich mierzy inny aspekt gry (ofensywa, obrona, kreacja)."
    )
    print("   W odroznieniu od regresji, w metodach rankingowych wspolliniowosc")
    print("   nie powoduje niestabilnosci wynikow.")

    # ---------------------------------------------------------------
    # 6. RANKING 1 — SAW
    # ---------------------------------------------------------------
    print("\n" + "=" * 60)
    print("6. RANKING 1 — SAW (Simple Additive Weighting)")
    print("=" * 60)
    saw_df = ranking_saw(df, STIMULANTS, DESTIMULANTS, WEIGHTS)
    print(f"   Top 10 SAW:")
    print(
        saw_df[["Player", "Pos", "Tm", "SAW_score", "SAW_rank"]]
        .head(10)
        .to_string(index=False)
    )
    saw_df.to_csv(OUTPUT_DIR / "ranking_saw.csv", index=False)
    print(f"   Zapisano: {OUTPUT_DIR / 'ranking_saw.csv'}")

    # ---------------------------------------------------------------
    # 7. RANKING 2 — TOPSIS
    # ---------------------------------------------------------------
    print("\n" + "=" * 60)
    print("7. RANKING 2 — TOPSIS")
    print("=" * 60)
    topsis_df = ranking_topsis(df, STIMULANTS, DESTIMULANTS, WEIGHTS)
    print(f"   Top 10 TOPSIS:")
    print(
        topsis_df[["Player", "Pos", "Tm", "TOPSIS_score", "TOPSIS_rank"]]
        .head(10)
        .to_string(index=False)
    )
    topsis_df.to_csv(OUTPUT_DIR / "ranking_topsis.csv", index=False)
    print(f"   Zapisano: {OUTPUT_DIR / 'ranking_topsis.csv'}")

    # ---------------------------------------------------------------
    # 8. RANKING 3 — HELLWIG
    # ---------------------------------------------------------------
    print("\n" + "=" * 60)
    print("8. RANKING 3 — METODA HELLWIGA")
    print("=" * 60)
    hellwig_df = ranking_hellwig(df, STIMULANTS, DESTIMULANTS)
    print(f"   Top 10 Hellwig:")
    print(
        hellwig_df[["Player", "Pos", "Tm", "Hellwig_score", "Hellwig_rank"]]
        .head(10)
        .to_string(index=False)
    )
    hellwig_df.to_csv(OUTPUT_DIR / "ranking_hellwig.csv", index=False)
    print(f"   Zapisano: {OUTPUT_DIR / 'ranking_hellwig.csv'}")

    # ---------------------------------------------------------------
    # 9. POROWNANIE RANKINGOW
    # ---------------------------------------------------------------
    print("\n" + "=" * 60)
    print("9. POROWNANIE RANKINGOW")
    print("=" * 60)
    rankings = {
        "SAW": saw_df,
        "TOPSIS": topsis_df,
        "Hellwig": hellwig_df,
    }
    comparison_df, spearman_mat, kendall_mat = compare_rankings(rankings, args.top_n)

    comparison_df.to_csv(OUTPUT_DIR / "ranking_comparison.csv", index=False)
    spearman_mat.to_csv(OUTPUT_DIR / "spearman_matrix.csv")
    kendall_mat.to_csv(OUTPUT_DIR / "kendall_matrix.csv")
    print(f"   Zapisano: {OUTPUT_DIR / 'ranking_comparison.csv'}")
    print(f"   Zapisano: {OUTPUT_DIR / 'spearman_matrix.csv'}")
    print(f"   Zapisano: {OUTPUT_DIR / 'kendall_matrix.csv'}")

    # ---------------------------------------------------------------
    # 10. WIZUALIZACJE WYNIKOW
    # ---------------------------------------------------------------
    print("\n" + "=" * 60)
    print("10. WIZUALIZACJE WYNIKOW")
    print("=" * 60)
    plot_ranking_bars(rankings, args.top_n, PLOTS_DIR)
    plot_bump_chart(rankings, args.top_n, PLOTS_DIR)
    plot_spearman_heatmap(spearman_mat, PLOTS_DIR)
    plot_rank_scatter(rankings, PLOTS_DIR)

    # ---------------------------------------------------------------
    # PODSUMOWANIE
    # ---------------------------------------------------------------
    print("\n" + "=" * 60)
    print("GOTOWE!")
    print("=" * 60)
    print(f"Przeanalizowano {len(df)} graczy.")
    print(f"Wyniki w katalogu: {OUTPUT_DIR.resolve()}")
    print(f"Wykresy w katalogu: {PLOTS_DIR.resolve()}")
    print()

    # Najlepszy gracz wg kazdej metody
    for name, rdf in rankings.items():
        best = rdf.iloc[0]
        print(
            f"  Najlepszy wg {name}: {best['Player']} ({best['Pos']}, {best['Tm']}) "
            f"— score: {best[f'{name}_score']:.4f}"
        )


if __name__ == "__main__":
    main()
