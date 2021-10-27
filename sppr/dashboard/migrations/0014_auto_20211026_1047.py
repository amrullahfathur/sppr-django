# Generated by Django 3.2.4 on 2021-10-26 03:47

from django.db import migrations
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0013_analisiskerangkalogis'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='analisiskerangkalogis',
            name='sasaran',
        ),
        migrations.RemoveField(
            model_name='analisiskerangkalogis',
            name='tujuan',
        ),
        migrations.AddField(
            model_name='analisiskerangkalogis',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='dashboard.analisiskerangkalogis'),
        ),
    ]
