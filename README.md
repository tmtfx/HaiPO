# HaiPO
A PO editor for Haiku

This project started as a personal PO editor for Haiku. It has been designed to accomplish my needings in translating po files for Friulian language under Haiku, but keeping in mind it could be usefull for other languages too. So it supports multiple plurals and other particularities.
It features the foundamental functions, as writing and saving the translations for the relative source string, handling comments and po headers. But as the project grew up it started integrating a spellchecking system and a Local/Remote Translation Memory.
It integrates a local TM server but a simple remote translation memory server is provided within this repository. You can feel free to create your own faster method for handling the TM requests; both (the integrated server or the external one) are provided just to show what you should transmit from and to the client. They are there to show you how to keep the compatibility.
The spellchecking system uses pyenchant, which in our use-case, relies on hunspell/myspell dictionaries.

tmserver.py
is the standalone translation memory server
