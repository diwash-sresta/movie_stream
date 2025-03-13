from django.shortcuts import render,redirect, get_object_or_404
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.shortcuts import render
import json

import requests
from requests.exceptions import RequestException
import logging
# from django.contrib.auth import login
# from .models import  Profile
# from django.contrib.auth.models import User
# from urllib.parse import urlencode
# from .forms import CustomSignUpForm 


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
    def get_movies(endpoint):
        data = get_tmdb_data(endpoint)
        return data['results'][:10] if data and 'results' in data else []

    context = {
        # Existing server-rendered data
        'trending_movies': get_movies('trending/movie/week'),
        'popular_movies': get_movies('movie/popular'),
        'top_rated_movies': get_movies('movie/top_rated'),
        'upcoming_movies': get_movies('movie/upcoming'),
        
        # JSON data for client-side filtering
        'movies_json': json.dumps({
            'trending': get_movies('trending/movie/week'),
            'popular': get_movies('movie/popular'),
            'topRated': get_movies('movie/top_rated'),
            'upcoming': get_movies('movie/upcoming')
        })
    }
    return render(request, 'movies/home.html', context)

def movies_list(request):
    """View for movies listing page"""
    page = request.GET.get('page', 1)
    category = request.GET.get('category', 'popular')
    
    # Map frontend categories to TMDB endpoints
    endpoint_map = {
        'popular': 'movie/popular',
        'top_rated': 'movie/top_rated',
        'upcoming': 'movie/upcoming',
        'now_playing': 'movie/now_playing',
    }
    
    endpoint = endpoint_map.get(category, 'movie/popular')
    
    # Fetch movies data from TMDB
    data = get_tmdb_data(endpoint, {'page': page})
    
    if not data:
        return render(request, 'movies/movies_list.html', {
            'error_message': 'Unable to fetch movies. Please try again later.'
        })
    
    # Set up pagination
    results = data.get('results', [])
    total_pages = data.get('total_pages', 1)
    current_page = data.get('page', 1)
    
    context = {
        'movies': results,
        'category': category,
        'categories': [
            {'id': 'popular', 'name': 'Popular'},
            {'id': 'top_rated', 'name': 'Top Rated'},
            {'id': 'upcoming', 'name': 'Upcoming'},
            {'id': 'now_playing', 'name': 'Now Playing'},
        ],
        'current_page': current_page,
        'total_pages': min(total_pages, 500),  # TMDB API limits to 500 pages
        'page_range': range(max(1, current_page - 2), min(total_pages + 1, current_page + 3)),
    }
    
    return render(request, 'movies/movies_list.html', context)

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

def tv_shows_list(request):
    """View for TV shows listing page"""
    page = request.GET.get('page', 1)
    category = request.GET.get('category', 'popular')
    
    # Map frontend categories to TMDB endpoints
    endpoint_map = {
        'popular': 'tv/popular',
        'top_rated': 'tv/top_rated',
        'on_the_air': 'tv/on_the_air',
        'airing_today': 'tv/airing_today',
    }
    
    endpoint = endpoint_map.get(category, 'tv/popular')
    
    # Fetch TV shows data from TMDB
    data = get_tmdb_data(endpoint, {'page': page})
    
    if not data:
        return render(request, 'movies/tv_shows_list.html', {
            'error_message': 'Unable to fetch TV shows. Please try again later.'
        })
    
    # Set up pagination
    results = data.get('results', [])
    total_pages = data.get('total_pages', 1)
    current_page = data.get('page', 1)
    
    context = {
        'shows': results,
        'category': category,
        'categories': [
            {'id': 'popular', 'name': 'Popular'},
            {'id': 'top_rated', 'name': 'Top Rated'},
            {'id': 'on_the_air', 'name': 'On The Air'},
            {'id': 'airing_today', 'name': 'Airing Today'},
        ],
        'current_page': current_page,
        'total_pages': min(total_pages, 500),  # TMDB API limits to 500 pages
        'page_range': range(max(1, current_page - 2), min(total_pages + 1, current_page + 3)),
    }
    
    return render(request, 'movies/tv_shows_list.html', context)

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

def season_detail(request, tv_id, season_number):
    """View for a specific TV season"""
    season_data = get_tmdb_data(f'tv/{tv_id}/season/{season_number}')
    
    if not season_data:
        return render(request, 'movies/season_detail.html', {
            'error_message': 'Unable to fetch season details. Please try again later.'
        })
    
    context = {
        'season': season_data,
        'tv_id': tv_id,
    }
    
    return render(request, 'movies/season_detail.html', context)

