# Generated by Django 2.2.2 on 2019-10-04 21:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toolbox', '0008_auto_20191004_1017'),
    ]

    operations = [
        migrations.CreateModel(
            name='CharacterPayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('character_id', models.BigIntegerField()),
                ('character_name', models.CharField(max_length=500)),
                ('amount', models.DecimalField(decimal_places=2, default=None, max_digits=20, null=True)),
                ('date', models.DateTimeField()),
            ],
        ),
    ]
