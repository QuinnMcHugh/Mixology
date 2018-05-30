# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.conf import settings


class Direction(models.Model):
    id = models.IntegerField(primary_key=True)
    instruction = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'direction'


class Drink(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'drink'


class Ingredient(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ingredient'


class Serving(models.Model):
    id = models.IntegerField(primary_key=True)
    measurement = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'serving'


class Recipe(models.Model):
    id = models.IntegerField(primary_key=True)
    steporder = models.IntegerField()
    drink = models.IntegerField()
    ingredient = models.IntegerField()
    serving = models.IntegerField()
    direction = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'recipe'


class Favorite(models.Model):
    drink = models.ForeignKey(Drink, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


class MyBar(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)

