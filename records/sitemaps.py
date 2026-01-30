from django.contrib.sitemaps import Sitemap
from .models import Book
from accounts.models import Team

class RecordSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        pub_teams = Team.objects.filter(public=True).distinct()
        pub_items = Book.objects.filter(team__in=pub_teams).distinct()
        return pub_items

    def location(self, obj):
        return f"/record/{obj.id}"

    def lastmod(self, obj): 
        return obj.edit_date