import requests
import sys
import zabbix_control.src.exceptions as exceptions

class API:

    GROUP_MAPS = {
        'hostgroup': {
            'id': 'groupid',
            'filter': 'name'
        }
    }

    def __init__(self, server, username, password, logger, **kwargs):
        self.server = server
        self.username = username
        self.password = password
        self.auth = None
        self.session = requests.Session()
        if 'verify_tls' not in kwargs.keys():
            self. verify_tls = True
        else:
            self.verify_tls = verify_tls
        self.logger = logger

    def login(self):
        self.auth = self.do_request(
            'user.login', {'user': self.username, 'password': self.password})[1]

    def name_to_id(self, item, name):
        return int(self.do_request(item+'.get', {'filter':{self.GROUP_MAPS[item]['filter']:[name]}})[1][0][self.GROUP_MAPS[item]['id']])

    def do_request(self, method, data):
        try:
            data = {'jsonrpc':'2.0','method': method, 'params': data,'id':1, 'auth':self.auth}
            response = self.session.post(self.server+'/api_jsonrpc.php', json=data)
            self.logger.debug(response.status_code)
            received_data = response.json()
            if 'error' in received_data:
                raise exceptions.ZabbixAPIException(received_data['error']['data']+' '+received_data['error']['message'])
            return 'success', received_data['result']
        except requests.exceptions.RequestException as error:
            return 'error', str(error)
        except exceptions.ZabbixAPIException as error:
            self.logger.error(error)
            return 'error', str(error)
