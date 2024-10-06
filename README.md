# HaiPO
A PO editor for Haiku

This project started as a personal PO editor for Haiku, designed to accomplish my needings in translating po files for Friulian language under the Haiku. But keeping in mind it could be usefull for other languages too. So supporting multiple plurals and other particularities.
It features some foundamental functions, as writing translations on relative source string position, handling comments and po headers, but the project grew at point of integrating a spellchecking system and a Local/Remote Translation Memory.
It integrates a local TM server but a simple remote translation memory server is provided within this repository, but you can feel free to create your own faster method for handling the requests; this is provided just to show what should be transmitted from and to the client, to show you how to keep the compatibility.
The spellchecking system uses pyenchant, which in our use-case, relies on hunspell/myspell dictionaries

tmserver.py
the translation memory uses translate-toolkit (use pip download translate-toolkit) after installing from haikudepot lxml_devel lxml2_devel lxslt_devel CMake and some others...I'll define them later

pip install
rapidfuzz
pip download
skbuild -> aggiungere in platforms bsd "haiku"
Levenshtein <- scaricare da pip e compilare da terminale python3 setup.py install 

per lo spellcheck utilizzare pyenchant e libreria enchant distribuiti in HaikuDepot
