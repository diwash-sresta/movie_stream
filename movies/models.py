from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    google_profile_picture = models.URLField(max_length=500, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

# Signal to create a Profile when a User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# Signal to save the Profile when the User is saved
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    poster_url = models.URLField(max_length=500)
    banner_url = models.URLField(max_length=500)
    tmdb_id = models.IntegerField(unique=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True)
    release_date = models.DateField(null=True)
    runtime = models.IntegerField(null=True)
    budget = models.BigIntegerField(null=True)
    revenue = models.BigIntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

class WatchlistItem(models.Model):
    MEDIA_TYPES = (
        ('movie', 'Movie'),
        ('tv', 'TV Show'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist_items')
    item_id = models.IntegerField()  # TMDB ID
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    title = models.CharField(max_length=255)
    poster_path = models.CharField(max_length=255, null=True, blank=True)
    vote_average = models.FloatField(null=True, blank=True)
    release_date = models.CharField(max_length=10, null=True, blank=True)  # YYYY-MM-DD format
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'item_id', 'media_type')
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.user.username}'s {self.media_type}: {self.title}"