# Live for Speed InSim Protocol

This document provides a detailed overview of the InSim protocol used by Live for Speed.

## What is InSim?

InSim (Internet Simulator) is the communication protocol that allows external applications to interact with Live for Speed in real-time. It uses TCP or UDP sockets to send and receive data packets.

**Official reference**: https://en.lfsmanual.net/wiki/InSim.txt

## Basic Connection

### Enabling InSim in LFS

To enable InSim on the LFS server or client:

```
/insim 29999
```

Where `29999` is the port (can be any available port).

### Initialization

The InSim connection follows these steps:

1. **Establish TCP/UDP connection** to the specified host and port
2. **Send IS_ISI packet** to initialize the InSim session
3. **Receive IS_VER packet** as confirmation
4. **Start receiving packets** according to configured flags

### IS_ISI Packet (InSim Init)

The initialization packet has this structure:

```c
struct IS_ISI {
    byte Size;        // 44 (packet bytes / 4)
    byte Type;        // ISP_ISI (1)
    byte ReqI;        // Request ID (0 normally)
    byte Zero;        // 0
    word UDPPort;     // UDP Port (0 for TCP)
    word Flags;       // Configuration flags
    byte InSimVer;    // InSim version (9 currently)
    byte Prefix;      // Prefix for commands (e.g., '!')
    word Interval;    // MCI/NLP interval in hundredths of a second
    char Admin[16];   // Admin password (if needed)
    char IName[16];   // Application name
};
```

## Main Packet Types

### Server Information Packets

| Packet | Code | Description |
|--------|------|-------------|
| IS_VER | 2 | LFS and InSim version |
| IS_STA | 5 | Server state |
| IS_ISM | 10 | InSim Multi information |

### Connection and Player Packets

| Packet | Code | Description |
|--------|------|-------------|
| IS_NCN | 18 | New player connection |
| IS_CNL | 19 | Player disconnects |
| IS_CPR | 20 | Player name change |
| IS_NPL | 21 | New player on track |
| IS_PLP | 22 | Player leaves pits |
| IS_PLL | 23 | Player leaves track |

### Telemetry Packets

| Packet | Code | Description | Frequency |
|--------|------|-------------|-----------|
| IS_MCI | 38 | Multi Car Info - Vehicle position and state | Configurable (Interval) |
| IS_NLP | 37 | Node and Lap - Position at track nodes | Configurable (Interval) |

### Race Event Packets

| Packet | Code | Description |
|--------|------|-------------|
| IS_RST | 17 | Race start |
| IS_LAP | 24 | Completed lap time |
| IS_SPX | 25 | Sector time |
| IS_PIT | 26 | Pit entry |
| IS_PSF | 27 | Pit stop finished |
| IS_PEN | 30 | Penalty |
| IS_FIN | 34 | Race finish |
| IS_RES | 35 | Results |

### Control Packets

| Packet | Code | Description |
|--------|------|-------------|
| IS_TINY | 3 | Small control packets |
| IS_SMALL | 4 | Small data packets |
| IS_MSO | 11 | Server messages |
| IS_III | 12 | General information |

## Detailed Telemetry

### IS_MCI - Multi Car Info

The most important packet for real-time telemetry:

```c
struct IS_MCI {
    byte Size;      // 4 + NumC * 28
    byte Type;      // ISP_MCI (38)
    byte ReqI;      // 0
    byte NumC;      // Number of cars (max 8)
    CompCar Info[8]; // Information for each car
};

struct CompCar {
    word Node;          // Current node (0-65535)
    word Lap;           // Current lap
    byte PLID;          // Player ID
    byte Position;      // Race position
    byte Info;          // Additional information
    byte Sp3;           // Spare
    int X;              // X position * 65536
    int Y;              // Y position * 65536
    int Z;              // Z position * 65536
    word Speed;         // Speed * 32768 / m/s
    word Direction;     // Car direction
    word Heading;       // Car heading
    short AngVel;       // Angular velocity
};
```

**Important conversions:**
- Real position (meters): `X / 65536.0`
- Real speed (m/s): `Speed / 32768.0`
- Speed (km/h): `(Speed / 32768.0) * 3.6`

### IS_LAP - Lap Time

Completed lap information:

```c
struct IS_LAP {
    byte Size;      // 20
    byte Type;      // ISP_LAP (24)
    byte ReqI;      // 0
    byte PLID;      // Player ID
    unsigned LTime; // Lap time (ms)
    unsigned ETime; // Total time (ms)
    word LapsDone;  // Completed laps
    word Flags;     // Lap flags
    byte Sp0;
    byte Penalty;   // Penalty in seconds
    byte NumStops;  // Number of stops
    byte Sp3;
};
```

### IS_SPX - Split Time

Sector time:

```c
struct IS_SPX {
    byte Size;      // 16
    byte Type;      // ISP_SPX (25)
    byte ReqI;      // 0
    byte PLID;      // Player ID
    unsigned STime; // Sector time (ms)
    unsigned ETime; // Total time (ms)
    byte Split;     // Sector number (1, 2, 3)
    byte Penalty;   // Accumulated penalty
    byte NumStops;  // Pit stops
    byte Sp3;
};
```

## InSim Flags

The flags in the IS_ISI packet control what type of information is received:

```c
#define ISF_RES_0       1       // Reserved
#define ISF_RES_1       2       // Reserved
#define ISF_LOCAL       4       // Local connection
#define ISF_MSO_COLS    8       // Send colors in messages
#define ISF_NLP         16      // Send NLP packets
#define ISF_MCI         32      // Send MCI packets
#define ISF_CON         64      // Contact information
#define ISF_OBH         128     // Object collisions
#define ISF_HLV         256     // Hot lap validity
#define ISF_AXM_LOAD    512     // Autocross objects
#define ISF_AXM_EDIT    1024    // Object editing
```

**Example for telemetry:**
```python
flags = ISF_MCI | ISF_NLP  # Receive MCI and NLP packets
flags = 32 | 16  # Equivalent in decimal
```

## Telemetry Intervals

The `Interval` parameter in the IS_ISI packet controls the frequency of MCI/NLP packets:

- **Value in hundredths of a second** (1 = 10ms)
- **Recommended minimum**: 50 (500ms = 2Hz)
- **Typical for telemetry**: 100 (1 second = 1Hz)
- **High frequency**: 10 (100ms = 10Hz)

```python
interval = 100  # 1 second (1Hz)
interval = 50   # 500ms (2Hz)
interval = 10   # 100ms (10Hz)
```

## Complete Example

```python
import socket
import struct

# Connection
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', 29999))

# IS_ISI packet
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
    100,                   # Interval (1 second)
    b'',                   # Admin password
    b'MyApp'.ljust(16, b'\x00')  # App name
)

sock.sendall(packet)

# Receive packets
while True:
    data = sock.recv(1024)
    if data:
        process_packet(data)
```

## References

### Official Documentation
- **InSim.txt**: https://en.lfsmanual.net/wiki/InSim.txt
- **LFS Manual**: https://en.lfsmanual.net/wiki/Main_Page

### Related Protocols
- **OutGauge**: Vehicle dashboard data
- **OutSim**: Vehicle physics data

### Resources
- **LFS Forum**: https://www.lfs.net/forum
- **LFS World**: https://www.lfs.net/
