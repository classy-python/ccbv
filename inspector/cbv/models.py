from django.db import models


class Project(models.Model):
    """ Represents a project in a python project hierarchy """

    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('project-detail', (), {
            'package': self.name,
        })


class ProjectVersion(models.Model):
    """ Represents a particular varsion of a project in a python project hierarchy """

    project = models.ForeignKey(Project)
    version_number = models.CharField(max_length=200)

    class Meta:
        unique_together = ('project', 'version_number')

    def __unicode__(self):
        return self.project.name + " " + self.version_number

    @models.permalink
    def get_absolute_url(self):
        return ('version-detail', (), {
            'package': self.project.name,
            'version': self.version_number,
        })


class Module(models.Model):
    """ Represents a module of a python project """

    project_version = models.ForeignKey(ProjectVersion)
    name = models.CharField(max_length=200)
    parent = models.ForeignKey('self', blank=True, null=True)
    docstring = models.TextField(blank=True, default='')

    class Meta:
        unique_together = ('project_version', 'name')

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('module-detail', (), {
            'package': self.project_version.project.name,
            'version': self.project_version.version_number,
            'module': self.name,
        })


# TODO: quite a few of the methods on here should probably be denormed.
class Klass(models.Model):
    """ Represents a class in a module of a python project hierarchy """

    module = models.ForeignKey(Module)
    name = models.CharField(max_length=200)
    docstring = models.TextField(blank=True, default='')

    class Meta:
        unique_together = ('module', 'name')

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('klass-detail', (), {
            'package': self.module.project_version.project.name,
            'version': self.module.project_version.version_number,
            'module': self.module.name,
            'klass': self.name
        })

    def get_ancestors(self):
        if not hasattr(self, '_ancestors'):
            self._ancestors = Klass.objects.filter(inheritance__child=self).order_by('inheritance__order')
        return self._ancestors

    def get_children(self):
        if not hasattr(self, '_descendants'):
            self._descendants = Klass.objects.filter(ancestor_relationships__parent=self).order_by('name')
        return self._descendants

    #TODO: This is all mucho inefficient. Perhaps we should use mptt for
    #       get_all_ancestors, get_all_children, get_methods, & get_attributes?
    def get_all_ancestors(self):
        if not hasattr(self, '_all_ancestors'):
            ancestors = self.get_ancestors().select_related('module__project_version__project')
            tree = []
            for ancestor in ancestors:
                tree += [ancestor]
                tree += ancestor.get_all_ancestors()
            self._all_ancestors = tree
        return self._all_ancestors

    def get_all_children(self):
        if not hasattr(self, '_all_descendants'):
            children = self.get_children().select_related('module__project_version__project')
            for child in children:
                children = children | child.get_all_children()
            self._all_descendants = children
        return self._all_descendants

    def get_methods(self):
        if not hasattr(self, '_methods'):
            methods = self.method_set.all().select_related('klass')
            for ancestor in self.get_all_ancestors():
                methods = methods | ancestor.get_methods()
            self._methods = methods
        return self._methods

    def get_attributes(self):
        if not hasattr(self, '_attributes'):
            attrs = self.attribute_set.all()
            for ancestor in self.get_all_ancestors():
                attrs = attrs | ancestor.get_attributes()
            self._attributes = attrs
        return self._attributes

    def get_prepared_attributes(self):
        attributes = self.get_attributes()
        # Make a dictionary of attributes based on name
        attribute_names = {}
        for attr in attributes:
            try:
                attribute_names[attr.name] += [attr]
            except KeyError:
                attribute_names[attr.name] = [attr]

        ancestors = self.get_all_ancestors()

        # Find overridden attributes
        for name, attrs in attribute_names.iteritems():
            # Skip if we have only one attribute.
            if len(attrs) == 1:
                continue

            # Sort the attributes by ancestors.
            def _key(a):
                try:
                    # If ancestor, return the index (>= 0)
                    return ancestors.index(a.klass)
                except:
                    # else a.klass == self, so return -1
                    return -1
            sorted_attrs = sorted(attrs, key=_key)

            # Mark overriden KlassAttributes
            for a in sorted_attrs[1:]:
                a.overridden = True
        return attributes


class Inheritance(models.Model):
    """ Represents the inheritance relationships for a Klass """

    parent = models.ForeignKey(Klass)
    child = models.ForeignKey(Klass, related_name='ancestor_relationships')
    order = models.IntegerField()

    class Meta:
        ordering = ('order',)
        unique_together = ('child', 'order')

    def __unicode__(self):
        return u'%s <- %s (%d)' % (self.parent, self.child, self.order)


class KlassAttribute(models.Model):
    """ Represents an attribute on a Klass """

    klass = models.ForeignKey(Klass, related_name='attribute_set')
    name = models.CharField(max_length=200)
    value = models.CharField(max_length=200)

    class Meta:
        ordering = ('name',)
        unique_together = ('klass', 'name')

    def __unicode__(self):
        return u'%s = %s' % (self.name, self.value)


class ModuleAttribute(models.Model):
    """ Represents an attribute on a Module """

    module = models.ForeignKey(Module, related_name='attribute_set')
    name = models.CharField(max_length=200)
    value = models.CharField(max_length=200)

    class Meta:
        ordering = ('name',)
        unique_together = ('module', 'name')

    def __unicode__(self):
        return u'%s = %s' % (self.name, self.value)


class Method(models.Model):
    """ Represents a method on a Klass """

    klass = models.ForeignKey(Klass)
    name = models.CharField(max_length=200)
    docstring = models.TextField(blank=True, default='')
    code = models.TextField()
    kwargs = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class Function(models.Model):
    """ Represents a function on a Module """

    module = models.ForeignKey(Module)
    name = models.CharField(max_length=200)
    docstring = models.TextField(blank=True, default='')
    code = models.TextField()
    kwargs = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)
