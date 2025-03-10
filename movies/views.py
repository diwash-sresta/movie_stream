from django.shortcuts import render
import requests
from django.conf import settings
from django.core.paginator import Paginator
from rest_framework import generics
from rest_framework.response import Response
from .serializers import MovieSerializer
from .models import Movie

TMDB_API_KEY = 'API_KEY'  # Replace with your actual TMDB API key
TMDB_BASE_URL = 'https://api.themoviedb.org/3'

def get_tmdb_data(endpoint, params=None):
    try:
        url = f"{TMDB_BASE_URL}/{endpoint}"
        default_params = {'api_key': TMDB_API_KEY, 'language': 'en-US'}
        if params:
            default_params.update(params)
        response = requests.get(url, params=default_params)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except (requests.RequestException, ValueError) as e:
        print(f"Error fetching data from TMDB: {e}")
        return {'results': []}  # Return empty results on error

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

class MovieListAPIView(generics.ListAPIView):
    serializer_class = MovieSerializer
    
    def get_queryset(self):
        trending = get_tmdb_data('trending/movie/week')
        movies = []
        for movie in trending.get('results', []):
            movies.append({
                'id': movie['id'],
                'title': movie['title'],
                'description': movie['overview'],
                'poster_url': f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"
            })
        return movies

    def list(self, request, *args, **kwargs):
        movies = self.get_queryset()
        return Response(movies)