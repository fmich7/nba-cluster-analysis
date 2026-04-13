# NBA Playoffs 2023/24 — Ranking graczy

Metody Analizy Danych — Projekt 1a (Porzadkowanie obiektow)

Dane
https://pr.nba.com/voting-results-2023-24-nba-regular-season-awards/

## Opis

Ranking graczy NBA Playoffs 2023/24 z wykorzystaniem trzech metod:

1. **SAW** (Simple Additive Weighting) z normalizacja min-max
2. **TOPSIS** (Technique for Order of Preference by Similarity to Ideal Solution)
3. **Metoda Hellwiga** (syntetyczny miernik rozwoju)

## Zmienne (8)

### Stymulanty
| Zmienna | Opis | Waga |
|---------|------|------|
| PTS | Punkty | 0.25 |
| AST | Asysty | 0.18 |
| TRB | Zbiorki | 0.15 |
| eFG% | Efektywnosc rzutowa | 0.14 |
| STL | Przechwyty | 0.10 |
| BLK | Bloki | 0.08 |

### Destymulanty
| Zmienna | Opis | Waga |
|---------|------|------|
| TOV | Straty | 0.05 |
| PF | Faule | 0.05 |

### Usuniete zmienne (z uzasadnieniem)
- **3P%, FT%** — procenty z zerowa liczba prob (0/0) daja 0%, co nie oznacza niskiej umiejetnosci. eFG% jest lepsza syntetyczna miara skutecznosci.
- **MP** — dane sa per-game averages, wiec czas gry jest posrednio wbudowany w inne statystyki. Wlaczenie MP powodowaloby podwojne liczenie i silna korelacje z PTS.

## Uruchomienie

```bash
python nba_ranking_analysis.py --csv Playoffs.csv --min-games 4 --min-mp 15 --top-n 20
```

### Parametry

| Parametr | Domyslnie | Opis |
|----------|-----------|------|
| `--csv` | `Playoffs.csv` | Sciezka do pliku CSV |
| `--min-games` | `4` | Minimalna liczba meczow |
| `--min-mp` | `15` | Minimalna srednia minut/mecz |
| `--top-n` | `20` | Ile graczy w tabelach top |

## Wyniki

Skrypt generuje:

- `output/descriptive_stats.csv` — statystyki opisowe
- `output/outliers.csv` — obserwacje odstajace (IQR)
- `output/ranking_saw.csv` — ranking SAW
- `output/ranking_topsis.csv` — ranking TOPSIS
- `output/ranking_hellwig.csv` — ranking Hellwig
- `output/ranking_comparison.csv` — porownanie (srednia ranga)
- `output/spearman_matrix.csv` — korelacja Spearmana
- `output/kendall_matrix.csv` — tau Kendalla
- `output/plots/` — wykresy (boxploty, histogramy, heatmapa korelacji, barploty, bump chart, scatter rang)

## Wymagane biblioteki

```
pandas numpy matplotlib seaborn scipy
```

## Stare pliki

Poprzednia wersja (clustering) w katalogu `outdated/`.
