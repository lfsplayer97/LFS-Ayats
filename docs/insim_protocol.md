# Protocol InSim de Live for Speed

Aquest document proporciona una visió detallada del protocol InSim utilitzat per Live for Speed.

## Què és InSim?

InSim (Internet Simulator) és el protocol de comunicació que permet a aplicacions externes interactuar amb Live for Speed en temps real. Utilitza sockets TCP o UDP per enviar i rebre paquets de dades.

**Referència oficial**: https://en.lfsmanual.net/wiki/InSim.txt

## Connexió Bàsica

### Habilitar InSim a LFS

Per habilitar InSim al servidor o client de LFS:

```
/insim 29999
```

On `29999` és el port (pot ser qualsevol port disponible).

### Inicialització

La connexió InSim segueix aquests passos:

1. **Establir connexió TCP/UDP** al host i port especificats
2. **Enviar paquet IS_ISI** per inicialitzar la sessió InSim
3. **Rebre paquet IS_VER** com a confirmació
4. **Començar a rebre paquets** segons els flags configurats

### Paquet IS_ISI (InSim Init)

El paquet d'inicialització té aquesta estructura:

```c
struct IS_ISI {
    byte Size;        // 44 (bytes del paquet / 4)
    byte Type;        // ISP_ISI (1)
    byte ReqI;        // Request ID (0 normalment)
    byte Zero;        // 0
    word UDPPort;     // Port UDP (0 per TCP)
    word Flags;       // Flags de configuració
    byte InSimVer;    // Versió InSim (9 actualment)
    byte Prefix;      // Prefix per comandaments (ex: '!')
    word Interval;    // Interval MCI/NLP en centèssimes de segon
    char Admin[16];   // Contrasenya admin (si cal)
    char IName[16];   // Nom de l'aplicació
};
```

## Tipus de Paquets Principals

### Paquets d'Informació del Servidor

| Paquet | Codi | Descripció |
|--------|------|------------|
| IS_VER | 2 | Versió de LFS i InSim |
| IS_STA | 5 | Estat del servidor |
| IS_ISM | 10 | Informació InSim Multi |

### Paquets de Connexions i Jugadors

| Paquet | Codi | Descripció |
|--------|------|------------|
| IS_NCN | 18 | Nova connexió de jugador |
| IS_CNL | 19 | Jugador desconnecta |
| IS_CPR | 20 | Canvi de nom de jugador |
| IS_NPL | 21 | Nou jugador a la pista |
| IS_PLP | 22 | Jugador surt dels pits |
| IS_PLL | 23 | Jugador deixa la pista |

### Paquets de Telemetria

| Paquet | Codi | Descripció | Freqüència |
|--------|------|------------|------------|
| IS_MCI | 38 | Multi Car Info - Posició i estat de vehicles | Configurable (Interval) |
| IS_NLP | 37 | Node and Lap - Posició en nodes de pista | Configurable (Interval) |

### Paquets d'Esdeveniments de Cursa

| Paquet | Codi | Descripció |
|--------|------|------------|
| IS_RST | 17 | Inici de cursa |
| IS_LAP | 24 | Temps de volta completada |
| IS_SPX | 25 | Temps de sector |
| IS_PIT | 26 | Entrada als pits |
| IS_PSF | 27 | Fi de parada als pits |
| IS_PEN | 30 | Penalització |
| IS_FIN | 34 | Final de cursa |
| IS_RES | 35 | Resultats |

### Paquets de Control

| Paquet | Codi | Descripció |
|--------|------|------------|
| IS_TINY | 3 | Paquets de control petit |
| IS_SMALL | 4 | Paquets de dades petit |
| IS_MSO | 11 | Missatges del servidor |
| IS_III | 12 | Informació general |

## Telemetria Detallada

### IS_MCI - Multi Car Info

El paquet més important per telemetria en temps real:

```c
struct IS_MCI {
    byte Size;      // 4 + NumC * 28
    byte Type;      // ISP_MCI (38)
    byte ReqI;      // 0
    byte NumC;      // Nombre de cotxes (màx 8)
    CompCar Info[8]; // Informació de cada cotxe
};

struct CompCar {
    word Node;          // Node actual (0-65535)
    word Lap;           // Volta actual
    byte PLID;          // Player ID
    byte Position;      // Posició a la cursa
    byte Info;          // Informació adicional
    byte Sp3;           // Spare
    int X;              // Posició X * 65536
    int Y;              // Posició Y * 65536
    int Z;              // Posició Z * 65536
    word Speed;         // Velocitat * 32768 / m/s
    word Direction;     // Direcció del cotxe
    word Heading;       // Orientació del cotxe
    short AngVel;       // Velocitat angular
};
```

