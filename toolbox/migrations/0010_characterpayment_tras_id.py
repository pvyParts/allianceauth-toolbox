# Generated by Django 2.2.2 on 2019-10-04 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toolbox', '0009_characterpayment'),
    ]

    operations = [
        migrations.AddField(
            model_name='characterpayment',
            name='tras_id',
            field=models.BigIntegerField(default=0),
            preserve_default=False,
        ),
    ]