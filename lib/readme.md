# What each file currently does

| Module	               | Main responsibilities                                                                                                                                                                                                                                                                                                 |
|--------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------| 
| dlna_preferences.py	   | • Contains the latest DLNA server used, which is supposed to be the preferred server.                                                                                                                                                                                                                                 |
| dlna_user_request.py	   | • Monitor a json file that contains the genre of music that the user wants to ear. This file can change at any moment.                                                                                                                                                                                                |
| dlna_network_wrapper.py  | • Allows the main program to have macro functions to interract with the DLNA server.                                                                                                                                                                                                                                  |
| dlna_network.py	       | • Handles SSDP discovery of DLNA MediaServers.  <br>• Retrieves the device description XML and extracts the ContentDirectory control URL. <br>• Sends SOAP Browse requests and parses the resulting DIDL‑Lite XML. <br>• Provides a helper (extract_mp3_items) that returns a flat list of MP3 URLs from a container. | 
| dlna_music.py            | • Stores the list of MP3 URLs. <br>• Can shuffle the playlist and play a mp3 clip.                                                                                                                                                                                                                                    | 
| dlna_logger.py           | Offre un service de logs, commun à tous les modules.                                                      | 
| keyboard_control.py      | Un listener de clavier (compatible Windows et Raspberry) pour envoyer quelques commandes à l'application. | 



# Problematiques

## pynput requires a graphical display (X server) to capture keyboard input

- On peut remplacer pyinput par termios and tty. OK en mode console, mais ne fonctionne plus sous Windows.
- Il faut implémenter du cross-platform.
   - option 1 : conditionnal imports (Uses only built-in Python modules)
   - option 2 : librairie cross-platfom `readchar`
   Lumo recommande l'option 1 dans notre cas.


## PyCharm ne redirige pas les touches vers l'app

Aller dans le menu `Run -> Edit Configuration -> Modify options` et cocher **Emulate terminal in output console**.


## Raspberry: pas d'echo sur le terminal SSH

Tapez ceci pour rétablir le mode normal sur le terminal bloqué:

```
stty sane
```
##  Schema mermaid

```mermaid
classDiagram
    %% Main Entry Point
    class VintageRadio {
        +main()
        +setup()
        +loop()
        +on_key_press()
        +show_clip_info()
    }

    %% Core Components
    class DLNAWrapper {
        +set_server()
        +scan_all_mp3_to_db()
        +get_urls_by_date_range()
        +get_clip_info()
        +get_track_details()
        +discover_servers()
        +find_music_container()
        +db
        +net
    }

    class DLNAMusic {
        +discover_tracks()
        +shuffle_playlist()
        +play_random_async()
        +start_track()
        +is_stopped()
        +stop()
        +get_playing_id()
        +rewind()
        +_instance
        +renderer
    }

    class UserRequest {
        +load_user_request()
        +has_changed()
        +get()
        +ack_has_changed()
        +repeating_reread()
    }

    class KeyboardController {
        +start()
        +stop()
        +callback
        +quit_event
    }

    class Display {
        +show()
        +add_line()
        +warning()
        +flush()
        +input()
    }

    %% Network Layer
    class DLNANetwork {
        +discover_servers()
        +browse()
        +browse_all_mp3()
        +extract_all_mp3_from_didl()
        +get_content_directory_control_url()
        +_extract_text()
    }

    %% Database Layer
    class DLNADatabase {
        +store_tracks()
        +get_tracks_by_date_range()
        +count()
        +get_track_info()
        +update_track()
        +calculate_file_hash()
        +conn
    }

    class DLNADbWrapper {
        +store_tracks()
        +get_tracks_for_decade()
        +get_track_info()
        +update_track_rating()
        +update_track_bpm()
        +db
    }

    %% External/Utility
    class tag_collector {
        +get_mp3_tags()
    }

    class VLC {
        +Instance
        +MediaPlayer
        +play()
        +stop()
    }

    %% Relationships
    VintageRadio --> DLNAWrapper
    VintageRadio --> DLNAMusic
    VintageRadio --> UserRequest
    VintageRadio --> KeyboardController
    VintageRadio --> Display

    DLNAWrapper --> DLNANetwork
    DLNAWrapper --> DLNADatabase
    DLNAWrapper --> tag_collector

    DLNAMusic --> VLC

    KeyboardController --> VintageRadio : callback

    DLNADbWrapper --> DLNADatabase

    %% Notes
    note for VintageRadio "Point d'entrée principal<br/>Gère la boucle asynchrone"
    note for DLNAWrapper "Wrapper réseau + DB<br/>Contient DLNANetwork et DLNADatabase"
    note for DLNAMusic "Gestion lecture VLC<br/>ReplayGain activé"
    note for KeyboardController "Thread d'écoute clavier<br/>Callback vers VintageRadio"
    note for DLNADatabase "SQLite pour métadonnées<br/>Hash 8 chars, Rating, BPM"
```
