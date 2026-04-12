PYTHON   := python3
JUPYTER  := jupyter
DATA     := Playoffs.csv
NOTEBOOK := nba_ranking_analysis.ipynb
HTML     := nba_ranking_analysis.html
DATASET  := nba_playoffs_2024_dataset.csv
BUILDER  := build_notebook.py
SCRIPT   := nba_ranking_analysis.py
OUTDIR   := output

.PHONY: all notebook html script clean help

all: notebook html ## Zbuduj notebook, wykonaj go i wyeksportuj do HTML

notebook: $(NOTEBOOK) ## Zbuduj i wykonaj notebook
$(NOTEBOOK): $(BUILDER) $(DATA)
	$(PYTHON) $(BUILDER)
	$(JUPYTER) nbconvert --to notebook --execute \
		--ExecutePreprocessor.timeout=300 \
		$(NOTEBOOK) --output $(NOTEBOOK)

html: $(HTML) ## Wyeksportuj notebook do HTML
$(HTML): $(NOTEBOOK)
	$(JUPYTER) nbconvert --to html $(NOTEBOOK)

script: ## Uruchom samodzielny skrypt (bez notebooka)
	$(PYTHON) $(SCRIPT) --csv $(DATA)

clean: ## Usuń wygenerowane pliki
	rm -f $(NOTEBOOK) $(HTML) $(DATASET)
	rm -rf $(OUTDIR)

help: ## Pokaż dostępne komendy
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'
