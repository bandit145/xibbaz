import xibbaz.src.exceptions as exceptions
import copy

class ZabbixObject:

    fields = []
    sub_items = []
    item_dep_map ={}
    # key name zabbix returns on search
    PARAM_MAP = {}
    GET_SELECT = None
    GET_FLAGS = None
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
        obj_data =  {key: self.__dict__[key] for key in self.fields if self.__dict__[key] and key not in self.sub_items}
        if id_req:
            obj_data[self.ID_KEY] = self.obj_id
        return obj_data

    # ensure object exists and if a diff exists update it
    def diff(self, other_obj):
        if self.get_obj_data() != other_obj.get_obj_data():
            self.changed = True
        else:
            self.changed = False
        return self.changed
        self.logger.debug('result:'+ str(self.changed))

    def __eq__(self, other_obj):
        return self.diff(other_obj)

    def create(self):
        self.id = int(self.api.do_request(self.API_NAME+'.create',self.get_obj_data())[self.RETURN_ID_KEY][0])

    def delete(self):
        self.api.do_request(self.API_NAME+'.delete', [self.id])

    def update(self):
        self.api.do_request(self.API_NAME+'.update', self.get_obj_data(id_req=True))

    def get_id(self):
        self.id = self.api.name_to_id(self.API_NAME, self.name)

    def generate_config(self):
        return self.get_obj_data()

    def build(self, info):
        combined_fields = self.fields + self.sub_items
        for param in combined_fields:
            self.logger.debug(param)
            if param in self.fields or param in self.sub_items:
                if param in self.PARAM_MAP.keys():
                    self.__dict__[param] = info[self.PARAM_MAP[param]]
                else:   
                    self.__dict__[param] = info[param]

    def get(self):
        self.logger.debug(str(self)+': getting data')
        response = self.api.get_item(self.API_NAME, self.name, selects=self.GET_SELECT, flags=self.GET_FLAGS)
        if len(response) > 0:
            self.id = int(response[self.ID_KEY])
            self.logger.debug(response)
            self.build(response)
        else:
            raise exceptions.ZabbixException('{name} does not exist'.format(name=self.name))

