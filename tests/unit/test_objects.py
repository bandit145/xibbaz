from xibbaz.src.objects import *
from unittest.mock import MagicMock
import mock_data
from xibbaz.src.api import API
import logging


def test_zabbix_object():
	mock_api = API('zabbix.com','admin', 'password', logging)
	mock_api.do_request = MagicMock(return_value=mock_data.template_do_request)
	zab_obj = ZabbixObject('test_template1', mock_api, logging)
	zab_obj.PARAM_MAP = {
		'templates': 'parentTemplates'
	}
	zab_obj.RETURN_ID_KEY = 'templateids'

	zab_obj.GET_SELECT = [
		'selectParentTemplates',
		'selectItems',
		'selectDiscoveries',
		'selectTriggers',
		'selectApplications'
	]
	zab_obj.ID_KEY = 'templateid'

	zab_obj.sub_items = [
		'groups',
		'templates',
		'applications',
		'discoveries',
		'items',
		'triggers'
	]

	zab_obj.fields = [
		'host',
		'description',
		'name',
		'groups',
		'templates',
		'macros',
		'applications',
		'discoveries',
		'items',
		'triggers'
	]
	zab_obj.get(type='template')
	assert zab_obj.host == 'test_template1'
	assert zab_obj.items[0]['itemid'] == "28533"
	assert zab_obj.items[1]['itemid'] == "28534"
	zab_obj.description = 'random_test_template'
	# mock_api.item_exists = MagicMock(return_value=True)
	# mock_api.get_item = MagicMock(return_value=mock_data.template_do_request[0])
	mock_api.name_to_id = MagicMock(return_value='10261')
	assert zab_obj.ensure(type='template')

	