from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("tracker", "0007_subtask_studysession_task")]

    operations = [
        migrations.CreateModel(
            name="RecallTopic",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=280)),
                ("category", models.CharField(blank=True, max_length=80)),
                ("learned_on", models.DateField()),
                ("next_review_on", models.DateField()),
                ("last_score", models.PositiveIntegerField(blank=True, null=True)),
                ("review_count", models.PositiveIntegerField(default=0)),
                ("active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="RecallReview",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("reviewed_on", models.DateField()),
                ("score", models.PositiveIntegerField()),
                ("next_review_on", models.DateField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("topic", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reviews", to="tracker.recalltopic")),
            ],
        ),
    ]
