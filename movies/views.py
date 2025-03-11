from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator

import requests
from requests.exceptions import RequestException
import logging

logger = logging.getLogger(__name__)

# Base TMDB API configuration
TMDB_API_KEY = getattr(settings, 'TMDB_API_KEY', '')
TMDB_BASE_URL = 'https://api.themoviedb.org/3'

def get_tmdb_data(endpoint, params=None):
    """Helper function to fetch data from TMDB API"""
    if params is None:
        params = {}
    
    params['api_key'] = TMDB_API_KEY
    params.setdefault('language', 'en-US')
    
    url = f"{TMDB_BASE_URL}/{endpoint}"
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        logger.error(f"TMDB API error: {e}")
        return None

def get_movie_trailer(videos_data):
    """Extract the official trailer from videos data"""
    if not videos_data or 'results' not in videos_data:
        return None
    
    # First priority: Find videos with type 'Trailer' and name containing 'Official'
    official_trailers = [
        video for video in videos_data['results']
        if video.get('site') == 'YouTube' and
        video.get('type') == 'Trailer' and
        'official' in video.get('name', '').lower()
    ]
    
    if official_trailers:
        return official_trailers[0]['key']
    
    # Second priority: Any video with type 'Trailer'
    trailers = [
        video for video in videos_data['results']
        if video.get('site') == 'YouTube' and
        video.get('type') == 'Trailer'
    ]
    
    if trailers:
        return trailers[0]['key']
    
    # Third priority: Any video with type 'Teaser'
    teasers = [
        video for video in videos_data['results']
        if video.get('site') == 'YouTube' and
        video.get('type') == 'Teaser'
    ]
    
    if teasers:
        return teasers[0]['key']
    
    # Last resort: Just take the first YouTube video if available
    youtube_videos = [
        video for video in videos_data['results']
        if video.get('site') == 'YouTube'
    ]
    
    if youtube_videos:
        return youtube_videos[0]['key']
    
    return None

def home(request):
    """View for the home page"""
    context = {
        'trending_movies': [],
        'popular_movies': [],
        'top_rated_movies': [],
        'upcoming_movies': []
    }
    
    # Try to fetch trending movies
    trending_data = get_tmdb_data('trending/movie/week')
    if trending_data and 'results' in trending_data:
        context['trending_movies'] = trending_data['results'][:10]
    
    # Try to fetch popular movies
    popular_data = get_tmdb_data('movie/popular')
    if popular_data and 'results' in popular_data:
        context['popular_movies'] = popular_data['results'][:10]
    
    # Try to fetch top rated movies
    top_rated_data = get_tmdb_data('movie/top_rated')
    if top_rated_data and 'results' in top_rated_data:
        context['top_rated_movies'] = top_rated_data['results'][:10]
    
    # Try to fetch upcoming movies
    upcoming_data = get_tmdb_data('movie/upcoming')
    if upcoming_data and 'results' in upcoming_data:
        context['upcoming_movies'] = upcoming_data['results'][:10]
    
    return render(request, 'movies/home.html', context)

def movie_detail(request, movie_id):
    """View for movie detail page"""
    # Fetch basic movie details
    movie_data = get_tmdb_data(f'movie/{movie_id}')
    if not movie_data:
        return render(request, 'movies/movie_detail.html', {
            'error_message': 'Unable to fetch movie details. Please try again later.'
        })
    
    # Fetch additional movie data 
    credits = get_tmdb_data(f'movie/{movie_id}/credits')
    videos = get_tmdb_data(f'movie/{movie_id}/videos')
    similar = get_tmdb_data(f'movie/{movie_id}/similar')
    
    # Add additional data to movie object
    if credits:
        movie_data['credits'] = credits
    if videos:
        movie_data['videos'] = videos
    
    # Get trailer key for the Play Trailer button
    trailer_key = None
    if videos:
        trailer_key = get_movie_trailer(videos)
    
    context = {
        'movie': movie_data,
        'similar_movies': similar.get('results', []) if similar else [],
        'trailer_key': trailer_key
    }
    
    return render(request, 'movies/movie_detail.html', context)

def search(request):
    """View for search results"""
    query = request.GET.get('q', '')
    page = request.GET.get('page', 1)
    
    if not query:
        return render(request, 'movies/search.html', {'query': '', 'results': []})
    
    # Fetch search results from TMDB API
    search_data = get_tmdb_data('search/multi', {
        'query': query,
        'page': page,
        'include_adult': 'false'
    })
    
    results = []
    if search_data and 'results' in search_data:
        results = search_data['results']
    
    # Set up pagination
    paginator = Paginator(results, 20)  # 20 results per page
    page_obj = paginator.get_page(page)
    
    context = {
        'query': query,
        'results': page_obj,
        'page_obj': page_obj,
        'paginator': paginator
    }
    
    return render(request, 'movies/search.html', context)

def tv_detail(request, tv_id):
    """View for TV show detail page"""
    # Implementation similar to movie_detail but for TV shows
    tv_data = get_tmdb_data(f'tv/{tv_id}')
    if not tv_data:
        return render(request, 'movies/tv_detail.html', {
            'error_message': 'Unable to fetch TV show details. Please try again later.'
        })
    
    # Fetch additional data
    credits = get_tmdb_data(f'tv/{tv_id}/credits')
    videos = get_tmdb_data(f'tv/{tv_id}/videos')
    similar = get_tmdb_data(f'tv/{tv_id}/similar')
    
    if credits:
        tv_data['credits'] = credits
    if videos:
        tv_data['videos'] = videos
    
    # Get trailer key for TV show
    trailer_key = None
    if videos:
        trailer_key = get_movie_trailer(videos)  # Reuse the same function for TV trailers
    
    context = {
        'show': tv_data,
        'similar_shows': similar.get('results', []) if similar else [],
        'trailer_key': trailer_key
    }
    
    return render(request, 'movies/tv_detail.html', context)

@require_http_methods(["GET"])
def get_movies_api(request, list_type):
    """API endpoint to fetch movies for front-end use"""
    valid_types = ['trending', 'popular', 'top_rated', 'upcoming']
    
    if list_type not in valid_types:
        return JsonResponse({'error': 'Invalid list type'}, status=400)
    
    # Map the requested type to the appropriate TMDB endpoint
    endpoint_map = {
        'trending': 'trending/movie/week',
        'popular': 'movie/popular',
        'top_rated': 'movie/top_rated',
        'upcoming': 'movie/upcoming'
    }
    
    data = get_tmdb_data(endpoint_map[list_type])
    
    if not data:
        return JsonResponse({'error': 'Failed to fetch data from TMDB'}, status=503)
    
    return JsonResponse(data)