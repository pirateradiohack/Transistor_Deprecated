import os
from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy

from .models import Feed


class CreatePodcastView(CreateView):
    model = Feed
    fields = ['url', 'max_entries']
    success_url = reverse_lazy("homepage")


class HomePageView(ListView):
    template_name = "homepage.html"
    model = Feed

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["feeds"] = Feed.objects.filter().order_by("-subscribe_date")
        statvfs = os.statvfs('/')
        free = statvfs.f_frsize * statvfs.f_bavail
        total = statvfs.f_frsize * statvfs.f_blocks
        free_space = free / total * 100
        free_space = float("{:.2f}".format(free_space))
        context["free_space"] = free_space
        return context


class UpdatePodcastView(UpdateView):
    model = Feed
    fields = ['max_entries']
    success_url = reverse_lazy("homepage")


class DeletePodcastView(DeleteView):
    model = Feed
    success_url = reverse_lazy("homepage")
