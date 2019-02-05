from zabbix_control.src.api import API
import logging


def test_do_request():
    api = API('http://localhost','','', logging)
    assert(api.do_request('apiinfo.version',{})) == ('success','4.0.3')


def test_login():
    user = 'Admin'
    password = 'zabbix'
    api = API('http://localhost', user, password, logging)
    assert(len(api.do_request('user.login',{'user':user,'password':password})[1])) == 32
    api.login()
    assert(len(api.auth)) == 32


def test_name_to_id():
    api = API('http://localhost', 'Admin', 'zabbix', logging)
    api.login()
    assert(api.name_to_id('hostgroup','Linux servers')) == 2

def test_error_return():
    api = API('http://localhost', 'Admin', 'zabbix', logging)
    api.login()
    assert(api.do_request('what',{})[0]) == 'error' 

def test_authenticated_do_request():
    api = API('http://localhost', 'Admin', 'zabbix', logging)
    api.login()
    assert(api.do_request('template.create',{'groups':{'groupid':2},'host':'test-template'}))[0] == 'success'
