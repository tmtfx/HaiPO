#msginit -i haipo.pot -o data/locale/it/LC_MESSAGES/haipo.po -l it

#!/bin/bash

# Nome del file POT di input
POT_FILE="haipo.pot"

# Nome del dominio (base del file .po)
DOMAIN="haipo"

# Cartella di base per le traduzioni
BASE_LOCALE_DIR="data/locale"

# --- Verifica Argomenti ---
if [ -z "$1" ]; then
    echo "Errore: Devi fornire il codice ISO della lingua come parametro."
    echo "Utilizzo: ./generate_po.sh <codice_lingua_iso>"
    echo "Esempio: ./generate_po.sh fur"
    exit 1
fi

# Codice lingua (es. "fur", "it", "en")
LANG_CODE="$1"

# Percorso completo dove verrà creato il file .po
OUTPUT_DIR="${BASE_LOCALE_DIR}/${LANG_CODE}/LC_MESSAGES"
OUTPUT_FILE="${OUTPUT_DIR}/${DOMAIN}.po"

# --- Esecuzione ---

echo "✅ Lingua target: ${LANG_CODE}"
echo "✅ File POT sorgente: ${POT_FILE}"
echo "⏳ Creazione della directory: ${OUTPUT_DIR}"

# Crea la struttura di directory se non esiste
mkdir -p "$OUTPUT_DIR"

if [ $? -ne 0 ]; then
    echo "❌ Errore durante la creazione della directory."
    exit 1
fi

echo "⏳ Generazione del file .po tramite msginit..."

# Esegue msginit
# -i: file input (POT)
# -o: file output (PO)
# -l: codice lingua
msginit -i "$POT_FILE" -o "$OUTPUT_FILE" -l "$LANG_CODE"

if [ $? -eq 0 ]; then
    echo "--------------------------------------------------------"
    echo "✨ Successo! File PO creato per la lingua ${LANG_CODE}."
    echo "Percorso: ${OUTPUT_FILE}"
    echo "--------------------------------------------------------"
else
    echo "❌ Errore durante l'esecuzione di msginit. Verifica che ${POT_FILE} esista."
    exit 1
fi