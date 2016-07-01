import collectd

# Datadog API
from datadog import initialize, api

VERBOSE_LOGGING = False
DD_CONFIG = None
COLLECTD_PREFIX = "collectd"

def dd_dev_tagging(vl, config=None):
    """Extract tags

    Keyword arguments:
        vl -- the collectd metric value
        config -- not really necessary, just conforming to prototype.
    """
    tags = []

    if vl and vl.plugin_instance:
        tags += [vl.plugin + "_device:" + vl.plugin_instance]

    return tags


ADV_SUPPORTED_PLUGINS = { 'snmp': dd_tagging }

def configure_callback(conf):
    """Receive configuration block"""
    global DD_CONFIG
    api_key = None
    tags = None
    dryrun = False

    for node in conf.children:
        key = node.key.lower()
        val = node.values[0]
        log_verbose('Analyzing config %s key (value: %s)' % (key, val))

        if key == 'api_key':
            api_key = val
        elif key == 'tags':
            tags = [tok.strip() for tok in val.split(',')]
        elif key == 'dryrun':
            dryrun = (val.lower() == "true") or (val.lower == "yes")
        elif key == 'verbose':
            global VERBOSE_LOGGING
            VERBOSE_LOGGING = (val.lower() == "true") or (val.lower == "yes") or VERBOSE_LOGGING
        else:
            collectd.warning('datadog plugin: Unknown config key: %s.' % key)
            continue

    if api_key:
        DD_CONFIG = { 'api_key': api_key, 'tags': tags, 'dryrun': dryrun }
	if not dryrun:
            initialize(api_key=DD_CONFIG['api_key'])


def write_callback(vl, data=None):
    if not DD_CONFIG:
        return

    points = []
    metric = "{prefix}.{plugin}.{metric}".format(
        prefix=COLLECTD_PREFIX,
        plugin=vl.plugin,
        metric=vl.type
    )
    v_time = float("{0:.2f}".format(vl.time))
    for i in vl.values:
        points.append((v_time, i))

    tags = list(DD_CONFIG['tags'])

    if vl.plugin in ADV_SUPPORTED_PLUGINS:
        tags += ADV_SUPPORTED_PLUGINS[vl.plugin](vl, DD_CONFIG)

    if not DD_CONFIG['dryrun']:
        api.Metric.send(metric=metric, points=points, host=vl.host, tags=tags)

    log_verbose('Sent metric {metric}@{ts} with tags {tags} and {points}'.format(
        metric=metric,
        ts=v_time,
        tags=", ".join(tags),
        points=points
    ))


def log_verbose(msg):
    if not VERBOSE_LOGGING:
        return
    collectd.info('datadog plugin [verbose]: %s' % msg)

# register callbacks
collectd.register_config(configure_callback)
collectd.register_write(write_callback)
