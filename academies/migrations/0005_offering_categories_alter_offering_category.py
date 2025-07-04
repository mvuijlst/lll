# Generated by Django 5.2.3 on 2025-06-22 18:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academies', '0004_category_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='offering',
            name='categories',
            field=models.ManyToManyField(blank=True, related_name='offerings', to='academies.category'),
        ),
        migrations.AlterField(
            model_name='offering',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='single_category_offerings', to='academies.category'),
        ),
    ]
