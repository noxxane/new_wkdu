"""program to scrape the wkdu website and create spotify playlists from their
playlists"""

import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
import requests
import spotipy


load_dotenv()


def playlist_url_from_playlist_id(playlist_id: int) -> str:
    """creates a playlist's url from its id"""
    return "https://wkdu.org/playlist/" + str(playlist_id)


# for $7 cold brew and $7 cold brew only, ostensibly
def seven_dollar_cold_brew_from_playlist_id(
    playlist_id: int,
) -> (str, list[tuple[str, str, str]]):
    """creates a spotify playlist from a seven dollar cold brew playlist"""
    html = requests.get(playlist_url_from_playlist_id(playlist_id), timeout=5).text
    soup = BeautifulSoup(html, "html.parser")

    playlist_tracks_table = soup.find("table", class_="cols-4")
    playlist_tracks_tbody = playlist_tracks_table.find("tbody")
    playlist_tracks = playlist_tracks_tbody.find_all("tr")
    playlist_tracks_formatted = []
    for playlist_track in playlist_tracks:
        playlist_track_tds = playlist_track.find_all("td")
        track_artist = playlist_track_tds[0].get_text().strip()
        track_title = playlist_track_tds[1].get_text().strip()
        track_album = playlist_track_tds[2].get_text().strip()
        playlist_tracks_formatted.append((track_artist, track_title, track_album))

    return (f"$7 cold brew {playlist_id}", playlist_tracks_formatted)


def add_playlist_to_spotify(
    playlist_name: str, playlist_tracks_formatted: list[tuple[str, str, str]]
):
    """adds a playlist to spotify from the playlist name and the artist, track
    name, and album of each track being added"""
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(scope="playlist-read-private playlist-modify-private")
    )

    new_playlist = sp.user_playlist_create(
        sp.current_user()['id'], "wkdu playlist :3", public=False, description=playlist_name
    )
    new_playlist_id = new_playlist["id"]

    track_uris = []
    for track in playlist_tracks_formatted:
        try:
            search_query = f"track:{track[1]} artist:{track[0]} album:{track[2]}"

            print("searching for track", track)
            search_response = sp.search(q=search_query, type="track", limit=10)
            track_uri = search_response["tracks"]["items"][0]["uri"]
            print("found track", track)
            track_uris.append(track_uri)
        except Exception as e:
            print("Error searching for track", str(track) + ": " + str(e))
            continue

    sp.user_playlist_add_tracks(sp.current_user()['id'], new_playlist_id, track_uris)


if __name__ == "__main__":
    test = seven_dollar_cold_brew_from_playlist_id(67354)
    add_playlist_to_spotify(test[0], test[1])
