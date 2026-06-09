# VintageRadio Libraries

## What each file does

| Module | Main responsibilities |
|--------|-----------------------|
| VintageRadio.py | • Main entry point with async event loop<br/>• Coordinates setup, keyboard controller, and playback loop<br/>• Handles command-line arguments and logging initialization |
| vr_engine.py | • Orchestrates DLNA server connection and database operations<br/>• Manages track scanning and metadata retrieval<br/>• Displays clip information on screen |
| dlna_music.py | • Stores MP3 URL playlist<br/>• Shuffles and plays tracks asynchronously via VLC<br/>• Tracks playback state (playing/stopped/rewind) |
| user_request.py | • Monitors JSON config file for mode/genre changes<br/>• Detects file modifications and triggers playlist refresh<br/>• Supports repeating reread interval |
| user_keyboard.py | • Keyboard listener thread (Windows/Raspberry compatible)<br/>• Sends commands: QUIT, NEXT, AGAIN, DISCOVER<br/>• Callback mechanism to VintageRadio |
| dlna_network.py | • SSDP discovery of DLNA MediaServers<br/>• SOAP Browse requests and DIDL-Lite XML parsing<br/>• Recursive container browsing and MP3 extraction |
| dlna_network_wrapper.py | • High-level DLNA operations with logging<br/>• Server selection (saved or interactive)<br/>• Music container navigation and MP3 URL collection |
| vr_database.py | • SQLite storage for MP3 metadata<br/>• Track queries by genre, year, decade<br/>• Rating and BPM fields for future features |
| vr_database_wrapper.py | • Database abstraction layer<br/>• Genre/decade track retrieval<br/>• Track info and update operations |
| user_display.py | • Screen output management<br/>• Shows "NOW PLAYING" with title, artist, year, genre |
| vr_logger.py | • Centralized logging service<br/>• Configurable verbosity levels (-v, -vv) |
| user_preferences.py | • Saves/loads preferred DLNA server URL<br/>• Persists server selection across restarts |