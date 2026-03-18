# Vintage Radio - Tips


## Q&A - Problématiques rencontrées

### pynput requires a graphical display (X server) to capture keyboard input

- On peut remplacer `pyinput` par `termios` and `tty`. OK en mode console, mais ne fonctionne plus sous Windows.
- Il faut implémenter du cross-platform.
   - option 1 : conditionnal imports (Uses only built-in Python modules)
   - option 2 : librairie cross-platfom `readchar`
   Lumo recommande l'option 1 dans notre cas.


### PyCharm ne redirige pas les touches vers l'app

Aller dans le menu `Run -> Edit Configuration -> Modify options` et cocher **Emulate terminal in output console**.


### Raspberry: pas d'echo sur le terminal SSH

Tapez ceci pour rétablir le mode normal sur le terminal bloqué:

```
stty sane
```

## Choix du module de sortie son

- Sous Raspberry `--aout {any,pulse,alsa,adummy,amem,afile,none}`
- sous Windows `--aout={any,mmdevice,directsound,waveout,amem,afile,adummy,none}`

Lumo recommande `mmdevice` pour Windows et `alsa` pour Raspberry.

Test sur Raspberry avec clvc:
- directsound : ok
- mmdevice : ok
- any : ok
- pulse : ok
- alsa: **no sound**

En tant que daemon:
- alsa : vlcpulse audio output error: PulseAudio server connection failure: Connection refused
- pulse : idem
- mmdevice : idem
- any : idem

### **** Liste des périphériques matériels PLAYBACK ****

```
 aplay -l
**** Liste des périphériques matériels PLAYBACK ****
carte 0 : Headphones [bcm2835 Headphones], périphérique 0 : bcm2835 Headphones [bcm2835 Headphones]
  Sous-périphériques : 8/8
  Sous-périphérique #0 : subdevice #0
  Sous-périphérique #1 : subdevice #1
  Sous-périphérique #2 : subdevice #2
  Sous-périphérique #3 : subdevice #3
  Sous-périphérique #4 : subdevice #4
  Sous-périphérique #5 : subdevice #5
  Sous-périphérique #6 : subdevice #6
  Sous-périphérique #7 : subdevice #7
carte 1 : vc4hdmi [vc4-hdmi], périphérique 0 : MAI PCM i2s-hifi-0 [MAI PCM i2s-hifi-0]
  Sous-périphériques : 1/1
  Sous-périphérique #0 : subdevice #0
```
