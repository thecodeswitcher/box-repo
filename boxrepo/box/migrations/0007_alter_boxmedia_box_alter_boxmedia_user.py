# Generated by Django 4.2.5 on 2023-10-02 14:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("box", "0006_alter_box_repo_alter_box_user_boxmedia"),
    ]

    operations = [
        migrations.AlterField(
            model_name="boxmedia",
            name="box",
            field=models.ForeignKey(
                default=None, on_delete=django.db.models.deletion.CASCADE, to="box.box"
            ),
        ),
        migrations.AlterField(
            model_name="boxmedia",
            name="user",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
