from charms.reactive import clear_flag, set_flag

services = {}


def add_service_to_hacluster(name, service_name):
    """Adds a service to be monitored under HAcluster.
       Takes a name for this entry and a service_name,
       which is the name used by systemd/initd to identify
       the service.
    """
    global services

    services[name] = service_name
    clear_flag('layer-hacluster.configured')
    set_flag('layer.hacluster.services_configured')


def remove_service_from_hacluster(name, service_name):
    """Removes a service to be monitored under HAcluster.
       Takes a name for this entry and a service_name,
       which is the name used by systemd/initd to identify
       the service.
    """
    global services

    if name in services:
        del services[name]
