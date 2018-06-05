from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.
from django.urls import reverse


class Cohort(models.Model):
    title = models.CharField(max_length=50)
    slug = models.SlugField()
    image = models.ImageField(upload_to='cohorts/')
    quote = models.TextField()
    mail_list = models.URLField()
    forum_post = models.URLField()
    start = models.DateField()
    end = models.DateField()
    students = models.ManyToManyField(get_user_model(), through='CohortStudent')

    def get_absolute_url(self):
        return reverse('cohorts:detail', kwargs={'slug': self.slug})


class CohortStudent(models.Model):
    cohort = models.ForeignKey(Cohort, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING)


class LiveClass(models.Model):
    start = models.DateTimeField()
    vimeo_id = models.CharField(max_length=11, db_index=False, blank=True)
    cohort = models.ForeignKey(Cohort, models.CASCADE)


class Webinar(models.Model):
    cohort = models.ForeignKey(Cohort, on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=50)
    speaker = models.CharField(max_length=50)
    speaker_title = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    vimeo_id = models.CharField(max_length=11, db_index=False, blank=True)
    start = models.DateTimeField()
