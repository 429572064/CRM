# Generated by Django 2.1.1 on 2018-11-19 21:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0002_classstudyrecord_student_studentstudyrecord'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classstudyrecord',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='讲师'),
        ),
        migrations.AlterField(
            model_name='student',
            name='class_list',
            field=models.ManyToManyField(blank=True, related_name='student', to='employee.ClassList', verbose_name='已报班级'),
        ),
        migrations.AlterField(
            model_name='studentstudyrecord',
            name='score',
            field=models.IntegerField(choices=[(100, 'A+'), (90, 'A'), (85, 'B+'), (80, 'B'), (70, 'B-'), (60, 'C+'), (50, 'C'), (40, 'C-'), (0, ' D'), (-1, 'N/A'), (-100, 'COPY'), (-1000, 'FAIL')], default=-1, null=True, verbose_name='本节成绩'),
        ),
    ]
