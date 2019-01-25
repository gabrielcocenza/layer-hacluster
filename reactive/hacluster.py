from charms.reactive import when, when_not, clear_flag, set_flag
from charms.reactive import endpoint_from_flag
from charmhelpers.core import hookenv
from charms.layer.kubernetes_common import get_ingress_address
from charmhelper.core import unitdata

db = unitdata.kv()


@when('ha.connected', 'layer.hacluster.services_configured')
@when_not('layer.hacluster.configured')
def configure_hacluster():
    """Configure HA resources in corosync"""
    hacluster = endpoint_from_flag('ha.connected')
    vips = hookenv.config('ha-cluster-vip').split()
    dns_record = hookenv.config('ha-cluster-dns')
    if vips and dns_record:
        set_flag('layer-hacluster.dns_vip.invalid')
        msg = "Unsupported configuration. " \
              "ha-cluster-vip and ha-cluster-dns cannot both be set",
        hookenv.log(msg)
        return
    else:
        clear_flag('layer-hacluster.dns_vip.invalid')
    if vips:
        for vip in vips:
            hacluster.add_vip(hookenv.application_name(), vip)
    elif dns_record:
        ip = get_ingress_address()
        hacluster.add_dnsha(hookenv.application_name(), ip, dns_record,
                            'public')

    services = db.get('services', {})
    for name, service in services.items():
        hacluster.add_init_service(name, service)

    hacluster.bind_resources()
    set_flag('layer-hacluster.configured')


@when('config.ha-cluster-vip.changed',
      'config.ha-cluster-dns.changed')
def update_config():
    clear_flag('layer-hacluster.configured')
