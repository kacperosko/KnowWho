# Generated by Django 4.2.7 on 2023-11-14 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0007_room_max_rounds'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='max_rounds',
            field=models.IntegerField(default=5),
        ),
    ]
