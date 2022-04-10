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


def get_new_episodes():
    """Saves new episodes in all feeds to the database.

    Checks the episode's URL against the episodes currently stored in the
    database. If not found, then a new `Episode` is added to the database.

    When an episode is saved in the model, its corresponding audio file is
    downloaded and its path is stored in the database for use in further
    deletion.

    We save only episodes with audio enclosures.
    """
    feeds = Feed.objects.all()
    for feed in feeds:
        feed.save()  # update feed metadata in model
        episodes = feedparser.parse(feed.url).entries
        episodes = [episode for episode in episodes if
                    _is_audio_episode(episode)]
        episodes = episodes[: feed.max_entries]
        for episode in episodes:
            if not Episode.objects.filter(link=episode.link).exists():
                audio = ""
                for enclosure in episode.enclosures:
                    if "audio" in enclosure.get("type"):
                        audio = enclosure.get("href")
                episode_in_db = Episode(
                    title=episode.title,
                    pub_date=parser.parse(episode.published),
                    link=episode.link,
                    feed=feed,
                    audio=audio,
                )
                episode_in_db.save()


def _is_audio_episode(episode):
    """Return True when at least one of the enclosures is of type audio."""
    audio_enclosures = [enclosure for enclosure in episode.enclosures if
                        "audio" in enclosure.get("type")]
    return audio_enclosures != []


def trim_old_episodes():
    """Remove old episodes from a feed."""
    feeds = Feed.objects.all()
    for feed in feeds:
        episodes = Episode.objects.filter(feed=feed).order_by("-pub_date")
        if len(episodes) > feed.max_entries:
            keep = episodes[: feed.max_entries]
            Episode.objects.filter(feed=feed).exclude(
                pk__in=[item.id for item in keep]
            ).delete()


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
            get_new_episodes,
            trigger="interval",
            minutes=30,
            id="episode updater",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job: Episode Updater.")

        scheduler.add_job(
            trim_old_episodes,
            trigger="interval",
            minutes=90,
            id="episode deleter",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job: Episode Deleter.")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