# rewrite to work down the tree and generate the config
class Configuration(ZabbixObject):

    fields = [
        'format',
        'source',
        'rules'
    ]

    RULES = {
            'applications': {'createMissing': False, 'deleteMissing': False},
            'discoveryRules': {'createMissing': True, 'updateExisting': True, 'deleteMissing': True},
            'httptests': {'createMissing': True, 'updateExisting': True, 'deleteMissing': True},
            'items': {'createMissing': True, 'updateExisting': True, 'deleteMissing': True},
            'templates': {'createMissing': True, 'updateExisting': True, 'deleteMissing': True},
            'triggers': {'createMissing': True, 'updateExisting': True, 'deleteMissing': True},
        }

    def __init__(self, source, api, logger):
        super().__init__(None, api, logger)
        self.raw_source = self.source
        self.int_conf = self.g

    def generate_internal_conf(self):
        self.int_conf = {}
        for key, value in self.raw_source:
            if key.lower() == 'templates':
                self.int_conf['templates'] = [Template(x['name'], x['groups'], self.api, self.logger).build(x) for x in new_source['templates']]

    def generate_zabbix_conf(self):
        zabbix_conf = {}
        zabbix_conf['templates'] = [x.generate_config() for x in self.int_conf['templates']]
        return zabbix_conf

    def apply(self):
        self.api.do_request(self.API_NAME+'.import', self.generate_zabbix_conf)

    def gather(self):
        response = self.api.get_item(self.API_NAME+'.export')

    def __get_template_ids__(self):
        response = self.api.do_request('template.get', {})
        return[x['templateid'] for x in response]

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
        'triggers',
        'macros'
    ]

    fields = [
        'host',
        'groups',
    ]

    def __init__(self, name, groups, api, logger):
        super().__init__(name, api, logger)
        self.host = name
        self.groups = groups

    def sub_item_get(self):
        for item in sub_items:
            for obj in getattr(self, item):
                obj.get()
    #check if equal
    def __eq__(other_obj):
        # return list of sub items that we will check for changes
        template_change = []
        changed_sub_items = {
            'templates': None,
            'applications': None, 
            'discoveries': None, 
            'items': None, 
            'macros': None,
            'triggers': None
        }
        template_change[0] = super().diff(other_obj)
        #if self.templates and templates.

    def generate_config(self):
        data_dump = self.get_obj_data()
        for item in self.sub_items:
            if getattr(self, item):
                data_dump[item] = [x.generate_config() for x in getattr(self, item)]
        return data_dump

    # TODO: Fix these by checking if they are none and use the required constructor args
    def build(self, info):
        super().build(info)
        if self.templates:
            self.templates = [Template(x['name'], self.api, self.logger).build(x) for x in self.templates]
        if self.applications:
            self.applications = [Application(x['name'], self.api, self.logger).build(x) for x in self.applications]
        #if self.discoveries:
        #    self.discoveries = [Discovery(x['name'], self.api, self.logger).build(x) for x in self.discoveries]
        if self.items:
            self.items = [Item(x['name'], self.api, self.logger).build(x) for x in self.items]
        if self.macros:
            self.macros = [Macro(x['name'], self.api, self.logger).build(x) for x in self.macros]
        if self.triggers:
            self.triggers = [Trigger(x['name'], self.api, self.logger).build(x) for x in self.triggers]

    def get(self):
        super().get()
        if self.templates:
            self.templates = [Template(x['name'], self.api, self.logger).build(x) for x in self.templates]
        if self.applications:
            self.applications = [Application(x['name'], self.api, self.logger).build(x) for x in self.applications]
        #if self.discoveries:
        #    self.discoveries = [Discovery(x['name'], self.api, self.logger).build(x) for x in self.discoveries]
        if self.items:
            self.items = [Item(x['name'], self.api, self.logger).build(x) for x in self.items]
        if self.macros:
            self.macros = [Macro(x['name'], self.api, self.logger).build(x) for x in self.macros]
        if self.triggers:
            self.triggers = [Trigger(x['name'], self.api, self.logger).build(x) for x in self.triggers]

class Trigger(ZabbixObject):

    RETURN_ID_KEY ='triggerids'
    ID_KEY = 'triggerid'
    GET_SELECT = [
        'selectTags',
    ]
    TRIGGER_PRIORITY = {
        '0':'not classified',
        'not classified': 0,
        '1': 'information',
        'information': 1,
        '2': 'warning',
        'warning': 2,
        '3': 'average',
        'average': 3,
        '4': 'high',
        'high': 4,
        '5': 'disaster',
        'disaster': 5
    }
    TRIGGER_STATUS = {
        '0': 'enabled',
        'enabled': 0,
        '1': 'disabled',
        'disabled': 1
    }
    TRIGGER_TYPE = {
        '0': 'single event',
        'single event': 0,
        '1': 'multiple events',
        'multiple events': 1
    }
    TRIGGER_RECOVERY_MODE = {
        '0': 'default',
        'default': 0,
        '1': 'recovery_expression',
        'recovery_expression': 1,
        '2': 'none',
        'none': 2
    }
    TRIGGER_MANUAL_CLOSE = {
        '0': 'no',
        'no': 0,
        '1': 'yes',
        'yes': 1
    }

    # sub_items = [
    #     'templates'
    # ]

    fields = [
        'description',
        'expression',
        'comments',
        'priority',
        'status',
        'type',
        'url',
        'recovery_mode',
        'recovery_expression',
        'correlation_mode',
        'correlation_tag',
        'manual_close',
        'tags'
    ]

    def __init__(self, name, expression, api, logger):
        self.description = self.name
        self.expression = expression
        super().__init__(name, api, logger)

    def get(self):
        self.expand
        super().get()


        
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

class ValueMap(ZabbixObject):

    GET_SELECT = [
        'selectMappings'
    ]

    fields = [
        'mappings',
        'name'
    ]
    RETURN_ID_KEY ='valuemapids'
    ID_KEY = 'valuemapid'

    def __init__(self, name, api, logger):
        super().__init__(name, api, logger)

