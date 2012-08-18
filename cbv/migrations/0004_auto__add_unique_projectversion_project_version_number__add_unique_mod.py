# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding unique constraint on 'ProjectVersion', fields ['project', 'version_number']
        db.create_unique('cbv_projectversion', ['project_id', 'version_number'])

        # Adding unique constraint on 'Module', fields ['project_version', 'name']
        db.create_unique('cbv_module', ['project_version_id', 'name'])

        # Adding unique constraint on 'Inheritance', fields ['order', 'parent']
        db.create_unique('cbv_inheritance', ['order', 'parent_id'])

        # Adding unique constraint on 'Attribute', fields ['klass', 'name']
        db.create_unique('cbv_attribute', ['klass_id', 'name'])

        # Adding unique constraint on 'Klass', fields ['name', 'module']
        db.create_unique('cbv_klass', ['name', 'module_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Klass', fields ['name', 'module']
        db.delete_unique('cbv_klass', ['name', 'module_id'])

        # Removing unique constraint on 'Attribute', fields ['klass', 'name']
        db.delete_unique('cbv_attribute', ['klass_id', 'name'])

        # Removing unique constraint on 'Inheritance', fields ['order', 'parent']
        db.delete_unique('cbv_inheritance', ['order', 'parent_id'])

        # Removing unique constraint on 'Module', fields ['project_version', 'name']
        db.delete_unique('cbv_module', ['project_version_id', 'name'])

        # Removing unique constraint on 'ProjectVersion', fields ['project', 'version_number']
        db.delete_unique('cbv_projectversion', ['project_id', 'version_number'])


    models = {
        'cbv.attribute': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('klass', 'name'),)", 'object_name': 'Attribute'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'klass': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cbv.Klass']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'cbv.inheritance': {
            'Meta': {'ordering': "('order',)", 'unique_together': "(('parent', 'order'),)", 'object_name': 'Inheritance'},
            'child': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ancestor_relationships'", 'to': "orm['cbv.Klass']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cbv.Klass']"})
        },
        'cbv.klass': {
            'Meta': {'unique_together': "(('module', 'name'),)", 'object_name': 'Klass'},
            'docstring': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'module': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cbv.Module']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'cbv.method': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Method'},
            'code': ('django.db.models.fields.TextField', [], {}),
            'docstring': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'klass': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cbv.Klass']"}),
            'kwargs': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'cbv.module': {
            'Meta': {'unique_together': "(('project_version', 'name'),)", 'object_name': 'Module'},
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
            'Meta': {'unique_together': "(('project', 'version_number'),)", 'object_name': 'ProjectVersion'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cbv.Project']"}),
            'version_number': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['cbv']
