from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("tracker", "0011_task_planning_fields")]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="tokens",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="task",
            name="token_selected_on",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="dailymission",
            name="reward_tokens",
            field=models.PositiveIntegerField(default=1),
        ),
    ]
