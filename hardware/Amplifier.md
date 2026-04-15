# Vintage Radio

Avec un haut-parleur de 4Ω et 5W, vous avez des spécifications très courantes pour les projets DIY Raspberry Pi.  
Voici ce que cela implique pour votre choix d'amplification :

## Analyse de votre haut-parleur

Impédance (4Ω) : C'est une impédance basse. Beaucoup d'amplis "grand public" sont conçus pour 8Ω. Il faut donc un ampli capable de gérer 4Ω sans surchauffer.
Puissance (5W) : C'est une petite puissance. Un ampli de 5W à 10W par canal sera largement suffisant. Si vous mettez un ampli de 50W, vous risquez de griller le haut-parleur si vous montez le volume trop haut.
Taille (7cm) : Idéal pour une petite enceinte de bureau ou une radio vintage compacte.

## La solution idéale : Carte HAT DAC + Ampli  

C'est la solution la plus propre pour un Raspberry Pi (pas de câbles externes, qualité audio supérieure à la prise jack).  
Je vous recommande vivement l'une de ces cartes (elles supportent toutes les 4Ω) :

### Option A : JustBoom DAC HAT (Le plus simple) - discontinued.

- Puissance : 2x 5W (parfaitement adapté à votre HP).
- Impédance : Supporte 4Ω à 8Ω.
- Avantages : Très facile à installer, logiciel inclus pour le contrôle du volume via GPIO ou logiciel.
- Prix : ~35-40€.

https://www.audiophonics.fr/en/dac-and-interfaces-for-raspberry-pi/justboom-dac-hat-dac-pcm5122-for-raspberry-pi-3-pi-2-a-b-p-11602.html


### Option B : HiFiBerry DAC+ Amp (Un peu plus de puissance)

- Puissance : 2x 12W (vous aurez de la marge, attention au volume !).
- Impédance : Supporte 4Ω.
- Avantages : Son très clair, bonne réputation.
- Prix : 48€.

https://www.amazon.fr/-/en/HiFiBerry-DACPLUS-RCA-RB-Hifiberry2/dp/B0147RA2PY?crid=FSKGIOH0OKNM&dib=eyJ2IjoiMSJ9.OOoNlo9uq9z7R7TSlO3EXlB9o6PKzJOx60zpB6jhVFYHsZj0oivba5k9ffBa1ch-TzWv0vJCcoAs0AyTGJRJu9kF6C3vlXSXid-Ay02DFilXJfzTSk6RiC5v2eG2JB8fpkOAFbWJxILxMKKGr740WyAI3NdL6FFld5KikBsPnxn8g21p4rOV9O-oz-s8cokGnLi068uCWUHVTUynzz2absTn5XyFnDZseQHCWAj3uziG5msSd5vXMSz6oWPjK-2qTdf3qQdZDFgv3yrn_ZhRQDWO69D7_8o3C29E-C8uS7w.q7uYB6zA8M8aqY3v7zRaFPBfLw0qDgLe9XOkO7hPZc8&dib_tag=se&keywords=raspberry%2Bamp%2Bdac%2Bhat&qid=1775921383&s=electronics&sprefix=rasperry%2Bamp%2Bdac%2Bhat%2Celectronics%2C234&sr=1-6&th=1


### Raspberry Pi DAC Audio IQaudio DAC+ 

- Fully HAT compliant accessory; EEPROM
- Full-HD audio - playback up to 24 bit/192 kHz
- Built-in hardware volume control (via ALSA), 2v RMS full
- Amplifier
- Prix : 27€.

https://www.amazon.fr/-/en/Raspberry-Pi-DAC-Audio-IQaudio/dp/B0BQCMYWYX?crid=FSKGIOH0OKNM&dib=eyJ2IjoiMSJ9.OOoNlo9uq9z7R7TSlO3EXlB9o6PKzJOx60zpB6jhVFYHsZj0oivba5k9ffBa1ch-TzWv0vJCcoAs0AyTGJRJu9kF6C3vlXSXid-Ay02DFilXJfzTSk6RiC5v2eG2JB8fpkOAFbWJxILxMKKGr740WyAI3NdL6FFld5KikBsPnxn8g21p4rOV9O-oz-s8cokGnLi068uCWUHVTUynzz2absTn5XyFnDZseQHCWAj3uziG5msSd5vXMSz6oWPjK-2qTdf3qQdZDFgv3yrn_ZhRQDWO69D7_8o3C29E-C8uS7w.q7uYB6zA8M8aqY3v7zRaFPBfLw0qDgLe9XOkO7hPZc8&dib_tag=se&keywords=raspberry+amp+dac+hat&qid=1775921383&s=electronics&sprefix=rasperry+amp+dac+hat%2Celectronics%2C234&sr=1-13

### Adafruit MAX98357A I2S Amp Breakout (Le moins cher)

