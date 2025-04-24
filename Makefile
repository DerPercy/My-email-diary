# Variablen
VENV_DIR = venv
PYTHON = $(VENV_DIR)/bin/python
SCRIPT = send_mail.py

# Ziel: Erstelle das virtuelle Environment, falls es nicht existiert
$(VENV_DIR)/bin/activate: 
	python3 -m venv $(VENV_DIR)
	$(PYTHON) -m pip install --upgrade pip

# Ziel: Installiere Abhängigkeiten (falls requirements.txt existiert)
install: $(VENV_DIR)/bin/activate
	@if [ -f requirements.txt ]; then $(PYTHON) -m pip install -r requirements.txt; fi

# Ziel: Starte das Skript
send: install
	$(PYTHON) $(SCRIPT)

fetch: install
	$(PYTHON) fetch_mail.py

# Ziel: Bereinige das virtuelle Environment
clean:
	rm -rf $(VENV_DIR)