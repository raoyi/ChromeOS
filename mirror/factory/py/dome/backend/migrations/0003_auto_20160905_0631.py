# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-05 06:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

  dependencies = [('backend', '0002_auto_20160904_1245'),]

  operations = [
      migrations.RemoveField(
          model_name='board',
          name='url',),
      migrations.AddField(
          model_name='board',
          name='host',
          field=models.CharField(
              default=b'localhost', max_length=200),),
      migrations.AddField(
          model_name='board',
          name='port',
          field=models.PositiveIntegerField(default=8080),),
  ]
