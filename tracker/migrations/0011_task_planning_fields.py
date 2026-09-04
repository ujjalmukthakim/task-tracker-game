from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("tracker", "0010_study_growth_tools")]

    operations = [
        migrations.AddField(model_name="task", name="category", field=models.CharField(blank=True, max_length=80)),
        migrations.AddField(model_name="task", name="importance", field=models.PositiveSmallIntegerField(default=50)),
        migrations.AddField(model_name="task", name="estimated_minutes", field=models.PositiveIntegerField(default=30)),
    ]
