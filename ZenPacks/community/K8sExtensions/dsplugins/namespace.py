
# stdlib Imports
import logging

# Zenoss imports
from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource import PythonDataSourcePlugin
# Twisted Imports
from twisted.internet.defer import inlineCallbacks, returnValue

# Setup logging
log = logging.getLogger('zen.K8sExtensions')


class Namespace(PythonDataSourcePlugin):

    @classmethod
    def config_key(cls, datasource, context):
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
        total_pods = 0
        for ds in config.datasources:
            if not ds.component:
                continue
            num_pods = len(results[ds.component])
            data['values'][ds.component]['podscount'] = num_pods
            total_pods += num_pods
        data['values'][None]['totalpodscount'] = total_pods
        log.debug('onSuccess - data: {}'.format(data))
        return data

    def onError(self, result, config):
        log.error('Error - result is {}'.format(result))
        # TODO: send event of collection failure
        return {}
