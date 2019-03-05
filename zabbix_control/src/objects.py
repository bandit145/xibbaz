import zabbix_control.src.excptions as exceptions

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

    def __init__(self, name, api, logger):
        for item in self.fields:
            self.__dict__[item] = None
        self.id = None
        self.name = name
        self. api = api
        self.logger = logger

    def get_obj_data(self):
        return {key: self.__dict__[key] for key in self.fields}

    def ensure(self):
        result = True
        if self.api.item_exists(type(self).__name__.lower(),self.name):
            zabbix_obj = ZabbixObject(self.name, self.api, self.logger).get()
            if self.__dict__ != zabbix_obj.__dict__:
                self.update()
            else:
                result = False
        else:
            self.create()
        return result

    def create(self):
        self.id = self.api.do_request(type(self).__name__.lower()+'.create',self.get_obj_data())[self.ID_KEY][0]

    def delete(self):
        self.api.do_request(type(self).__name__.lower()+'.delete', self.get_obj_data())

    def update(self):
        self.api.do_request(type(self).__name__.lower(), self.get_obj_data())

    def get(self):
        if self.api.item_exists(str(self).lower(), self.name):
            response = self.api.get_item(str(self), self.name)
            for param in response.keys():
                self.__dict__[param] = response[param]


class ZabbixItem(ZabbixObject):
    self.type = None

    def __init__(self, name, api, logger, **kwargs):
        super().__init__(name, api, logger)
        for item in kwargs.keys():
            if item in self.fields:
                setattr(self, item, kwargs[item])


class ZabbixAgentItem(ZabbixItem):

    self.type = 0
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

    def __init__(self, name, api, logger, **kwargs):
        try:
            super().__init__(name, api, logger)
            for item in self.fields():
                setattr(self, item, kwargs[item])
        except KeyError as error:
            raise exceptions.ZabbixPropertyException(error)

class ZabbixSNMPItem(ZabbixObject):

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
        try:
            if kwargs
            super().__init__(name, api, logger)
            for item in self.fields():
                setattr(self, item, kwargs[item])
        except KeyError as error:
            raise exceptions.ZabbixPropertyException(error)



class Template(ZabbixObject):

    fields = [
        'host',
        'description',
        'name',
        'groups',
        'templates',
        'macros'
    ]
    items = []
    triggers = []

    def __init__(self, name, linked_templates, items, triggers, api, logger):
        super().__init__(name, api, logger)
        self.item = items
        self.triggers = triggers
        self.templates = linked_templates

    def ensure(self):
        result = True
        items_result = [ x.ensure() for x in self.items ]
        triggers_result = [ x.ensure() for x in self.items ]
        if True not in triggers_result and True not in items_result:
            result = False
        if self.api.item_exists(type(self).__name__.lower(),self.name):
            zabbix_obj = ZabbixObject(self.name, self.api, self.logger).get()
            if self.__dict__ != zabbix_obj.__dict__:
                self.update()
            else:
                result = False
        else:
            self.create()
        return result


class HostGroup(ZabbixObject):

    fields = [
        'name'
    ]
    ID_KEY ='groupids'

    def __init__(self, name, api, logger):
        super().__init__(name, api, logger)
