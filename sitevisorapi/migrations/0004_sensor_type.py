# Generated by Django 4.1.13 on 2024-03-23 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitevisorapi', '0003_alter_project_kafka_topics'),
    ]

    operations = [
        migrations.AddField(
            model_name='sensor',
            name='type',
            field=models.CharField(default='Temperature', max_length=255),
            preserve_default=False,
        ),
    ]