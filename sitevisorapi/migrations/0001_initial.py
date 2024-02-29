# Generated by Django 4.1.13 on 2024-02-29 11:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Point',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x', models.FloatField()),
                ('y', models.FloatField()),
                ('z', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Sensor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('level', models.IntegerField()),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sitevisorapi.point')),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('level', models.IntegerField()),
                ('color', models.IntegerField()),
                ('opacity', models.FloatField()),
                ('height', models.FloatField(default=3)),
                ('point1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='room_point1', to='sitevisorapi.point')),
                ('point2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='room_point2', to='sitevisorapi.point')),
            ],
        ),
    ]
