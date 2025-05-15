from django.db import models

class Review(models.Model):
    rating = models.IntegerField()
    comment = models.TextField()
    product_name = models.CharField(max_length=255)
    user_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review of {self.product_name} by {self.user_name} - {self.rating} stars"