**Conversions importants:**
- Posició real (metres): `X / 65536.0`
- Velocitat real (m/s): `Speed / 32768.0`
- Velocitat (km/h): `(Speed / 32768.0) * 3.6`

### IS_LAP - Lap Time

Informació de volta completada:

```c
struct IS_LAP {
    byte Size;      // 20
    byte Type;      // ISP_LAP (24)
    byte ReqI;      // 0
    byte PLID;      // Player ID
    unsigned LTime; // Temps de volta (ms)
    unsigned ETime; // Temps total (ms)
    word LapsDone;  // Voltes completades
    word Flags;     // Flags de la volta
    byte Sp0;
    byte Penalty;   // Penalització en segons
    byte NumStops;  // Número de parades
    byte Sp3;
};
```

### IS_SPX - Split Time

Temps de sector:

```c
struct IS_SPX {
    byte Size;      // 16
    byte Type;      // ISP_SPX (25)
    byte ReqI;      // 0
    byte PLID;      // Player ID
    unsigned STime; // Temps del sector (ms)
    unsigned ETime; // Temps total (ms)
    byte Split;     // Número de sector (1, 2, 3)
    byte Penalty;   // Penalització acumulada
    byte NumStops;  // Parades als pits
    byte Sp3;
};
```

## Flags d'InSim

Els flags al paquet IS_ISI controlen quin tipus d'informació es rep:

```c
#define ISF_RES_0       1       // Reserved
#define ISF_RES_1       2       // Reserved
#define ISF_LOCAL       4       // Connexió local
#define ISF_MSO_COLS    8       // Enviar colors als missatges
#define ISF_NLP         16      // Enviar paquets NLP
#define ISF_MCI         32      // Enviar paquets MCI
#define ISF_CON         64      // Informació de contactes
#define ISF_OBH         128     // Colisions amb objectes
#define ISF_HLV         256     // Hot lap validity
#define ISF_AXM_LOAD    512     // Objectes d'autocross
#define ISF_AXM_EDIT    1024    // Edició d'objectes
```

**Exemple per telemetria:**
```python
flags = ISF_MCI | ISF_NLP  # Rebre paquets MCI i NLP
flags = 32 | 16  # Equivalent en decimal
```

## Intervals de Telemetria

El paràmetre `Interval` al paquet IS_ISI controla la freqüència dels paquets MCI/NLP:

- **Valor en centèssimes de segon** (1 = 10ms)
- **Mínim recomanat**: 50 (500ms = 2Hz)
- **Típic per telemetria**: 100 (1 segon = 1Hz)
- **Alta freqüència**: 10 (100ms = 10Hz)

```python
interval = 100  # 1 segon (1Hz)
interval = 50   # 500ms (2Hz)
interval = 10   # 100ms (10Hz)
```

## Exemple Complet

```python
import socket
import struct

# Connexió
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', 29999))

# Paquet IS_ISI
packet = struct.pack(
    "=4BH2BH16s16s",
    44,                    # Size
    1,                     # Type (ISP_ISI)
    0,                     # ReqI
    0,                     # Zero
    0,                     # UDPPort
    48,                    # Flags (ISF_MCI | ISF_NLP)
    9,                     # InSimVer
    ord('!'),              # Prefix
    100,                   # Interval (1 segon)
    b'',                   # Admin password
    b'MyApp'.ljust(16, b'\x00')  # App name
)

sock.sendall(packet)

# Rebre paquets
while True:
    data = sock.recv(1024)
    if data:
        process_packet(data)
```

## Referències

### Documentació Oficial
- **InSim.txt**: https://en.lfsmanual.net/wiki/InSim.txt
- **LFS Manual**: https://en.lfsmanual.net/wiki/Main_Page

### Protocols Relacionats
- **OutGauge**: Dades del dashboard del vehicle
- **OutSim**: Dades de física del vehicle

### Recursos
- **LFS Forum**: https://www.lfs.net/forum
- **LFS World**: https://www.lfs.net/
