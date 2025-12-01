# HaiPO
A PO editor for Haiku

This project started as a personal PO editor for Haiku. It has been designed to accomplish my needings in translating po files for Friulian language under Haiku, but keeping in mind it could be usefull for other languages too. So it supports multiple plurals and other particularities.
It features the foundamental functions, as writing and saving the translations for the relative source strings, handling comments and po headers. But, as the project grew up, it started integrating a spellchecking system and a Local/Remote Translation Memory.
It integrates a built-in TM server but it is a simple proof of concept, it should be better creating a standalone one. You can feel free to create your own faster method for handling the TM requests; there's also a standalone TM server written in python that mimics the integrated one. Both servers (the integrated and the external one) are provided just to show you the transmission logic that occurs between server and client.
The spellchecking system uses pyenchant, which in our use-case, relies on hunspell/myspell dictionaries.
And well, like any serious app, it is localized, and you can use HaiPO to localize it in your language. Feel free to send me the .po file through e-mail (f.t.public@gmail.com) or with a PR.

tmserver.py
is the standalone translation memory server
