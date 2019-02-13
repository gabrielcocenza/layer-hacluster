from charms.reactive import when, when_not, clear_flag, set_flag
from charms.reactive import endpoint_from_flag
from charmhelpers.core import hookenv
from charms.layer.kubernetes_common import get_ingress_address
from charmhelpers.core import unitdata

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

    # current services are services that have been bound and corosync knows about them
    # desired services are services that have been added, but not bound yet
    # deleted services are services that have been bound, but are desired to be gone
    services = db.get('services', {'current_services': {},
                                   'desired_services': {},
                                   'deleted_services': {}})
    for name, service in services['deleted_services'].items():
        hacluster.remove_init_service(name, service)
    for name, service in services['desired_services'].items():
        hacluster.add_init_service(name, service)
        services['current_services'][name] = service

    services['deleted_services'] = {}
    services['desired_services'] = {}

    hacluster.bind_resources()
    set_flag('layer-hacluster.configured')


@when('config.changed.ha-cluster-vip',
      'ha.connected')
def update_vips():
    hacluster = endpoint_from_flag('ha.connected')
    config = hookenv.config()
    original_vips = set(config.previous('ha-cluster-vip').split())
    new_vips = set(config['ha-cluster-vip'].split())
    old_vips = original_vips - new_vips

    for vip in old_vips:
        hacluster.remove_vip(hookenv.application_name(), vip)

    clear_flag('layer-hacluster.configured')


@when('config.changed.ha-cluster-dns',
      'ha.connected')
def update_dns():
    hacluster = endpoint_from_flag('ha.connected')
    config = hookenv.config()
    original_dns = set(config.previous('ha-cluster-dns').split())
    new_dns = set(config['ha-cluster-dns'].split())
    old_dns = original_dns - new_dns

    for dns in old_dns:
        hacluster.remove_dnsha(hookenv.application_name, 'public')

    clear_flag('layer-hacluster.configured')
