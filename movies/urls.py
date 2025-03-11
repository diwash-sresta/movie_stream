# from django.urls import path
# from . import views
# from .views import MovieListAPIView

# app_name = 'movies'

# urlpatterns = [
#     path('', views.home, name='home'),
#     path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
#     path('search/', views.search_movies, name='search'),
#     path('api/movies/', MovieListAPIView.as_view(), name='movie-list-api'),
#     path('mirzapur/', views.mirzapur_view, name='mirzapur'),
#     path('api/movies/mirzapur/', views.MirzapurAPIView.as_view(), name='mirzapur-api'),
#     path('three-idiots/', views.three_idiots_view, name='three_idiots'),
#     path('api/movies/three-idiots/', views.ThreeIdiotsAPIView.as_view(), name='three-idiots-api'),
# ]


from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    # Main Pages
    path('', views.home, name='home'),
    path('movies/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('tv/<int:tv_id>/', views.tv_detail, name='tv_detail'),
    path('search/', views.search, name='search'),
    
    # API endpoints for JavaScript usage
    path('api/movies/<str:list_type>/', views.get_movies_api, name='get_movies_api'),
]