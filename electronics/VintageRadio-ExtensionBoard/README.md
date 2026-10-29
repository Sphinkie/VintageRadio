# Vintage Radio

## Extension boards

### Objectifs

La carte d'extension offre des connecteurs permetant de connecter directement dessus: 
- LEDs
- Boutons
- Potentionmètres

Elle contient donc les composants d'interface nécessaires, tels que résistances ou circuits intégrés.


### Contraintes

Elle se pluggue sur le connecteur 40 du Rpi + Inno de façon à accéder directement aux bus SPI, I2C, GPIO, et au +5v.

Il faut faire attention au volume de ce blioc et à son placement car le boitier n'est très grand.

Le boitier contient en particulier un HP avec un aimant assez puissant: d'où un risque de pertubation dû au champ magnitique ? A demander.


### Accessoires

D'autres minicartes (mini-boards) sont à prévoir pour supporter certains composants:

- minicarte de support de la LEDbar : connecteur 8pin

- au niveau du "Power" switch : connecteur alim + switch/Led + Res + regulateur de tension