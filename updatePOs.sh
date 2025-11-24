#!/bin/bash
#for lang in data/locale/*/LC_MESSAGES/*.po; do
#    #msgmerge -o "$lang" "$lang" haipo.pot
#      msgmerge -o haipo.po haipo.po haipo.pot
#done

#!/bin/bash

# Nome del file POT di input (la fonte degli aggiornamenti)
POT_FILE="haipo.pot"

# Cartella di base in cui cercare i file PO (ad esempio: data/locale)
BASE_LOCALE_DIR="data/locale"

# --- Verifica preliminare ---

if [ ! -f "$POT_FILE" ]; then
    echo "❌ Errore: File POT non trovato: $POT_FILE"
    echo "Assicurati di aver generato il template con xgettext prima di eseguire l'aggiornamento."
    exit 1
fi

echo "✅ File POT sorgente trovato: $POT_FILE"
echo "--- Avvio dell'aggiornamento di tutti i file PO con msgmerge ---"

# Trova tutti i file .po nella struttura locale/lingua/LC_MESSAGES
# Utilizziamo find per cercare tutti i file che terminano con '.po' nella directory BASE_LOCALE_DIR
find "$BASE_LOCALE_DIR" -name "*.po" | while read PO_FILE; do
    
    echo "⏳ Aggiornamento di: $PO_FILE"
    
    # Esegue msgmerge per aggiornare il file PO
    # Sintassi: msgmerge -o <output_file> <existing_po_file> <new_pot_file>
    # Stiamo sovrascrivendo il file esistente con i dati uniti.
    
    msgmerge -U "$PO_FILE" "$POT_FILE"
    
    if [ $? -eq 0 ]; then
        echo "   ✨ OK: Aggiornamento completato. Controllare le stringhe # fuzzy."
    else
        echo "   ❌ Errore durante l'unione per il file: $PO_FILE"
    fi
    
done

echo "---"
echo "✅ Aggiornamento di tutti i file PO completato."
echo "Non dimenticare di compilare i file .mo con msgfmt dopo la revisione!"