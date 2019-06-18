

class ZabbixObject:

    fields = []
    sub_items = []
    item_dep_map ={}
    # key name zabbix returns on search
    PARAM_MAP = {}
    GET_SELECT = None
    RETURN_ID_KEY = None
    # actual ID key name for update/delete operations
    ID_KEY = None
    API_NAME = None
    # changed == True if needs update from client
    changed = False
    # remove checked if need removal
    remove = False

    def __init__(self, name, api, logger, **kwargs):
        for item in self.fields:
            self.__dict__[item] = None
        for item in self.sub_items:
            self.__dict__[item] = None
        self.id = None
        self.name = name
        self.api = api
        if 'type' in kwargs.keys():
            self.API_NAME = kwargs['type'].lower()
        else:
            self.API_NAME = type(self).__name__.lower()
        self.logger = logger

    # parse data into object
    def get_obj_data(self, id_req=False):
        obj_data =  {key: self.__dict__[key] for key in self.fields if self.__dict__[key]}
        if id_req:
            obj_data[self.ID_KEY] = self.obj_id
        return obj_data

    # ensure object exists and if a diff exists update it
    def diff(self, other_obj):
        if self.get_obj_data() != other_obj.get_obj_data():
            self.changed = True
        else:
            self.changed = False
        self.logger.debug('result:'+ str(self.changed))

    def create(self):
        self.id = int(self.api.do_request(self.API_NAME+'.create',self.get_obj_data())[self.RETURN_ID_KEY][0])

    def delete(self):
        self.api.do_request(self.API_NAME+'.delete', [self.id])

    def update(self):
        self.api.do_request(self.API_NAME+'.update', self.get_obj_data(id_req=True))

    def get_id(self):
        self.id = self.api.name_to_id(self.API_NAME, self.name)

    def build(self, info):
        for param in self.fields:
            self.logger.debug(param)
            if param in self.PARAM_MAP.keys():
                self.__dict__[param] = info[self.PARAM_MAP[param]]
            else:
                self.__dict__[param] = info[param]

    def get(self):
        self.logger.debug(str(self)+': getting data')
        # get_obj faciltates us being able to morph this class to contain anything we need
        # for diffing against full class objects
        # this supports getting this from kwargs as a testing hook (so you can test this class in isolation), you wouldn't need to use this for anything else
        response = self.api.get_item(self.API_NAME, self.name)
        if len(response) > 0:
            self.id = response[self.ID_KEY]
            self.logger.debug(response)
            self.build(response)
        else:
            raise exceptions.ZabbixException('{name} does not exist'.format(name=self.name))


class Item(ZabbixObject):

    ZABBIX_ITEM_TYPE = {
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

    def __init__(self, name, api, logger, **kwargs):
        try:
            super().__init__(name, api, logger)
            self.type = 0
            for item in self.fields():
                setattr(self, item, kwargs[item])
        except KeyError as error:
            raise exceptions.ZabbixPropertyException(error)


class Template(ZabbixObject):

    PARAM_MAP = {
        'templates': 'parentTemplates',
    }

    RETURN_ID_KEY = 'templateids'

    GET_SELECT = [
        'selectParentTemplates',
        'selectItems',
        'selectDiscoveries',
        'selectTriggers',
        'selectApplications'
    ]

    ID_KEY = 'templateid'

    sub_items = [
        'groups',
        'templates',
        'applications',
        'discoveries',
        'items',
        'applications',
        'triggers'
    ]

    fields = [
        'host',
        'groups',
        'templates',
        'macros'
    ]

    def __init__(self, name, linked_templates, applications ,groups, items, triggers, api, logger):
        super().__init__(name, api, logger)
        self.item = items
        self.triggers = triggers
        self.templates = linked_templates
        self.host = name
        self.groups = groups

    def sub_item_get(self):
        for item in sub_items:
            for obj in getattr(self, item):
                obj.get()

    def ensure(self):
        result = True
        if self.items:
            items_result = [x.ensure() for x in self.items]
        triggers_result = [x.ensure() for x in self.items if self.triggers]
        if True not in triggers_result and True not in items_result:
            result = False
        result = super().ensure()
        return result

    def get(self):
        super().get()
        self.templates = [Template(x['name'], api, logger).build(x) for x in self.templates]
        self.applications = [Application(x['name'], api, logger).build(x) for x in self.applications]
        self.discoveries = [Discovery(x['name'], api, logger).build(x) for x in self.discoveries]
        self.item = [Item(x['name'], api, logger).build(x) for x in self.items]
        self.triggers = [Trigger(x['name'], api, logger).build(x) for x in self.triggers]
        

class HostGroup(ZabbixObject):

    GET_SELECT = [
        'selectTemplates'
    ]

    sub_items = [
        'templates'
    ]

    fields = [
        'name'
    ]
    RETURN_ID_KEY ='groupids'
    ID_KEY = 'groupid'

    def __init__(self, name, api, logger):
        super().__init__(name, api, logger)

    def get(self):
        super().get()
        self.templates = [Template(x['name'], api, logger).get() for x in self.templates]

