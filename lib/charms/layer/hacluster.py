from charms.reactive import clear_flag, set_flag
from charmhelper.core import unitdata

db = unitdata.kv()


def add_service_to_hacluster(name, service_name):
    """Adds a service to be monitored under HAcluster.
       Takes a name for this entry and a service_name,
       which is the name used by systemd/initd to identify
       the service.
    """
    services = db.get('services', {})
    services[name] = service_name
    db.set('services', services)
    clear_flag('layer-hacluster.configured')
    set_flag('layer.hacluster.services_configured')


def remove_service_from_hacluster(name, service_name):
    """Removes a service to be monitored under HAcluster.
       Takes a name for this entry and a service_name,
       which is the name used by systemd/initd to identify
       the service.
    """
    services = db.get('services', {})
    del services[name]
    db.set('services', services)
