# django-polymorphic-models

장고 모델을 다형적으로 만드는 방법을 실험하는 POC 코드들의 모음집!

## [Inheritance](./inheritance/)

상속을 사용하기 위해선 부모 클래스에 `abstract = True`를 포함한 `Meta` 클래스를 추가해야 합니다.
이 옵션을 부여하면 Django ORM이 추상 클래스로 간주하여 테이블을 생성하지 않습니다.

```python
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
```

아래는 상속받은 자식 모델이 연관테이블을 사용하는 사례를 보여줍니다.

```python
>>> from inheritance.models import *
>>> relation_a = RelationA(a="relation a")
>>> relation_b = RelationB(b="relation b")
>>> child_a = ChildA(relation_a=relation_a, title="child a", content="content")
>>> relation_a.save()
>>> relation_b.save()
>>> child_a.save()
>>> relation_a.childa_set.all()
<QuerySet [<ChildA: ChildA object (1)>]>
>>> relation_a.childa_set.create(
...     title="another a",
...     content="another content"
... )
<ChildA: ChildA object (2)>
>>> for childa in relation_a.childa_set.all():
...     print(f"title: {childa.title}, content: {childa.content}")
...
title: child a, content: content
title: another a, content: another content
```
