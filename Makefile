# export nba_ranking_analysis.ipynb to nba_ranking_analysis.html
.PHONY: export
export:
	jupyter nbconvert --to html nba_ranking_analysis.ipynb --output nba_ranking_analysis.html

export2:
	jupyter nbconvert --to html ./projekt2/telco_churn_analysis.ipynb --output telco_churn_analysis.html --output-dir ./projekt2
