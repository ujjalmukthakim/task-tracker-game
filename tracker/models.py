from django.db import models


class Profile(models.Model):
    name = models.CharField(max_length=60, default="Hero")
    points = models.IntegerField(default=0)
    lifetime_xp = models.IntegerField(default=0)
    daily_focus_goal = models.PositiveIntegerField(default=120)
    longest_streak = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)


class Task(models.Model):
    class Priority(models.TextChoices):
        LOW = "low", "Easy · 10 XP"
        NORMAL = "normal", "Important · 25 XP"
        HIGH = "high", "Very important · 50 XP"
        LEGENDARY = "legendary", "Legendary · 100 XP"
    title = models.CharField(max_length=180)
    description = models.CharField(max_length=360, blank=True)
    priority = models.CharField(max_length=12, choices=Priority.choices, default=Priority.NORMAL)
    is_daily = models.BooleanField(default=False)
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)


class Completion(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="completions")
    date = models.DateField()
    completed = models.BooleanField(default=False)
    points_awarded = models.IntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["task", "date"], name="unique_task_day")]


class StudySession(models.Model):
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(default=0)
    points_awarded = models.IntegerField(default=0)
    reflection = models.CharField(max_length=280, blank=True)


class Distraction(models.Model):
    text = models.CharField(max_length=180)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)


class DailyMission(models.Model):
    date = models.DateField(unique=True)
    study_minutes = models.PositiveIntegerField(default=60)
    easy_target = models.PositiveIntegerField(default=1)
    legendary_target = models.PositiveIntegerField(default=0)
    reward_xp = models.PositiveIntegerField(default=80)
    penalty_xp = models.PositiveIntegerField(default=50)
    completed = models.BooleanField(default=False)
    punished = models.BooleanField(default=False)


class InventoryItem(models.Model):
    key = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=80)
    icon = models.CharField(max_length=12)
    description = models.CharField(max_length=160)
    cost = models.PositiveIntegerField()
    purchased_at = models.DateTimeField(auto_now_add=True)
