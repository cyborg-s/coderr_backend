# Generated by Django 5.2.1 on 2025-05-20 09:20

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews_app', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name='review',
            old_name='comment',
            new_name='description',
        ),
        migrations.RemoveField(
            model_name='review',
            name='product_name',
        ),
        migrations.RemoveField(
            model_name='review',
            name='user_name',
        ),
        migrations.AddField(
            model_name='review',
            name='business_user',
            field=models.ForeignKey(default='1', on_delete=django.db.models.deletion.CASCADE, related_name='received_reviews', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='review',
            name='reviewer',
            field=models.ForeignKey(default='1', on_delete=django.db.models.deletion.CASCADE, related_name='written_reviews', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='review',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
