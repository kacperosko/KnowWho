# Generated by Django 4.1 on 2023-12-26 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0016_alter_question_global_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='global_key',
            field=models.CharField(max_length=64, null=True, unique=True),
        ),
    ]