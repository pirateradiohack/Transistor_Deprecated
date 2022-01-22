import logging

import feedparser
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from dateutil import parser
from django.conf import settings
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from podcasts.models import Episode, Feed

logger = logging.getLogger(__name__)


def save_new_episodes(feed):
    """Saves new episodes to the database.

    Checks the episode GUID against the episodes currently stored in the
    database. If not found, then a new `Episode` is added to the database.

    Args:
        feed: requires a Feed object
    """
    channel = feedparser.parse(feed.url)
    feed.save()
    entries = channel.entries[: feed.max_entries]
    for item in entries:
        if not Episode.objects.filter(link=item.link).exists():
            enclosures = item.enclosures
            audio = ""
            for enclosure in enclosures:
                if "audio" in enclosure.get("type"):
                    audio = enclosure.get("href")
            episode = Episode(
                title=item.title,
                pub_date=parser.parse(item.published),
                link=item.link,
                feed=feed,
                audio=audio,
            )
            episode.save()


def trim_old_episodes(feed):
    """Remove old episodes from a feed."""
    entries = Episode.objects.filter(feed=feed).order_by("-pub_date")
    if len(entries) > feed.max_entries:
        keep = entries[: feed.max_entries]
        Episode.objects.filter(feed=feed).exclude(
            pk__in=[item.id for item in keep]
        ).delete()


def update_feeds():
    """Update all feeds to their latest episodes."""
    feeds = Feed.objects.all()
    for feed in feeds:
        save_new_episodes(feed)
        trim_old_episodes(feed)


def delete_old_job_executions(max_age=604_800):
    """Deletes all apscheduler job execution logs older than `max_age`."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),  # Midnight on Monday, before start of the next work week.
            id="Delete Old Job Executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added weekly job: Delete Old Job Executions.")

        scheduler.add_job(
            update_feeds,
            trigger="interval",
            minutes=30,
            id="feed updater",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job: Feed Updater.")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
