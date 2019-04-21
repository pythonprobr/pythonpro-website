from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, UpdateView
from django_sitemaps import Sitemap

from pythonpro.core.forms import UserEmailForm
from pythonpro.core.models import User
from pythonpro.promos.facade import find_all_videos


def index(request):
    return render(request, 'core/index.html', {})


def thanks(request):
    return render(request, 'core/lead_thanks.html', {})


def teck_talks(request):
    return render(request, 'core/tech_talks.html', {})


def podcast(request):
    return render(request, 'core/podcast.html', {})


@login_required
def profile(request):
    return render(request, 'core/profile_detail.html', {})


def sitemap(request):
    map = Sitemap(
        build_absolute_uri=request.build_absolute_uri,
    )

    for section in 'core:index core:podcast core:tech_talks modules:index'.split():
        map.add(reverse(section), changefreq='weekly')

    for video in find_all_videos():
        map.add(video.get_absolute_url(), changefreq='monthly')

    return map.response(
        pretty_print=settings.DEBUG,
    )


class _ProfileUpdateName(UpdateView):
    model = User
    fields = ('first_name',)
    template_name = 'core/profile_name.html'
    success_url = reverse_lazy('core:profile')

    def get_object(self, queryset=None):
        return self.request.user


profile_name = login_required(_ProfileUpdateName.as_view())


class _ProfileUpdateEmail(UpdateView):
    form_class = UserEmailForm
    template_name = 'core/profile_email.html'
    success_url = reverse_lazy('core:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


profile_email = login_required(_ProfileUpdateEmail.as_view())


class _ProfileChangePassword(PasswordChangeView):
    template_name = 'core/profile_password.html'
    success_url = reverse_lazy('core:index')


profile_password = _ProfileChangePassword.as_view()


class _WaitingListView(TemplateView):
    template_name = 'core/waiting_list.html'


waiting_list = _WaitingListView.as_view()
