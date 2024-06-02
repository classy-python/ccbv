import pytest
from django.core.management import call_command
from django.views.generic import UpdateView

from cbv.models import Klass

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

    def test_real(self) -> None:
        """
        Test the MRO of a real class hierarchy, taken from the Django's UpdateView.
        """
        # The version of Django that we are using for this test is 3.1
        # because that is the version we have in our dependencies when we run tests.
        # If this fails in future, it is probably because the version of Django
        # has been updated and the MRO of the UpdateView has changed.
        # In that case, feel free to update the version we're loading here.
        call_command("loaddata", "3.1.json")

        mro = Klass.objects.get(name="UpdateView").get_all_ancestors()

        # For the sake of comparison, we convert the Klass objects to a tuple of strings,
        # where the first element is the module name and the second is the class name.
        mro_strings = [(k.module.name, k.name) for k in mro]

        # The first element is the class itself, so we skip it.
        # The last element is object, so we skip it.
        real_ancestors = UpdateView.__mro__[1:][:-1]

        assert mro_strings == [(c.__module__, c.__name__) for c in real_ancestors]
