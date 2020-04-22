def get_redirect_url(redirect):
    if redirect.links.exists():
        return redirect.links.order_by('?').first().url

    return redirect.url
