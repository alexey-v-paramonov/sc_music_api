import redis

from django.core.management.base import BaseCommand

class Command(BaseCommand):

    def handle(self, *args, **options):
        r = redis.Redis(host="localhost", port=6379, db=0)
        stats_total_requests = int(r.get('stats_total_requests'))
        stats_cached_responses = int(r.get('stats_cached_responses'))
        cached_responses_percent = round(float(stats_cached_responses) / float(stats_total_requests) * 100., 2)
        print('\n\n')
        print(f'Total requests: {stats_total_requests}')
        print(f'Cached responses: {stats_cached_responses}')
        print(f'Percent of cached reponses: {cached_responses_percent}%')

        stats_spotify_requests = int(r.get('stats_spotify_requests'))
        stats_spotify_found = int(r.get('stats_spotify_found'))
        stats_spotify_errors = int(r.get('stats_spotify_errors')) if r.get('stats_spotify_errors') is not None else 0
        print('\n[Spotify]')
        print(f'Total requests: {stats_spotify_requests}')
        print(f'Found: {stats_spotify_found}')
        print(f'Failed: {stats_spotify_errors}')

        stats_apple_requests = int(r.get('stats_apple_requests'))
        stats_apple_found = int(r.get('stats_apple_found'))
        stats_apple_errors = int(r.get('stats_apple_errors')) if r.get('stats_apple_errors') is not None else 0
        print('\n[Apple]')
        print(f'Total requests: {stats_apple_requests}')
        print(f'Found: {stats_apple_found}')
        print(f'Failed: {stats_apple_errors}')

        stats_lastfm_requests = int(r.get('stats_lastfm_requests'))
        stats_lastfm_found = int(r.get('stats_lastfm_found'))
        stats_lastfm_errors = int(r.get('stats_lastfm_errors')) if r.get('stats_lastfm_errors') is not None else 0
        print('\n[lastfm]')
        print(f'Total requests: {stats_lastfm_requests}')
        print(f'Found: {stats_lastfm_found}')
        print(f'Failed: {stats_lastfm_errors}')

        stats_soundexchange_requests = int(r.get('stats_soundexchange_requests'))
        stats_soundexchange_found = int(r.get('stats_soundexchange_found'))
        stats_soundexchange_errors = int(r.get('stats_soundexchange_errors')) if r.get('stats_soundexchange_errors') is not None else 0
        print('\n[soundexchange]')
        print(f'Total requests: {stats_soundexchange_requests}')
        print(f'Found: {stats_soundexchange_found}')
        print(f'Failed: {stats_soundexchange_errors}')

        stats_musicbrainz_requests = int(r.get('stats_musicbrainz_requests'))
        stats_musicbrainz_found = int(r.get('stats_musicbrainz_found'))
        stats_musicbrainz_errors = int(r.get('stats_musicbrainz_errors')) if r.get('stats_musicbrainz_errors') is not None else 0
        print('\n[musicbrainz]')
        print(f'Total requests: {stats_musicbrainz_requests}')
        print(f'Found: {stats_musicbrainz_found}')
        print(f'Failed: {stats_musicbrainz_errors}')
