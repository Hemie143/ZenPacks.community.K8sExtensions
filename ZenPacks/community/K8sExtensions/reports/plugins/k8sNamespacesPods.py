# ZenReports.Utils contains some useful helpers for creating records to return.
import re
from Products.ZenReports.Utils import Record

# The class name must match the filename.
class k8sNamespacesPods(object):

    # The run method will be executed when your report calls the plugin.
    def run(self, dmd, args):
        deviceClass = dmd.Devices.Kubernetes
        clusterMatch = args.get('clusterFilter', '') or ''

        rows = []
        for cluster in deviceClass.getDevices():
            clusterName = cluster.titleOrId()
            r = re.match(clusterMatch, clusterName)
            if not r:
                continue

            namespaces = cluster.k8sNamespaces
            for ns in namespaces.objectValuesGen():
                for pod in ns.k8sPods.objectValuesGen():
                    rows.append(Record(
                        cluster=clusterName,
                        namespaces=ns.titleOrId(),
                        pods=pod.titleOrId(),
                    ))
        return rows