from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import spotipy
from spotipy.cache_handler import CacheFileHandler
import sys
from spotipy.oauth2 import SpotifyClientCredentials
from django.conf import settings

class MusicAPI(APIView):

    authentication_classes = ()
    permission_classes = ()

    def get(self, request):
        q = request.query_params.get("q")
        if not q:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        track_info = {}
        client_credentials_manager = SpotifyClientCredentials(
            settings.SPOTIFY_CLIENT_ID,
            settings.SPOTIFY_CLIENT_SECRET,
            cache_handler=CacheFileHandler(cache_path="/tmp/spotify_token")
        )
        spotify = spotipy.Spotify(
            client_credentials_manager=client_credentials_manager,
            requests_timeout=2
        )
        try:
            results = spotify.search(
                q=q,
                limit=1,
                type='track'
            )
        except Exception as e:
            print(e)
            pass

        if results and results['tracks']['items']:
            track = results['tracks']['items'][0]
            ext_ids = track.get('external_ids', {})
            track_info['isrc'] = ext_ids.get('isrc', None)
            album = track.get('album', {})
            if album.get('images', []) and len(album['images']) >= 3:
                track_info['small_image'] = album['images'][-1]['url']
                track_info['medium_image'] = album['images'][-2]['url']
                track_info['large_image'] = album['images'][-3]['url']

        return Response(track_info)
