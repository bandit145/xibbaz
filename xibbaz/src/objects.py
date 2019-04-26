import xibbaz.src.exceptions as exceptions

ZABBIX_ITEM_TYPES = {
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


class ZabbixObject:

    fields = []
    sub_items = []
    # key name zabbix returns on search
    PARAM_MAP = {}
    RETURN_ID_KEY = None
    # actual ID key name for update/delete operations
    ID_KEY = None

    def __init__(self, **kwargs):
        try:
            for item in self.fields:
                self.__dict__[item] = None
            self.id = None
            for item in kwargs.keys():
                if item in self.fields:
                    setattr(self, item, kwargs[item])
                elif item in self.sub_items:
                    # rename item to class name
                    item_name = item
                    item_name[0] = item_name[0].upper()
                    del item_name[len(item_name)-1]
                    sub_item_list = [ getattr(item_name)(**x) for x in kwargs['item']]
                    setattr(self, item, sub_item_list)
        except KeyError as error:
            raise exceptions.ZabbixPropertyException(error)

    # parse data into object
    def get_obj_data(self, id_req=False):
        obj_data =  {key: self.__dict__[key] for key in self.fields if self.__dict__[key]}
        if id_req:
            obj_data[self.ID_KEY] = self.id
        return obj_data

    def is_changed(self, other_obj):
        if self.get_obj_data() != other_obj.get_obj_data():
            return True
        return False


class ZabbixItem(ZabbixObject):

    def __init__(self, name, **kwargs):
            super().__init__(name, **kwargs)
            self.type = None



class AgentItem(ZabbixItem):

    fields = [
        'delay',
        'key_',
        'hostid',
        'name',
        'type',
        'value_type',
        'description',
        'history',
        'inventory_link',
        'master_itemid'
        'status',
        'applications',
        'preprocessing'
    ]

    def __init__(self, name, **kwargs):
        super().__init__(name, api, **kwargs)
        self.type = 0



class SNMPV1Item(ZabbixObject):

    fields = [
        'delay',
        'name',
        'type',
        'value_type',
        'description',
        'history',
        'inventory_link',
        'master_itemid',
        'status',
        'snmp_community',
        'snmp_oid',
        'applications',
        'preprocessing'
    ]

    #implements own init for snmp v1 vs v2
    def __init__(self, name, api, logger, **kwargs):
            super().__init__(name, api, logger)
            self.type = 1
           


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
        'triggers'
    ]

    fields = [
        'host',
        'description',
        'name',
        'groups',
        'templates',
        'macros'
        'discoveries',
        'items',
        'triggers'
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
        'triggers',
        'tags'
    ]
    ID_KEY = 'triggerid'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
