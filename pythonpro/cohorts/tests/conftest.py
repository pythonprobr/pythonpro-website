from datetime import datetime, timedelta
from os import path

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from model_mommy import mommy

from pythonpro import settings
from pythonpro.cohorts.models import Cohort, Webinar

img_path = path.join(settings.BASE_DIR, 'pythonpro', 'core', 'static', 'img', 'instructors', 'renzo-nuccitelli.png')


@pytest.fixture
def cohort(client, django_user_model):
    user = mommy.make(django_user_model)
    image = SimpleUploadedFile(name='renzo-nuccitelli.png', content=open(img_path, 'rb').read(),
                               content_type='image/png')
    cohort = mommy.make(Cohort, slug='guido-van-rossum', title='Guido van Rossum', students=[user], image=image)
    return cohort


@pytest.fixture
def webinars(cohort):
    now = datetime.utcnow()
    image = SimpleUploadedFile(name='renzo-nuccitelli.png', content=open(img_path, 'rb').read(),
                               content_type='image/png')
    return [
        mommy.make(Webinar, cohort=cohort, vimeo_id=str(i), image=image, start=now + timedelta(days=i)) for i in
        range(100, 105)
    ]
