import requests
import xibbaz.src.exceptions as exceptions


class API:

    GROUP_MAPS = {
        'hostgroup': {
            'id': 'groupid',
            'filter': 'name'
        },
        'template': {
            'id': 'templateid',
            'filter': 'name'
        },
        'item':{
            'id': 'itemid',
            'filter': 'name'
        },
        'trigger':{
            'id': 'triggerid',
            'filter': 'description'
        }
    }

    def __init__(self, server, username, password, logger, **kwargs):
        self.server = server
        self.username = username
        self.password = password
        self.auth = None
        self.request_num = 0
        self.session = requests.Session()
        if 'verify_tls' not in kwargs.keys():
            self.session.verify_tls = True
        else:
            self.session.verify_tls = verify_tls
        self.logger = logger

    def login(self):
        result = self.do_request(
            'user.login', {'user': self.username, 'password': self.password})
        self.auth = result

    def get_item(self, item, filter_list, **kwargs): 
        data = {'filter':{self.GROUP_MAPS[item]['filter']:filter_list}}
        return self.do_request(item+'.get', data, **kwargs)[0]

    def name_to_id(self, item, name):
        return int(self.get_item(item, name)[self.GROUP_MAPS[item]['id']])

    def item_exists(self, item, name):
        self.logger.debug('checking if item exists: '+str({'filter':{self.GROUP_MAPS[item]['filter']:[name]}}))
        response = self.do_request(item+'.get', {'filter':{self.GROUP_MAPS[item]['filter']:[name]}})
        if len(response) > 0:
            return True
        return False

    def do_request(self, method, data, **kwargs):
        self.request_num += 1
        data = {'jsonrpc':'2.0','method': method, 'params': data,'id':self.request_num, 'auth':self.auth}
        if kwargs['flags']:
            [setattr(data, x, True) for x in kwargs['flags']]
        if kwargs['selects']:
            [setattr(data, x, 'extend') for x in kwargs['selects']]
        self.logger.debug(data)
        response = self.session.post(self.server+'/api_jsonrpc.php', json=data)
        self.logger.debug(response.status_code)
        self.logger.debug(response.json())
        received_data = response.json()
        if 'error' in received_data:
            self.logger.debug(data)
            raise exceptions.ZabbixAPIException(received_data['error']['data']+' '+received_data['error']['message'])
        self.logger.debug(received_data['result'])
        return received_data['result']
