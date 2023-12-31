# Generated by Django 4.2.7 on 2023-11-12 18:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0005_answerassign'),
    ]

    operations = [
        migrations.AddField(
            model_name='answerassign',
            name='player_choice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='answer_assign_player_choice_relationship', to='game.player'),
        ),
        migrations.AlterField(
            model_name='answerassign',
            name='related_answer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='answer_assign_answer_relationship', to='game.answer'),
        ),
        migrations.AlterField(
            model_name='answerassign',
            name='related_player',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='answer_assign_player_relationship', to='game.player'),
        ),
    ]
