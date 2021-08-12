# ZenReports.Utils contains some useful helpers for creating records to return.
import re
from Products.ZenReports.Utils import Record

# The class name must match the filename.
class k8sPodsCount(object):

    # The run method will be executed when your report calls the plugin.
    def run(self, dmd, args):
        deviceClass = dmd.Devices.Kubernetes
        clusterMatch = args.get('clusterFilter', '') or ''

        rows = []
        totalpodsTotal = 0
        licpodsTotal = 0
        for cluster in deviceClass.getDevices():
            clusterName = cluster.titleOrId()
            r = re.match(clusterMatch, clusterName)
            if not r:
                continue
            totalpods = int(cluster.getRRDValue('count_totalpodscount'))
            licpods = int(cluster.getRRDValue('count_licpodscount'))
            totalpodsTotal += totalpods
            licpodsTotal += licpods
            rows.append(Record(
                cluster=clusterName,
                totalpods=totalpods,
                licpods=licpods,
            ))

        rows.append(Record(
            cluster='Grand Total',
            totalpods=totalpodsTotal,
            licpods=licpodsTotal,
        ))
        return rows