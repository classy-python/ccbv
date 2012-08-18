# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Removing unique constraint on 'Attribute', fields ['klass', 'name']
        db.delete_unique('cbv_attribute', ['klass_id', 'name'])

        # Deleting model 'Attribute'
        db.delete_table('cbv_attribute')

        # Adding model 'ModuleAttribute'
        db.create_table('cbv_moduleattribute', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('module', self.gf('django.db.models.fields.related.ForeignKey')(related_name='attribute_set', to=orm['cbv.Module'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('cbv', ['ModuleAttribute'])

        # Adding unique constraint on 'ModuleAttribute', fields ['module', 'name']
        db.create_unique('cbv_moduleattribute', ['module_id', 'name'])

        # Adding model 'Function'
        db.create_table('cbv_function', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('module', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cbv.Module'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('docstring', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('code', self.gf('django.db.models.fields.TextField')()),
            ('kwargs', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('cbv', ['Function'])

        # Adding model 'KlassAttribute'
        db.create_table('cbv_klassattribute', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('klass', self.gf('django.db.models.fields.related.ForeignKey')(related_name='attribute_set', to=orm['cbv.Klass'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('cbv', ['KlassAttribute'])

        # Adding unique constraint on 'KlassAttribute', fields ['klass', 'name']
        db.create_unique('cbv_klassattribute', ['klass_id', 'name'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'KlassAttribute', fields ['klass', 'name']
        db.delete_unique('cbv_klassattribute', ['klass_id', 'name'])

        # Removing unique constraint on 'ModuleAttribute', fields ['module', 'name']
        db.delete_unique('cbv_moduleattribute', ['module_id', 'name'])

        # Adding model 'Attribute'
        db.create_table('cbv_attribute', (
            ('value', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('klass', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cbv.Klass'])),
        ))
        db.send_create_signal('cbv', ['Attribute'])

        # Adding unique constraint on 'Attribute', fields ['klass', 'name']
        db.create_unique('cbv_attribute', ['klass_id', 'name'])

        # Deleting model 'ModuleAttribute'
        db.delete_table('cbv_moduleattribute')

        # Deleting model 'Function'
        db.delete_table('cbv_function')

        # Deleting model 'KlassAttribute'
        db.delete_table('cbv_klassattribute')


    models = {
        'cbv.function': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Function'},
            'code': ('django.db.models.fields.TextField', [], {}),
            'docstring': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kwargs': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
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
            'module': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cbv.Module']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'cbv.klassattribute': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('klass', 'name'),)", 'object_name': 'KlassAttribute'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'klass': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attribute_set'", 'to': "orm['cbv.Klass']"}),
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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'cbv.module': {
            'Meta': {'unique_together': "(('project_version', 'name'),)", 'object_name': 'Module'},
            'docstring': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cbv.Module']", 'null': 'True', 'blank': 'True'}),
            'project_version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cbv.ProjectVersion']"})
        },
        'cbv.moduleattribute': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('module', 'name'),)", 'object_name': 'ModuleAttribute'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
