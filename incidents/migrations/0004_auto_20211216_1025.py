# Generated by Django 3.2.9 on 2021-12-16 07:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('incidents', '0003_alter_authlevel_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='countyusers',
            name='auth_level',
        ),
        migrations.AlterField(
            model_name='authlevel',
            name='name',
            field=models.CharField(max_length=50, unique=True),
        ),
    ]
