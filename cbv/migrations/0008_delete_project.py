# Generated by Django 3.1.14 on 2022-12-29 13:57

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("cbv", "0007_remove_project_fk"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Project",
        ),
    ]