def search(request):
    """View for search results"""
    query = request.GET.get('q', '').strip()
    page = request.GET.get('page', 1)
    
    if not query:
        return render(request, 'movies/search.html', {
            'query': '',
            'results': [],
            'error_message': None
        })
    
    try:
        # Search for movies, TV shows, and people
        search_data = get_tmdb_data('search/multi', {
            'query': query,
            'page': page,
            'include_adult': 'false'
        })
        
        if not search_data:
            raise Exception('Failed to fetch search results')

        # Get results and make sure they have a media_type
        results = search_data.get('results', [])
        
        # Set up pagination
        paginator = Paginator(results, 20)  # 20 results per page
        page_obj = paginator.get_page(page)
        
        context = {
            'query': query,
            'results': page_obj,
            'page_obj': page_obj,
            'paginator': paginator,
            'total_results': search_data.get('total_results', 0)
        }
        
        return render(request, 'movies/search.html', context)
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return render(request, 'movies/search.html', {
            'query': query,
            'results': [],
            'error_message': 'An error occurred while searching. Please try again.'
        })
    
def similar_movies(request, movie_id):
    """View for displaying similar movies"""
    try:
        # Get similar movies from TMDB API
        similar_data = get_tmdb_data(f'movie/{movie_id}/similar')
        
        if not similar_data:
            raise Exception('Failed to fetch similar movies')
        
        # Get the original movie details for context
        movie_data = get_tmdb_data(f'movie/{movie_id}')
        
        if not movie_data:
            raise Exception('Failed to fetch movie details')
        
        # Set up pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(similar_data.get('results', []), 20)  # 20 movies per page
        similar_movies = paginator.get_page(page)
        
        context = {
            'movie': movie_data,
            'similar_movies': similar_movies,
            'page_obj': similar_movies,
            'total_results': similar_data.get('total_results', 0)
        }
        
        return render(request, 'movies/similar_movies.html', context)
        
    except Exception as e:
        logger.error(f"Error fetching similar movies: {str(e)}")
        return render(request, 'movies/similar_movies.html', {
            'error_message': 'Unable to fetch similar movies. Please try again later.'
        })

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

# def signup(request):
#     if request.method == 'POST':
#         form = CustomSignUpForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             messages.success(request, 'Welcome to Expense Tracker!')
#             return redirect('trackense:expense_list')
#     else:
#         form = CustomSignUpForm()
#     return render(request, 'registration/signup.html', {'form': form})

# def google_login(request):
#     """Redirect users to Google's OAuth consent screen."""
#     params = {
#         'client_id': settings.GOOGLE_CLIENT_ID,
#         'redirect_uri': settings.GOOGLE_REDIRECT_URI,
#         'response_type': 'code',
#         'scope': 'openid email profile',
#         'access_type': 'offline',
#         'prompt': 'select_account',
#     }
#     auth_url = f"{settings.GOOGLE_AUTH_URL}?{urlencode(params)}"
#     return redirect(auth_url)

# def google_callback(request):
#     """Handle the callback from Google OAuth."""
#     code = request.GET.get('code')
#     if not code:
#         return redirect('login')  # Redirect to login if no code is provided

#     # Exchange the authorization code for an access token
#     token_data = {
#         'code': code,
#         'client_id': settings.GOOGLE_CLIENT_ID,
#         'client_secret': settings.GOOGLE_CLIENT_SECRET,
#         'redirect_uri': settings.GOOGLE_REDIRECT_URI,
#         'grant_type': 'authorization_code',
#     }
#     response = requests.post(settings.GOOGLE_TOKEN_URL, data=token_data)
#     if response.status_code != 200:
#         return redirect('login')  # Handle error

#     access_token = response.json().get('access_token')

#     # Fetch user info using the access token
#     user_info_response = requests.get(settings.GOOGLE_USER_INFO_URL, headers={
#         'Authorization': f'Bearer {access_token}'
#     })
#     if user_info_response.status_code != 200:
#         return redirect('login')  # Handle error

#     user_info = user_info_response.json()
#     email = user_info.get('email')
#     first_name = user_info.get('given_name', '')
#     last_name = user_info.get('family_name', '')
#     google_profile_picture = user_info.get('picture', '')  # Get the Google profile picture URL

#     # Create or get the user
#     user, created = User.objects.get_or_create(
#         username=email,
#         defaults={'email': email, 'first_name': first_name, 'last_name': last_name}
#     )

#     # Update or create the user's profile with the Google profile picture
#     profile, profile_created = Profile.objects.get_or_create(user=user)
#     profile.google_profile_picture = google_profile_picture
#     profile.save()

#     # Log the user in with the specified backend
#     login(request, user, backend='django.contrib.auth.backends.ModelBackend')
#     return redirect('trackense:dashboard') 
