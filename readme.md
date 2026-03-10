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
sudo apt install python3-pip python3-vlc
sudo apt install python3-pynput
sudo apt install python3-pynput
pip3 install -r requirements.txt   # (optional, if you add extra deps)
git clone https://github.com/Sphinkie/VintageRadio
cd Programmes/VintageRadio
python list_dlna.py
...
# update with:
git pull
...
# run with
python VintageRadio.py
```

### Sur Windows:

- appliquer le module `python vlc` dans l'environnement virtuel.
  (ou faire `pip install python-vlc`).

- Utilise la librairie Python `libvlc.dll`.
