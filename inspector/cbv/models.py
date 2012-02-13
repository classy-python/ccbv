from django.db import models


class Project(models.Model):
    """
    Represents a project in a python project hierarchy
    """
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('project-detail', (), {
            'package': self.name,
        })


class ProjectVersion(models.Model):
    """
    Represents a particular varsion of a project in a python project hierarchy
    """
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
    """
    Represents a module of a python project
    """
    project_version = models.ForeignKey(ProjectVersion)
    name = models.CharField(max_length=200)
    parent = models.ForeignKey('self', blank=True, null=True)

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


class Klass(models.Model):
    """
    Represents a class in a module of a python project hierarchy
    """
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
        return Klass.objects.filter(inheritance__child=self)

    def get_children(self):
        return Klass.objects.filter(ancestor_relationships__parent=self)

    def get_all_children(self):
        children = self.get_children()
        for child in children:
            children = children | child.get_children()
        return children

    def get_methods(self):
        methods = self.method_set.all()
        for ancestor in self.get_ancestors():
            methods = methods | ancestor.get_methods()
        return methods

    def get_attributes(self):
        attrs = self.attribute_set.all()
        for ancestor in self.get_ancestors():
            attrs = attrs | ancestor.get_attributes()
        return attrs


class Inheritance(models.Model):
    """
    Represents the inheritance relationships for a Klass
    """
    parent = models.ForeignKey(Klass)
    child = models.ForeignKey(Klass, related_name='ancestor_relationships')
    order = models.IntegerField()

    class Meta:
        ordering = ('order',)
        unique_together = ('child', 'order')

    def __unicode__(self):
        return '%s <- %s (%d)' % (self.parent, self.child, self.order)


class Attribute(models.Model):
    """
    Represents the attributes on a Klass
    """
    klass = models.ForeignKey(Klass)
    name = models.CharField(max_length=200)
    value = models.CharField(max_length=200)

    class Meta:
        ordering = ('name',)
        unique_together = ('klass', 'name')

    def __unicode__(self):
        return u'%s = %s' % (self.name, self.value)


class Method(models.Model):
    """
    Represents the methods on a Klass
    """
    klass = models.ForeignKey(Klass)
    name = models.CharField(max_length=200)
    docstring = models.TextField(blank=True, default='')
    code = models.TextField()
    kwargs = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)
