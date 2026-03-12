# VintageRadio pour Raspberry

> work in progress

## Description 

A command-line python program for RaspberryPi that plays music served by a DLNA NAS (Synology).

Faire CTRL-C pour stopper

## Tips

### Sur Raspberry:

- Apairer la sortie audio avec une enceinte bluetooth si souhaité.
- Installation:
```bash
sudo apt update
sudo apt install python3-pip python3-vlc python3-mutagen
pip3 install -r requirements.txt   # (optional, if you add extra deps)
git clone https://github.com/Sphinkie/VintageRadio
...
# update with:
git pull
...
# run with
cd Programmes/VintageRadio
python VintageRadio.py
```

### Sur Windows:

- appliquer les modules `python vlc` et `mutagen` dans l'environnement virtuel.
  (ou faire `pip install python-vlc` et `pip install mutagen` ).

- Utilise la librairie Python `libvlc.dll`.

- Ajouter la DLl de VLC au path
   `setx Path "%Path%;C:\Program Files\VideoLAN\VLC"`