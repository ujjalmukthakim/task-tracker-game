from django.db import models


class Profile(models.Model):
    name = models.CharField(max_length=60, default="Hero")
    points = models.IntegerField(default=0)
    lifetime_xp = models.IntegerField(default=0)
    tokens = models.PositiveIntegerField(default=0)
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
    category = models.CharField(max_length=80, blank=True)
    importance = models.PositiveSmallIntegerField(default=50)
    estimated_minutes = models.PositiveIntegerField(default=30)
    priority = models.CharField(max_length=12, choices=Priority.choices, default=Priority.NORMAL)
    is_daily = models.BooleanField(default=False)
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    token_selected_on = models.DateField(null=True, blank=True)


class Completion(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="completions")
    date = models.DateField()
    completed = models.BooleanField(default=False)
    points_awarded = models.IntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["task", "date"], name="unique_task_day")]


class SubTask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="subtasks")
    title = models.CharField(max_length=180)
    completed = models.BooleanField(default=False)
    points_awarded = models.IntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class StudySession(models.Model):
    task = models.ForeignKey(Task, null=True, blank=True, on_delete=models.SET_NULL, related_name="study_sessions")
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
    reward_tokens = models.PositiveIntegerField(default=1)
    penalty_xp = models.PositiveIntegerField(default=50)
    completed = models.BooleanField(default=False)
    punished = models.BooleanField(default=False)


class InventoryItem(models.Model):
    key = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=80)
    icon = models.CharField(max_length=12)
    description = models.CharField(max_length=160)
    cost = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=1)
    effect = models.CharField(max_length=40, blank=True)
    duration_minutes = models.PositiveIntegerField(default=0)
    active_until = models.DateTimeField(null=True, blank=True)
    purchased_at = models.DateTimeField(auto_now_add=True)


class ActivityLog(models.Model):
    """A small, player-facing ledger: every XP gain or loss has a reason."""
    created_at = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField()
    reason = models.CharField(max_length=220)
    kind = models.CharField(max_length=20, default="xp")


class RecallTopic(models.Model):
    """A note to revisit using a simple, confidence-based review schedule."""
    title = models.CharField(max_length=280)
    category = models.CharField(max_length=80, blank=True)
    learned_on = models.DateField()
    next_review_on = models.DateField()
    last_score = models.PositiveIntegerField(null=True, blank=True)
    review_count = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class RecallReview(models.Model):
    topic = models.ForeignKey(RecallTopic, on_delete=models.CASCADE, related_name="reviews")
    reviewed_on = models.DateField()
    score = models.PositiveIntegerField()
    next_review_on = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)


class DailyStudyPlan(models.Model):
    """A lightweight daily intention, separate from individual quests."""
    date = models.DateField(unique=True)
    intention = models.CharField(max_length=220, blank=True)
    planned_minutes = models.PositiveIntegerField(default=60)
    energy = models.PositiveIntegerField(default=3)
    reflection = models.CharField(max_length=420, blank=True)
    updated_at = models.DateTimeField(auto_now=True)


class StudySettings(models.Model):
    exam_name = models.CharField(max_length=100, blank=True)
    exam_date = models.DateField(null=True, blank=True)
    weekly_goal_minutes = models.PositiveIntegerField(default=300)


class DailyWellbeing(models.Model):
    date = models.DateField(unique=True)
    sleep_hours = models.DecimalField(max_digits=3, decimal_places=1, default=7)
    water_cups = models.PositiveIntegerField(default=0)
    movement_minutes = models.PositiveIntegerField(default=0)
    mood = models.PositiveIntegerField(default=3)
    updated_at = models.DateTimeField(auto_now=True)


class StudyResource(models.Model):
    title = models.CharField(max_length=160)
    url = models.URLField(blank=True)
    category = models.CharField(max_length=80, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class WeeklyReflection(models.Model):
    week_start = models.DateField(unique=True)
    win = models.CharField(max_length=320, blank=True)
    blocker = models.CharField(max_length=320, blank=True)
    next_focus = models.CharField(max_length=320, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
