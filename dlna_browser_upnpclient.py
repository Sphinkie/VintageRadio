#!/usr/bin/env python3
"""
DLNA browser built with the upnpclient library.

Features
--------
* Discover all UPnP/DLNA MediaServer devices on the LAN.
* Optional persistent “preferred” server stored in preferend_dlna.ini.
* Interactive fallback when the preferred server is missing or unreachable.
* Walk through three configurable folders:
      Audios → <sub‑folder‑1> → <sub‑folder‑2>
* List every *.mp3* file found in the final folder (title + URL).

Author : Lumo (Proton AI)
"""

import configparser
import sys
from pathlib import Path
from typing import List, Optional

# ----------------------------------------------------------------------
# upnpclient import
# ----------------------------------------------------------------------
import upnpclient

# ----------------------------------------------------------------------
# Configuration constants (edit if your server uses different names)
# ----------------------------------------------------------------------
INI_FILE = Path("preferend_dlna.ini")
DEFAULT_ROOT = "Audios"          # top‑level folder on the server
DEFAULT_SUB1 = "By Folder"       # first sub‑folder (change as needed)
DEFAULT_SUB2 = "Blues"           # second sub‑folder (change as needed)

# ----------------------------------------------------------------------
# Helper functions for the INI file
# ----------------------------------------------------------------------
def load_preferred_url() -> Optional[str]:
    """Read the stored URL from preferend_dlna.ini (or return None)."""
    if not INI_FILE.is_file():
        return None
    cfg = configparser.ConfigParser()
    cfg.read(INI_FILE)
    try:
        return cfg["server"]["url"]
    except Exception:
        return None


def save_preferred_url(url: str) -> None:
    """Write the given URL into preferend_dlna.ini."""
    cfg = configparser.ConfigParser()
    cfg["server"] = {"url": url}
    with INI_FILE.open("w", encoding="utf-8") as f:
        cfg.write(f)


# ----------------------------------------------------------------------
# Discovery of MediaServer devices
# ----------------------------------------------------------------------
def discover_media_servers(timeout: int = 5) -> List[upnpclient.Device]:
    """
    Perform an SSDP M‑SEARCH for devices of type
    urn:schemas-upnp-org:device:MediaServer:1.
    Returns a list of upnpclient.Device objects.
    """
    # upnpclient.discover returns every device that answers the search.
    # We filter only MediaServer devices.
    all_devices = upnpclient.discover(timeout=timeout)
    media_servers = [
        dev
        for dev in all_devices
        if dev.device_type == "urn:schemas-upnp-org:device:MediaServer:1"
    ]
    return media_servers


# ----------------------------------------------------------------------
# Interactive server selection (fallback)
# ----------------------------------------------------------------------
def choose_server_interactively(devices: List[upnpclient.Device]) -> upnpclient.Device:
    print("\n=== Serveurs DLNA découverts ===")
    for idx, dev in enumerate(devices, start=1):
        # Friendly name is a property provided by upnpclient
        print(f"{idx}. {dev.friendly_name} (URL={dev.location})")
    while True:
        choice = input("\nNuméro du serveur à utiliser : ").strip()
        if not choice.isdigit():
            print("Veuillez entrer un nombre.")
            continue
        i = int(choice) - 1
        if 0 <= i < len(devices):
            return devices[i]
        print("Choix hors plage, réessayez.")


