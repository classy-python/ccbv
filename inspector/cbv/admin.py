from django.site import admin

import models

admin.site.register(models.Project)
admin.site.register(models.ProjectVersion)
admin.site.register(models.Module)
admin.site.register(models.View)
admin.site.register(models.Inheritance)
admin.site.register(models.Method)
