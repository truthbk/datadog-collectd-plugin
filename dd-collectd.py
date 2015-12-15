import collectd

# Datadog API
from datadog import initialize, api

SUPPORTED_PLUGINS = ['snmp']

VERBOSE_LOGGING = False
DD_CONFIG = None


def configure_callback(conf):
    """Receive configuration block"""
    api_key = None
    tags = None
    tag_by_dev = False

    for node in conf.children:
        key = node.key.lower()
        val = node.values[0]
        log_verbose('Analyzing config %s key (value: %s)' % (key, val))

        if key == 'api_key':
            api_key = val
        elif key == 'tags':
            tags = [tok.strip() for tok in val.split(',')]
        elif key == 'tag_by_device':
            tag_by_dev = (val.lower() == "true") or (val.lower == "yes")
        elif key == 'verbose':
            global VERBOSE_LOGGING
            VERBOSE_LOGGING = bool(node.values[0]) or VERBOSE_LOGGING
        else:
            collectd.warning('datadog plugin: Unknown config key: %s.' % key)
            continue

    if api_key:
        DD_CONFIG = {'api_key': api_key, 'tags': tags, 'by_dev': tag_by_dev}
        initialize(api_key=DD_CONFIG['api_key'])


def write_callback(vl, data=None):
    if vl.plugin not in SUPPORTED_PLUGINS:
        return

    points = []
    metric = vl.plugin + "." + vl.type
    for i in vl.values:
        points.append((vl.time, i))
    tags = DD_CONFIG['api_key']
    if DD_CONFIG['by_dev']:
        tags += [vl.plugin + "_device:" + vl.type_instance]  # or plugin_instance?
    api.Metric.send(metric=metric, points=points, host=vl.host, tags=tags)
    log_verbose('Sent metric {metric}@{ts} with tags {tags}'.format(
        metric=metric[1],
        ts=metric[0],
        tags=", ".join(tags)
    ))


def log_verbose(msg):
    if not VERBOSE_LOGGING:
        return
    collectd.info('redis plugin [verbose]: %s' % msg)

# register callbacks
collectd.register_config(configure_callback)
collectd.register_read(write_callback)
