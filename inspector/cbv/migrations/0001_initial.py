# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Project'
        db.create_table('cbv_project', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('cbv', ['Project'])

        # Adding model 'ProjectVersion'
        db.create_table('cbv_projectversion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cbv.Project'])),
            ('version_number', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('cbv', ['ProjectVersion'])

        # Adding model 'Module'
        db.create_table('cbv_module', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project_version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cbv.ProjectVersion'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cbv.Module'], null=True, blank=True)),
        ))
        db.send_create_signal('cbv', ['Module'])

        # Adding model 'Klass'
        db.create_table('cbv_klass', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('module', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cbv.Module'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('cbv', ['Klass'])

        # Adding model 'Inheritance'
        db.create_table('cbv_inheritance', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cbv.Klass'])),
            ('child', self.gf('django.db.models.fields.related.ForeignKey')(related_name='children', to=orm['cbv.Klass'])),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('cbv', ['Inheritance'])

        # Adding model 'Method'
        db.create_table('cbv_method', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('klass', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cbv.Klass'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('docstring', self.gf('django.db.models.fields.TextField')()),
            ('code', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('cbv', ['Method'])


    def backwards(self, orm):
        
        # Deleting model 'Project'
        db.delete_table('cbv_project')

        # Deleting model 'ProjectVersion'
        db.delete_table('cbv_projectversion')

        # Deleting model 'Module'
        db.delete_table('cbv_module')

        # Deleting model 'Klass'
        db.delete_table('cbv_klass')

        # Deleting model 'Inheritance'
        db.delete_table('cbv_inheritance')

        # Deleting model 'Method'
        db.delete_table('cbv_method')


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
