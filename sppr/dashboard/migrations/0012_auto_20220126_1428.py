# Generated by Django 3.2.4 on 2022-01-26 07:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0011_auto_20211221_0859'),
    ]

    operations = [
        migrations.AlterField(
            model_name='isustrategis',
            name='tahun',
            field=models.IntegerField(choices=[(2019, 2019), (2020, 2020), (2021, 2021), (2022, 2022), (2023, 2023), (2024, 2024), (2025, 2025), (2026, 2026)], default=2019),
        ),
        migrations.AlterField(
            model_name='tujuanlfa',
            name='tahun',
            field=models.IntegerField(choices=[(2019, 2019), (2020, 2020), (2021, 2021), (2022, 2022), (2023, 2023), (2024, 2024), (2025, 2025), (2026, 2026)], default=2019),
        ),
    ]
