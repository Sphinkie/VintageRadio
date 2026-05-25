# Vintage Radio

## Liste des résistances nécessaires

### Leds

| Ref  | Role            | Tension | Piloté par | Ref   | Résistance | Vf   | mA     | Commentaire      |
| ---- | --------------- | ------- | ---------- | ---- | ---------- | ---- | ------ | ---------------- |
|✓ L0  | Témoin logiciel | 3.3v    | Rpi GPIO   |✓ R0  | 120Ω       | 2.1v | 10 mA  | jaune (plus vive)|
|✓ POW | Power ring      | 5v      | Alim board |✓ RP  | 120Ω       | 3.2v | 15 mA  | bleue 16mm chrome|
|✓ L1  | backlight       | 5v      | Alim board |✓ R1  | 380Ω       | 3.2v | 4.7 mA | white            |
|✓ L2  | backlight       | 5v      | Alim board |✓ R2  | 380Ω       | 3.2v | 4.7 mA | white            |
|✓ L3  | backlight       | 5v      | Alim board |✓ R3  | 150Ω       | 2.0v | 20 mA  | amber E10        |
|✓ L4  | backlight       | 5v      | Alim board |✓ R4  | 150Ω       | 2.0v | 20 mA  | amber E10        |
|✓ V1  | value_1         | 3.3v    | 74HC595    |✓ R11 | 200Ω       | 2.2v | 5.5 mA | verte (moins vive)          |
|✓ V2  | value_2         | 3.3v    | 74HC595    |✓ R12 | 200Ω       | 2.2v | 5.5 mA | verte            |
|✓ V3  | value_3         | 3.3v    | 74HC595    |✓ R13 | 200Ω       | 2.2v | 5.5 mA | verte            |
|✓ V4  | value_4         | 3.3v    | 74HC595    |✓ R14 | 200Ω       | 2.2v | 5.5 mA | verte            |
|✓ V5  | value_5         | 3.3v    | 74HC595    |✓ R15 | 200Ω       | 2.2v | 5.5 mA | verte            |
|✓ V6  | value_6         | 3.3v    | 74HC595    |✓ R16 | 200Ω       | 2.2v | 5.5 mA | verte            |
|✓ V7  | value_7         | 3.3v    | 74HC595    |✓ R17 | 200Ω       | 2.2v | 5.5 mA | verte            |
| M1   | Year            | 3.3v    | Rpi GPIO   | R21 | 150Ω       | 2.1v | 8 mA   | superamber       |
| M2   | Beat            | 3.3v    | Rpi GPIO   | R22 | 150Ω       | 2.1v | 8 mA   | superamber       |
| M3   | Genre           | 3.3v    | Rpi GPIO   | R23 | 150Ω       | 2.1v | 8 mA   | superamber       |
| M4   | BT              | 3.3v    | Rpi GPIO   | R24 | 150Ω       | 2.1v | 8 mA   | superamber       |

### Boutons poussoirs (Pull-up)

Résistances de tirage vers 3.3v sur les entrées des PCF8574 (les PCF8574 ont des pull-up internes ~100kΩ trop faibles — les 10kΩ externes assurent la robustesse).

B = Bouton poussoir.
SW = Interrupteurs à 2 positions.

| Ref   | Role       | Tension | Lu par  | Ref   |Résistance | Commentaire     |
| ----- | ---------- | ------- | ------- | ----- |---------- | --------------- |
|✓ B1   | Year       | 3.3 v   | PCF8574 |✓ RS1  |10kΩ | pull-up — SIL-9 |
|✓ B2   | Genre      | 3.3 v   | PCF8574 |✓ RS1  |10kΩ | pull-up — SIL-9 |
|✓ B3   | Beat       | 3.3 v   | PCF8574 |✓ RS1  |10kΩ | pull-up — SIL-9 |
|✓ SW4  | Bluetooth  | 3.3 v   | PCF8574 |✓ RS1  |10kΩ | pull-up — SIL-9 |
|✓ B5   | Again      | 3.3 v   | PCF8574 |✓ RS1  |10kΩ | pull-up — SIL-9 |
|✓ B6   | Star me    | 3.3 v   | PCF8574 |✓ RS1  |10kΩ | pull-up — SIL-9 |
|✓ B7   | Next       | 3.3 v   | PCF8574 |✓ RS1  |10kΩ | pull-up — SIL-9 |
|✓ B8   | Reset DB   | 3.3 v   | PCF8574 |✓ R31  |20kΩ | pull-up — résistance séparée |
|✓ SW9  | Local/DLNA | 3.3 v   | PCF8574 |✓ R32  |20kΩ | pull-up — résistance séparée |
|✓ SW10 | Power      | 12 v    | --      | --  |-- | Alimente le système (avec LED séparée) |
