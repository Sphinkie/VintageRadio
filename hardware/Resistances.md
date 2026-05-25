# Vintage Radio

## Liste des résistances nécessaires

### Leds

| Name | Role            | Tension | Piloté par | Name | Résistance | Vf   | mA   | Commentaire      |
| ---- | --------------- | ------- | ---------- | ---- | ---------- | ---- | ---- | ---------------- |
| On   | Témoin logiciel | 3.3v    | Rpi GPIO   |  | 150Ω       | 2.1v | 8    | jaune            |
| POW  | Power ring      | 5v      | Alim board |  | 120Ω       | 3.2v | 15   | bleue 16mm chrome|
| L1   | backlight       | 5v      | Alim board |  | 380Ω       | 3.2v | 4.7  | white            |
| L2   | backlight       | 5v      | Alim board |  | 380Ω       | 3.2v | 4.7  | white            |
| L3   | backlight       | 5v      | Alim board |  | 150Ω       | 2.0v | 20   | amber E10        |
| L4   | backlight       | 5v      | Alim board |  | 150Ω       | 2.0v | 20   | amber E10        |
| V1   | value_1         | 3.3v    | 74HC595    |  | 150Ω       | 2.2v | 7.3  | verte            |
| V2   | value_2         | 3.3v    | 74HC595    |  | 150Ω       | 2.2v | 7.3  | verte            |
| V3   | value_3         | 3.3v    | 74HC595    |  | 150Ω       | 2.2v | 7.3  | verte            |
| V4   | value_4         | 3.3v    | 74HC595    |  | 150Ω       | 2.2v | 7.3  | verte            |
| V5   | value_5         | 3.3v    | 74HC595    |  | 150Ω       | 2.2v | 7.3  | verte            |
| V6   | value_6         | 3.3v    | 74HC595    |  | 150Ω       | 2.2v | 7.3  | verte            |
| V7   | value_7         | 3.3v    | 74HC595    |  | 150Ω       | 2.2v | 7.3  | verte            |
| M1   | Year            | 3.3v    | Rpi GPIO   |  | 150Ω       | 2.1v | 8    | superamber       |
| M2   | Beat            | 3.3v    | Rpi GPIO   |  | 150Ω       | 2.1v | 8    | superamber       |
| M3   | Genre           | 3.3v    | Rpi GPIO   |  | 150Ω       | 2.1v | 8    | superamber       |
| M4   | BT              | 3.3v    | Rpi GPIO   |  | 150Ω       | 2.1v | 8    | superamber       |

### Boutons poussoirs (Pull-up)

Résistances de tirage vers 3.3v sur les entrées des PCF8574 (les PCF8574 ont des pull-up internes ~100kΩ trop faibles — les 10kΩ externes assurent la robustesse).

B = Bouton poussoir.
SW = Interrupteurs à 2 positions.

| Name | Role       | Tension | Lu par  | Résistance | Commentaire     |
| ---- | ---------- | ------- | ------- | ---------- | --------------- |
| B1   | Year       | 3.3v    | PCF8574 | 10kΩ       | pull-up — SIL-9 |
| B2   | Beat       | 3.3v    | PCF8574 | 10kΩ       | pull-up — SIL-9 |
| B3   | Genre      | 3.3v    | PCF8574 | 10kΩ | pull-up — SIL-9 |
| SW4  | Bluetooth  | 3.3v    | PCF8574 | 10kΩ | pull-up — SIL-9 |
| B5   | Again      | 3.3v    | PCF8574 | 10kΩ | pull-up — SIL-9 |
| B6   | Star me    | 3.3v    | PCF8574 | 10kΩ | pull-up — SIL-9 |
| B7   | Next       | 3.3v    | PCF8574 | 10kΩ | pull-up — SIL-9 |
| B8   | Reset DB   | 3.3v    | PCF8574 | 10kΩ | pull-up — résistance séparée |
| SW9  | Local/DLNA | 3.3v    | PCF8574 | 10kΩ | pull-up — résistance séparée |
| SW10 | Power      | 12v     | --      | -- | Alimente le système (avec LED séparée) |
