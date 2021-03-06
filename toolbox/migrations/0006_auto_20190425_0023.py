# Generated by Django 2.1.7 on 2019-04-25 00:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toolbox', '0005_auto_20190419_0836'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='evenote',
            options={'permissions': (('view_basic_eve_notes', 'Can View own corps notes'), ('add_basic_eve_notes', 'Can Add own corp members to notes'), ('view_eve_notes', 'Can view all eve notes'), ('add_new_eve_notes', 'Can add new eve notes'), ('add_to_blacklist', 'Can add to Blacklist'), ('view_eve_blacklist', 'Can View the Blacklist'), ('view_restricted_eve_notes', 'Can View restricted eve notes'), ('view_ultra_restricted_eve_notes', 'Can View ultra_restricted eve notes'), ('add_restricted_eve_notes', 'Can Add restricted eve notes'), ('add_ultra_restricted_eve_notes', 'Can Add ultra_restricted eve notes'))},
        ),
        migrations.AlterModelOptions(
            name='evenotecomment',
            options={'permissions': (('view_eve_note_comments', 'Can view eve note comments'), ('add_new_eve_note_comments', 'Can add comments on eve notes'), ('view_eve_note_restricted_comments', 'Can view restricted eve note comments'), ('add_new_eve_note_restricted_comments', 'Can add new restricted comments to eve notes'), ('view_eve_note_ultra_restricted_comments', 'Can view ultra restricted eve note comments'), ('add_new_eve_note_ultra_restricted_comments', 'Can add new ultra restricted comments to eve notes'))},
        ),
        migrations.AddField(
            model_name='evenote',
            name='alliance_id',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='evenote',
            name='alliance_name',
            field=models.CharField(default=None, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='evenote',
            name='corporation_id',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='evenote',
            name='corporation_name',
            field=models.CharField(default=None, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='evenotecomment',
            name='ultra_restricted',
            field=models.BooleanField(default=False),
        ),
    ]
