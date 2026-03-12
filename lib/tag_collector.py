# lib/tag_collector.py

import requests
from mutagen.id3 import ID3, TBP, TRCK, COMM, TCON
from mutagen.mp3 import MP3
from typing import Tuple, Optional
from lib.dlna_logger import get_logger

log = get_logger(__name__)

def get_mp3_tags(url: str, max_bytes: int = 100000) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Fetches ID3v2 tags (BPM, Rating, Genre) from an MP3 file hosted on a DLNA server.
    
    Uses HTTP Range requests to fetch only the last ~100KB of the file where ID3v2 tags
    are typically located (or the first 100KB if the server doesn't support ranges).
    
    Args:
        url: The full URL to the MP3 file.
        max_bytes: Maximum bytes to fetch (default 100KB).
        
    Returns:
        Tuple of (bpm, rating, genre)
        Returns (None, None, None) if tags are missing or fetch fails.
    """
    try:
        # 1. Try to get file size to determine where to fetch from
        # We want the ID3v2 tag which is usually at the START of the file, 
        # but sometimes at the end (ID3v1). Let's try fetching the HEAD first.
        head_resp = requests.head(url, timeout=5)
        file_size = int(head_resp.headers.get('content-length', 0))
        
        # ID3v2 tags are at the BEGINNING of the file.
        # We only need to fetch the first ~100KB to get the ID3v2 header and frames.
        # ID3v2 tags are at the start, ID3v1 at the end.
        # Let's fetch the first 100KB.
        range_start = 0
        range_end = min(file_size - 1, max_bytes - 1) if file_size > 0 else max_bytes - 1
        
        headers = {'Range': f'bytes={range_start}-{range_end}'}
        log.debug(f"Fetching tags from {url} (Range: {range_start}-{range_end})")
        
        resp = requests.get(url, headers=headers, timeout=10, stream=True)
        resp.raise_for_status()
        
        # 2. Parse the ID3 tags from the fetched bytes
        # We need to read the bytes into a file-like object
        from io import BytesIO
        audio_data = BytesIO(resp.content)
        
        # Try to load ID3 tags
        try:
            tags = ID3(audio_data)
        except Exception:
            # Maybe it's an ID3v1 tag at the end? Or no tags?
            # If we fetched the start and found nothing, try the end if we didn't fetch it.
            # But for simplicity, let's assume ID3v2 at start is standard for DLNA.
            log.warning(f"No ID3 tags found in the first {max_bytes} bytes of {url}")
            return None, None, None

        # 3. Extract specific fields
        # BPM is usually TBP (Beats Per Minute)
        bpm_frame = tags.get('TBP')
        bpm = bpm_frame.text[0] if bpm_frame and bpm_frame.text else None
        
        # Rating is tricky. It's often stored in:
        # - COMM (User Defined Text Information) with description "Rating"
        # - POPM (Popularimeter) - requires parsing binary data
        # - Or a custom frame like 'XSOP' or 'RATING'
        rating = None
        
        # Check for COMM (Comments) that might contain rating
        comm_frames = tags.getall('COMM')
        for comm in comm_frames:
            if 'rating' in comm.desc.lower() or 'stars' in comm.desc.lower():
                rating = comm.text[0] if comm.text else None
                break
        
        # Check for POPM (Popularimeter) - this is binary, complex to parse simply
        # If you need POPM, you'd need to parse the binary structure:
        # email, count, rating (1 byte), seek position
        popm_frame = tags.get('POPM')
        if popm_frame:
            # popm_frame.rating is a single byte (0-255)
            # Convert to 0-5 stars roughly
            raw_rating = popm_frame.rating
            if raw_rating > 0:
                rating = f"{round(raw_rating / 51)} stars" # Rough approximation (255/51 ≈ 5)

        # Genre is usually TCON
        genre_frame = tags.get('TCON')
        genre = genre_frame.text[0] if genre_frame and genre_frame.text else None

        return bpm, rating, genre

    except requests.exceptions.RequestException as e:
        log.error(f"Failed to fetch tags from {url}: {e}")
        return None, None, None
    except Exception as e:
        log.error(f"Error parsing tags from {url}: {e}")
        return None, None, None
        
        
""" usage


pip install mutagen

# In dlna_music.py

from lib.get_mp3_tags import get_mp3_tags

class DLNAMusic:
    # ... existing code ...

    def get_track_details(self, url: str) -> dict:
        """
        Fetches detailed metadata including BPM and Rating.
        Falls back to standard DLNA metadata if tags are missing.
        """
        bpm, rating, genre = get_mp3_tags(url)
        
        return {
            'url': url,
            'bpm': bpm,
            'rating': rating,
            'genre': genre,
            # You can also combine with DLNA metadata here if needed
        }

    def play_random_async(self):
        # ... existing logic ...
        uri = self.shuffled_tracklist[self.current_pos]
        
        # Optional: Get details before playing
        details = self.get_track_details(uri)
        if details['bpm']:
            log.info(f"Playing track with BPM: {details['bpm']}")
        if details['rating']:
            log.info(f"User Rating: {details['rating']}")
            
        self.start_track(uri)
        # ... rest of logic ...

Important Notes on DLNA & Tags

    Server Support: This method works regardless of whether the Synology NAS exposes the tags via DLNA. It reads the tags directly from the file stream.
    Performance: Fetching 100KB is very fast (milliseconds on LAN). It does not download the whole song.
    Rating Format: The "5 stars" rating is often stored in the POPM frame as a byte (0-255). The code above converts this to a rough "X stars" string. If your Synology NAS uses a different custom frame (e.g., XSOP), you may need to adjust the tags.get() call.
    BPM: The TBP frame is standard. If your NAS doesn't write this, it will return None.

Testing

You can test this function directly in a Python shell on your Pi:

from lib.get_mp3_tags import get_mp3_tags

# Replace with a real URL from your DLNA server
url = "http://192.168.1.42:5000/m/MP3/2913.mp3" 
bpm, rating, genre = get_mp3_tags(url)

print(f"BPM: {bpm}")
print(f"Rating: {rating}")
print(f"Genre: {genre}")
"""        