# Generated by Django 5.2.1 on 2025-05-26 09:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('offers_app', '0007_alter_offer_created_at_alter_offer_description_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='offer',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, help_text='Timestamp when the offer was created.'),
        ),
        migrations.AlterField(
            model_name='offer',
            name='description',
            field=models.TextField(help_text='Detailed description of the offer.'),
        ),
        migrations.AlterField(
            model_name='offer',
            name='image',
            field=models.ImageField(blank=True, help_text='Optional image for the offer.', null=True, upload_to='offers/'),
        ),
        migrations.AlterField(
            model_name='offer',
            name='title',
            field=models.CharField(help_text='Title of the offer.', max_length=255),
        ),
        migrations.AlterField(
            model_name='offer',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, help_text='Timestamp of the last update of the offer.'),
        ),
        migrations.AlterField(
            model_name='offer',
            name='user',
            field=models.ForeignKey(help_text='The user who created this offer.', on_delete=django.db.models.deletion.CASCADE, related_name='offers', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='offerdetail',
            name='delivery_time_in_days',
            field=models.PositiveIntegerField(help_text='Delivery time in days for this variant.'),
        ),
        migrations.AlterField(
            model_name='offerdetail',
            name='features',
            field=models.JSONField(default=list, help_text='List of special features or characteristics of the offer.'),
        ),
        migrations.AlterField(
            model_name='offerdetail',
            name='offer',
            field=models.ForeignKey(help_text='The associated offer to which this detail belongs.', on_delete=django.db.models.deletion.CASCADE, related_name='details', to='offers_app.offer'),
        ),
        migrations.AlterField(
            model_name='offerdetail',
            name='offer_type',
            field=models.CharField(help_text='Type of the offer (e.g., Basic, Premium, etc.).', max_length=20),
        ),
        migrations.AlterField(
            model_name='offerdetail',
            name='price',
            field=models.DecimalField(decimal_places=2, help_text='Price of the offer variant.', max_digits=10),
        ),
        migrations.AlterField(
            model_name='offerdetail',
            name='revisions',
            field=models.IntegerField(help_text='Number of allowed revisions.'),
        ),
        migrations.AlterField(
            model_name='offerdetail',
            name='title',
            field=models.CharField(help_text='Title or name of the offer variant.', max_length=255),
        ),
    ]
