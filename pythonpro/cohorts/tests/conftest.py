from os import path

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from model_bakery import baker

from pythonpro import settings
from pythonpro.cohorts.models import Cohort

img_path = path.join(settings.BASE_DIR, 'pythonpro', 'core', 'static', 'img', 'instructors', 'renzo-nuccitelli.jpeg')


@pytest.fixture
def cohort(client, django_user_model):
    user = baker.make(django_user_model)
    image = SimpleUploadedFile(name='renzo-nuccitelli.jpeg', content=open(img_path, 'rb').read(),
                               content_type='image/png')
    cohort = baker.make(Cohort, slug='guido-van-rossum', title='Guido van Rossum', students=[user], image=image)
    return cohort