- Puissance : 3.2W (un peu juste pour 5W, mais souvent suffisant pour une petite pièce).
- Technologie : Classe D (très efficace, chauffe peu).
- Nécessite un peu plus de câblage manuel que les HAT.
- Prix : ~5€ 

https://www.adafruit.com/product/3006

### InnoMaker (Plus récentes)

- InnoMaker DAC Mini Hat PCM5122 Audio Card for Raspberry Pi 5/4/3B+/Zero 2W, 
   HiFi Sound Shield 384kHz/32bit with RCA Output and 3.5mm jack (pas on-Board)
   29€ Amazon
   
https://www.amazon.fr/-/en/InnoMaker-PCM5122-Raspberry-Shield-384kHz/dp/B0D12M8D2T?crid=FSKGIOH0OKNM&dib=eyJ2IjoiMSJ9.OOoNlo9uq9z7R7TSlO3EXlB9o6PKzJOx60zpB6jhVFaAx7VF4iLTpEnXyI4X0x7m_GqNr1k8LzAxxvEfIGQACzeCKxVOHrUvNv5ixUDjrResc-ufCaJoHpWVvQ_wPZr-pkOAFbWJxILxMKKGr740W530ylsqx3AV_CjB9khffjWp2Nhr3v1lCWpJ8nGtQDOitHU5lLjf4crRXugBpzcSlpC0W5jvFtZLIe4FgapmWFDD8TrvSKohmmMAYN1l8nRdn9UNN3js56PZETWe9fWECmNyUoDuv3q1pr3NJBOp-mI.Sbv57pebClzFm3l9pW9wiJU7Y-L2pCUs7vMjiWkE96o&dib_tag=se&keywords=raspberry+amp+dac+hat&qid=1776239563&s=electronics&sprefix=rasperry+amp+dac+hat%2Celectronics%2C234&sr=1-2

- InnoMaker RPI HiFi AMP Hat TAS5713 Amplifier Audio Module 25W Class D Power.  
   Sound Card Extension Board for Raspberry Pi 5/4/3/B+/Pi/Zero Capacitor Nichicon.   
   Sortie sur connecteur.  
   Alternative power supply = 12/20v.  
   36€ Amazon.

https://www.amazon.fr/-/en/InnoMaker-Amplifier-Extension-Raspberry-Capacitor/dp/B07CZZ95B9?crid=FSKGIOH0OKNM&dib=eyJ2IjoiMSJ9.OOoNlo9uq9z7R7TSlO3EXlB9o6PKzJOx60zpB6jhVFaAx7VF4iLTpEnXyI4X0x7m_GqNr1k8LzAxxvEfIGQACzeCKxVOHrUvNv5ixUDjrResc-ufCaJoHpWVvQ_wPZr-pkOAFbWJxILxMKKGr740W530ylsqx3AV_CjB9khffjWp2Nhr3v1lCWpJ8nGtQDOitHU5lLjf4crRXugBpzcSlpC0W5jvFtZLIe4FgapmWFDD8TrvSKohmmMAYN1l8nRdn9UNN3js56PZETWe9fWECmNyUoDuv3q1pr3NJBOp-mI.Sbv57pebClzFm3l9pW9wiJU7Y-L2pCUs7vMjiWkE96o&dib_tag=se&keywords=raspberry+amp+dac+hat&qid=1776239563&s=electronics&sprefix=rasperry+amp+dac+hat%2Celectronics%2C234&sr=1-5

## Comment câbler votre haut-parleur

Sur ces cartes HAT, vous trouverez généralement deux borniers (pour stéréo gauche/droite). 

### Branchement

Comme vous n'avez qu'un seul haut-parleur, connectez les deux fils de votre haut-parleur sur le bornier LEFT (Gauche) ou RIGHT (Droite).

### Configuration logicielle

Dans votre fichier de configuration audio (`/boot/config.txt` ou via `raspi-config`), vous pouvez **forcer la sortie en Mono** si vous voulez que le son sorte des deux canaux (si vous branchez le HP sur un seul, il n'y aura pas de problème, mais le son sera centré).
Ou simplement laisser VLC jouer en stéréo : le canal gauche sortira sur votre HP, le droit sera silencieux.



## Attention à l'alimentation

Ces cartes HAT tirent leur courant directement du port GPIO du Raspberry Pi.

Assurez-vous d'utiliser une alimentation USB de bonne qualité (2.5A ou 3A) pour le Pi.
Si l'alimentation est faible, vous entendrez des craquements quand la musique est forte (le voltage chute).

## Résumé du plan d'action

Achetez une DAC HAT pour ampli 5W/4Ω.  
Branchez-la sur les GPIO du Pi.    
Soudez ou vissez votre haut-parleur sur les borniers de la carte.  

Configurez le Pi pour utiliser la carte audio (`sudo raspi-config` -> `Advanced Options` -> `Audio` -> `HAT`).  
=> Dans le code Python (lib/dlna_music.py), VLC détectera automatiquement la nouvelle carte audio.  

