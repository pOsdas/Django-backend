# Generated by Django 5.2 on 2025-04-18 22:10

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AuthUser',
            fields=[
                ('user_id', models.AutoField(primary_key=True, serialize=False)),
                ('password', models.BinaryField()),
                ('refresh_token', models.TextField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
