from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name


class ProjectVersion(models.Model):
    project = models.ForeignKey(Project)
    version_number = models.CharField(max_length=200)

    def __unicode__(self):
        return self.version_number


class Module(models.Model):
    project_version = models.ForeignKey(Module)
    name = models.CharField(max_length=200)
    parent = models.ForeignKey('self', blank=True, null=True)

    def __unicode__(self):
        return self.name


class Klass(models.Model):
    module = models.ForeignKey(Module)
    name = models.CharField(max_length=200)
    ancestors = models.ManyToMany('self', through='Inheritance')

    def __unicode__(self):
        return self.name


class Inheritance(models.Model):
    parent = models.ForeignKey(View)
    child = modes.ForeignKey(View)
    order = models.IntegerField()

    def __unicode__(self):
        return '%s -> %s (%d)' % (self.parent, self.child, self.order)


class Method(models.Model):
    klass = models.ForeignKey(Klass)
    name = models.CharField(max_length=200)
    docstring = models.TextField()
    code = modelsTextField()

    def __unicode__(self):
        return self.name
