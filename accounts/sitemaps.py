from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):

    priority = 1.0
    changefreq = 'yearly'

    def items(self):
        return ['records:index', 'accounts:contact', 'accounts:about', 'accounts:terms', 'accounts:policy', 'accounts:signup', 'accounts:login']

    def location(self, item):
        return reverse(item)
