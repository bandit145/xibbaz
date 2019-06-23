from xibbaz.src.objects import *
from unittest.mock import MagicMock
import mock_data
from xibbaz.src.api import API
import logging
import copy

def init_zabbixtemplate_obj(mock_api):
	zab_obj = ZabbixObject('test_template1', mock_api, logging, type='template')
	zab_obj.PARAM_MAP = Template.PARAM_MAP
	zab_obj.RETURN_ID_KEY = Template.RETURN_ID_KEY
	zab_obj.GET_SELECT = Template.GET_SELECT
	zab_obj.ID_KEY = Template.ID_KEY
	zab_obj.sub_items = Template.sub_items
	zab_obj.fields = Template.fields
	return zab_obj

def test_zabbix_object_id():
	mock_api = API('zabbix.com','admin', 'password', logging)
	mock_api.do_request = MagicMock(return_value=mock_data.template_do_request)
	zab_obj = init_zabbixtemplate_obj(mock_api)
	zab_obj.get_id()
	assert zab_obj.id == 10261

def test_zabbix_object_get():
	mock_api = API('zabbix.com','admin', 'password', logging)
	mock_api.do_request = MagicMock(return_value=mock_data.template_do_request)
	zab_obj = init_zabbixtemplate_obj(mock_api)
	zab_obj.get()
	assert zab_obj.host == 'test_template1'
	assert zab_obj.groups[0]['groupid'] == '2'

def test_zabbix_object_create():
	mock_api = API('zabbix.com','admin', 'password', logging)
	mock_api.do_request = MagicMock(return_value={'templateids':["10261"]})
	zab_obj = init_zabbixtemplate_obj(mock_api)
	zab_obj.host = 'random_template'
	zab_obj.groups = {'groupid': 1}
	zab_obj.templates = None
	zab_obj.macros = None
	zab_obj.create()
	assert zab_obj.id == 10261

def test_zabbix_object_diffing():
	mock_api = API('zabbix.com','admin', 'password', logging)
	diff_api = API('zabbix.com','admin', 'password', logging)
	mock_api.do_request = MagicMock(return_value=copy.deepcopy(mock_data.template_do_request))
	diff_api.do_request = MagicMock(return_value=copy.deepcopy(mock_data.template_do_request))
	zab_obj  = init_zabbixtemplate_obj(mock_api)
	diff_obj = init_zabbixtemplate_obj(diff_api)
	
	zab_obj.get()
	diff_obj.get()
	#zab_obj.description = 'random_test_template'
	# mock_api.item_exists = MagicMock(return_value=True)
	# mock_api.get_item = MagicMock(return_value=mock_data.template_do_request[0])
	#mock_api.name_to_id = MagicMock(return_value='10261')
	assert zab_obj.get_obj_data() == diff_obj.get_obj_data()
	zab_obj.diff(diff_obj)
	assert not zab_obj.changed
	del diff_obj.groups[0]
	assert zab_obj.get_obj_data() != diff_obj.get_obj_data()
	zab_obj.diff(diff_obj)
	assert zab_obj.changed

def test_zabbix_item_obj():
	mock_api = API('zabbix.com','admin', 'password', logging)
	mock_api.do_request = MagicMock(return_value=mock_data.item_do_request)
	item_obj = Item('testitem', mock_api, logging)
	item_obj.get()
	assert item_obj.name == 'testitem'
	assert item_obj.id == 28534
	assert item_obj.value_type == 'numeric (unsigned)'

def test_zabbix_item_create():
	mock_api = API('zabbix.com','admin', 'password', logging)
	mock_api.do_request = MagicMock(return_value={'itemids':['28534']})
	item_obj = Item('testitem', mock_api, logging)
	item_obj.value_type = 'numeric (unsigned)'
	item_obj.create()
	assert item_obj.id == 28534


def test_zabbix_item_diffing():
	pass