class Macro(ZabbixObject):
    specific_item_fields = [

    ]
    fields = [
        'value',
        'macro'
    ]

    def __init__(self, name, value, api, logger):
        self.fields.extend(self.specific_item_fields)
        super().__init__(name, api, logger)
        self.macro = name
        self.value = value

class HostMacro(ZabbixObject):
    RETURN_ID_KEY ='hostmacroids'
    ID_KEY = 'hostmacroid'
    specific_item_fields = [
        'hostmacroid'
    ]

    def __init__(self, name, api, logger):
        super().__init__(name, api, logger, type='usermacro')

class GlobalMacro(ZabbixObject):
    RETURN_ID_KEY ='globalmacroids'
    ID_KEY = 'globalmacroid'
    fields = [
        'value',
        'macro'
    ]
    specific_item_fields = [
        'globalmacroid'
    ]

    def __init__(self, name, value, api, logger):
        super().__init__(name, api, logger, type='usermacro')
        self.macro = name
        self.value = value

    def create(self):
        self.id = int(self.api.do_request(self.API_NAME+'.createglobal',self.get_obj_data())[self.RETURN_ID_KEY][0])

    def delete(self):
        self.api.do_request(self.API_NAME+'.deleteglobal', [self.id])

    def update(self):
        self.api.do_request(self.API_NAME+'.updateglobal', self.get_obj_data(id_req=True))

# zabbix items
class Item(ZabbixObject):
    ID_KEY = 'itemid'
    GET_SELECT = [
        'selectApplications'
    ]
    RETURN_ID_KEY = 'itemids'
    ZABBIX_ITEM_TYPE = None
    VALUE_TYPES = {
        'numeric (unsigned)': 3,
        "3": 'numeric (unsigned)',
        'numeric (float)': 0,
        '0':'numeric (float)',
        'character': 1,
        '1': 'character',
        'log': 2,
        '2': 'log',
        'text': 4,
        '4' :'text'
    }

    specific_item_fields = [

    ]

    fields = [
        'name',
        'key_',
        'value_type',
        'delay',
        'type',
        'applications',
        'history',
        'trends',
        'description',
        'valuemapid',
        'units'
    ]

    def __init__(self, name, api, logger, **kwargs):
        self.fields.extend(self.specific_item_fields)
        super().__init__(name, api, logger, type='item')

    def create(self):
        # patch ints into fields
        tmp_fields = self.fields.copy()
        self.value_type = self.VALUE_TYPES[self.value_type]
        super().create()
        self.fields = tmp_fields

    def get(self):
        super().get()
        # patch names into value_type 
        self.value_type = self.VALUE_TYPES[self.value_type]

class ZabbixAgentItem(Item):

    ZABBIX_ITEM_TYPE = 0

    def __init__(self, name, api, logger, **kwargs):
        super().__init__(name, api, logger, type='item')

class SNMPV1AgentItem(Item):

    ZABBIX_ITEM_TYPE = 1
    specific_item_fields = [
        'snmp_oid',
        'snmp_community',
        'port'
    ]

    def __init__(self, name, api, logger, **kwargs):
        super().__init__(name, api, logger, type='item')

class ZabbixTrapperItem(Item):

    ZABBIX_ITEM_TYPE = 2
    specific_item_fields = [
        'trapper_hosts'
    ]

    def __init__(self, name, api, logger, **kwargs):
        super().__init__(name, api, logger, type='item')

class SimpleCheckItem(Item):

    ZABBIX_ITEM_TYPE = 3
    specific_item_fields = [
        'username',
        'password'
    ]

    def __init__(self, name, api, logger, **kwargs):
        super().__init__(name, api, logger, type='item')

class SNMPV2AgentItem(Item):

    ZABBIX_ITEM_TYPE = 4
    specific_item_fields = [
        'port',
        'snmp_oid',
        'snmp_community'
    ]

    def __init__(self, name, api, logger, **kwargs):
        super().__init__(name, api, logger, type='item')

