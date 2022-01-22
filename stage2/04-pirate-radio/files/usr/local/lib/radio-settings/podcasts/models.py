import shutil
from pathlib import Path

import feedparser
import requests
from content_aggregator.settings import PODCASTS_PATH
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.text import slugify


class Feed(models.Model):
    title = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    subscribe_date = models.DateTimeField(auto_now_add=True)
    url = models.URLField()
    link = models.URLField(blank=True)
    max_entries = models.PositiveSmallIntegerField(
        default=3, verbose_name="Number of episodes to keep"
    )
    image = models.URLField(blank=True)
    fs_path = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.title}"

    def save(self, *args, **kwargs):
        channel = feedparser.parse(self.url)
        self.title = channel.feed.get("title", "No Title")
        self.description = channel.feed.get("description", "No Description")
        self.link = channel.feed.get("link")
        self.image = channel.feed.get("image").get("href")
        self.slug = slugify(self.title)
        self.fs_path = PODCASTS_PATH + "/" + self.slug
        super(Feed, self).save(*args, **kwargs)


@receiver(post_delete, sender=Feed)
def _delete_feed_fs_path(sender, instance, **kwargs):
    shutil.rmtree(instance.fs_path, ignore_errors=True)


class Episode(models.Model):
    title = models.CharField(max_length=200)
    pub_date = models.DateTimeField()
    link = models.URLField()
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    audio = models.URLField(blank=True)
    local_filename = models.CharField(max_length=255, blank=True)

    def download_file(self, url):
        Path(self.feed.fs_path).mkdir(parents=True, exist_ok=True)
        filetype = '.' + url.split('.')[-1]
        pub_date = self.pub_date.strftime("%Y-%m-%d")
        self.local_filename = pub_date + "-" + slugify(self.title) + filetype
        destination = self.feed.fs_path + "/" + self.local_filename
        with requests.get(url, stream=True) as r:
            with open(destination, "wb") as f:
                shutil.copyfileobj(r.raw, f)

    def __str__(self) -> str:
        return f"{self.feed.title}: {self.title}"

    def save(self, *args, **kwargs):
        if self.audio != "":
            self.download_file(self.audio)
        super(Episode, self).save(*args, **kwargs)


@receiver(post_delete, sender=Episode)
def _delete_episode_fs_path(sender, instance, **kwargs):
    audio_file = Path(instance.feed.fs_path + '/' + instance.local_filename)
    try:
        audio_file.unlink()
    except FileNotFoundError:
        pass
