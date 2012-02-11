# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Method.kwargs'
        db.add_column('cbv_method', 'kwargs', self.gf('django.db.models.fields.CharField')(default='', max_length=200), keep_default=False)

        # Adding field 'Klass.docstring'
        db.add_column('cbv_klass', 'docstring', self.gf('django.db.models.fields.TextField')(default=''), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Method.kwargs'
        db.delete_column('cbv_method', 'kwargs')

        # Deleting field 'Klass.docstring'
        db.delete_column('cbv_klass', 'docstring')


    models = {
        'cbv.inheritance': {
            'Meta': {'object_name': 'Inheritance'},
            'child': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'children'", 'to': "orm['cbv.Klass']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cbv.Klass']"})
        },
        'cbv.klass': {
            'Meta': {'object_name': 'Klass'},
            'ancestors': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cbv.Klass']", 'through': "orm['cbv.Inheritance']", 'symmetrical': 'False'}),
            'docstring': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cbv.Module']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'cbv.method': {
            'Meta': {'object_name': 'Method'},
            'code': ('django.db.models.fields.TextField', [], {}),
            'docstring': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'klass': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cbv.Klass']"}),
            'kwargs': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'cbv.module': {
            'Meta': {'object_name': 'Module'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cbv.Module']", 'null': 'True', 'blank': 'True'}),
            'project_version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cbv.ProjectVersion']"})
        },
        'cbv.project': {
            'Meta': {'object_name': 'Project'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'cbv.projectversion': {
            'Meta': {'object_name': 'ProjectVersion'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cbv.Project']"}),
            'version_number': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['cbv']
