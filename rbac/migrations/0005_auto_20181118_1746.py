# Generated by Django 2.1.1 on 2018-11-18 17:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rbac', '0004_auto_20181115_2139'),
    ]

    operations = [
        migrations.AddField(
            model_name='permission',
            name='name',
            field=models.CharField(default=1, max_length=32, verbose_name='url别名'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='permission',
            name='pid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='rbac.Permission', verbose_name='父权限'),
        ),
    ]