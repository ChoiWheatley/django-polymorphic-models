"""
출처: [Abstract Base Classes](https://docs.djangoproject.com/en/5.0/topics/db/models/#abstract-base-classes)

여러 테이블에 걸쳐 공통된 컬럼이 필요한 경우, 파이썬의 클래스 상속 기능을 사용하면 됩니다. 이 경우 Meta 클래스에 `abstract = True` 프로퍼티를 추가해야 ORM이 추상 클래스를 테이블로 치환하지 않습니다.
"""

from django.db import models


class RelationA(models.Model):
    a = models.CharField(max_length=255)


class RelationB(models.Model):
    b = models.CharField(max_length=255)


class BaseModel(models.Model):
    title = models.CharField(max_length=255)
    content = models.CharField(max_length=255)

    class Meta:
        abstract = True


class ChildA(BaseModel):
    relation_a = models.ForeignKey(RelationA, on_delete=models.CASCADE)


class ChildB(BaseModel):
    relation_b = models.ForeignKey(RelationB, on_delete=models.CASCADE)
