import zabbix_control.src.objects as objects
import zabbix_control.src.exceptions as exceptions

SUPPORTED_TYPES = [
	'Template',
	'HostGroup'
]


def get_objects(obj_type, obj_list, api):
	result_list = []
	if obj_typ not in SUPPORTED_TYPES:
		raise exceptions.ZabbixUnsupportedTypeException(obj_type+' Is not a supported type')
	for item in api.get_items(obj_type.lower(), obj_list):
		result_list.append(getattr(objects, obj_type)(**item))


def update_objects(obj_type, obj_list, api):
	update_list = [ x.get_obj_data() for x in obj_list ]
	api.massupdate(obj_type.lower(), update_list)
