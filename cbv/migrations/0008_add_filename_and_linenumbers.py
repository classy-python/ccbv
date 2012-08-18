# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'ModuleAttribute.line_number'
        db.add_column('cbv_moduleattribute', 'line_number', self.gf('django.db.models.fields.IntegerField')(default=1), keep_default=False)

        # Adding field 'Module.filename'
        db.add_column('cbv_module', 'filename', self.gf('django.db.models.fields.CharField')(default='', max_length=511), keep_default=False)

        # Adding field 'Function.line_number'
        db.add_column('cbv_function', 'line_number', self.gf('django.db.models.fields.IntegerField')(default=1), keep_default=False)

        # Adding field 'KlassAttribute.line_number'
        db.add_column('cbv_klassattribute', 'line_number', self.gf('django.db.models.fields.IntegerField')(default=1), keep_default=False)

        # Adding field 'Method.line_number'
        db.add_column('cbv_method', 'line_number', self.gf('django.db.models.fields.IntegerField')(default=1), keep_default=False)

        # Adding field 'Klass.line_number'
        db.add_column('cbv_klass', 'line_number', self.gf('django.db.models.fields.IntegerField')(default=1), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'ModuleAttribute.line_number'
        db.delete_column('cbv_moduleattribute', 'line_number')

        # Deleting field 'Module.filename'
        db.delete_column('cbv_module', 'filename')

        # Deleting field 'Function.line_number'
        db.delete_column('cbv_function', 'line_number')

        # Deleting field 'KlassAttribute.line_number'
        db.delete_column('cbv_klassattribute', 'line_number')

        # Deleting field 'Method.line_number'
        db.delete_column('cbv_method', 'line_number')

        # Deleting field 'Klass.line_number'
        db.delete_column('cbv_klass', 'line_number')


    models = {
        'cbv.function': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Function'},
            'code': ('django.db.models.fields.TextField', [], {}),
            'docstring': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kwargs': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'line_number': ('django.db.models.fields.IntegerField', [], {}),
            'module': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cbv.Module']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'cbv.inheritance': {
            'Meta': {'ordering': "('order',)", 'unique_together': "(('child', 'order'),)", 'object_name': 'Inheritance'},
            'child': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ancestor_relationships'", 'to': "orm['cbv.Klass']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cbv.Klass']"})
        },
        'cbv.klass': {
            'Meta': {'unique_together': "(('module', 'name'),)", 'object_name': 'Klass'},
            'docstring': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line_number': ('django.db.models.fields.IntegerField', [], {}),
            'module': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cbv.Module']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'cbv.klassattribute': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('klass', 'name'),)", 'object_name': 'KlassAttribute'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'klass': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attribute_set'", 'to': "orm['cbv.Klass']"}),
            'line_number': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'cbv.method': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Method'},
            'code': ('django.db.models.fields.TextField', [], {}),
            'docstring': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'klass': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cbv.Klass']"}),
            'kwargs': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'line_number': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'cbv.module': {
            'Meta': {'unique_together': "(('project_version', 'name'),)", 'object_name': 'Module'},
            'docstring': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'filename': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '511'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cbv.Module']", 'null': 'True', 'blank': 'True'}),
            'project_version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cbv.ProjectVersion']"})
        },
        'cbv.moduleattribute': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('module', 'name'),)", 'object_name': 'ModuleAttribute'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line_number': ('django.db.models.fields.IntegerField', [], {}),
            'module': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attribute_set'", 'to': "orm['cbv.Module']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '200'})
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
