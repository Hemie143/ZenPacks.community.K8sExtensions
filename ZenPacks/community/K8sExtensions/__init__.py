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

    def customize_template(self, template, data):
        # Datasource
        for ds_name, ds_data in data['datasources'].items():
            if hasattr(template.datasources, ds_name):
                template.manage_deleteRRDDataSources([ds_name])
            ds = template.manage_addRRDDataSource(ds_name, 'PythonDataSource.Python')
            if 'plugin_classname' in ds_data:
                ds.plugin_classname = ds_data['plugin_classname']
            # Datapoint
            for dp_name in ds_data['datapoints']:
                dp = ds.manage_addRRDDataPoint(dp_name)
                dp.rrdmin = 0

        # Graph Definition
        for gd_name, gd_data in data['graphs'].items():
            if hasattr(template.graphDefs, gd_name):
                template.manage_deleteGraphDefinitions([gd_name])
            graph = template.manage_addGraphDefinition(gd_name)
            graph.units = 'pods'
            graph.miny = 0
            # Graph Datapoints
            dpNames = []
            for gdp_name, gdp_data in gd_data['graphpoints'].items():
                gdp = graph.manage_addDataPointGraphPoints(dpNames=[gdp_data['dpName']], includeThresholds=False)
                gdp = gdp[0]
                gdp.legend = ' ' + gdp_name
        return

    def namespace_custom(self, app):
        data = {
            'datasources': {
                'count': {
                    'datapoints': {
                        'podscount',
                        'licpodscount',
                    },
                    'plugin_classname': 'ZenPacks.community.K8sExtensions.dsplugins.namespace.Namespace'
                }
            },
            'graphs': {
                'Pods Count': {
                    'graphpoints': {
                        'Pods count': {
                            'dpName': 'count_podscount',
                        },
                        'Licensed Pods count': {
                            'dpName': 'count_licpodscount',
                        },
                    }
                }
            }
        }

        log.info('Customizing K8sNamespace template')
        try:
            template = app.zport.dmd.Devices.Kubernetes.rrdTemplates.K8sNamespace
            log.info('Template K8sNamespace found')
        except:
            log.error('Template K8sNamespace not found')
            return
        self.customize_template(template, data)
        log.info('Completed customization K8sNamespace template')
        return

    def cluster_custom(self, app):
        data = {
            'datasources': {
                'count': {
                    'datapoints': {
                        'totalpodscount',
                        'licpodscount',
                    },
                    'plugin_classname': 'ZenPacks.community.K8sExtensions.dsplugins.namespace.Namespace'
                }
            },
            'graphs': {
                'Pods Total Count': {
                    'graphpoints': {
                        'Total count': {
                            'dpName': 'count_totalpodscount',
                        },
                        'Total count for licenses': {
                            'dpName': 'count_licpodscount',
                        }
                    }
                }
            }
        }

        log.info('Customizing K8sCluster template')
        try:
            template = app.zport.dmd.Devices.Kubernetes.rrdTemplates.K8sCluster
            log.info('Template K8sCluster found')
        except:
            log.error('Template K8sCluster not found')
            return
        self.customize_template(template, data)
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
        # TODO: Don't hardcode the data. This implies that the data should be moved up from functions to class level.
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
