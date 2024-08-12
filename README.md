# django-polymorphic-models

장고 모델을 다형적으로 만드는 방법을 실험하는 POC 코드들의 모음집!

## 상속을 활용한 방식 [Inheritance](./inheritance/)

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

아래는 마이그레이션한 이후 테이블 컬럼을 보여주는 예시입니다:

![alt text](<static/Screenshot 2024-08-12 at 23.14.24.png>)

![alt text](<static/Screenshot 2024-08-12 at 23.14.37.png>)

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

## 여러 FK 중 하나만 사용하는 방식 [Composite](./composite/)

이번엔 상속이 아닌, 컴포지트(합성) 관계로 엮인 두 릴레이션을 가지고 실험해보겠습니다.

`Composite` 모델에서 볼 수 있듯, `relation_a`와 `relation_b` 두 FK가 nullable
한 것을 알 수 있습니다. 따라서 `RelationA` 모델도 여러개의 `Composite`를 가질 수 있으며,
`RelationB` 모델도 여러개의 `Composite`를 가질 수 있음을 의미합니다. 하지만 동시에 두 FK를
가질 수는 없겠죠. 코드에서 ORM이 `RelationX` 인스턴스가 올바르게 연관 `Composite` 로우를
참조하는지 여부를 살펴봅시다.

```python
class RelationA(models.Model):
    a = models.CharField(max_length=255)


class RelationB(models.Model):
    b = models.CharField(max_length=255)


class Composite(models.Model):
    title = models.CharField(max_length=255)
    content = models.CharField(max_length=255)
    relation_a = models.ForeignKey(RelationA, null=True, on_delete=models.CASCADE)
    relation_b = models.ForeignKey(RelationB, null=True, on_delete=models.CASCADE)
```

아래는 마이그레이션 후 컬럼 결과를 스크린 캡쳐한 것입니다:

![alt text](<static/Screenshot 2024-08-12 at 23.27.01.png>)

아래 코드를 통해 `RelationA`, `RelationB`와 각각 연관된 `Composite` 로우들을 몇개 만들어봅시다.
반복문과 프린트 결과를 통해 `relation_a` 인스턴스, `relation_b` 인스턴스별로 올바르게 조인이 되는
모습을 확인할 수 있습니다.

```python
>>> from composite.models import *
>>> relation_a = RelationA(a="relation a")
>>> relation_a.save()
>>> relation_b = RelationB(b="relation b")
>>> relation_b.save()
>>> composite_a = Composite(title="composite", content="composite content", relation_a=relation_a)
>>> composite_a.save()
>>> relation_a.composite_set.all()
<QuerySet [<Composite: Composite object (1)>]>
>>> relation_a.composite_set.create(
...     title="another title",
...     content="another content"
... )
<Composite: Composite object (2)>
>>> composite_b = Composite(title="composite b", content="content b", relation_b=relation_b)
>>> composite_b.save()
>>> relation_b.composite_set.all()
<QuerySet [<Composite: Composite object (3)>]>
>>> for each in relation_a.composite_set.all():
...     print(f"title: {each.title}, content: {each.content}")
...
title: composite, content: composite content
title: another title, content: another content
>>> for each in relation_b.composite_set.all():
...     print(f"title: {each.title}, content: {each.content}")
...
title: composite b, content: content b
>>> relation_b.composite_set.create(
...     title="another b",
...     content="another b"
... )
<Composite: Composite object (4)>
>>> for each in relation_b.composite_set.all():
...     print(f"title: {each.title}, content: {each.content}")
...
title: composite b, content: content b
title: another b, content: another b
```

다음은 임의로 새 `RelationB` 인스턴스와 `Composite` 리스트를 만들어 연관시킨 뒤에
올바르게 쿼리하는지 여부를 검사하는지 파악해보기 위한 코드입니다. 분명 Composite 테이블에
relation_a도 있고 relation_b도 섞여있는데 relation_b 그중에서 본인의 id인 로우들만
조인해서 가져오는 모습을 볼 수 있습니다.

```python
>>> relation_b2 = RelationB(b="new b")
>>> relation_b2.save()
>>> relation_b2.composite_set.create(title="title b2", content="content b2")
<Composite: Composite object (5)>
>>> relation_b2.composite_set.create(title="title b2", content="content b2")
<Composite: Composite object (6)>
>>> relation_b2.composite_set.create(title="another title b2", content="another content b2")
<Composite: Composite object (7)>
>>> del relation_b2
>>> relation_b2 = RelationB.objects.get(id=2)
>>> for each in relation_b2.composite_set.all():
...     print(f"title: {each.title}, content: {each.content}")
...
title: title b2, content: content b2
title: title b2, content: content b2
title: another title b2, content: another content b2
```

아래는 `Composite` 모델에 해당하는 테이블의 전체 데이터를 가져온 결과입니다.

![alt text](<static/Screenshot 2024-08-13 at 00.18.19.png>)

## 결론

타입에 따라 FK를 다르게 가져가야 하는 경우에 상속을 활용한 다중 테이블과 nullable한
여러 릴레이션을 가지는 하나의 테이블 두 가지 방법 모두 가능합니다.

클래스 다이어그램으로 나타낸다면 아래의 도식과 같이 나타낼 수 있습니다.

![alt text](<static/scan - 3.jpg>)

### 상속을 사용했을때 장점과 단점

**장점:**

- **명확한 분리:** 각 `Child` 모델은 특정한 연관 관계에 대한 명확한 정의를 가지며, 이는 데이터 무결성을 보장하고, 모델의 목적이 명확합니다.
- **유연성:** 각 테이블은 고유의 추가 필드를 가질 수 있으며, 각 연관 관계에 맞춤화된 로직을 추가할 수 있습니다.
- **데이터 무결성:** 각 모델은 자신에게 필요한 연관 관계만을 강제하므로, 잘못된 참조를 방지할 수 있습니다.

**단점:**

- **테이블 증가:** 각 연관 관계마다 별도의 테이블이 필요하여 테이블의 수가 증가합니다.
- **복잡성:** 여러 테이블을 관리해야 하므로 관리 포인트가 늘어날 수 있습니다.

### 여러 FK를 각각의 컬럼으로 사용하고 그중 하나만 사용하는 방식의 장점과 단점

**장점:**

- **단순화된 구조:** 모든 연관 관계가 단일 테이블에 저장되므로, 데이터베이스 구조가 단순해지고 관리가 용이합니다.
- **확장성:** 새롭게 연관될 테이블이 추가될 경우 기존 구조를 유지하면서 손쉽게 새로운 외래 키를 추가할 수 있습니다.

**단점:**

- **데이터 무결성 문제:** 두 외래 키 중 하나만 사용되어야 한다는 논리를 데이터베이스가 강제하지 않기 때문에, 잘못된 참조가 저장될 위험이 있습니다. 이는 어플리케이션 레벨에서 추가적인 검증을 필요로 합니다.
- **유연성 부족:** 각 연관 관계에 대한 커스텀 로직이나 추가 필드를 가지기 어렵습니다.
