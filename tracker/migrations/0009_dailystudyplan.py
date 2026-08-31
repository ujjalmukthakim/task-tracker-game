from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("tracker", "0008_recalltopic_recallreview")]

    operations = [
        migrations.CreateModel(
            name="DailyStudyPlan",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField(unique=True)),
                ("intention", models.CharField(blank=True, max_length=220)),
                ("planned_minutes", models.PositiveIntegerField(default=60)),
                ("energy", models.PositiveIntegerField(default=3)),
                ("reflection", models.CharField(blank=True, max_length=420)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
