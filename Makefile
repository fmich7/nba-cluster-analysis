# export nba_ranking_analysis.ipynb to nba_ranking_analysis.html
.PHONY: export
export:
	jupyter nbconvert --to html nba_ranking_analysis.ipynb --output nba_ranking_analysis.html
