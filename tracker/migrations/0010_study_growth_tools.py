from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("tracker", "0009_dailystudyplan")]

    operations = [
        migrations.CreateModel(name="StudySettings", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("exam_name", models.CharField(blank=True, max_length=100)),
            ("exam_date", models.DateField(blank=True, null=True)),
            ("weekly_goal_minutes", models.PositiveIntegerField(default=300)),
        ]),
        migrations.CreateModel(name="DailyWellbeing", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("date", models.DateField(unique=True)), ("sleep_hours", models.DecimalField(decimal_places=1, default=7, max_digits=3)),
            ("water_cups", models.PositiveIntegerField(default=0)), ("movement_minutes", models.PositiveIntegerField(default=0)),
            ("mood", models.PositiveIntegerField(default=3)), ("updated_at", models.DateTimeField(auto_now=True)),
        ]),
        migrations.CreateModel(name="StudyResource", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("title", models.CharField(max_length=160)), ("url", models.URLField(blank=True)), ("category", models.CharField(blank=True, max_length=80)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
        ]),
        migrations.CreateModel(name="WeeklyReflection", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("week_start", models.DateField(unique=True)), ("win", models.CharField(blank=True, max_length=320)),
            ("blocker", models.CharField(blank=True, max_length=320)), ("next_focus", models.CharField(blank=True, max_length=320)),
            ("updated_at", models.DateTimeField(auto_now=True)),
        ]),
    ]
