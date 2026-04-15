# Vintage Radio

## Bill Of Material

**F**: disponible chez Farnell.

- [ ] Amplificateur audio (mono)
   InnoMaker RPI HiFi AMP Hat TAS5713 Amplifier Audio Module 25W Class D Power.  
   Sound Card Extension Board for Raspberry Pi 5/4/3/B+/Pi/Zero.  
   Capacitor Nichicon. Connexion SPI. Sortie sur connecteur. Réglage du gain.  
   Power supply = 12/20v.  
   36€ Amazon.  
   
- [x] Ecran ePaper
   Deux modèles à disposition dan le stock:
   - ePaper 2.13" - 5cm x 2.5xm - SPI - 250 x 122
   - ePaper 2.9" - 3cm x 6.8cm - SPI - 296 x 128
   Connexion SPI.

- [x] Haut parleur - 4Ω - 5 W - Diamètre 7cm

- [x] 3x PushButton (Again / Star me / Next)

- [x] 4x PushButton (Genre / Year / Beat / Blutooth)

- [x] 1x Micro PushButton (Reset database) - En face arrière.

- [x] 1x Switch Button (Local files/DLNA)

- [x] 8x Résistance pour PushButton (10kΩ) SIL 9

- [x] 1x Power Button (incl. LED)
- [ ] 1x Resistance ??

- [x] 1x LED (status "ON") Jaune.
- [ ] 1x Resistance 150Ω

- [x] 2x LED E10 (Eclairage tuning)
- [ ] 2x Resistance ??

- [x] 1x LED bar (Affichage du rating) (7 Leds vertes) 2.2v 20mA => 150Ω sous 5v
- [ ] 7x Resistance 150Ω - Vérifier dans le stock

- F [ ] 4x LED (Mode) Ambre. Prévoir 2 à 3 cd (20 à 30 lumen)
- [ ] 4x Resistance ??

- [x] 1x LED (Eclairage ePaper) - Double blanche avec résistances 380Ω

- F [ ] 2x 74HC595 Registres à décalage pour controle des LEDs 

- F [ ] 1x MCP23017 (16 pins) ou PCF8574 (8pins) I2C Expander pour controle des Pushbutton

- F [ ] 2x MCP3008 Convertisseur analogique-numerique (ADC).  
   8 canaux, 10 bits (1024 valeurs) - Connexion SPI.  
   Simple à câbler, bibliothèque Python (spidev).   
   Adafruit 5€ Product ID: 856  
	
- [ ] Potentiomètre 10kΩ - linéaire A.
   Trop difficile à trouver en 180° (*half-turn*) => on prend un *single-turn*.
	
- [ ] Potentiomètre 10kΩ - linéaire A - Avec interrupteur.

- [ ] Ecran plexi
