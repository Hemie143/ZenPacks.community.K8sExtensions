
# stdlib Imports
import logging
import re

# Zenoss imports
from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource import PythonDataSourcePlugin
# Twisted Imports
from twisted.internet.defer import inlineCallbacks, returnValue

# Setup logging
log = logging.getLogger('zen.K8sExtensions')


class Namespace(PythonDataSourcePlugin):
    proxy_attributes = (
        'zK8sLicNamespaceFilter',
        'zK8sLicPodFilter',
    )

    @classmethod
    def config_key(cls, datasource, context):
        # TODO: Do not run for K8sCluster (remove in yaml ?)
        log.debug('In config_key {} {} {}'.format(context.device().id,
                                                  datasource.getCycleTime(context),
                                                  'k8sExt'))
        return (
            context.device().id,
            datasource.getCycleTime(context),
            'k8sExt'
        )

    @classmethod
    def params(cls, datasource, context):
        log.debug('Starting params')
        params = {}
        params['pods'] = context.k8sPods.objectIds()
        log.debug('params is {}'.format(params))
        return params

    @inlineCallbacks
    def collect(self, config):
        """
        No default collect behavior. You must implement this method.
        This method must return a Twisted deferred. The deferred results will
        be sent to the onResult then either onSuccess or onError callbacks
        below.
        """
        log.debug('Starting collect Namespace')
        results = {ds.component:ds.params['pods'] for ds in config.datasources if ds.component}

        # This function MUST be a generator
        yield True
        returnValue(results)

    def onSuccess(self, results, config):
        log.debug('Success - results is {}'.format(results))
        data = self.new_data()

        ds0 = config.datasources[0]
        licPodsFilter = ds0.zK8sLicPodFilter
        pattern = re.compile("(" + ")|(".join(licPodsFilter) + ")")

        total_pods = 0
        lic_pods = 0
        for ds in config.datasources:
            if not ds.component:
                continue
            pods = results[ds.component]
            num_pods = len(pods)
            for pod in pods:
                # Remove first 4 chars as the id is prefixed with "pod-"
                r = re.match(pattern, pod[4:])
                if r:
                    lic_pods += 1
            data['values'][ds.component]['count_podscount'] = num_pods
            total_pods += num_pods

        data['values'][None]['count_totalpodscount'] = total_pods
        data['values'][None]['count_licpodscount'] = lic_pods
        log.debug('onSuccess - data: {}'.format(data))
        return data

    def onError(self, result, config):
        log.error('Error - result is {}'.format(result))
        # TODO: send event of collection failure
        return {}
