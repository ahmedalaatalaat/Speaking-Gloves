from django.db import models

# Create your models here.

class AnnotatedImage(models.Model):
    image = models.ImageField(upload_to='annotated_images/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"AnnotatedImage {self.id} - {self.created_at}"