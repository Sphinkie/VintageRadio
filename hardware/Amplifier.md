Avec un haut-parleur de 4Ω et 5W, vous avez des spécifications très courantes pour les projets DIY Raspberry Pi.Voici ce que cela implique pour votre choix d'amplification :

1. Analyse de votre haut-parleur

Impédance (4Ω) : C'est une impédance basse. Beaucoup d'amplis "grand public" sont conçus pour 8Ω. Il faut donc un ampli capable de gérer 4Ω sans surchauffer.
Puissance (5W) : C'est une petite puissance. Un ampli de 5W à 10W par canal sera largement suffisant. Si vous mettez un ampli de 50W, vous risquez de griller le haut-parleur si vous montez le volume trop haut.
Taille (7cm) : Idéal pour une petite enceinte de bureau ou une radio vintage compacte.

2. La solution idéale : Carte HAT DAC + Ampli
C'est la solution la plus propre pour un Raspberry Pi (pas de câbles externes, qualité audio supérieure à la prise jack).
Je vous recommande vivement l'une de ces cartes (elles supportent toutes les 4Ω) :

Option A : JustBoom DAC HAT (Le plus simple) - discontinued.

Puissance : 2x 5W (parfaitement adapté à votre HP).
Impédance : Supporte 4Ω à 8Ω.
Avantages : Très facile à installer, logiciel inclus pour le contrôle du volume via GPIO ou logiciel.
Prix : ~35-40€.
https://www.audiophonics.fr/en/dac-and-interfaces-for-raspberry-pi/justboom-dac-hat-dac-pcm5122-for-raspberry-pi-3-pi-2-a-b-p-11602.html


Option B : HiFiBerry DAC+ Amp (Un peu plus de puissance)

Puissance : 2x 12W (vous aurez de la marge, attention au volume !).
Impédance : Supporte 4Ω.
Avantages : Son très clair, bonne réputation.
Prix : ~45-50€.

Option C : Adafruit MAX98357A I2S Amp Breakout (Le moins cher)

Puissance : 3.2W (un peu juste pour 5W, mais souvent suffisant pour une petite pièce).
Technologie : Classe D (très efficace, chauffe peu).
Prix : ~5€ (mais nécessite un peu plus de câblage manuel que les HAT).
https://www.adafruit.com/product/3006

plus récentes:

- InnoMaker DAC Mini Hat PCM5122 Audio Card for Raspberry Pi 5/4/3B+/Zero 2W, 
   HiFi Sound Shield 384kHz/32bit with RCA Output and 3.5mm jack
   30€ Amazon

- InnoMaker RPI HiFi AMP Hat TAS5713 Amplifier Audio Module 25W Class D Power 
   Sound Card Extension Board for Raspberry Pi 5/4/3/B+/Pi/Zero Capacitor Nichicon 
   36€ Amazon.
   Sortie sur connecteur.
   alternative powedr supply = 12/20v

3. Comment câbler votre haut-parleur
Sur ces cartes HAT, vous trouverez généralement deux borniers (pour stéréo gauche/droite). Comme vous n'avez qu'un seul haut-parleur :

Branchement : Connectez les deux fils de votre haut-parleur sur le bornier LEFT (Gauche) ou RIGHT (Droite).
Configuration logicielle :

Dans votre fichier de configuration audio (/boot/config.txt ou via raspi-config), vous pouvez forcer la sortie en Mono si vous voulez que le son sorte des deux canaux (si vous branchez le HP sur un seul, il n'y aura pas de problème, mais le son sera centré).
Ou simplement laisser VLC jouer en stéréo : le canal gauche sortira sur votre HP, le droit sera silencieux.



4. Attention à l'alimentation
Ces cartes HAT tirent leur courant directement du port GPIO du Raspberry Pi.

Assurez-vous d'utiliser une alimentation USB de bonne qualité (2.5A ou 3A) pour le Pi.
Si l'alimentation est faible, vous entendrez des craquements quand la musique est forte (le voltage chute).

Résumé du plan d'action

Achetez une JustBoom DAC HAT (ou équivalent HiFiBerry) car elle correspond parfaitement à vos 5W/4Ω.
Branchez-la sur les GPIO du Pi.
Soudez ou vissez votre haut-parleur sur les borniers de la carte.
Configurez le Pi pour utiliser la carte audio (sudo raspi-config -> Advanced Options -> Audio -> HAT).
Dans votre code Python (lib/dlna_music.py), VLC détectera automatiquement la nouvelle carte audio.

Voulez-vous que je vous montre comment modifier le code Python pour s'assurer que VLC utilise bien cette nouvelle carte audio par défaut ?