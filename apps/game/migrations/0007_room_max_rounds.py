# Generated by Django 4.2.7 on 2023-11-14 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0006_answerassign_player_choice_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='max_rounds',
            field=models.IntegerField(default=1),
        ),
    ]