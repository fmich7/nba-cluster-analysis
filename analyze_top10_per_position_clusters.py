from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


RANKING_WEIGHTS: dict[str, float] = {
    "PTS": 0.30,
    "TRB": 0.12,
    "AST": 0.18,
    "STL": 0.10,
    "BLK": 0.08,
    "eFG%": 0.12,
    "FT%": 0.03,
    "3P%": 0.04,
    "MP": 0.08,
    "TOV": -0.12,
    "PF": -0.03,
}

CLUSTER_FEATURES = [
    "Age",
    "MP",
    "FG",
    "FGA",
    "FG%",
    "3P",
    "3PA",
    "3P%",
    "2P",
    "2PA",
    "2P%",
    "eFG%",
    "FT",
    "FTA",
    "FT%",
    "ORB",
    "DRB",
    "TRB",
    "AST",
    "STL",
    "BLK",
    "TOV",
    "PF",
    "PTS",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Klasteryzacja tylko dla TOP N graczy na kazdej pozycji. "
            "TOP N wyznaczany jest przez ranking score."
        )
    )
    parser.add_argument(
        "--csv",
        type=str,
        default=None,
        help="Sciezka do CSV. Domyslnie szuka Playoffs.csv w biezacym lub nadrzednym katalogu.",
    )
    parser.add_argument(
        "--top-per-pos",
        type=int,
        default=10,
        help="Ilu graczy wybrac z kazdej pozycji do klasteryzacji (domyslnie 10).",
    )
    parser.add_argument(
        "--clusters",
        type=int,
        default=5,
        help="Liczba klastrow KMeans.",
    )
    parser.add_argument(
        "--min-games",
        type=int,
        default=3,
        help="Minimalna liczba meczow przy tworzeniu rankingu TOP.",
    )
    parser.add_argument(
        "--min-mp",
        type=float,
        default=8.0,
        help="Minimalna srednia liczba minut na mecz przy tworzeniu rankingu TOP.",
    )
    return parser.parse_args()


def resolve_csv_path(path_arg: str | None) -> Path:
    if path_arg:
        csv_path = Path(path_arg).expanduser().resolve()
        if not csv_path.exists():
            raise FileNotFoundError(f"Nie znaleziono pliku CSV: {csv_path}")
        return csv_path

    candidates = [Path("Playoffs.csv"), Path("playoffs.csv"), Path("..").joinpath("Playoffs.csv")]
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()

    raise FileNotFoundError("Nie znaleziono Playoffs.csv. Podaj sciezke przez --csv.")


def load_data(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path, sep=";")
    required = {"Player", "Pos", "Tm", "G", "MP"}
    missing = sorted(list(required - set(df.columns)))
    if missing:
        raise ValueError(f"Brak wymaganych kolumn: {missing}")

    if "Rk" in df.columns:
        df = df.drop(columns=["Rk"])
    return df


