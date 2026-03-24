# coding: UTF-8
# ==================================================================
# lib/tag_collector.py
# ==================================================================
# VintageRadio - Download et analyse des entêtes MP3.
# Lumo (2026)
# Important Notes on DLNA & Tags
#
#     Server Support: This method works regardless of whether the Synology NAS exposes the tags via DLNA. It reads the tags directly from the file stream.
#     Performance   : Fetching 100KB is very fast (milliseconds on LAN). It does not download the whole song.
#     Rating Format : The "5 stars" rating is often stored in the POPM frame as a byte (0-255). The code above converts this to a rough "X stars" string.
#                     If your Synology NAS uses a different custom frame (e.g., XSOP), you may need to adjust the tags.get() call.
#     BPM           : The TBP frame is standard.
# ==================================================================

import sys
import requests
from typing import Tuple, Optional
from lib.vr_logger import get_logger
try:
    from mutagen.id3 import ID3
except ImportError:
    sys.exit("python-mutagen not found – install with: sudo apt install python3-mutagen")

log = get_logger(__name__)


# ----------------------------------------------------------------------
# Récupération de l'entête d'un fichier MP3
# ----------------------------------------------------------------------
def get_track_tags(track_url: str, max_bytes: int = 100000) -> Tuple[Optional[str], Optional[str]]:
    """
    Fetches ID3v2 tags (BPM, Rating, Genre) from an MP3 file hosted on a DLNA server.
    Uses HTTP Range requests to fetch only the last ~100KB of the file where ID3v2 tags
    are typically located (or the first 100KB if the server doesn't support ranges).
    We want the ID3v2 tag which is usually at the START of the file.
    Note that ID3v1 tags are located at the end of the file (not managed here).
    Documentation: https://mutagen.readthedocs.io/en/latest/index.html
    Ordre des tags: TIT2(titre) TPE2(artist) TALB(album) TCON(genre) APIC(picture) POPM(rating) TPE1(artist) TDRC(année)
    A noter que le RATING est situé après le(s) picture(s), ce qui empêche de se limiter à un nombre
    minimal d'octets à télécharger...
    Args:
        track_url: The full URL to the MP3 file.
        max_bytes: Maximum bytes to fetch (default 100KB).
        
    Returns:
        Tuple of (bpm, rating)
        Returns (None, None) if tags are missing or if fetch fails.
    """
    try:
        # Try to get the head.
        head_resp = requests.head(track_url, timeout=5)
        # Try to get file size.
        file_size = int(head_resp.headers.get('content-length', 0))
        # Define the range of bytes to download.
        range_start = 0
        range_end = min(file_size - 1, max_bytes - 1) if file_size > 0 else max_bytes - 1
        headers = {'Range': f'bytes={range_start}-{range_end}'}
        log.debug(f"Fetching tags from {track_url} (Range: {range_start}-{int(range_end/1000)}kB)")
        # Let's fetch the first 100K bytes.
        resp = requests.get(track_url, headers=headers, timeout=10, stream=True)
        # not 200 OK will raise an error.
        resp.raise_for_status()

        # 2. Parse the ID3 tags from the fetched bytes
        # We need to read the bytes into a file-like object
        from io import BytesIO
        audio_data = BytesIO(resp.content)

        # -----------------------------------------------------------------
        # Try to load ID3 tags
        # -----------------------------------------------------------------
        try:
            tags = ID3(audio_data)
            # print(f"tags {tags}") # Full dump
        except Exception:
            # For simplicity, let's assume ID3v2 at start is standard for DLNA.
            log.warning(f"No ID3 tags found in the first {max_bytes} bytes of {track_url}")
            return None, None

        # ---------------------------------------------------------------------
        # Extract BPM specific field (Beats Per Minute).
        # - BPM is usually TBPM
        # ---------------------------------------------------------------------
        bpm_frame = tags.get('TBPM')
        log.debug(f"bpm_frame: {bpm_frame}")
        track_bpm = bpm_frame.text[0] if (bpm_frame and bpm_frame.text) else None

        # ---------------------------------------------------------------------
        # Extract Rating specific field (number of stars).
        # - COMM (User Defined Text Information) with description "Rating"
        # - POPM (Popularimeter) - requires parsing binary data
        # - Or a custom frame like 'XSOP' or 'RATING'
        # ---------------------------------------------------------------------
        mp3_rating = None
        # ---------------------------------------------------------------------
        # Check for COMM (User Comment) that might contain rating
        # ---------------------------------------------------------------------
        # comm_frames = tags.getall('COMM')
        # print (f"COMM {COMM}")
        # for comm in comm_frames:
        #     print(f"comm {comm.text}")
        #     if 'rating' in comm.desc.lower() or 'stars' in comm.desc.lower():
        #         rating = comm.text[0] if comm.text else None
        #         break
        # ---------------------------------------------------------------------
        # Check for POPM (Popularimeter)
        # ---------------------------------------------------------------------
        # Parse the POPM binary structure: email, count, rating (1 byte).
        # Ex: 'POPM:Windows Media Player 9 Series': POPM(email='Windows Media Player 9 Series', rating=196)
        # Ex: 196 = 3.8 stars
        # There may be more than one "POPM" frame in each tag, but only one with the same email address.
        popm_frame = tags.getall('POPM')
        if popm_frame:
            # popm_frame.rating is a single byte (0-255) to be converted to 0-5 (stars)
            log.debug(f"popm_frame: {popm_frame}")
            raw_rating = popm_frame[0].rating
            log.debug(f"raw_rating: {raw_rating}")
            if raw_rating > 0:
                mp3_rating = f"{round(raw_rating / 51)} stars"  # Rough approximation (255/51 ≈ 5)

        # ---------------------------------------------------------------------
        # Extract Genre specific field.
        # - TCON
        # ---------------------------------------------------------------------
        # genre_frame = tags.get('TCON')
        # genre = genre_frame.text[0] if genre_frame and genre_frame.text else None
        # For convenience, use the ‘genres’ property (list) rather than the ‘text’ attribute.
        # genre = genre_frame.genres[0]

        # ---------------------------------------------------------------------
        # On retourne les valeurs trouvées (peuvent être None)
        # ---------------------------------------------------------------------
        return track_bpm, mp3_rating

    except requests.exceptions.RequestException as e:
        log.error(f"Failed to fetch tags from {track_url}: {e}")
        return None, None
    except Exception as e:
        log.error(f"Error parsing tags from {track_url}: {e}")
        return None, None


# -------------------------------------------------------------
# Testing
# -------------------------------------------------------------
if __name__ == "__main__":
    url = "http://192.168.0.101:50002/m/MP3/2913.mp3"
    bpm, rating = get_track_tags(url)
    # ou tags = self.get_track_tags(url)
    print(f"BPM: {bpm}")
    print(f"Rating: {rating}")
