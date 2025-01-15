from django.db import models

# Create your models here.
class StaticMedia(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='static/')
    
    def __str__(self):
        return self.name