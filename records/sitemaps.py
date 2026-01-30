from django.contrib.sitemaps import Sitemap
from .models import *

class RecordSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Book.objects.distinct().order_by('-id')

    def location(self, obj):
        return f"/record/{obj.id}"

    def lastmod(self, obj): 
        return obj.edit_date