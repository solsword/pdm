out/report.txt: analyze_traces.py data/player_models.json data/gs-choices.json data/traces/*
	./analyze_traces.py data/player_models.json data/gs-choices.json data/traces/* > $@

.PHONY: default
default: out/report.txt

.PHONY: clean
clean:
	rm out/report.txt
