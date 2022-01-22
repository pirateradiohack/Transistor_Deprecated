from django.urls import path

from .views import HomePageView, CreatePodcastView, DeletePodcastView, UpdatePodcastView

urlpatterns = [
    path("new_podcast", CreatePodcastView.as_view(), name="new_podcast"),
    path("", HomePageView.as_view(), name="homepage"),
    path("<pk>/update_podcast", UpdatePodcastView.as_view(), name="update_podcast"),
    path("<pk>/delete_podcast", DeletePodcastView.as_view(), name="delete_podcast"),
]
