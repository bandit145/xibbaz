from zabbix_control.src.api import API
import zabbix_control.src.objects as objects
import logging

api = API('http://localhost','Admin','zabbix', logging)
api.login()

def test_create_group():
	group = objects.HostGroup('test_group', api, logging)
	assert group.ensure()
	assert not group.ensure()
	group.delete()
	# create for rest of tests
	assert group.ensure()

def test_create_template_empty():
	host_group_id = api.name_to_id('hostgroup', 'test_group')
	template = objects.Template('test_template_empty', None, None ,[{'groupid':host_group_id}] ,None, None, api, logging)
	assert template.ensure()
	assert not template.ensure()
	template.delete()
	assert template.ensure()




# def test_create_template():
# 	api = API('http://localhost','Admin','zabbix', logging)
# 	template = objects.Template('test_template', None, api, logging)
# 	logging.debug(type(template).__name__.lower())