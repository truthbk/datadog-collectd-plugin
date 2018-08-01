# datadog-collectd-plugin
A Datadog plugin for collectd using collectd's Python plugin.

This is a POC, it allows tapping into the `snmp` check to report a metrics to DD.

Unfortunately, the collectd python API is kind of limited, not allowing us to generate the relevant tags we'd need for a full-fledged plugin. For instance, with SNMP we'd need to be able to tag metrics based on some MIB columns (eg. interface number or name), I was unable to achieve this.

## Setup

Make sure you put the provided python script in the correct location for your collectd setup, in the provided sample configuration that location was:
```
/opt/collectd/plugin/python/
```

Multiple module paths may be specified with the collectd python plugin so the location should be quite flexible. 

Please drop the contents of the provided `dd-collectd.conf` into your `/etc/collectd.conf` file, and restart collectd.


