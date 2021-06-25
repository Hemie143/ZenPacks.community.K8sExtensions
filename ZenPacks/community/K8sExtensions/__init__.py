import logging
import os

from ZenPacks.zenoss.ZenPackLib import zenpacklib

CFG = zenpacklib.load_yaml([os.path.join(os.path.dirname(__file__), "zenpack.yaml")], verbose=False, level=30)
schema = CFG.zenpack_module.schema

log = logging.getLogger('zen.K8sExtensions.install')
from Products.ZenModel.ZenPack import ZenPackBase
from Products.ZenModel.DataPointGraphPoint import DataPointGraphPoint
# from Products.Zuul.form import schema

class ZenPack(schema.ZenPack):
    # TODO: Enhance list of ds, dp and gd and how this is handled

    def namespace_custom(self, app):
        ds_name = 'count'
        dp_name = 'podscount'
        gd_name = 'Pods Count'

        log.info('Customizing K8sNamespace template')
        try:
            template = app.zport.dmd.Devices.Kubernetes.rrdTemplates.K8sNamespace
            log.info('Template K8sNamespace found')
        except:
            log.error('Template K8sNamespace not found')
            return

        if hasattr(template.datasources, ds_name):
            template.manage_deleteRRDDataSources([ds_name])
        # Datasource
        ds = template.manage_addRRDDataSource(ds_name, 'PythonDataSource.Python')
        ds.plugin_classname = 'ZenPacks.community.K8sExtensions.dsplugins.namespace.Namespace'
        ds.component = '${here/id}'
        # Datapoint
        dp = ds.manage_addRRDDataPoint(dp_name)
        dp.rrdmin = 0
        # Graph Definition
        if hasattr(template.graphDefs, gd_name):
            template.manage_deleteGraphDefinitions([gd_name])
        graph = template.manage_addGraphDefinition(gd_name)
        graph.units = 'pods'
        graph.miny = 0
        # Graph Datapoint
        graph.manage_addDataPointGraphPoints(dpNames=[dp.name()], includeThresholds=False)
        log.info('Completed customization K8sNamespace template')

    def cluster_custom(self, app):
        ds_name = 'count'
        dp_name = 'totalpodscount'
        gd_name = 'Pods Total Count'

        log.info('Customizing K8sCluster template')
        try:
            template = app.zport.dmd.Devices.Kubernetes.rrdTemplates.K8sCluster
            log.info('Template K8sCluster found')
        except:
            log.error('Template K8sCluster not found')
            return

        if hasattr(template.datasources, ds_name):
            template.manage_deleteRRDDataSources([ds_name])
        # Datasource
        ds = template.manage_addRRDDataSource(ds_name, 'PythonDataSource.Python')
        ds.plugin_classname = 'ZenPacks.community.K8sExtensions.dsplugins.namespace.Namespace'
        # ds.component = '${here/id}'
        # Datapoint
        dp = ds.manage_addRRDDataPoint(dp_name)
        dp.rrdmin = 0
        # Graph Definition
        if hasattr(template.graphDefs, gd_name):
            template.manage_deleteGraphDefinitions([gd_name])
        graph = template.manage_addGraphDefinition(gd_name)
        graph.units = 'pods'
        graph.miny = 0
        # Graph Datapoint
        graph.manage_addDataPointGraphPoints(dpNames=[dp.name()], includeThresholds=False)
        log.info('Completed customization K8sCluster template')

    def install(self, app):
        self.cluster_custom(app)
        self.namespace_custom(app)
        ZenPackBase.install(self, app)

    def upgrade(self, app):
        self.cluster_custom(app)
        self.namespace_custom(app)
        ZenPackBase.upgrade(self, app)

    def remove(self, app, leaveObjects=False):
        log.info('Cleaning up K8sCluster template')
        try:
            template = app.zport.dmd.Devices.Kubernetes.rrdTemplates.K8sCluster
        except:
            return
        if hasattr(template.datasources, 'count'):
            template.manage_deleteRRDDataSources(['count'])
        if hasattr(template.graphDefs, 'Pods Total Count'):
            template.manage_deleteGraphDefinitions(['Pods Total Count'])
        log.info('Cleaned up K8sCluster template')

        log.info('Cleaning up K8sNamespace template')
        try:
            template = app.zport.dmd.Devices.Kubernetes.rrdTemplates.K8sNamespace
        except:
            return
        if hasattr(template.datasources, 'count'):
            template.manage_deleteRRDDataSources(['count'])
        if hasattr(template.graphDefs, 'Pods Count'):
            template.manage_deleteGraphDefinitions(['Pods Count'])
        log.info('Cleaned up K8sNamespace template')
        ZenPackBase.remove(self, app, leaveObjects)
