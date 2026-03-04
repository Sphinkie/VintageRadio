# ----------------------------------------------------------------------
# Bibliothèque tierce requise: python‑dlna (ou toute autre implémentation
# de découverte SSDP/UPnP).  Vous pouvez l’installer avec:
#     pip install python-dlna
# https://pypi.org/project/dlna/
# https://pypi.org/project/Coherence/ abandonné
# https://github.com/coherence-project/Coherence
# Bibliothèque DLNA: si vous utilisez une autre lib
# (ex. Coherence, miniupnpc), remplacez les appels à DLNAClient,
# content_directory, etc., par les équivalents de votre choix.
# ----------------------------------------------------------------------

import os
import importlib.util
import configparser
from pathlib import Path
from typing import List, Optional
import time
# from dlna import DLNAClient, DLNADevice  # ← à adapter selon la lib choisie
from coherence.base import Coherence
from coherence.upnp.core import device
from coherence.upnp.core import DIDLLite


CONFIG_FILE = "preferred_dlna.ini"


class Servers:

    # --------------------------------------------------------
    # Constructeur
    # --------------------------------------------------------
    def __init__(self):
        # Crée un contrôleur Coherence (client UPnP/DLNA)
        self.coh = Coherence({'logmode': 'warning'})
        pass

    def discover_dlna_servers(self, timeout: int = 5) -> List[device]:
        """
        type exact: coherence.upnp.core.Device
        Recherche les serveurs DLNA/UPnP présents sur le réseau local.
        Retourne une liste d'objets ``DLNADevice`` (ou équivalent).
        """
        # Attendre que la découverte se fasse (environ 5s)
        time.sleep(5)
        # devices = client.discover(timeout=timeout)
        devices = self.coh.devices.values()

        # ------- TESTS UNITAIRE
        # Parcourir les appareils découverts
        for device in self.coh.devices.values():
            print(f"Nom : {device.get_friendly_name()}")
            # Vérifier s’il possède le service ContentDirectory (typique d’un MediaServer)
            if hasattr(device, 'content_directory'):
                cd = device.content_directory
                # Exemple: lister les objets racine du serveur
                root = cd.browse('0')  # '0' = ID du conteneur racine
                for item in root:
                    print(" -", item.title)
        return devices


    def load_preferred_server(self) -> Optional[str]:
        """
        Lit le fichier INI et renvoie le nom (ou l'URL) du serveur préféré,
        ou ``None`` s’il n’existe pas ou ne contient pas la clé attendue.
        """
        cfg_path = Path(CONFIG_FILE)
        if not cfg_path.is_file():
            return None

        parser = configparser.ConfigParser()
        parser.read(cfg_path)

        # On attend une section [server] avec la clé ``url`` (modifiable)
        try:
            return parser["server"]["url"]
        except Exception:
            return None


    def save_preferred_server(self, url: str) -> None:
        """
        Enregistre l’URL du serveur choisi dans le fichier INI.
        """
        parser = configparser.ConfigParser()
        parser["server"] = {"url": url}
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            parser.write(f)


    def choose_server_interactively(self, servers: List[device]) -> device:
        """
        Affiche la liste des serveurs découverts et demande à l’utilisateur
        d’en sélectionner un.
        """
        print("\nServeurs DLNA détectés:")
        for idx, dev in enumerate(servers, start=1):
            # ``friendly_name`` est généralement présent dans les bibliothèques UPnP
            print(f"{idx}. {dev.friendly_name} ({dev.location})")

        while True:
            choice = input("\nEntrez le numéro du serveur à utiliser: ").strip()
            if not choice.isdigit():
                print("Veuillez entrer un nombre valide.")
                continue
            idx = int(choice) - 1
            if 0 <= idx < len(servers):
                return servers[idx]
            print("Choix hors plage, réessayez.")


    def browse_folder(
        self,
        device: device,
        base_path: str,
        subfolders: List[str],
    ) -> List[dict]:
        """
        Parcourt récursivement les sous‑dossiers indiqués et retourne la
        liste brute d’objets «item» (dépend de la lib utilisée).
        """
        # La plupart des bibliothèques exposent un service ContentDirectory
        cd_service = device.content_directory

        # Étape 1: accéder au dossier racine (ex. «Audios»)
        container_id = cd_service.browse_container(base_path)

        # Étape 2: descendre dans chaque sous‑dossier demandé
        for sub in subfolders:
            # Recherche du sous‑dossier parmi les enfants du conteneur actuel
            children = cd_service.list_children(container_id)
            match = next((c for c in children if c.title == sub), None)
            if not match:
                raise FileNotFoundError(f"Sous‑dossier « {sub} » introuvable.")
            container_id = match.id

        # Retourner les éléments du dernier conteneur (les fichiers)
        return cd_service.list_children(container_id)


    def list_mp3_files(self, items: List[dict]) -> List[str]:
        """
        Filtre les objets retournés pour ne garder que les fichiers .mp3
        et renvoie leurs titres (ou URLs selon la lib).
        """
        mp3 = []
        for it in items:
            # Certaines libs utilisent ``resource`` ou ``url`` pour le lien réel
            title = it.title
            url = getattr(it, "resource", getattr(it, "url", ""))

            if title.lower().endswith(".mp3"):
                mp3.append(f"{title} – {url}")
        return mp3

"""
Voici quelques projets réels que vous pouvez réellement installer et qui offrent les fonctions nécessaires :
Bibliothèque	Installation	Principales capacités DLNA/UPnP
Coherence	pip install Coherence	Implémentation complète du client UPnP/DLNA ; découverte de périphériques, navigation dans les ContentDirectory, lecture de médias.
python-upnp-ssdp	pip install python-upnp-ssdp	Découverte SSDP (Simple Service Discovery Protocol) pour repérer les appareils DLNA sur le LAN. Nécessite d’appeler ensuite les services UPnP (ex. via requests ou urllib).
pyupnp	pip install pyupnp	Client léger pour envoyer des requêtes SOAP aux services UPnP ; permet de parcourir les dossiers et de récupérer les métadonnées.
miniupnpc (bindings C)	pip install miniupnpc	Principalement destiné à la gestion du NAT, mais inclut aussi des fonctions de découverte SSDP utiles pour repérer les appareils DLNA.
async_upnp_client	pip install async_upnp_client	Bibliothèque asynchrone moderne ; découverte SSDP, appel de services UPnP, navigation dans les ContentDirectory. Idéale si vous travaillez déjà avec asyncio.
"""