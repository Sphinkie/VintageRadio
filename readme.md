# VintageRadio pour Raspberry

> work in progress

## Description 

A command-line python program for RaspberryPi that plays music served by a DLNA NAS (Synology).

## Tips

### Sur Raspberry:

- Apairer la sortie audio avec une enceinte bluetooth si souhaité.
- commandes utiles:
```
apt instal python3-vlc
git clone https://github.com/Sphinkie/VintageRadio
cd Programmes/VintageRadio
python list_dlna.py
...
# update with:
git pull
```

### Sur Windows:

- appliquer le module `python vlc` dans l'environnement virtiel.
  (ou faire `pip install python-vlc`).

Utilise la librairie Python `libvlc.dll`.
