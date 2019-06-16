import xibbaz.src.exceptions as exceptions
import sys

class ZabbixObject:

    fields = []
    sub_items = []
    item_dep_map ={}
    # key name zabbix returns on search
    obj_id = None
    update = False
    create = False
    # actual ID key name for update/delete operations
    ID_KEY = None

    def __init__(self, **kwargs):
        try:
            if self.ID_KEY in kwargs.keys():
                self.obj_id = kwargs[self.ID_KEY]
            for item in kwargs.keys():
                if item in self.fields:
                    setattr(self, item, kwargs[item])
                elif item in self.sub_items:
                    # rename item to class name
                    item_name = list(item)
                    item_name[0] = item_name[0].upper()
                    del item_name[len(item_name)-1]
                    item_name = ''.join(item_name)
                    sub_item_list = [ getattr(sys.modules[__name__] ,item_name)(**x) for x in kwargs[item]]
                    setattr(self, item, sub_item_list)
                else:
                    setattr(self, item, None)
        except KeyError as error:
            raise exceptions.ZabbixPropertyException(error)


    # parse data into object
    def get_obj_data(self, id_req=False):
        obj_data =  {key: self.__dict__[key] for key in self.fields if self.__dict__[key]}
        if id_req:
            obj_data[self.ID_KEY] = self.obj_id
        return obj_data

    # sanity check that item will be valid in new config state
    def verify_integrity(self, zab_server):
        pass

    # returns self and self.update for easy sorting
    def is_changed(self, other_obj):
        if self.get_obj_data(id_req=True) != other_obj.get_obj_data(id_req=True):
            self.update = True
        return self, self.update


class Item(ZabbixObject):

    TYPES = {
        'zabbix_agent': 0,
        'snmpv1_agent': 1,
        'zabbix_trapper': 2,
        'simple_check': 3,
        'snmpv2_agent': 4,
        'zabbix_internal': 5,
        'snmpv3_agent': 6,
        'zabbix_agent_active': 7,
        'zabbix_aggregate': 8,
        'web_item': 9,
        'external_check': 10,
        'database_monitor': 11,
        'ipmi_agent': 12,
        'ssh_agent': 13,
        'telnet_agent': 14,
        'calculated': 15,
        'jmx_agent': 16,
        'snmp_trap': 17,
        'dependant_item': 18,
        'http_agent': 19
    }

    ID_KEY = 'itemid'

    fields = [
        'type'
        'delay',
        'hostid',
        'interfaceid',
        'key_',
        'url',
        'allow_traps',
        'authtype',
        'description',
        'error',
        'follow_redirects',
        'headers',
        'history',
        'http_proxy',
        'jmx_endpoint',
        'output_format',
        'params',
        'password',
        'port',
        'post_type',
        'posts',
        'privatekey',
        'publickey',
        'query_fields',
        'request_method',
        'retrieve_mode',
        'snmp_community',
        'snmp_oid',
        'snmpv3_authpassphrase',
        'snmpv3_authprotocol',
        'snmpv3_ocntextname',
        'snmpv3_privpassphrase',
        'snmpv3_privprotocol',
        'snmpv3_securitylevel',
        'snmpv3_securityname',
        'ssl_cert_file',
        'ssl_key_file',
        'ssl_key_password',
        'status',
        'status_codes',
        'timeout',
        'trapper_hosts',
        'trends',
        'units',
        'username',
        'verify_host',
        'verify_peer'
    ]

    def __init__(self, name, **kwargs):
            super().__init__(**kwargs)


class Application(ZabbixObject):
    fields = [
        'hosid',
        'name'
    ]
    def __init__(self, name, **kwargs):
            super().__init__(**kwargs)

class Template(ZabbixObject):

    PARAM_MAP = {
        'templates': 'parentTemplates',
    }

    RETURN_ID_KEY = 'templateids'

    ID_KEY = 'templateid'

    sub_items = [
        'groups',
        'templates',
        'items',
        'applications',
        'triggers'
    ]

    fields = [
        'host',
        'description',
        'name'
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def sub_item_get(self):
        for item in sub_items:
            for obj in getattr(self, item):
                obj.get()


class Group(ZabbixObject):

    fields = [
        'name'
    ]
    ID_KEY = 'groupid'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

# tag sub object for Trigger
class Tag(ZabbixObject):
    fields = [
        'tag',
        'value'
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class Application(ZabbixObject):
    fields = [
        'tag',
        'value'
    ]
    ID_KEY = 'applicationid'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Trigger(ZabbixObject):
    fields = [
        'name',
        'description',
        'expression',
        'comments',
        'priority',
        'type',
        'url',
        'recovery_mode',
        'recovery_expression',
        'correlation_mode',
        'correlation_tag',
        'manual_close'
    ]
    # Trigger depedendencies
    sub_items = [
        'tags'
    ]
    ID_KEY = 'triggerid'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
