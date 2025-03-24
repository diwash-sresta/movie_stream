from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

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
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('watchlist/', views.watchlist_view, name='watchlist'),
    path('tubi/', views.tubi_movies, name='tubi_movies'),
    path('api/tv/<str:list_type>/', views.get_tv_shows_api, name='get_tv_shows_api'),


    # Password Reset URLs
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='movies/accounts/password_reset_form.html',
             email_template_name='movies/accounts/password_reset_email.html',
             subject_template_name='movies/accounts/password_reset_subject.txt'
         ),
         name='password_reset'),
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='movies/accounts/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='movies/accounts/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='movies/accounts/password_reset_complete.html'
         ),
         name='password_reset_complete'),


    
    # API endpoints for JavaScript usage
    path('api/movies/<str:list_type>/', views.get_movies_api, name='get_movies_api'),
    path('api/watchlist/add/', views.add_to_watchlist, name='add_to_watchlist'),
    path('api/watchlist/remove/', views.remove_from_watchlist, name='remove_from_watchlist'),

    
]