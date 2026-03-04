# coding: UTF-8
# ==================================================================
# DLNA
# ==================================================================
# David de Lorenzo (2026)
# ==================================================================

from servers import Servers

# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


# ---------------------------------------------------------------------
# Programme principal python dlna_browser.py
# ---------------------------------------------------------------------
def main(
            audio_root: str = "Audios",
            subfolder_by_folder: str = "By Folder",
            subfolder_blues: str = "Blues",
    ) -> None:
        dl_servers = Servers()
        # 1️⃣ Découverte des serveurs DLNA
        servers = dl_servers.discover_dlna_servers()
        if not servers:
            print("Aucun serveur DLNA trouvé sur le LAN.")
            return

        # 2️⃣ Chargement du serveur préféré (si le fichier INI existe)
        preferred_url = dl_servers.load_preferred_server()
        # chosen_device: Optional[Device] = None
        chosen_device = None

        if preferred_url:
            # Vérifier que le serveur préféré figure bien parmi ceux découverts
            matching = [d for d in servers if d.location == preferred_url]
            if matching:
                chosen_device = matching[0]
            else:
                print(
                    "Le serveur indiqué dans preferend_dlna.ini n’est pas accessible "
                    "sur le LAN actuel."
                )

        # 3️⃣ Si aucun serveur valide n’a été trouvé, demander à l’utilisateur
        if not chosen_device:
            chosen_device = dl_servers.choose_server_interactively(servers)

            # Proposer de mémoriser le choix
            save = input("Souhaitez‑vous mémoriser ce serveur dans preferend_dlna.ini ? (o/n) ")
            if save.strip().lower().startswith("o"):
                dl_servers.save_preferred_server(chosen_device.location)
                print("Serveur mémorisé.")

        # 4️⃣ Navigation jusqu’au dossier cible
        try:
            items = dl_servers.browse_folder(
                chosen_device,
                base_path=audio_root,
                subfolders=[subfolder_by_folder, subfolder_blues],
            )
        except FileNotFoundError as e:
            print(f"Erreur lors de la navigation: {e}")
            return

        # 5️⃣ Liste des fichiers MP3
        mp3_files = dl_servers.list_mp3_files(items)
        if not mp3_files:
            print("Aucun fichier MP3 trouvé dans le dossier sélectionné.")
        else:
            print("\nFichiers MP3 disponibles:")
            for f in mp3_files:
                print(f"- {f}")

    # Si on a un fichier preferend_dlna.ini, se connecter au serveur préféré s'il est accessible
    # Sinon (pas de fichier INI, ou préferé non-accessible):
    #    afficher la liste des serveurs accessibles et demander d'en choisir un.
    #    Demander si il faut le mémoriser dans le fichier INI
    # Se connecter au serveur DLNA, dossier Audios
    # Se connecter au sous-dossier "By Folder" (paramétrable)
    # Se connecter au sous-dossier "Blues" (paramétrable)
    # Jouer les fichiers mp3 de ce dossier avec la library audiomux (ou mpv)

# ---------------------------------------------------------------------
# Program launcher
# ---------------------------------------------------------------------
if __name__ == "__main__":
    # Vous pouvez personnaliser les noms de dossiers ici
    main(
        audio_root="Audios",
        subfolder_by_folder="By Folder",   # à changer si besoin
        subfolder_blues="Blues",           # à changer si besoin
    )

