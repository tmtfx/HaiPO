# HaiPO
My personal PO editor for Haiku

This po file editor has been designed to accomplish my needings in translating po files for Friulian language under the Haiku 
operating system. But I think it can be used for any language out there.
It features some basic functions of normal po editors, as writing translations on relative source string position, handling
comments and headers, but also integrates a rudimental spellchecking system if enabled and a Remote Translation Memory if
enabled as well. A simple remote translation memory server is provided within this repository, but you can feel free to create
faster methods for handling the requests; this is provided just to show what should be transmitted from and to the client.


tmserver.py
for tranlation memory uses translate-toolkit (use pip translate-toolkit) after installing from haikudepot lxml_devel lxml2_devel lxslt_devel CMake and some others...I'll define them later

pip
rapidfuzz
skbuild -> aggiungere in platforms bsd "haiku"
Levenshtein <- scaricare da pip e compilare da terminale python3 setup.py install 

