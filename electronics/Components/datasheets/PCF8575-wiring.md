# PCF8575 — Câblage I2C et boutons

## Principe

Un module PCF8575 sur le bus I2C.  
Chaque module a une adresse distincte configurée par ses broches A0/A1/A2.

| Module | A0  | A1  | A2  | Adresse I2C |
| ------ | --- | --- | --- | ----------- |
| #1     | GND | GND | GND | 0x20        |

Le PCF8575 dispose de 16 I/O (P00–P07 + P10–P17). 

## Exeple de schéma

```mermaid
graph TD

    RPI["🖥 Raspberry Pi\nGPIO SDA / SCL\n(I2C bus)"]

    subgraph PCF1["PCF8575 #1 — 0x20\n(A0=A1=A2=GND)"]
        direction LR
        SDA1["SDA"] & SCL1["SCL"]
        P00["P00"] --- B1["B1 — Year"]
        P01["P01"] --- B2["B2 — Genre"]
        P02["P02"] --- B3["B3 — Beat"]
        P03["P03"] --- SW4["SW4 — Bluetooth"]
        P04["P04"] --- B5["B5 — Again"]
        P05["P05"] --- B6["B6 — Star me"]
        P06["P06"] --- B7["B7 — Next"]
        P07["P07"] --- B8["B8 — Reset DB"]
        P10["P10"] --- SW9["SW9 — Local/DLNA"]
        P11["P11–P17 (libres)"]
    end

    subgraph PCF2["PCF8575 #2 — 0x21\n(A0=VCC, A1=A2=GND)"]
        direction LR
        SDA2["SDA"] & SCL2["SCL"]
        P20["P00–P17 (libres — extension)"]
    end

    RPI -- "SDA" --> SDA1 & SDA2
    RPI -- "SCL" --> SCL1 & SCL2
```

## Câblage des boutons

Chaque bouton est câblé entre la broche I/O du PCF8575 et **GND**.  
La résistance pull-up (RS1 = SIL-9 10kΩ, ou R31/R32 = 20kΩ) tire la broche
vers **3.3V** au repos. L'appui tire vers GND → lecture LOW = appuyé.

```
3.3V ──┬── [10kΩ] ──┬── PCF8575 Pxx
       │            │
       │         [Bouton]
       │            │
      GND          GND
```

## Code Python (lecture)

```python
import smbus2

bus = smbus2.SMBus(1)

# Lire les 16 pins du chip #1 (2 octets : port0, port1)
data = bus.read_i2c_block_data(0x20, 0, 2)
port0, port1 = data[0], data[1]

# Exemple : tester B1 (P00, bit0 de port0)
if not (port0 & 0x01):   # LOW = bouton appuyé
    print("B1 Year appuyé")
```
