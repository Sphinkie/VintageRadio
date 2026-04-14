# Vintage Radio

## Bill of Material

-   Convertisseur analogique-numerique (ADC)
	MCP3008 (SPI) : 8 canaux, 10 bits (1024 valeurs). Très simple à câbler, bibliothèque Python (spidev) très 
	Adafruit 5€ Product ID: 856 
	
-   Potentiomètre 10kΩ - linéaire.
	Trop difficile à trouver en 180° (half-turn) => on pren un single-turn.
	A vérifier dans le stock.
	
-	Ampli

- ePaper 2.13" 5x2.5xm SPI

- ePaper 2.9"	3x6.8 cm SPI


	
###  MCP3008 - 8-Channel 10-Bit ADC With SPI Interface 

```  
  Potentiomètre 10kΩ          MCP3008              Raspberry Pi
┌─────────────┐           ┌──────────┐          ┌──────────────┐
│  Broche 1 ──┴── GND     │ VSS (1)  │──────────┴── GND        │
│  Broche 2 ──┬── CH0 (1) │ VREF (2) │──────────┴── 3.3V       │
│  Broche 3 ──┴── 3.3V    │ AGND (3) │──────────┴── GND        │
└─────────────┘           │ DGND (4) │──────────┴── GND        │
                          │ VDD (5)  │──────────┴── 3.3V       │
                          │ DVDD (6) │──────────┴── 3.3V       │
                          │ CLK (7)  │──────────┴── GPIO 23 (SCLK)
                          │ DOUT (8) │──────────┴── GPIO 24 (MISO)
                          │ DIN (9)  │──────────┴── GPIO 25 (MOSI)
                          │ CS (10)  │──────────┴── GPIO 8 (CE0)
                          └──────────┘          └──────────────┘
```

#### Activation du SPI:

```shell
sudo raspi-config
# Aller dans : Interface Options -> SPI -> Yes
sudo apt-get install python3-spidev						  
```

####  Cablage

Alimentation (Power) :

    - 3.3V : Relié aux broches VDD, DVDD, VREF du MCP3008 et à la broche 3 du potentiomètre.
    - GND : Relié aux broches VSS, AGND, DGND du MCP3008 et à la broche 1 du potentiomètre.

Signal Analogique :

    - La broche centrale du potentiomètre (Broche 2) va sur CH0 (Canal 0) du MCP3008.

Interface SPI (Communication) :

    - CLK (Horloge) ↔ GPIO 23 (SCLK)
    - DOUT (Données du MCP vers le Pi) ↔ GPIO 24 (MISO)
    - DIN (Données du Pi vers le MCP) ↔ GPIO 25 (MOSI)
    - CS (Chip Select) ↔ GPIO 8 (CE0)


```mermaid
graph LR
    subgraph Potentiometre_10k [Potentiomètre 10kOhms Linéaire]
        P1[Broche 1<br/>GND]
        P2[Broche 2<br/>Signal]
        P3[Broche 3<br/>3.3V]
    end

    subgraph MCP3008 [Convertisseur ADC MCP3008]
        direction TB
        VSS[VSS<br/>GND]
        VREF[VREF<br/>3.3V]
        AGND[AGND<br/>GND]
        DGND[DGND<br/>GND]
        VDD[VDD<br/>3.3V]
        DVDD[DVDD<br/>3.3V]
        CLK[CLK<br/>Horloge]
        DOUT[DOUT<br/>Données Sortie]
        DIN[DIN<br/>Données Entrée]
        CS[CS<br/>Sélection]
        CH0[CH0<br/>Canal 0]
    end

    subgraph Raspberry_Pi [Raspberry Pi GPIO]
        GND_PI[GND<br/>Pin 6/9/14...]
        V33[3.3V<br/>Pin 1/17]
        SCLK[SCLK<br/>GPIO 23<br/>Pin 16]
        MISO[MISO<br/>GPIO 24<br/>Pin 18]
        MOSI[MOSI<br/>GPIO 25<br/>Pin 22]
        CE0[CE0<br/>GPIO 8<br/>Pin 24]
    end

    %% Connexions Alimentation & Masse
    P1 --- GND_PI
    P3 --- V33
    
    VSS --- GND_PI
    AGND --- GND_PI
    DGND --- GND_PI
    
    VREF --- V33
    VDD --- V33
    DVDD --- V33

    %% Connexions Signal
    P2 --- CH0

    %% Connexions SPI
    CLK --- SCLK
    DOUT --- MISO
    DIN --- MOSI
    CS --- CE0

    %% Styles
    style Potentiometre_10k fill:#f9f,stroke:#333,stroke-width:2px
    style MCP3008 fill:#bbf,stroke:#333,stroke-width:2px
    style Raspberry_Pi fill:#bfb,stroke:#333,stroke-width:2px
	
```


