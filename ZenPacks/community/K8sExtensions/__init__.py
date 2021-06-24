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
    ds_name = 'count'
    dp_name = 'podscount'
    gd_name = 'Pods Count'

    def install(self, app):

        log.info('Customizing K8sNamespace template')
        try:
            template = app.zport.dmd.Devices.Kubernetes.rrdTemplates.K8sNamespace
            log.info('Template K8sNamespace found')
        except:
            log.error('Template K8sNamespace not found')
            return

        if hasattr(template.datasources, self.ds_name):
            template.manage_deleteRRDDataSources([self.ds_name])
        # Datasource
        ds = template.manage_addRRDDataSource(self.ds_name, 'PythonDataSource.Python')
        ds.plugin_classname = 'ZenPacks.community.K8sExtensions.dsplugins.namespace.Namespace'
        ds.component = '${here/id}'
        # Datapoint
        dp = ds.manage_addRRDDataPoint(self.dp_name)
        dp.rrdmin = 0
        log.info('dp: {}'.format(dp.name()))
        # Graph Definition
        if hasattr(template.graphDefs, self.gd_name):
            template.manage_deleteGraphDefinitions([self.gd_name])
        graph = template.manage_addGraphDefinition(self.gd_name)
        print(graph.__dict__)
        graph.units = 'pods'
        graph.miny = 0
        # Graph Datapoint
        '''
        dp_id = '{}_{}'.format(self.ds_name, self.dp_name)
        template.manage_addDataSourcesToGraphs(ids=[self], graphIds=[self.gd_name])
        '''
        # dp_id = '{}_{}'.format(self.ds_name, self.dp_name)
        graph.manage_addDataPointGraphPoints(dpNames=[dp.name()], includeThresholds=False)

        print(graph.__dict__)

        '''
        gdp = gd.createGraphPoint(DataPointGraphPoint, 'zenperfsql')
        gdp.dpName = 'zenperfsql_%s' % dpn
        gdp.format = format
        gdp.stacked = stacked
        '''

        '''
        component: ${here/id}
        '''

        '''
        for gdn, dpn, stacked, format in self._gdmap:
            dp = ds.manage_addRRDDataPoint(dpn)
            if dpn in ['dataPoints']:
                dp.rrdtype = 'DERIVE'
                dp.rrdmin = 0
            gd = getattr(pct.graphDefs, gdn, None)
            if not gd: continue
            if hasattr(gd.graphPoints, 'zenperfsql'): continue
            gdp = gd.createGraphPoint(DataPointGraphPoint, 'zenperfsql')
            gdp.dpName = 'zenperfsql_%s'%dpn
            gdp.format = format
            gdp.stacked = stacked
        '''
        log.info('Completed customization K8sNamespace template')
        ZenPackBase.install(self, app)

    def upgrade(self, app):

        print('***init***upgrade')
        '''
        if not hasattr(app.zport.dmd.Events.Status, 'PyDBAPI'):
            app.zport.dmd.Events.createOrganizer("/Status/PyDBAPI")
        pct = app.zport.dmd.Monitors.rrdTemplates.PerformanceConf
        if hasattr(pct.datasources, 'zenperfsql'):
            pct.manage_deleteRRDDataSources(['zenperfsql'])
        ds = pct.manage_addRRDDataSource('zenperfsql', 'BuiltInDS.Built-In')
        for gdn, dpn, stacked, format in self._gdmap:
            dp = ds.manage_addRRDDataPoint(dpn)
            if dpn in ['dataPoints']:
                dp.rrdtype = 'DERIVE'
                dp.rrdmin = 0
            gd = getattr(pct.graphDefs, gdn, None)
            if not gd: continue
            if hasattr(gd.graphPoints, 'zenperfsql'): continue
            gdp = gd.createGraphPoint(DataPointGraphPoint, 'zenperfsql')
            gdp.dpName = 'zenperfsql_%s'%dpn
            gdp.format = format
            gdp.stacked = stacked
        '''
        ZenPackBase.upgrade(self, app)

    def remove(self, app, leaveObjects=False):
        log.info('Cleaning up K8sNamespace template')
        try:
            template = app.zport.dmd.Devices.Kubernetes.rrdTemplates.K8sNamespace
        except:
            return
        if hasattr(template.datasources, self.ds_name):
            template.manage_deleteRRDDataSources([self.ds_name])
        if hasattr(template.graphDefs, self.gd_name):
            template.manage_deleteGraphDefinitions([self.gd_name])
        log.info('Cleaned up K8sNamespace template')
        ZenPackBase.remove(self, app, leaveObjects)