def to_numeric_with_median(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = df.copy()
    for col in columns:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    medians = out[columns].median(numeric_only=True)
    out[columns] = out[columns].fillna(medians)
    return out


def add_ranking_score(df: pd.DataFrame) -> pd.DataFrame:
    available_weights = {k: v for k, v in RANKING_WEIGHTS.items() if k in df.columns}
    if len(available_weights) < 4:
        raise ValueError("Za malo kolumn do policzenia ranking score.")

    out = to_numeric_with_median(df, list(available_weights.keys()))

    z_values: dict[str, np.ndarray] = {}
    for col in available_weights:
        vals = out[col].to_numpy(dtype=float)
        std = vals.std(ddof=0)
        if std == 0 or np.isnan(std):
            z_values[col] = np.zeros_like(vals)
        else:
            z_values[col] = (vals - vals.mean()) / std

    denominator = sum(abs(w) for w in available_weights.values())
    score = np.zeros(len(out), dtype=float)
    for col, weight in available_weights.items():
        score += weight * z_values[col]
    out["ranking_score"] = score / denominator
    return out


def select_top_per_position(df: pd.DataFrame, top_per_pos: int, min_games: int, min_mp: float) -> pd.DataFrame:
    out = df.copy()
    out["G"] = pd.to_numeric(out["G"], errors="coerce")
    out["MP"] = pd.to_numeric(out["MP"], errors="coerce")

    filtered = out[(out["G"].fillna(0) >= min_games) & (out["MP"].fillna(0) >= min_mp)].copy()
    if filtered.empty:
        raise ValueError("Po filtrach min-games i min-mp nie zostal zaden gracz.")

    filtered = add_ranking_score(filtered)

    top = (
        filtered.sort_values(["Pos", "ranking_score"], ascending=[True, False])
        .groupby("Pos", group_keys=False)
        .head(top_per_pos)
        .reset_index(drop=True)
    )
    return top


def run_clustering(df: pd.DataFrame, n_clusters: int) -> tuple[pd.DataFrame, np.ndarray, KMeans, list[str]]:
    feature_columns = [col for col in CLUSTER_FEATURES if col in df.columns]
    if len(feature_columns) < 5:
        raise ValueError("Za malo kolumn numerycznych do klasteryzacji.")

    work = to_numeric_with_median(df, feature_columns)
    x = work[feature_columns].to_numpy(dtype=float)
    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(x)

    model = KMeans(n_clusters=n_clusters, random_state=42, n_init=20)
    labels = model.fit_predict(x_scaled)

    out = work.copy()
    out["cluster"] = labels
    return out, x_scaled, model, feature_columns


def evaluate(df_clustered: pd.DataFrame, x_scaled: np.ndarray, model: KMeans) -> None:
    print("\n=== KLASTRY VS POZYCJA (TOP NA POZYCJE) ===")
    ctab = pd.crosstab(df_clustered["cluster"], df_clustered["Pos"])
    print(ctab.to_string())

    cluster_to_pos = ctab.idxmax(axis=1).to_dict()
    df_eval = df_clustered.copy()
    df_eval["pred_pos_from_cluster"] = df_eval["cluster"].map(cluster_to_pos)
    accuracy = (df_eval["pred_pos_from_cluster"] == df_eval["Pos"]).mean()

    print("\nMapowanie cluster -> pozycja (wiekszosc):")
    for cluster_id, pos in sorted(cluster_to_pos.items(), key=lambda x: x[0]):
        print(f"  Cluster {cluster_id}: {pos}")

    print(f"\nPrzyblizona zgodnosc klastrow z pozycja: {accuracy:.2%}")

    if len(df_clustered) > model.n_clusters:
        sil = silhouette_score(x_scaled, model.labels_)
        print(f"Silhouette score: {sil:.3f}")


def main() -> None:
    args = parse_args()
    csv_path = resolve_csv_path(args.csv)
    print(f"Wczytuje dane z: {csv_path}")

    raw = load_data(csv_path)
    top_df = select_top_per_position(
        raw,
        top_per_pos=max(1, args.top_per_pos),
        min_games=max(0, args.min_games),
        min_mp=max(0.0, args.min_mp),
    )

    print("\n=== LICZBA WYBRANYCH GRACZY ===")
    print(top_df["Pos"].value_counts().sort_index().to_string())

    n_samples = len(top_df)
    n_clusters = max(2, min(args.clusters, n_samples))
    if n_clusters != args.clusters:
        print(f"\nUwaga: dostosowano liczbe klastrow do {n_clusters} (liczba probek: {n_samples}).")

    clustered, x_scaled, model, _features = run_clustering(top_df, n_clusters=n_clusters)
    evaluate(clustered, x_scaled, model)

    out_file = Path("top10_per_position_clustered_output.csv")
    export_cols = [
        "Player",
        "Tm",
        "Pos",
        "G",
        "MP",
        "PTS",
        "TRB",
        "AST",
        "STL",
        "BLK",
        "ranking_score",
        "cluster",
    ]
    export_cols = [c for c in export_cols if c in clustered.columns]
    clustered[export_cols].to_csv(out_file, index=False)
    print(f"\nZapisano wynik do: {out_file.resolve()}")


if __name__ == "__main__":
    main()