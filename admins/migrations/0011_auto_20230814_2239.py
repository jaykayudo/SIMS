# Generated by Django 3.2 on 2023-08-14 21:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admins', '0010_auto_20230814_2210'),
    ]

    operations = [
        migrations.AddField(
            model_name='departmentcourse',
            name='max_unit',
            field=models.IntegerField(default=25),
        ),
        migrations.AddField(
            model_name='departmentcourse',
            name='min_unit',
            field=models.IntegerField(default=15),
        ),
    ]
