# nba-cluster-analysis

## Clustering tylko dla TOP N na pozycje

Skrypt `analyze_top10_per_position_clusters.py`:

- tworzy ranking score,
- wybiera TOP N graczy dla kazdej pozycji,
- robi klasteryzacje tylko na tej grupie,
- zapisuje wynik do `top10_per_position_clustered_output.csv`.

Uruchomienie (TOP 10 na kazda pozycje):

```bash
python analyze_top10_per_position_clusters.py --csv Playoffs.csv --top-per-pos 10 --clusters 5
```
