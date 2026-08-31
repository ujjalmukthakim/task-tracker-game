from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard), path("tasks/", views.tasks),
    path("tasks/<int:task_id>/toggle/", views.toggle_task), path("tasks/<int:task_id>/", views.task_detail),
    path("tasks/<int:task_id>/subtasks/", views.subtasks), path("tasks/<int:task_id>/subtasks/<int:subtask_id>/", views.subtasks),
    path("profile/", views.profile_settings), path("timer/", views.timer), path("shop/", views.shop),
    path("distractions/", views.distractions),
    path("recall/", views.recall), path("recall/<int:topic_id>/review/", views.review_recall),
    path("study-plan/", views.study_plan),
    path("study-tools/", views.study_tools), path("resources/<int:resource_id>/", views.resource_detail),
]
