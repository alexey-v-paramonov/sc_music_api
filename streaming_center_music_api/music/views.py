import json
import string
import requests
import redis
import spotipy
import musicbrainzngs

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from spotipy.cache_handler import CacheFileHandler
from spotipy.oauth2 import SpotifyClientCredentials


class MusicAPI(APIView):

    authentication_classes = ()
    permission_classes = ()

    def is_successful_search(self, track_info):
        return bool(
            track_info.get("isrc")
            or track_info.get("small_image")
            or track_info.get("medium_image")
            or track_info.get("large_image")
        )

    def is_everything_found(self, track_info):
        return bool(
            track_info.get("isrc")
            and track_info.get("small_image")
            and track_info.get("medium_image")
            and track_info.get("large_image")
        )

    def is_clipart_complete(self, track_info):
        return bool(
            track_info.get("small_image")
            and track_info.get("medium_image")
            and track_info.get("large_image")
        )

    def get(self, request):
        # artist - title query
        q = request.query_params.get("q", "").strip()
        # artist and title in separate params
        title = request.query_params.get("t", "").strip()
        artist = request.query_params.get("a", "").strip()
        do_q = q and len(q) > 5
        if do_q and q.find(" - ") > 0:
            artist, title = (q.split(" - ")[0], " - ".join(q.split(" - ")[1:]))

        do_title_artist = title and artist

        if not (do_q or do_title_artist):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        key = (q if do_q else f"{artist} - {title}").translate(str.maketrans("", "", string.punctuation)).replace(" ", "").lower()
        r = redis.Redis(host="localhost", port=6379, db=0)
        cached_track_info = r.get(key)
        if cached_track_info:
            data = json.loads(cached_track_info)
            data['cached'] = True
            data["key"] = key
            return Response(data)

        track_info = {}
        client_credentials_manager = SpotifyClientCredentials(
            settings.SPOTIFY_CLIENT_ID,
            settings.SPOTIFY_CLIENT_SECRET,
            cache_handler=CacheFileHandler(cache_path="/tmp/spotify_token"),
        )
        spotify = spotipy.Spotify(
            client_credentials_manager=client_credentials_manager, requests_timeout=2
        )
        results = None
        try:
            results = spotify.search(
                q=(q if do_q else f"{artist} - {title}"),
                limit=1,
                type="track"
            )
        except Exception as e:
            pass

        if results and results["tracks"]["items"]:
            track = results["tracks"]["items"][0]
            ext_ids = track.get("external_ids", {})
            track_info["isrc"] = ext_ids.get("isrc", None)
            album = track.get("album", {})
            if album.get("images", []) and len(album["images"]) >= 3:
                track_info["small_image"] = album["images"][-1]["url"]
                track_info["medium_image"] = album["images"][-2]["url"]
                track_info["large_image"] = album["images"][-3]["url"]

        # LastFM (no ISRC)
        if not self.is_clipart_complete(track_info) and do_title_artist:
            API_BASE = "https://ws.audioscrobbler.com/2.0/";
            artist_q = artist
            track_q = title
            url = f"{API_BASE}?artist={artist_q}&track={track_q}&method=track.getInfo&api_key={settings.LASTFM_API_KEY}&format=json"
            try:
                response = requests.get(url, timeout=2)
            except:
                response = None

            if response and response.ok:
                j = response.json()
                track_info["track_mbid"] = j.get('track', {}).get('mbid')
                images = j.get('track', {}).get('album', {}).get('image')
                if images and len(images) > 2:
                    track_info["small_image"] = images[-3]["#text"]
                    track_info["medium_image"] = images[-2]["#text"]
                    track_info["large_image"] = images[-1]["#text"]

        # Soundexchange API
        if do_title_artist and not track_info.get("isrc"):
            url = "https://isrcsearch.ifpi.org/#!/search"
            client = requests.session()

            response = client.get(url, timeout=2)
            if response.ok:
                url = "https://isrcsearch.ifpi.org/api/v1/search"
                data = {
                    "number": 1,
                    "searchFields": {
                        "artistName": artist,
                        "trackTitle": title,
                    },
                    "showReleases": 0,
                    "start": 0,
                }
                response = client.post(
                    url, json=data, timeout=2,
                    headers={
                        "x-csrftoken": client.cookies["csrftoken"],
                        "referer": "https://isrcsearch.ifpi.org/"
                    }
                )
                if response.ok:
                    docs = response.json().get("displayDocs", [])
                    if docs and len(docs) > 0:
                        track_info["isrc"] = docs[0].get("isrcCode")
                        # print(track_info["isrc"])

        # Use Musicbrainz for ISRC lookup
        if not track_info.get("isrc") and hasattr(settings, "MUSICBRAINZ_AGENT"):
            musicbrainzngs.set_useragent(settings.MUSICBRAINZ_AGENT, "0.1", settings.MUSICBRAINZ_AGENT_URL)
            query = {"query": q}
            if do_title_artist:
                query = {
                    "artist": artist,
                    "recording": title
                }
            try:
                result = musicbrainzngs.search_recordings(**query, strict=True)
            except:
                pass
            else:
                for mbr in result.get('recording-list', []):
                    score = int(mbr.get('ext:score', 0))
                    if score > 90:
                        isrc = mbr.get('isrc-list', [])
                        if isrc:
                            track_info['isrc'] = isrc[0]
                            break

        # Store into the cache if something was found
        if self.is_successful_search(track_info):
            track_info["q"] = q
            track_info["a"] = artist
            track_info["t"] = title
            track_info["cached"] = False
            track_info["key"] = key
            r.set(key, json.dumps(track_info), ex=settings.TRACK_INFO_EXPIRE_SECONDS)
        else:
            r.set(key, json.dumps(track_info), ex=settings.NOT_FOUND_INFO_EXPIRE_SECONDS)
        return Response(track_info)
