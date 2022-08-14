import pytest

from .factories import InheritanceFactory, KlassFactory


@pytest.mark.django_db
class TestKlassAncestorMRO:
    def test_linear(self) -> None:
        """
        Test a linear configuration of classes. C inherits from B which
        inherits from A.

        A
        |
        B
        |
        C

        C.__mro__ would be [C, B, A].
        """
        a = KlassFactory.create(name="a")
        b = KlassFactory.create(name="b")
        c = KlassFactory.create(name="c")
        InheritanceFactory.create(parent=a, child=b)
        InheritanceFactory.create(parent=b, child=c)

        mro = c.get_all_ancestors()

        assert mro == [b, a]

    def test_diamond(self) -> None:
        r"""
        Test a diamond configuration of classes. This example has A as a parent
        of B and C, and D has B and C as parents.

          A
         / \
        B   C
         \ /
          D

        D.__mro__ would be [D, B, C, A].
        """
        a = KlassFactory.create(name="a")
        b = KlassFactory.create(name="b")
        c = KlassFactory.create(name="c")
        d = KlassFactory.create(name="d")
        InheritanceFactory.create(parent=a, child=b)
        InheritanceFactory.create(parent=a, child=c)
        InheritanceFactory.create(parent=b, child=d)
        InheritanceFactory.create(parent=c, child=d, order=2)

        mro = d.get_all_ancestors()

        assert mro == [b, c, a]
