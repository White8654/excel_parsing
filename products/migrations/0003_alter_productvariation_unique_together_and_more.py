# Generated by Django 4.1.13 on 2024-09-03 20:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_alter_productvariation_last_updated_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='productvariation',
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name='productvariation',
            name='last_updated',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='productvariation',
            name='variation_text',
            field=models.CharField(max_length=100),
        ),
    ]
