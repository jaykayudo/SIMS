# Generated by Django 3.2 on 2023-08-14 16:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('admins', '0007_course_semester'),
    ]

    operations = [
        migrations.CreateModel(
            name='SchoolSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.CharField(max_length=10, unique=True)),
                ('current', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='DepartmentCourse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.IntegerField(choices=[(1, '100 Level'), (2, '200 Level'), (3, '300 Level'), (4, '400 Level'), (5, '500 Level'), (6, '600 Level')])),
                ('semester', models.IntegerField(choices=[(1, 'First Semester'), (2, 'Second Semester')])),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admins.department')),
            ],
        ),
        migrations.CreateModel(
            name='DeparmentCourseLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit', models.IntegerField()),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admins.course')),
            ],
        ),
        migrations.CreateModel(
            name='CourseRegistration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semester', models.IntegerField(choices=[(1, 'First Semester'), (2, 'Second Semester')])),
                ('level', models.IntegerField(choices=[(1, '100 Level'), (2, '200 Level'), (3, '300 Level'), (4, '400 Level'), (5, '500 Level'), (6, '600 Level')])),
                ('date_submitted', models.DateField(auto_now_add=True)),
                ('last_updated', models.DateField(auto_now=True)),
                ('courses', models.ManyToManyField(to='admins.Course')),
                ('session', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='admins.schoolsession')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admins.student')),
            ],
        ),
    ]
