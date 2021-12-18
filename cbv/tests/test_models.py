from django.test import TestCase

from .factories import InheritanceFactory


class KlassAncestorMROTest(TestCase):
    def test_linear(self):
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
        b_child_of_a = InheritanceFactory.create(child__name="b", parent__name="a")
        a = b_child_of_a.parent
        b = b_child_of_a.child
        c = InheritanceFactory.create(parent=b, child__name="c").child

        mro = c.get_all_ancestors()
        self.assertSequenceEqual(mro, [b, a])

    def test_diamond(self):
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
        b_child_of_a = InheritanceFactory.create(child__name="b", parent__name="a")
        a = b_child_of_a.parent
        b = b_child_of_a.child

        c = InheritanceFactory.create(parent=a, child__name="c").child
        d = InheritanceFactory.create(parent=b, child__name="d").child
        InheritanceFactory.create(parent=c, child=d, order=2)

        mro = d.get_all_ancestors()
        self.assertSequenceEqual(mro, [b, c, a])
