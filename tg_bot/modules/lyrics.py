import requests
import urllib.parse

class Song:
    @staticmethod
    def find_song(title: str, artist: str = "") -> str:
        """
        Fetches lyrics using a tokenless public API.
        Maintains the exact function interface you need.
        """
        # Clean inputs
        title_clean = title.strip()
        artist_clean = artist.strip()
        
        # Method 1: Try LRCLIB (Highly reliable public lyrics database)
        try:
            query = f"{title_clean} {artist_clean}".strip()
            url = f"https://lrclib.net/api/search?q={urllib.parse.quote(query)}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    # Look for plain lyrics or fall back to synced lyrics text
                    track = data[0]
                    lyrics = track.get("plainLyrics") or track.get("syncedLyrics")
                    if lyrics:
                        return lyrics.strip()
        except Exception:
            pass # Fall through to next method if this fails

        # Method 2: Fallback to Lyrics.ovh (Tokenless exact match)
        if artist_clean:
            try:
                url = f"https://api.lyrics.ovh/v1/{urllib.parse.quote(artist_clean)}/{urllib.parse.quote(title_clean)}"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    lyrics = response.json().get("lyrics", "")
                    if lyrics:
                        return lyrics.strip()
            except Exception:
                pass

        return "Lyrics not found or API unavailable."

# lyrics = Song.find_song("Blinding Lights", "The Weeknd")
# print(lyrics)
