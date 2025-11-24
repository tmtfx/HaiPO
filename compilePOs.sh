#!/bin/bash
#find locale -name "*.po" -exec sh -c 'msgfmt -c -o "${0/.po/.mo}" "$0"' {} \;

# Cartella di base in cui cercare i file PO
BASE_LOCALE_DIR="data/locale"

echo "--- Avvio della compilazione di tutti i file PO in MO ---"

# Trova tutti i file .po nella struttura data/locale/.../LC_MESSAGES/
find "$BASE_LOCALE_DIR" -name "*.po" | while read PO_FILE; do
    
    # Deriva il percorso del file .mo di output sostituendo .po con .mo
    MO_FILE="${PO_FILE/.po/.mo}"
    
    echo "⏳ Compilazione di: $PO_FILE -> $MO_FILE"
    
    # Esegue msgfmt con le opzioni richieste
    # -o: file output (.mo)
    # --check-format: controlla gli errori di formattazione nelle stringhe
    # --statistics: mostra un riepilogo delle stringhe tradotte/fuzzy/non tradotte
    msgfmt --check-format --statistics -o "$MO_FILE" "$PO_FILE"
    
    if [ $? -eq 0 ]; then
        echo "   ✨ OK: Compilazione riuscita."
    else
        echo "   ❌ Errore durante la compilazione (controlla gli errori di formattazione sopra)."
    fi
    
done

echo "---"
echo "✅ Compilazione di tutti i file .mo completata."