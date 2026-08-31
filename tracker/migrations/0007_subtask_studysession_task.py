from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("tracker", "0006_inventory_effects_activitylog")]
    operations = [
        migrations.AddField(model_name="studysession", name="task", field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name="study_sessions", to="tracker.task")),
        migrations.CreateModel(name="SubTask", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("title", models.CharField(max_length=180)),
            ("completed", models.BooleanField(default=False)),
            ("points_awarded", models.IntegerField(default=0)),
            ("completed_at", models.DateTimeField(blank=True, null=True)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
            ("task", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="subtasks", to="tracker.task")),
        ]),
    ]
