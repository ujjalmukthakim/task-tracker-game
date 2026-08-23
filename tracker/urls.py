from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard), path("tasks/", views.tasks),
    path("tasks/<int:task_id>/toggle/", views.toggle_task), path("tasks/<int:task_id>/", views.task_detail),
    path("profile/", views.profile_settings), path("timer/", views.timer), path("shop/", views.shop),
    path("distractions/", views.distractions),
]