# ----------------------------------------------------------------------
# Browse recursively through a list of folder names
# ----------------------------------------------------------------------
def browse_to_folder(
    device: upnpclient.Device, path_parts: List[str]
): # -> List[upnpclient.DIDLObject]:
    """
    Starting at the root container (ID='0'), descend through each folder name
    supplied in ``path_parts``.  Returns the list of DIDL objects that live
    in the final container.
    """
    # The ContentDirectory service is identified by its URN.
    cd_service = device.service(
        "urn:schemas-upnp-org:service:ContentDirectory:1"
    )
    if cd_service is None:
        raise RuntimeError(
            "Ce serveur ne propose pas de service ContentDirectory."
        )

    container_id = "0"  # root container per UPnP spec
    for part in path_parts:
        # Browse the direct children of the current container.
        result = cd_service.Browse(
            ObjectID=container_id,
            BrowseFlag="BrowseDirectChildren",
            Filter="*",
            StartingIndex=0,
            RequestedCount=0,
            SortCriteria="",
        )
        # ``result`` is a dict; the parsed DIDL‑Lite objects are under the key
        # 'Result' (already converted to Python objects by upnpclient).
        children = result["Result"]

        # Find the child whose title matches the folder we want.
        match = next((c for c in children if getattr(c, "title", "") == part), None)
        if match is None:
            raise FileNotFoundError(f"Sous‑dossier « {part} » introuvable.")
        container_id = match.id  # descend into that folder

    # Final browse – list the items that live in the last container.
    final_res = cd_service.Browse(
        ObjectID=container_id,
        BrowseFlag="BrowseDirectChildren",
        Filter="*",
        StartingIndex=0,
        RequestedCount=0,
        SortCriteria="",
    )
    return final_res["Result"]


# ----------------------------------------------------------------------
# Filter MP3 files from a list of DIDL objects
# ----------------------------------------------------------------------
def filter_mp3_items(items: List[str]) -> List[str]:  # upnpclient.DIDLObject
    """
    Keep only items whose title ends with '.mp3' and return a readable string
    containing title and absolute URL.
    """
    mp3_list = []
    for it in items:
        title = getattr(it, "title", "")
        if title.lower().endswith(".mp3"):
            # Each item usually has at least one resource (the URL to the file).
            if it.resources:
                url = it.resources[0].uri
                mp3_list.append(f"{title} – {url}")
    return mp3_list


# ----------------------------------------------------------------------
# Main orchestration
# ----------------------------------------------------------------------
def main(
    root_folder: str = DEFAULT_ROOT,
    subfolder1: str = DEFAULT_SUB1,
    subfolder2: str = DEFAULT_SUB2,
) -> None:
    # --------------------------------------------------------------
    # 1️⃣ Discover MediaServer devices
    # --------------------------------------------------------------
    servers = discover_media_servers()
    if not servers:
        print("Aucun serveur DLNA/MediaServer détecté sur le LAN.")
        sys.exit(0)

    # --------------------------------------------------------------
    # 2️⃣ Try to load a previously saved favourite
    # --------------------------------------------------------------
    preferred_url = load_preferred_url()
    chosen: Optional[upnpclient.Device] = None

    if preferred_url:
        matching = [d for d in servers if d.location == preferred_url]
        if matching:
            chosen = matching[0]
        else:
            print(
                "Le serveur enregistré dans preferend_dlna.ini n’est pas présent "
                "sur le réseau actuel."
            )

    # --------------------------------------------------------------
    # 3️⃣ Interactive fallback if needed
    # --------------------------------------------------------------
    if not chosen:
        chosen = choose_server_interactively(servers)

        resp = input(
            "Mémoriser ce serveur dans preferend_dlna.ini ? (o/n) "
        ).strip().lower()
        if resp.startswith("o"):
            save_preferred_url(chosen.location)
            print("Serveur mémorisé.")

    # --------------------------------------------------------------
    # 4️⃣ Browse to the target folder hierarchy
    # --------------------------------------------------------------
    try:
        items = browse_to_folder(
            chosen,
            path_parts=[root_folder, subfolder1, subfolder2],
        )
    except FileNotFoundError as e:
        print(f"Erreur de navigation : {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"Erreur de service : {e}")
        sys.exit(1)

    # --------------------------------------------------------------
    # 5️⃣ List MP3 files
    # --------------------------------------------------------------
    mp3_files = filter_mp3_items(items)
    if not mp3_files:
        print("Aucun fichier MP3 trouvé dans le dossier demandé.")
    else:
        print("\n=== Fichiers MP3 disponibles ===")
        for line in mp3_files:
            print("- " + line)


# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Adjust the folder names here if your server uses different ones.
    main(
        root_folder="Audios",
        subfolder1="By Folder",   # change as needed
        subfolder2="Blues",       # change as needed
    )