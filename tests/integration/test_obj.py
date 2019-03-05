from zabbix_control.src.api import API
import zabbix_control.src.objects as objects
import logging


def test_create_group():
	api = API('http://localhost','Admin','zabbix', logging)
	api.login()
	group = objects.HostGroup('test_group', api, logging)
	assert group.ensure()
	#assert group.id


# def test_create_template():
# 	api = API('http://localhost','Admin','zabbix', logging)
# 	template = objects.Template('test_template', None, api, logging)
# 	logging.debug(type(template).__name__.lower())