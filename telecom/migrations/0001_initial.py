# Generated by Django 2.1.3 on 2018-11-23 05:44

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(default='', max_length=20)),
                ('password', models.CharField(default='', max_length=20)),
                ('encryptPassword', models.CharField(default='', max_length=50)),
                ('icc_id', models.CharField(default='', max_length=40)),
                ('user', models.CharField(default='', max_length=40)),
                ('net', models.CharField(default='', max_length=100)),
                ('remark', models.CharField(default='', max_length=100)),
                ('sort', models.IntegerField(default=None, null=True)),
                ('update', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
