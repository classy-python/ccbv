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
    project_version = models.ForeignKey(ProjectVersion)
    name = models.CharField(max_length=200)
    parent = models.ForeignKey('self', blank=True, null=True)

    def __unicode__(self):
        return self.name


class Klass(models.Model):
    module = models.ForeignKey(Module)
    name = models.CharField(max_length=200)
    docstring = models.TextField(blank=True, default='')

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


class Inheritance(models.Model):
    parent = models.ForeignKey(Klass)
    child = models.ForeignKey(Klass, related_name='ancestor_relationships')
    order = models.IntegerField()

    def __unicode__(self):
        return '%s <- %s (%d)' % (self.parent, self.child, self.order)


class Attribute(models.Model):
    klass = models.ForeignKey(Klass)
    name = models.CharField(max_length=200)
    value = models.CharField(max_length=200)

    def __unicode__(self):
        return u'%s = %s' % (self.name, self.value)


class Method(models.Model):
    klass = models.ForeignKey(Klass)
    name = models.CharField(max_length=200)
    docstring = models.TextField(blank=True, default='')
    code = models.TextField()
    kwargs = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name
