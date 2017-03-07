# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-07 02:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=200)),
                ('guardian_name', models.CharField(help_text="Enter the name of the child's guardian.", max_length=200)),
                ('child_name', models.CharField(help_text='Enter the name of the child that you are looking for a team.', max_length=200)),
                ('child_interest', models.TextField(help_text="Enter your child's interest and relevant experience.", max_length=1000)),
                ('school_district_name', models.CharField(help_text="Enter the name of your child's school district. Some school-based teams are restricted to children in the district.", max_length=200)),
                ('town_name', models.CharField(editable=False, max_length=200)),
                ('zip_code', models.PositiveSmallIntegerField(help_text='5 digit ZIP code of where you live.')),
                ('years_of_FIRST_experience', models.PositiveSmallIntegerField(default=0, help_text='Enter the number of seasons that your child has participated in FIRST programs.')),
                ('interested_in_jFLL', models.BooleanField(default=False, help_text='Select if your child is interested in joining a Junior FIRST Lego League (jFLL) team.')),
                ('interested_in_FLL', models.BooleanField(default=False, help_text='Select if your child is interested in joining an FIRST Lego League (FLL) team.')),
                ('interested_in_FTC', models.BooleanField(default=False, help_text='Select if your child is interested in joining an FIRST Tech Challenge (FTC) team.')),
                ('interested_in_FRC', models.BooleanField(default=False, help_text='Select if your child is interested in joining an FIRST Robotics Competition (FRC) team.')),
                ('first_update', models.DateField(auto_now_add=True)),
                ('last_update', models.DateField(auto_now=True)),
                ('update_count', models.PositiveIntegerField(editable=False)),
                ('looking_request_count', models.PositiveIntegerField(editable=False)),
                ('requested_count', models.PositiveIntegerField(editable=False)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_program', models.CharField(choices=[('-', '-'), ('J', 'jFLL'), ('L', 'FLL'), ('T', 'FTC'), ('R', 'FRC')], default='-', max_length=1)),
                ('username', models.CharField(max_length=200)),
                ('team_name', models.CharField(help_text='Enter the name of your team.', max_length=200)),
                ('team_number', models.IntegerField(blank=True, help_text='Enter the team of your team. Prospective teams, established jFLL, or established FLL teams can leave the field blank.', null=True)),
                ('school_district_name', models.CharField(blank=True, help_text='Enter the name of your school district if your team is restricted to members living in the district. Otherwise, leave the field blank.', max_length=200, null=True)),
                ('town_name', models.CharField(editable=False, max_length=200)),
                ('zip_code', models.PositiveSmallIntegerField(help_text='5 digit ZIP code of where you meet.')),
                ('year_founded', models.PositiveSmallIntegerField(blank=True, help_text='Enter the year that your team was founded. Leave field blank for prospective teams.', null=True)),
                ('description', models.TextField(help_text="Enter a brief team's description and include your team's objectives.", max_length=2000)),
                ('achievement', models.TextField(help_text='Describe your recent achievements.', max_length=1000)),
                ('web_site', models.URLField(blank=True, help_text='Enter the URL of your team online presence.', null=True)),
                ('looking_for_teammate', models.BooleanField(default=True, help_text='Select if you are actively looking for new teammates. Only then will you receive messages from prospective team members.')),
                ('prospective_teammate_profile', models.CharField(blank=True, help_text='Optional description of the profile of prospective teammates.', max_length=200, null=True)),
                ('looking_to_mentor_another_team', models.BooleanField(default=False, help_text='Select if you are interested in mentoring another team. Only then will you receive messages from prospective teams.')),
                ('prospective_team_profile', models.CharField(blank=True, help_text='Optional description of the profile of prospective teams that you are interested in mentoring.', max_length=200, null=True)),
                ('looking_for_mentorship', models.BooleanField(default=False, help_text='Select if you are interested being mentored by another team. Only then will you receive message from prospective expert teams.')),
                ('help_request', models.CharField(blank=True, help_text='Optional description of the expertise you would like to get help with.', max_length=200, null=True)),
                ('first_update', models.DateField(auto_now_add=True)),
                ('last_update', models.DateField(auto_now=True)),
                ('update_count', models.PositiveIntegerField(editable=False)),
                ('looking_request_count', models.PositiveIntegerField(editable=False)),
                ('requested_count', models.PositiveIntegerField(editable=False)),
            ],
        ),
    ]
