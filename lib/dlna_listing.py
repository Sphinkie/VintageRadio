# coding: UTF-8
# ==================================================================
# dlna_listing.py
# ==================================================================
# VintageRadio - Helpers.
# David de Lorenzo (2026)
# ==================================================================
from typing import List, Tuple, Optional
from lib.dlna_network import DLNANetwork


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


# --------------------------------------------------------------------- #
# Helper to turn a description URL into the ContentDirectory control URL
# --------------------------------------------------------------------- #
def resolve_control(url: str) -> Optional[str]:
    return DLNANetwork.get_content_directory_control_url(url)

# --------------------------------------------------------------------- #
# Si le serveur préféré est dans la liste des serveurs découverts: il est sélectionné.
# Sinon l'utilisateur en choisit un.
# La fonction retourne l'url du serveur s'il faut le mémoriser dans les nouvelles préférences.
# --------------------------------------------------------------------- #
def choose_server(servers, preferred_server_url: str):
    server_control_url: Optional[str] = None
    if not servers:
            print("No DLNA servers were discovered on the LAN.")
            return
    # If the user answered a server that matches the saved one, reuse it; otherwise ask.
    if preferred_server_url:
        # Look for the same description URL among the fresh results
        matching = [s for s in servers if s[0] == preferred_server_url]
        if matching:
            server_control_url = resolve_control(matching[0][0])
    if not server_control_url:
        # Ask the user which server to use
        chosen_server = pick_server_interactively(servers)
        if not chosen_server:
            print("No server selected – exiting.")
            return
        server_control_url = resolve_control(chosen_server)
        if not server_control_url:
            print("Chosen server does not expose a ContentDirectory service.")
            return
        return chosen_server
