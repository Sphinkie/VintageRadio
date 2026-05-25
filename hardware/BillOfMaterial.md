# Vintage Radio

## Bill Of Material



### Outputs
   
- [x] Ecran ePaper
   Deux modèles à disposition dan le stock:
   - ePaper 2.13" - 5cm x 2.5xm - SPI - 250 x 122
   - ePaper 2.9" - 3cm x 6.8cm - SPI - 296 x 128
   Connexion SPI.

- [x] Haut parleur - 4Ω - 5 W - Diamètre 7cm

- [x] 1x LED Jaune (status "ON"). 
- [] 1x Resistance 150Ω (sous 3.3v)

- [ ] 4x LED (Mode) Ambre. Prévoir 2 à 3 cd (20 à 30 lumen).  | 
- [] 4x Résistance 150Ω (sous 3.3v — Vf=2.1v, 8mA/led).  

- [x] 1x LED bar (Affichage du rating) (7 Leds vertes) 2.2v 20mA
- [] 7x Résistance 150Ω (sous 3.3v — Vf=2.2v, 7.3mA/led, 51mA total — dans la limite 74HC595 70mA max)

- [x] 2x LED E10 (Eclairage tuning) : [L3 + L4 ]
- [] 2x Résistance 150Ω (sous 5v — Vf=2.0v, 20mA/led)

- [x] 1x LED (Eclairage ePaper) - Blanche - [L1 + L2]
- [x] Résistances 380Ω (incluses) - (nécessite 5v).  

### Inputs

- [x] 3x PushButton (Again / Star me / Next)
- [x] 4x PushButton (Genre / Year / Beat / Bluetooth).   
- [x] 8x Résistance pour PushButton (10kΩ) SIL-9

- [x] 1x micro PushButton (Reset database) - En face arrière.  
- [] 1x Résistance 10k

- [x] 1x Switch Button (Local files/DLNA) - En face arrière.
- [] 1x Résistance 10k

- [x] 1x Power Button (incl. LED) - En face arrière. Bouton 16mm chrome, anneau LED bleue.
- [] 1x Résistance 120Ω (LED ring bleue, sous 5v — Vf=3.2v, 15mA)

### Composants


- [x] Amplificateur audio (mono)
   InnoMaker RPI HiFi AMP Hat TAS5713 Amplifier Audio Module 25W Class D Power.  
   Sound Card Extension Board for Raspberry Pi 5/4/3/B+/Pi/Zero.  
   Capacitor Nichicon. Connexion SPI. Sortie sur connecteur. Réglage du gain.  
   Power supply = 12/20v.  
   36€ Amazon.  
   
- [x] 2x 74HC595 Registres à décalage pour controle des LEDs. Format DIP-16.  
   Amazon 9€ (les 10)

- [x] PCF8574 (8pins) I2C Expander pour controle des Pushbutton. Format miniboard.  
   Amazon 7€ (les 2)

- [x] MCP3008 Convertisseur analogique-numerique Adafruit (ADC).  Format DIP-16.
   8 canaux, 10 bits (1024 valeurs) - Connexion SPI. Lib Python: spidev.   
   Amazon 22€ (les 2)
	
- [ ] Potentiomètre 10kΩ - linéaire A.  
   Trop difficile à trouver en 180° (*half-turn*) => on prend un *single-turn*.  
	
- [ ] Potentiomètre 10kΩ - linéaire A - Avec interrupteur.  
   WELTRON 002045038963 WCIP20CIPS-08-60F1-10K-20%-Lin Rotary Potentiometer with Switch Mono 0.4 W 10 kΩ 1 pc(s) 
   Amazon 5.50: 

- [ ] Ecran plexi


### Récapitulatif des résistances

  | Valeur     | Qté       | Usage                          | En stock | 
  | ---------- | --------- | ------------------------------ | -------- |
  | 120Ω       | 1         | P — LED bleue power ring       |          |
  | 150Ω       | 6         | On + L3 + L4 + M1–M4           |          |
  | 150Ω       | 1 SIL     | V1–V7  (7 pull-ups, 1 spare)   |          |
  | 380Ω       | 2         | L1 + L2 — backlight ePaper     | oui      |
  | 10kΩ SIL-9 | 1 boîtier | B1–B7 (7 pull-ups, 1 spare)    | oui      |
  | 10kΩ       | 2         | B8 Reset + SW9 Local/DLNA      |          |