class ZabbixInternalItem(Item):

    ZABBIX_ITEM_TYPE = 5

    def __init__(self, name, api, logger, **kwargs):
        super().__init__(name, api, logger, type='item')

class SNMPV3AgentItem(Item):

    ZABBIX_ITEM_TYPE = 6
    specific_item_fields = [
        'port',
        'snmp_oid',
        'snmp_community',
        'snmpv3_authprotocol',
        'snmpv3_privprotocol',
        'snmpv3_contextname',
        'snmpv3_securitylevel',
        'snmpv3_authpassphrase',
        'snmpv3_privpassphrase'
    ]

    def __init__(self, name, api, logger, **kwargs):
        super().__init__(name, api, logger, type='item')

class ZabbixAgentActiveItem(Item):

    ZABBIX_ITEM_TYPE = 7

    def __init__(self, name, api, logger, **kwargs):
        super().__init__(name, api, logger, type='item')

class ZabbixAggregateItem(Item):

    ZABBIX_ITEM_TYPE = 8

    def __init__(self, name, api, logger, **kwargs):
        super().__init__(name, api, logger, type='item')

class ExternalCheckItem(Item):

    ZABBIX_ITEM_TYPE = 10

    def __init__(self, name, api, logger, **kwargs):
        super().__init__(name, api, logger, type='item')

class DatabaseMonitorItem(Item):

    ZABBIX_ITEM_TYPE = 11
    specific_item_fields = [
        'username',
        'password',
        'params'
    ]

    def __init__(self, name, api, logger, **kwargs):
        super().__init__(name, api, logger, type='item')

class IPMIAgentItem(Item):

    ZABBIX_ITEM_TYPE = 12
    specific_item_fields = [
        'ipmi_sensor'
    ]

    def __init__(self, name, api, logger, **kwargs):
        super().__init__(name, api, logger, type='item')

class SSHAgentItem(Item):

    ZABBIX_ITEM_TYPE = 13
    specific_item_fields = [
        'params',
        'username',
        'password',
        'publickey',
        'privatekey'
    ]

    def __init__(self, name, api, logger, **kwargs):
        super().__init__(name, api, logger, type='item')

class TelnetAgentItem(Item):

    ZABBIX_ITEM_TYPE = 14
    specific_item_fields = [
        'username',
        'password',
        'params'
    ]

    def __init__(self, name, api, logger, **kwargs):
        super().__init__(name, api, logger, type='item')

class CalculatedItem(Item):

    ZABBIX_ITEM_TYPE = 15
    specific_item_fields = [
        'formula'
    ]

    def __init__(self, name, api, logger, **kwargs):
        super().__init__(name, api, logger, type='item')

class JMXAgentItem(Item):

    ZABBIX_ITEM_TYPE = 16
    specific_item_fields = [
        'jmx_endpoint',
        'username',
        'password'
    ]

    def __init__(self, name, api, logger, **kwargs):
        super().__init__(name, api, logger, type='item')

class SNMPTrapItem(Item):

    ZABBIX_ITEM_TYPE = 17

    def __init__(self, name, api, logger, **kwargs):
        super().__init__(name, api, logger, type='item')

class DependantItem(Item):

    ZABBIX_ITEM_TYPE = 18
    specific_item_fields = [
        'master_itemid'
    ]

    def __init__(self, name, api, logger, **kwargs):
        super().__init__(name, api, logger, type='item')    

class HTTPAgentItem(Item):

    ZABBIX_ITEM_TYPE = 19
    specific_item_fields = [
        'url',
        'query_fields',
        'request_method',
        'timeout',
        'post_type',
        'posts',
        'headers',
        'status_codes',
        'follow_redirects',
        'retrive_mode',
        'output_format',
        'http_proxy',
        'verify_peer',
        'verify_host',
        'ssl_cert_file',
        'ssl_key_file',
        'ssl_key_password',
        'allow_traps',
        'trapper_hosts'

    ]

    def __init__(self, name, api, logger, **kwargs):
        super().__init__(name, api, logger, type='item')

