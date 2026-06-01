# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VintageRadio is a Python async application that turns a Raspberry Pi into a vintage-style radio, streaming MP3s from a Synology NAS (or any DLNA/UPnP MediaServer) via VLC. Development happens on Windows; deployment targets Raspberry Pi with a systemd service.

## Running the Application

```bash
# Install dependencies (Raspberry Pi)
sudo apt install python3-pip python3-vlc python3-mutagen
pip3 install -r requirements.txt

# Run directly
python3 VintageRadio.py

# Run as systemd service (production)
sudo systemctl start vintageradio
```

No build step — pure Python, run directly.

## Architecture

The application has three layers that communicate via async tasks and shared state:

**Entry point → Engine → Network/Playback**

1. **`VintageRadio.py`** — bootstraps the asyncio event loop, handles SIGINT, and schedules the three recurring async tasks:
   - `user_request` reread every 5 s (mode/genre/year changes)
   - BPM/rating metadata updates every 6 s
   - 1-second main loop for playback state

2. **`lib/vr_engine.py`** — top-level coordinator. On startup: discovers DLNA server (with `preferred_dlna.ini` fallback), scans all MP3s into SQLite, then enters the play loop. Drives the display and database queries.

3. **Network stack (two-layer design):**
   - `lib/dlna_network.py` — raw SSDP M-SEARCH, SOAP requests, DIDL-Lite XML parsing
   - `lib/dlna_network_wrapper.py` — high-level server selection and music container navigation

4. **Playback stack:**
   - `lib/dlna_music.py` — manages VLC instance, playlist loading, shuffle/sort, track sequencing, ReplayGain normalization

5. **User interface:**
   - `lib/user_keyboard.py` — keyboard listener thread (commands: NEXT, AGAIN, QUIT, RESET, DISCOVER)
   - `lib/user_request.py` — polls `user_request.json` every 5 s for mode/genre/year changes
   - `lib/user_display.py` — console output
   - `lib/user_preferences.py` — persists DLNA server selection to `preferred_dlna.ini`

6. **Data layer:**
   - `lib/vr_database.py` — SQLite schema and raw queries (genre, year, rating, BPM)
   - `lib/vr_database_wrapper.py` — abstraction: queries by genre/decade/rating/random

7. **Utilities:**
   - `lib/tag_collector.py` — fetches ID3 tags (BPM, Rating) directly from MP3 URLs via HTTP Range requests (no full download)
   - `lib/utilities.py` — `calculate_file_hash()`, hash 8 chars basé sur le nom de fichier
   - `lib/vr_logger.py` — logger centralisé (`get_logger`, `set_logging` avec niveaux -v / -vv)

## Database Path

The SQLite database is at `./data/music_metadata.db` (relative to the project root). The `lib/data/` folder is a test artifact and is not used at runtime.

## User Control via JSON

The file `user_request.json` (in repo root) is the runtime control interface — edit it while the app is running to change playback mode, genre filter, year filter, and BPM threshold. It is polled every 5 seconds.

## Key Dependencies

| Package | Purpose |
|---------|---------|
| `python-vlc` | Audio playback engine |
| `mutagen` | MP3 metadata read/write |
| `requests` | SOAP/HTTP requests to DLNA server |
| `sqlite3` | Built-in, no install needed |

## Hardware Context

The roadmap adds physical controls (GPIO): power button, volume knob, mode rotary, genre/year/rating rotary, and track navigation buttons. `lib/gpio_controller.py` is the placeholder for this. The hardware BOM and 3D models are in `hardware/`.

## No Tests, No CI

There is no test suite and no CI pipeline. This is a personal/hobby project.
