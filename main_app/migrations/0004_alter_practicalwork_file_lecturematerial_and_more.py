# Generated by Django 5.0.6 on 2024-06-03 14:31

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0003_remove_course_teacher_course_teachers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='practicalwork',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='practical_works/'),
        ),
        migrations.CreateModel(
            name='LectureMaterial',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('file', models.FileField(blank=True, null=True, upload_to='lecture_materials/')),
                ('course', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main_app.course')),
            ],
            options={
                'db_table': 'lecture_materials',
            },
        ),
        migrations.CreateModel(
            name='PracticalWorkSubmission',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('file', models.FileField(blank=True, null=True, upload_to='practical_work_submissions/')),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('practical_work', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main_app.practicalwork')),
                ('student', models.ForeignKey(blank=True, limit_choices_to={'role': 'student'}, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'practical_work_submissions',
            },
        ),
    ]
