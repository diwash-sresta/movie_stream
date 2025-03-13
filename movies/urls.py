from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    # Main Pages
    path('', views.home, name='home'),
    path('movies/', views.movies_list, name='movies_list'),
    path('movies/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('tv/', views.tv_shows_list, name='tv_shows_list'),
    path('tv/<int:tv_id>/', views.tv_detail, name='tv_detail'),
    path('tv/<int:tv_id>/season/<int:season_number>/', views.season_detail, name='season_detail'),
    path('search/', views.search, name='search'),
    path('movies/<int:movie_id>/similar/', views.similar_movies, name='similar_movies'),
    # path('signup/', views.signup, name='signup'),

    
    # API endpoints for JavaScript usage
    path('api/movies/<str:list_type>/', views.get_movies_api, name='get_movies_api'),
]