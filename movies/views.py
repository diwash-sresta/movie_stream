from django.shortcuts import render
import requests
from django.conf import settings
from django.core.paginator import Paginator
from rest_framework import generics
from rest_framework.response import Response
from .serializers import MovieSerializer
from .models import Movie
import logging

logger = logging.getLogger(__name__)

TMDB_BASE_URL = 'https://api.themoviedb.org/3'

def get_tmdb_data(endpoint, params=None):
    try:
        api_key = settings.TMDB_API_KEY
        if not api_key:
            logger.error("TMDB API key is not configured")
            return {'results': []}
            
        url = f"{TMDB_BASE_URL}/{endpoint}"
        default_params = {'api_key': api_key, 'language': 'en-US'}
        if params:
            default_params.update(params)
        
        response = requests.get(url, params=default_params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"TMDB API request failed: {e}")
        return {'results': []}
    except Exception as e:
        logger.error(f"Error in TMDB request: {e}")
        return {'results': []}

def home(request):
    try:
        trending = get_tmdb_data('trending/movie/week')
        popular = get_tmdb_data('movie/popular')
        context = {
            'trending_movies': trending.get('results', [])[:12],
            'popular_movies': popular.get('results', [])[:12]
        }
    except Exception as e:
        print(f"Error in home view: {e}")
        context = {
            'trending_movies': [],
            'popular_movies': [],
            'error_message': 'Unable to fetch movies at this time.'
        }
    return render(request, 'movies/home.html', context)

def movie_detail(request, movie_id):
    movie = get_tmdb_data(f'movie/{movie_id}')
    videos = get_tmdb_data(f'movie/{movie_id}/videos')
    similar = get_tmdb_data(f'movie/{movie_id}/similar')
    context = {
        'movie': movie,
        'videos': videos['results'],
        'similar_movies': similar['results'][:6]
    }
    return render(request, 'movies/movie_detail.html', context)

def search_movies(request):
    query = request.GET.get('q', '')
    if query:
        results = get_tmdb_data('search/movie', {'query': query})
        movies = results['results']
    else:
        movies = []
    return render(request, 'movies/search.html', {'movies': movies, 'query': query})

def mirzapur_view(request):
    return render(request, 'movies/mirzapur.html')

def three_idiots_view(request):
    return render(request, 'movies/three_idiots.html')

class MirzapurAPIView(generics.RetrieveAPIView):
    serializer_class = MovieSerializer

    def retrieve(self, request, *args, **kwargs):
        mirzapur_data = {
            'id': 1,
            'title': 'Mirzapur',
            'description': 'A shocking incident at a wedding procession ignites a series of events entangling the lives of two families in the lawless city of Mirzapur.',
            'poster_url': 'https://www.themoviedb.org/t/p/w500/kSkZ3hcRZmDRJwRcGXNXrBEzZFS.jpg',
            'banner_url': 'https://www.themoviedb.org/t/p/original/6zrsTJ8sYvkHOWpH6RyuyCN3hFy.jpg',
            'rating': 8.4,
            'release_year': 2018,
            'seasons': 2,
            'episodes': [
                {
                    'title': 'Episode 1: Rules',
                    'description': 'The story begins in Mirzapur...',
                    'duration': '45m'
                },
                # Add more episodes...
            ],
            'cast': [
                {
                    'name': 'Pankaj Tripathi',
                    'character': 'Kaleen Bhaiya',
                    'image': 'https://www.themoviedb.org/t/p/w138_and_h175_face/afHWUZqHwUcPYvzcTxJWM6JqDXK.jpg'
                },
                # Add more cast members...
            ]
        }
        return Response(mirzapur_data)

class ThreeIdiotsAPIView(generics.RetrieveAPIView):
    serializer_class = MovieSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            # Verify API key first
            if not settings.TMDB_API_KEY:
                raise ValueError("TMDB API key is not configured")

            movie_id = 20453  # TMDB ID for 3 Idiots
            try:
                # Fetch main movie details
                movie = get_tmdb_data(f'movie/{movie_id}')
                # Fetch cast and crew
                credits = get_tmdb_data(f'movie/{movie_id}/credits')
                # Fetch videos and images
                videos = get_tmdb_data(f'movie/{movie_id}/videos')
                images = get_tmdb_data(f'movie/{movie_id}/images')

                data = {
                    'id': movie.get('id'),
                    'title': movie.get('title'),
                    'tagline': movie.get('tagline'),
                    'overview': movie.get('overview'),
                    'release_date': movie.get('release_date'),
                    'runtime': f"{movie.get('runtime')} min",
                    'certification': 'UA',
                    'rating': movie.get('vote_average'),
                    'banner_url': f"https://image.tmdb.org/t/p/original{movie.get('backdrop_path')}",
                    'poster_url': f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}",
                    'genres': [genre['name'] for genre in movie.get('genres', [])],
                    'status': movie.get('status'),
                    'original_language': movie.get('original_language'),
                    'keywords': [keyword['name'] for keyword in movie.get('keywords', {}).get('keywords', [])],
                    'cast': [
                        {
                            'name': person['name'],
                            'character': person['character'],
                            'image': f"https://image.tmdb.org/t/p/w185{person['profile_path']}" if person['profile_path'] else None
                        }
                        for person in credits.get('cast', [])[:10]  # Get top 10 cast members
                    ],
                    'crew': [
                        {
                            'name': person['name'],
                            'job': person['job'],
                            'department': person['department']
                        }
                        for person in credits.get('crew', [])
                        if person['job'] in ['Director', 'Screenplay', 'Story', 'Writer']
                    ],
                    'videos': [
                        {
                            'key': video['key'],
                            'name': video['name'],
                            'type': video['type']
                        }
                        for video in videos.get('results', [])
                        if video['site'] == 'YouTube'
                    ],
                    'images': {
                        'backdrops': [
                            f"https://image.tmdb.org/t/p/original{img['file_path']}"
                            for img in images.get('backdrops', [])[:5]
                        ],
                        'posters': [
                            f"https://image.tmdb.org/t/p/w500{img['file_path']}"
                            for img in images.get('posters', [])[:5]
                        ]
                    }
                }
                return Response(data)
            except Exception as e:
                print(f"Error fetching movie details: {e}")
                return Response({'error': 'Failed to fetch movie details'}, status=500)
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            return Response(
                {'error': str(e)}, 
                status=500
            )
        except Exception as e:
            logger.error(f"Error fetching movie details: {e}")
            return Response(
                {'error': 'Failed to fetch movie details'}, 
                status=500
            )

class MovieListAPIView(generics.ListAPIView):
    serializer_class = MovieSerializer
    
    def get_queryset(self):
        trending = get_tmdb_data('trending/movie/week')
        movies = []
        for movie in trending.get('results', []):
            movies.append({
                'id': movie['id'],
                'title': movie['title'],
                'description': movie.get('overview', ''),
                'poster_url': f"https://image.tmdb.org/t/p/w500{movie.get('poster_path', '')}",
                'banner_url': f"https://image.tmdb.org/t/p/original{movie.get('backdrop_path', '')}"
            })
        return movies

    def list(self, request, *args, **kwargs):
        try:
            movies = self.get_queryset()
            return Response(movies)
        except Exception as e:
            print(f"Error fetching movies: {e}")
            return Response([])