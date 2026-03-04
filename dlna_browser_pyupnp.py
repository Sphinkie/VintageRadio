#!/usr/bin/env python3
"""
DLNA browser built with pyupnp 0.9 β (fixed import for UpnpFactory).

Author : Lumo (Proton AI)
"""

import configparser
import sys
from pathlib import Path
from typing import List, Optional

# ----------------------------------------------------------------------
# Import UpnpFactory – the correct path for pyupnp 0.9 β (fallback for very old releases)
# ----------------------------------------------------------------------
try:
    # New location introduced in 0.9 β
    from pyupnp import UpnpFactory          # type: ignore
except ImportError:                         # pragma: no cover
    # Very old releases (< 0.3.0) kept it under pyupnp.client
    from pyupnp.client import UpnpFactory   # type: ignore

# Remaining pyupnp imports (unchanged)
from pyupnp.ssdp import SsdpSearcher
from pyupnp.services.contentdirectory import ContentDirectoryService

# ----------------------------------------------------------------------
# Configuration constants
# ----------------------------------------------------------------------
INI_FILE = Path("preferend_dlna.ini")
DEFAULT_ROOT = "Audios"
DEFAULT_SUB1 = "By Folder"
DEFAULT_SUB2 = "Blues"

# ----------------------------------------------------------------------
# Helper functions for the INI file
# ----------------------------------------------------------------------
def load_preferred_url() -> Optional[str]:
    if not INI_FILE.is_file():
        return None
    cfg = configparser.ConfigParser()
    cfg.read(INI_FILE)
    try:
        return cfg["server"]["url"]
    except Exception:
        return None


def save_preferred_url(url: str) -> None:
    cfg = configparser.ConfigParser()
    cfg["server"] = {"url": url}
    with INI_FILE.open("w", encoding="utf-8") as f:
        cfg.write(f)


# ----------------------------------------------------------------------
# Discovery of MediaServer devices
# ----------------------------------------------------------------------
def discover_media_servers(timeout: int = 5) -> List[dict]:
    """
    SSDP M‑SEARCH for UPnP MediaServer devices.
    Returns a list of dictionaries containing the raw SSDP headers.
    """
    searcher = SsdpSearcher()
    st = "urn:schemas-upnp-org:device:MediaServer:1"
    responses = searcher.search(st, timeout=timeout)
    return responses


# ----------------------------------------------------------------------
# Build a pyupnp device object from a description URL
# ----------------------------------------------------------------------
def build_device(description_url: str):
    """
    Download the device description XML and create a pyupnp device.
    """
    factory = UpnpFactory()
    return factory.create_device(description_url)


# ----------------------------------------------------------------------
# Interactive server selection
# ----------------------------------------------------------------------
def choose_server_interactively(devices: List[dict]) -> dict:
    print("\n=== Serveurs DLNA découverts ===")
    for idx, dev in enumerate(devices, start=1):
        print(f"{idx}. {dev['location']} (USN={dev['usn']})")
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
    cd_service: ContentDirectoryService,
    path_parts: List[str],
) -> List[dict]:
    """
    Walk from the root container (ID='0') through each folder name in ``path_parts``.
    Returns the list of DIDL‑Lite items that live in the final container.
    """
    container_id = "0"
    for part in path_parts:
        result = cd_service.browse(container_id, "BrowseDirectChildren")
        children = result["Result"].items
        match = next((c for c in children if c.title == part), None)
        if match is None:
            raise FileNotFoundError(f"Sous‑dossier « {part} » introuvable.")
        container_id = match.id

    final_result = cd_service.browse(container_id, "BrowseDirectChildren")
    return final_result["Result"].items


# ----------------------------------------------------------------------
# Filter MP3 files from a list of DIDL‑Lite items
# ----------------------------------------------------------------------
def filter_mp3_items(items: List[dict]) -> List[str]:
    mp3_urls = []
    for it in items:
        if it.title.lower().endswith(".mp3"):
            if it.resources:
                url = it.resources[0].uri
                mp3_urls.append(f"{it.title} – {url}")
    return mp3_urls


# ----------------------------------------------------------------------
# Main orchestration
# ----------------------------------------------------------------------
def main(
    root_folder: str = DEFAULT_ROOT,
    subfolder1: str = DEFAULT_SUB1,
    subfolder2: str = DEFAULT_SUB2,
) -> None:
    # 1️⃣ Discover servers
    servers = discover_media_servers()
    if not servers:
        print("Aucun serveur DLNA/MediaServer détecté sur le LAN.")
        sys.exit(0)

    # 2️⃣ Load preferred URL (if any)
    preferred_url = load_preferred_url()
    chosen = None

    if preferred_url:
        matching = [s for s in servers if s["location"] == preferred_url]
        if matching:
            chosen = matching[0]
        else:
            print(
                "Le serveur enregistré dans preferend_dlna.ini n’est pas présent "
                "sur le réseau actuel."
            )

    # 3️⃣ Interactive fallback
    if not chosen:
        chosen = choose_server_interactively(servers)
        resp = input("Mémoriser ce serveur dans preferend_dlna.ini ? (o/n) ").strip().lower()
        if resp.startswith("o"):
            save_preferred_url(chosen["location"])
            print("Serveur mémorisé.")

    # 4️⃣ Build device object
    print(f"\nConnexion au serveur : {chosen['location']}")
    device = build_device(chosen["location"])

    # Verify ContentDirectory service presence
    if not device.has_service("urn:schemas-upnp-org:service:ContentDirectory:1"):
        print("Ce dispositif ne propose pas de service ContentDirectory – impossible de parcourir les dossiers.")
        sys.exit(1)

    cd_service: ContentDirectoryService = device.get_service(
        "urn:schemas-upnp-org:service:ContentDirectory:1"
    )

    # 5️⃣ Navigate to the target folder
    try:
        items = browse_to_folder(
            cd_service,
            path_parts=[root_folder, subfolder1, subfolder2],
        )
    except FileNotFoundError as e:
        print(f"Erreur de navigation : {e}")
        sys.exit(1)

    # 6️⃣ List MP3 files
    mp3_list = filter_mp3_items(items)
    if not mp3_list:
        print("Aucun fichier MP3 trouvé dans le dossier demandé.")
    else:
        print("\n=== Fichiers MP3 disponibles ===")
        for line in mp3_list:
            print("- " + line)


# ----------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Adjust folder names here if your server uses different ones.
    main(
        root_folder="Audios",
        subfolder1="By Folder",   # change as needed
        subfolder2="Blues",       # change as needed
    )