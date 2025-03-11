from rest_framework import serializers
from .models import Movie

class MovieSerializer(serializers.ModelSerializer):
    poster_url = serializers.SerializerMethodField()
    banner_url = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = ['id', 'title', 'description', 'poster_url', 'banner_url']

    def get_poster_url(self, obj):
        if hasattr(obj, 'poster_path'):
            return f"https://image.tmdb.org/t/p/w500{obj.poster_path}"
        return obj.poster_url if hasattr(obj, 'poster_url') else None

    def get_banner_url(self, obj):
        if hasattr(obj, 'backdrop_path'):
            return f"https://image.tmdb.org/t/p/original{obj.backdrop_path}"
        return obj.banner_url if hasattr(obj, 'banner_url') else None
