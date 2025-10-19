# LFS-Ayats

Prototype telemetry radar for Live for Speed (LFS).  The project connects to
InSim for control commands, listens to OutSim telemetry, and renders a simple
ASCII radar that mirrors the original prototype behaviour.

## Requirements

* Python 3.10 or newer

No third-party dependencies are required; only the Python standard library is
used.

## Configuration

All runtime settings are stored in [`config.json`](config.json):

```json
{
  "insim": {
    "host": "127.0.0.1",
    "port": 29999,
    "admin_password": "",
    "interval_ms": 100
  },
  "outsim": {
    "port": 30000,
    "update_hz": 60
  },
  "sp_radar_enabled": true,
  "sp_beeps_enabled": true,
  "mp_radar_enabled": true,
  "mp_beeps_enabled": false,
  "beep_mode": "standard"
}
```

* **`insim.host` / `insim.port`** – address of the LFS InSim server.
* **`insim.admin_password`** – optional admin password if your server requires
  authentication.
* **`insim.interval_ms`** – desired update interval for InSim packets.
* **`outsim.port`** – UDP port the game broadcasts OutSim packets to (configure
  this in `cfg.txt` within LFS).
* **`outsim.update_hz`** – documentation value for your preferred update rate;
  currently informational only for the prototype.
* **`sp_radar_enabled` / `sp_beeps_enabled`** – toggle the radar renderer and
  beep subsystem while driving in single-player sessions.
* **`mp_radar_enabled` / `mp_beeps_enabled`** – equivalent toggles when InSim
  reports that you are connected to a multiplayer host.
* **`beep_mode`** – selects the strategy used by the beep subsystem (currently a
  placeholder string).

The app automatically swaps between the single-player (`sp_*`) and
multiplayer (`mp_*`) settings whenever InSim updates its state. When the
`ISS_MULTI` flag is set, the multiplayer configuration is applied; otherwise the
single-player options remain in effect. Configuration edits are watched on disk
and hot-reloaded at runtime, so you can tweak these values without restarting
the program.

Adjust the values to match your LFS setup before running the program.

## Running the radar

1. Ensure LFS is configured to send OutSim packets to the machine running this
   script and that InSim is enabled.
2. Start the prototype:

   ```bash
   python main.py
   ```

   The script connects to InSim, waits for OutSim telemetry, and continuously
   prints the ASCII radar to the terminal. Press `Ctrl+C` to exit.

## Development notes

The telemetry helpers live in the `src/` package:

* [`src/insim_client.py`](src/insim_client.py) – minimal TCP wrapper for InSim.
* [`src/outsim_client.py`](src/outsim_client.py) – UDP listener parsing OutSim
  frames.
* [`src/radar.py`](src/radar.py) – ASCII renderer for OutSim positions.

These modules are intentionally small and can be extended with additional
functionality from the InSim/OutSim specifications as needed.

## Additional documentation

| Resource | Description |
| --- | --- |
| [Interactive documentation site](docs/site/index.html) | Browser-based overview of the prototype with interactive summaries and deep links to common workflows. |
| [LFS manual extracts](docs/) | Official PDF guides (commands, controls, scripting, and more) that complement the interactive notes with the full simulator manuals. |
