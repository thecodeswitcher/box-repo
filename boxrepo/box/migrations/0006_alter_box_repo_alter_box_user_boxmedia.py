# Generated by Django 4.2.5 on 2023-09-28 16:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("box", "0005_box_box_description_box_box_name_box_created_at_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="box",
            name="repo",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="boxes",
                to="box.repo",
            ),
        ),
        migrations.AlterField(
            model_name="box",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="boxes",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.CreateModel(
            name="BoxMedia",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("file_name", models.TextField(default="")),
                (
                    "box",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="box.box",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
