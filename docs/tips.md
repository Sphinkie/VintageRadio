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

### Liste des périphériques matériels PLAYBACK 

```shell
$ aplay -l
 
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

### Liste des périphériques matériels PULSE

Cette commande done la liste des sortie audio connues (**bluez** = bluetooth)

```shell
$ pactl list short sinks
# 56      alsa_output.platform-3f00b840.mailbox.stereo-fallback   PipeWire        s16le 2ch 48000Hz       SUSPENDED
# 118     bluez_output.20_18_5B_06_45_B0.1        PipeWire        s16le 2ch 44100Hz       SUSPENDED

# Obtenir la liste détaillée
$ pactl list sinks

# Obtenir des détails sur l'équipement bluetooth connecté (dont l'adresse MAC)
$ bluetoothctl info
```

### Configurer PipeWire pour la connexion automatique à l'enceinte JLB

```shell
# Assignation
$ pactl set-default-sink bluez_output.20_18_5B_06_45_B0.1
# Unmute
$ pactl set-sink-mute bluez_output.20_18_5B_06_45_B0.1 0
# Volume 80%
$ pactl set-sink-volume bluez_output.20_18_5B_06_45_B0.1 80%
# Voir le résultat
$ pactl info
 Chaîne du serveur : /run/user/1000/pulse/native
 Version du protocole de bibliothèque : 35
 Version du protocole du serveur : 35
 Local : oui
 Index client : 138
 Tile Size : 65472
 Nom d’utilisateur : pi
 Nom d’hôte : Raspberry
 Nom du serveur : PulseAudio (on PipeWire 1.4.2)
 Version du serveur : 15.0.0
 Spécification d’échantillon par défaut : float32le 2ch 48000Hz
 Plan de canaux par défaut : front-left,front-right
 Destination par défaut : bluez_output.20_18_5B_06_45_B0.1
 Source par défaut : bluez_output.20_18_5B_06_45_B0.1.monitor
 Cookie : 3b8b:f4f4
```

Note : voir !484 et svtes pour Alsa


### Create the PipeWire Configuration File

Create the permanent PipeWire configuration for your Bluetooth speaker. 
This will ensure the sink preference persists across reboots and is more robust than the runtime pactl command.

> DO NOT USE: pas trouvé la cause, mais en partique, la présence de ce fichier *empèche* la connection à l'enceinte bluetooth.

```shell
sudo mkdir -p /etc/pipewire/pipewire.conf.d
sudo nano /etc/pipewire/pipewire.conf.d/99-default-sink.conf
```

Add This Content.

```
# Default audio sink configuration for VintageRadio
# Created: 2026-03-21

context.properties = {
    # Set the default audio sink to your Bluetooth speaker
    # This persists across reboots
    default.audio.sink = bluez_output.20_18_5B_06_45_B0.1
    
    # Optional: Set default sample rate (matches your speaker capability)
    default.clock.rate = 44100
    
    # Optional: Prevent automatic suspension when idle
    # default.clock.quantum = 1024
}

context.modules = [
    # Ensure Bluetooth modules are loaded
    { name = libpipewire-module-bluez5
      args = {
        bluez5.enable = true
        bluez5.enable-sbc-xq = true
        bluez5.enable-msbc = true
        bluez5.enable-hw-volume = true
        bluez5.headset-roles = [ hsp_hs hsp_ag hfp_hf hfp_ag a2dp_sink a2dp_source ]
      }
    }
]
```

Restart PipeWire Services.

```shell
# Restart PipeWire and PulseAudio compatibility layer
systemctl --user restart pipewire pipewire-pulse wireplumber
# Or with sudo if the services are running at system level
# sudo systemctl restart pipewire pipewire-pulse wireplumber

# Wait a moment for services to stabilize
sleep 3

# Verify the default sink
pactl info | grep "Default Sink"
# You should see:
# Default Sink: bluez_output.20_18_5B_06_45_B0.1

sudo systemctl restart vintageradio.service
```

### If You Change Speakers Later

If you replace your JBL Flip 5 with a different Bluetooth speaker:

```shell
# 1. Find the new sink name
pactl list short sinks | grep bluez

# 2. Edit the configuration
sudo nano /etc/pipewire/pipewire.conf.d/99-default-sink.conf

# 3. Update the sink name
# Change: default.audio.sink = bluez_output.NEW_MAC_ADDRESS.1

# 4. Restart services
systemctl restart pipewire pipewire-pulse
# Or with sudo if the services are running at system level
# sudo systemctl restart pipewire pipewire-pulse

```
