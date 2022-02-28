# Generated by Django 3.2.9 on 2021-12-16 07:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('incidents', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthLevel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='countyusers',
            name='auth_level',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.DO_NOTHING, to='incidents.authlevel'),
        ),
    ]
