#!/bin/bash

# Script per inizializzare un file .po (gettext) a partire da un file .pot
# Uso: ./crea_po.sh <file_pot_input> <file_po_output> <codice_iso_lingua>

## 1. Verifica degli argomenti
# Controlla se sono stati forniti esattamente 3 argomenti
if [ "$#" -ne 3 ]; then
    echo "Errore: Devi fornire esattamente 3 argomenti."
    echo "Uso: $0 <file_pot_input> <file_po_output> <codice_iso_lingua>"
    exit 1
fi

## 2. Assegnazione delle variabili
# Assegna i parametri alle variabili per chiarezza
FILE_POT="$1"
FILE_PO="$2"
LINGUA_ISO="$3"

## 3. Verifica del file .pot
# Controlla se il file .pot esiste
if [ ! -f "$FILE_POT" ]; then
    echo "Errore: Il file POT di input '$FILE_POT' non esiste."
    exit 1
fi

## 4. Esecuzione di msginit
echo "Inizializzazione del file PO..."
echo "  - File POT: $FILE_POT"
echo "  - File PO destinazione: $FILE_PO"
echo "  - Lingua (ISO): $LINGUA_ISO"

# Esegue il comando msginit con gli argomenti forniti
# -i <file.pot> specifica il file di input (template)
# -o <file.po> specifica il file di output
# -l <lingua> specifica il codice lingua (Locale)
msginit -i "$FILE_POT" -o "$FILE_PO" -l "$LINGUA_ISO"

# 5. Verifica del risultato
if [ $? -eq 0 ]; then
    echo
    echo "✅ Successo: Il file PO '$FILE_PO' per la lingua '$LINGUA_ISO' è stato creato con successo."
else
    echo
    echo "❌ Errore: Il comando 'msginit' non è riuscito a creare il file PO."
    exit 1
fi