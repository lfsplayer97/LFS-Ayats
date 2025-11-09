# Packet Reference

Quick reference guide for InSim packets in LFS.

**Full specification**: https://en.lfsmanual.net/wiki/InSim.txt

## Packet Structure

All InSim packets follow this basic structure:

```c
struct PacketHeader {
    byte Size;      // Packet size in multiples of 4
    byte Type;      // Packet type (ISP_*)
    byte ReqI;      // Request ID (usually 0)
    byte SubT;      // Sub-type (depends on packet)
};
```

## Quick Reference Table

| Code | Name | Description | Direction | Priority |
|------|------|-------------|-----------|----------|
| 1 | IS_ISI | InSim Init | → LFS | Critical |
| 2 | IS_VER | Version | ← LFS | High |
| 3 | IS_TINY | Tiny packet | ↔ Both | Medium |
| 5 | IS_STA | State | ← LFS | High |
| 11 | IS_MSO | Message Out | ← LFS | Low |
| 17 | IS_RST | Race Start | ← LFS | High |
| 18 | IS_NCN | New Connection | ← LFS | Medium |
| 19 | IS_CNL | Connection Leave | ← LFS | Medium |
| 21 | IS_NPL | New Player | ← LFS | High |
| 22 | IS_PLP | Player Leave Pits | ← LFS | Medium |
| 24 | IS_LAP | Lap Time | ← LFS | High |
| 25 | IS_SPX | Split Time | ← LFS | High |
| 26 | IS_PIT | Pit Stop | ← LFS | Medium |
| 27 | IS_PSF | Pit Stop Finish | ← LFS | Medium |
| 30 | IS_PEN | Penalty | ← LFS | Medium |
| 34 | IS_FIN | Finished Race | ← LFS | High |
| 35 | IS_RES | Result | ← LFS | High |
| 37 | IS_NLP | Node and Lap | ← LFS | High |
| 38 | IS_MCI | Multi Car Info | ← LFS | Critical |

## Telemetry Packets

### IS_MCI (Multi Car Info)

Most important for real-time telemetry.

**Frequency**: Configurable via `Interval` parameter (centèssimes de segon)

**Contains**:
- Position (X, Y, Z)
- Speed
- Direction
- Heading
- Angular velocity
- Node
- Lap

**Data conversions**:
```python
# Position in meters
x_meters = x / 65536.0
y_meters = y / 65536.0
z_meters = z / 65536.0

# Speed in m/s
speed_ms = speed / 32768.0

# Speed in km/h
speed_kmh = (speed / 32768.0) * 3.6
```

### IS_NLP (Node and Lap)

Alternative to IS_MCI with node-based positioning.

**Frequency**: Configurable via `Interval` parameter

**Contains**:
- Node position
- Lap number
- Player ID
- Position in race

## Lap Information Packets

### IS_LAP (Lap Time)

Complete lap information.

**Contains**:
- Lap time (ms)
- Total elapsed time (ms)
- Laps done
- Penalty time
- Number of pit stops

### IS_SPX (Split Time)

Sector timing information.

**Contains**:
- Split time (ms)
- Total elapsed time (ms)
- Split number (1, 2, 3)
- Penalty accumulation
- Number of pit stops

## Race Control Packets

### IS_RST (Race Start)

Race configuration and start.

**Contains**:
- Race laps / qualifying minutes
- Track name
- Weather
- Wind
- Flags
- Number of players

### IS_FIN (Finished)

Player finished race.

**Contains**:
- Player ID
- Total time
- Number of stops
- Confirmation flags

### IS_RES (Result)

Race result for a player.

**Contains**:
- Player name
- Username
- Final position
- Result time
- Laps completed

## Player Management Packets

### IS_NCN (New Connection)

New player connection.

**Contains**:
- Username
- Player name
- Admin status
- Total connections

### IS_NPL (New Player)

Player joins track.

**Contains**:
- Player name
- Plate
- Car name
- Skin name
- Tyres
- Handicaps

## Control Packets

### IS_TINY (Tiny)

Small control packets.

**Sub-types**:
- TINY_VER (1): Request version
- TINY_CLOSE (2): Close InSim
- TINY_PING (3): Ping
- TINY_REPLY (4): Ping reply
- TINY_SST (7): Request state
- TINY_GTH (8): Get time

### IS_SMALL (Small)

Small data packets.

**Usage**: Various small data requests/responses

## Implementation Examples

### Requesting Server State

```python
# Send TINY_SST to request IS_STA
tiny_packet = struct.pack("=4B", 1, 3, 0, 7)  # TINY_SST
client.send_packet(tiny_packet)
```

### Enabling Telemetry

```python
# Initialize with MCI and NLP packets
flags = 0x30  # ISF_MCI | ISF_NLP
interval = 100  # 1 second (100 centiseconds)

isi_packet = struct.pack(
    "=4BH2BH16s16s",
    44, 1, 0, 0,
    0, flags, 9, ord('!'), interval,
    b'', b'MyApp'.ljust(16, b'\x00')
)
client.send_packet(isi_packet)
```

## Packet Priorities

### Critical (Must Handle)
- IS_ISI: Connection initialization
- IS_MCI: Telemetry data
- IS_VER: Version confirmation

### High (Should Handle)
- IS_STA: Server state
- IS_LAP: Lap times
- IS_SPX: Split times
- IS_NPL: Player tracking
- IS_RST: Race start
- IS_FIN: Race finish
- IS_RES: Results

### Medium (Nice to Have)
- IS_NCN: Connection tracking
- IS_PLP: Pit tracking
- IS_PIT: Pit stops
- IS_PEN: Penalties

### Low (Optional)
- IS_MSO: Chat messages
- Other informational packets

## Error Handling

Always handle these scenarios:

1. **Packet size mismatch**: Validate size field
2. **Unknown packet types**: Log and skip
3. **Incomplete packets**: Buffer and wait
4. **Connection loss**: Reconnect logic
5. **Invalid data**: Validate ranges

## Performance Considerations

### High Frequency (10+ Hz)
- IS_MCI: Can generate lots of data
- Buffer appropriately
- Consider async processing

### Medium Frequency (1-5 Hz)
- IS_NLP: Regular updates
- Batch processing possible

### Low Frequency (Event-based)
- IS_LAP, IS_SPX: Per lap/split
- Process immediately

## References

- **InSim.txt**: https://en.lfsmanual.net/wiki/InSim.txt
- **LFS Forum**: https://www.lfs.net/forum
- **Code examples**: See `examples/` directory
