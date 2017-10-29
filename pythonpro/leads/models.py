from django.db import models


class Lead(models.Model):
    """Class representing leads, e.g. people interested on courses"""
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    creation = models.DateTimeField(auto_now_add=True)
