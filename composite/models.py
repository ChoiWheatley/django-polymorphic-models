from django.db import models


class RelationA(models.Model):
    a = models.CharField(max_length=255)


class RelationB(models.Model):
    b = models.CharField(max_length=255)


class Composite(models.Model):
    title = models.CharField(max_length=255)
    content = models.CharField(max_length=255)
    relation_a = models.ForeignKey(RelationA, null=True, on_delete=models.CASCADE)
    relation_b = models.ForeignKey(RelationB, null=True, on_delete=models.CASCADE)
