class ZabbixObject:
    fields = []
    get_fields = []

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
        if self.api.item_exists(type(self).__name__.lower(),self.name):
            zabbix_obj = ZabbixObject(self.name, self.api, self.logger).get()
            if self.__dict__ != zabbix_obj.__dict__:
                self.update()
                return True
            else:
                return False
        else:
            self.create()
            return True

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


class Template(ZabbixObject):

    fields = [
        'templateid',
        'host',
        'description',
        'name',
        'groups',
        'templates',
        'macros'
    ]

    def __init__(self, name, linked_templates, api, logger):
        super().__init__(name, api, logger)
        self.templates = linked_templates


class HostGroup(ZabbixObject):

    fields = [
        'name'
    ]
    ID_KEY ='groupids'

    def __init__(self, name, api, logger):
        super().__init__(name, api, logger)
