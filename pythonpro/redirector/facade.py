def _count_access_in_link(link):
    link.total_access += 1
    link.save()


def get_redirect_url(redirect):
    if redirect.links.exists():
        link = redirect.links.order_by('total_access', 'id').first()
        _count_access_in_link(link)
        return link.url

    return redirect.url
