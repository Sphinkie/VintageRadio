1  # list_dlna.py
import os
import configparser
import vlc
import time
from pathlib import Path
from typing import List, Tuple, Optional
from dlna_network import DLNANetwork

# --------------------------------------------------------------------- #
# Configuration handling (preferred_dlna.ini)
# --------------------------------------------------------------------- #
CONFIG_FILE = Path("preferred_dlna.ini")
CONFIG_SECTION = "server"

# --------------------------------------------------------------------- #
# Dynamic Configuration (future GPI/O)
# --------------------------------------------------------------------- #
MODE = "By Genre"   # fre: "Par genre"
MODE_ID = "1"       # 1: By Genre
GENRE = "Blues"
GENRE_ID = "2"  # (Blues)


# --------------------------------------------------------------------- #
# Lecture des préférences
# --------------------------------------------------------------------- #
def load_preferred() -> Optional[str]:
    """Return the saved server control URL, or None if the file is missing."""
    if not CONFIG_FILE.is_file():
        print("file not found: ", CONFIG_FILE)
        return None
    cfg = configparser.ConfigParser()
    cfg.read(CONFIG_FILE)
    return cfg.get(CONFIG_SECTION, "control_url", fallback=None)


# --------------------------------------------------------------------- #
# Ecriture des préférences
# --------------------------------------------------------------------- #
def save_preferred(url: str) -> None:
    """Persist the chosen server's control URL for next runs."""
    cfg = configparser.ConfigParser()
    cfg[CONFIG_SECTION] = {"control_url": url}
    with CONFIG_FILE.open("w") as fp:
        cfg.write(fp)
    print(CONFIG_FILE, " written")


# --------------------------------------------------------------------- #
# Helper to turn a human‑readable server description into a control URL
# --------------------------------------------------------------------- #
def pick_server_interactively(servers: List[Tuple[str, str]]) -> Optional[str]:
    """
    Show a numbered list of discovered servers (showing just the host part)
    and ask the user to choose one.  Returns the selected *control URL*.
    """
    if not servers:
        print("No DLNA server found on the local network.")
        return None

    print("\nDiscovered DLNA MediaServers:")
    for idx, (desc_url, usn) in enumerate(servers, start=1):
        host = desc_url.split("/", 3)[2]  # crude host extraction
        print(f"[{idx}] {host}")

    while True:
        choice = input(f"Select a server (1‑{len(servers)} or press Enter to abort): ")
        if not choice:
            return None
        if choice.isdigit():
            i = int(choice)
            if 1 <= i <= len(servers):
                return servers[i - 1][0]  # return the description URL
        print("Invalid selection – try again.")


# -----------------------------------------------------------------
# Helper to turn a description URL into the ContentDirectory control URL
# DDL; sorti du MAiN
# -----------------------------------------------------------------
def resolve_control(url: str) -> Optional[str]:
    return DLNANetwork.get_content_directory_control_url(url)


# --------------------------------------------------------------------- #
# Main orchestration
# --------------------------------------------------------------------- #
def main():
    net = DLNANetwork()

    # 1️⃣ Try to load a previously saved server
    control_url: Optional[str] = None
    preferred_desc_url = load_preferred()
    # print(preferred_desc_url)

    # -----------------------------------------------------------------
    # If we have a saved description URL, verify that it is still reachable
    # -----------------------------------------------------------------
    if preferred_desc_url:
        print(f"Trying previously saved server: {preferred_desc_url}")
        ctrl = resolve_control(preferred_desc_url)
        if ctrl:
            control_url = ctrl
            print("Saved server is reachable.")
        else:
            print("Saved server could not be reached or does not expose ContentDirectory.")

    # -----------------------------------------------------------------
    # If we still have no usable server, discover anew
    # -----------------------------------------------------------------
    if not control_url:
        servers = net.discover_servers()
        if not servers:
            print("No DLNA servers were discovered on the LAN.")
            return

        # If the user supplied a description URL (from discovery) that matches
        # the saved one, reuse it; otherwise ask.
        if preferred_desc_url:
            # Look for the same description URL among the fresh results
            matching = [s for s in servers if s[0] == preferred_desc_url]
            if matching:
                control_url = resolve_control(matching[0][0])
        if not control_url:
            # Ask the user which server to use
            chosen_desc = pick_server_interactively(servers)
            if not chosen_desc:
                print("No server selected – exiting.")
                return
            control_url = resolve_control(chosen_desc)
            if not control_url:
                print("Chosen server does not expose a ContentDirectory service.")
                return

            # Offer to remember the choice
            remember = input("Remember this server for next time? (y/N): ").strip().lower()
            if remember == "y":
                save_preferred(chosen_desc)

    # -----------------------------------------------------------------
    # At this point we have a valid control URL
    # -----------------------------------------------------------------
    print(f"\nUsing ContentDirectory control URL: {control_url}")
    assert control_url is not None

    # -----------------------------------------------------------------
    # Configurable folder hierarchy – you can change these constants
    # -----------------------------------------------------------------
    ROOT_ID = "0"  # the root container (Music / Photo / Video)

    # -------------------------------------------------------------
    # Helper to find a child container by its title (case‑insensitive)
    # Note : DIDL‑Lite(Digital Item Description Language) is the standard
    # XML schema that DLNA / UPnP servers use to describe the media
    # objects they expose (containers, tracks, images, etc.).
    # -------------------------------------------------------------
    def find_child_id(parent_id: str, title: str) -> Optional[str]:
        didl = net.browse(control_url, object_id=parent_id)
        if didl is None:  # DDL
            return None
        for container in didl.findall('.//{*}container'):
            dc_title = container.find('{*}title')
            if dc_title is not None and dc_title.text and dc_title.text.strip().lower() == title.lower():
                return container.attrib.get('id')
        return None

    # -------------------------------------------------------------
    # Resolve the two configurable sub‑folders
    # -------------------------------------------------------------
    # 1️⃣ “Music” – we assume it is a direct child of the root
    music_container_id = find_child_id(ROOT_ID, "Music")
    if music_container_id is None:
        music_container_id = find_child_id(ROOT_ID, "Musique")
    if music_container_id is None:
        print("Could not locate a 'Music' container on the server.")
        return

    # 2️⃣ “By Genre” (configurable)
    container_id = find_child_id(music_container_id, MODE)
    if container_id is None:
        print("Could not locate a '" + MODE + "' container under 'Music'.")
        return

    # 3️⃣ “Blues” (configurable)
    genre_id = find_child_id(container_id, GENRE)
    if genre_id is None:
        print("Could not locate a 'Blues' container under 'By Genre'.")
        return

    # -------------------------------------------------------------
    # Finally list MP3 files inside the Blues container
    # -------------------------------------------------------------
    didl_blues = net.browse(control_url, object_id=genre_id)
    if didl_blues is None:  # DDL
        print("Failed to browse the 'Blues' container.")
        return

    mp3_urls = net.extract_mp3_items(didl_blues)
    if mp3_urls is None:   # DDL
        print("No MP3 files were found in the 'Blues' folder.")
        return

    print("\n--- MP3 files found in 'Blues' ---")
    for url in mp3_urls:
        print(url)

    print("\n--- Start playing ---")
    for url in mp3_urls:
        # Create a VLC instance and media player
        player = vlc.MediaPlayer(url)
        # Start playback (returns immediately)
        player.play()
        # Wait until the track ends
        while player.get_state() != vlc.State.Ended:
            time.sleep(0.5)          # poll every half-second

# -------------------------------------------------------------
# Launch Main Program
# -------------------------------------------------------------
if __name__ == "__main__":
    main()
