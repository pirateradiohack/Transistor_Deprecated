from django.contrib import admin

from .models import Feed, Episode


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ("title", "subscribe_date")


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ("title", "get_feed_title", "pub_date")

    @admin.display(description='Feed Title', ordering='feed__title')
    def get_feed_title(self, obj):
        return obj.feed.title
