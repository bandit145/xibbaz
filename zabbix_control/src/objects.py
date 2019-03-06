import zabbix_control.src.exceptions as exceptions

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
    # key name zabbix returns on search
    RETURN_ID_KEY = ''
    # actual ID key name for update/delete operations
    ID_KEY = ''

    def __init__(self, name, api, logger):
        for item in self.fields:
            self.__dict__[item] = None
        self.id = None
        self.name = name
        self. api = api
        self.logger = logger

    def get_obj_data(self, id_req=False):
        obj_data =  {key: self.__dict__[key] for key in self.fields if self.__dict__[key]}
        if id_req:
            obj_data[self.ID_KEY] = self.id
        return obj_data

    # ensure object exists and if a diff exists update it
    def ensure(self):
        result = True
        if self.api.item_exists(type(self).__name__.lower(), self.name):
            # since we do not use zabbix as the source of truth we pull the id at 
            # run time to prepare for a possible update (but not everything)
            self.id = self.api.name_to_id(type(self).__name__.lower(), self.name)
            zabbix_obj = ZabbixObject(self.name, self.api, self.logger)
            zabbix_obj.fields = self.fields
            zabbix_obj.get(type=type(self).__name__.lower())
            self.logger.debug('current obj: '+str(self.get_obj_data()))
            self.logger.debug('zabbix server object: '+str(zabbix_obj.get_obj_data()))
            if self.get_obj_data() != zabbix_obj.get_obj_data():
                self.update()
            else:
                result = False
        else:
            self.create()
        self.logger.debug('result:'+ str(result))
        return result

    def create(self):
        self.id = self.api.do_request(type(self).__name__.lower()+'.create',self.get_obj_data())[self.RETURN_ID_KEY][0]

    def delete(self):
        self.api.do_request(type(self).__name__.lower()+'.delete', [self.id])

    def update(self):
        self.api.do_request(type(self).__name__.lower()+'.update', self.get_obj_data(id_req=True))

    def get(self, **kwargs):
        self.logger.debug(str(self)+': getting data')
        # get_obj faciltates us being able to morph this class to contain anything we need
        # for diffing against full class objects
        if 'type' in kwargs.keys():
            get_obj = kwargs['type']
        else:
            get_obj = type(self).__name__.lower()
        self.id = self.api.name_to_id(get_obj, self.name)
        if self.api.item_exists(get_obj, self.name):
            response = self.api.get_item(get_obj, self.name)
            for param in self.fields:
                self.__dict__[param] = response[param]


class ZabbixItem(ZabbixObject):

    def __init__(self, name, api, logger, **kwargs):
        self.type = None
        super().__init__(name, api, logger)
        for item in kwargs.keys():
            if item in self.fields:
                setattr(self, item, kwargs[item])


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

    def __init__(self, name, api, logger, **kwargs):
        try:
            super().__init__(name, api, logger)
            self.type = 0
            for item in self.fields():
                setattr(self, item, kwargs[item])
        except KeyError as error:
            raise exceptions.ZabbixPropertyException(error)

class SNMPItem(ZabbixObject):

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
            super().__init__(name, api, logger)
            for item in self.fields():
                setattr(self, item, kwargs[item])
        except KeyError as error:
            raise exceptions.ZabbixPropertyException(error)



class Template(ZabbixObject):

    RETURN_ID_KEY = 'templateids'

    ID_KEY = 'templateid'

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
    groups = []

    def __init__(self, name, linked_templates, groups, items, triggers, api, logger):
        super().__init__(name, api, logger)
        self.item = items
        self.triggers = triggers
        self.templates = linked_templates
        self.host = name
        self.groups = groups

    def ensure(self):
        result = True
        items_result = [ x.ensure() for x in self.items ]
        triggers_result = [ x.ensure() for x in self.items ]
        if True not in triggers_result and True not in items_result:
            result = False
        result = super().ensure()
        return result


class HostGroup(ZabbixObject):

    fields = [
        'name'
    ]
    RETURN_ID_KEY ='groupids'
    ID_KEY = 'groupid'

    def __init__(self, name, api, logger):
        super().__init__(name, api, logger)
