from django.db import models

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
