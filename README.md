# nba-cluster-analysis

## Analiza clustering dla `Playoffs.csv`

Skrypt `analyze_playoffs_clusters.py`:

- wczytuje dane z CSV (separator `;`),
- pokazuje statystyki ogolne i statystyki per pozycja,
- wykonuje klasteryzacje KMeans,
- porownuje klastry z rzeczywista pozycja `Pos`,
- zapisuje wynik do `clustered_players_output.csv`.

### Instalacja pakietow

```bash
pip install -r requirements.txt
```

### Uruchomienie

Jesli plik jest obok katalogu projektu :

```bash
python analyze_playoffs_clusters.py --csv Playoffs.csv --clusters 5
```

Mozesz tez podac inna liczbe klastrow i liczbe cech w profilu:

```bash
python analyze_playoffs_clusters.py --csv "C:\\sciezka\\Playoffs.csv" --clusters 5 --top-features 10
```

## Ranking graczy z danych playoffs

Skrypt `build_playoffs_ranking.py` tworzy ranking na podstawie wazonego wyniku ze statystyk (m.in. PTS, TRB, AST, STL, BLK, eFG%, TOV).

Uruchomienie:

```bash
python build_playoffs_ranking.py --csv Playoffs.csv
```

Przyklad z parametrami filtrowania:

```bash
python build_playoffs_ranking.py --csv Playoffs.csv --min-games 3 --min-mp 8 --top 20
```

Wynik zapisuje sie do pliku `player_ranking_output.csv`.

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
