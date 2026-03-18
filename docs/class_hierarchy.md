## Hiérarchie des classes

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
    class VREngine {
        +get_dlna_server()
        +scan_all_mp3()
        +get_track_from_db()
        +show_clip_info()
        +ready()
        +close()
        +db_w
        +net_wrapper
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
        +after_track_callback
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

    %% Network Layer
    class DLNANetwork {
        +discover_servers()
        +browse()
        +browse_recursive()
        +extract_mp3_items()
        +get_content_directory_control_url()
        +_parse_ssdp_response()
        +_soap_envelope()
        +xml_merge()
    }

    class DLNAWrapper {
        +set_server()
        +find_music_container()
        +find_container()
        +find_child_id()
        +get_file_urls()
        +get_clip_info()
        +get_mp3_items()
        +resolve_control()
        +discover_servers()
        +choose_server()
        +pick_server_interactively()
        +net
        +didl_container
        +server_control_url
        +music_container_id
    }

    %% Database Layer
    class VRDatabase {
        +store_tracks()
        +get_tracks_by_date_range()
        +count()
        +get_track_info()
        +get_track_urls_by_genre()
        +update_track()
        +close()
        +conn
    }

    class DBWrapper {
        +store_tracks()
        +get_tracks_for_decade()
        +get_track_info()
        +get_tracks_for_genre()
        +update_track_rating()
        +update_track_bpm()
        +db
    }

    %% Utility
    class Display {
        +show()
        +add_line()
        +warning()
        +flush()
        +input()
    }

    class vr_logger {
        +get_logger()
        +set_logging()
    }

    %% External
    class VLC {
        +Instance
        +MediaPlayer
        +play()
        +stop()
    }

    %% Relationships
    VintageRadio --> VREngine
    VintageRadio --> DLNAMusic
    VintageRadio --> UserRequest
    VintageRadio --> KeyboardController
    VintageRadio --> Display

    VREngine --> DLNAWrapper
    VREngine --> DBWrapper
    VREngine --> Display

    DLNAWrapper --> DLNANetwork
    DLNAWrapper --> vr_logger

    DLNAMusic --> VLC

    KeyboardController --> VintageRadio : callback

    DBWrapper --> VRDatabase

    %% Notes
    note for VintageRadio "Point d'entrée principal<br/>Gère la boucle asynchrone asyncio"
    note for VREngine "Coordination DB + Réseau<br/>Initialisation des composants"
    note for DLNAMusic "Gestion lecture VLC<br/>Playlist asynchrone"
    note for KeyboardController "Thread d'écoute clavier<br/>Callback vers VintageRadio"
    note for VRDatabase "SQLite pour métadonnées<br/>Hash 8 chars, Rating, BPM"
    note for DLNANetwork "SSDP + SOAP + DIDL<br/>Découverte et navigation"