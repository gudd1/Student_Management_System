# Generated by Django 3.2.5 on 2021-08-18 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Student_Management_Sytem_app', '0003_alter_students_course_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('myList', models.TextField(null=True)),
            ],
        ),
    ]
