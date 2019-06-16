from xibbaz.src.objects import *
import mock_data
import logging


def test_template_object():
	zab_obj = Template(**mock_data.template_do_request)
	new_zab_obj = Template(**mock_data.template_do_request)
	new_zab_obj.description = 'test'
	assert zab_obj.host == 'test_template1'
	logging.debug(zab_obj.items[0].__dict__)
	assert zab_obj.items[0].obj_id == "28533"
	assert zab_obj.items[1].obj_id == "28534"
	assert zab_obj.is_changed(new_zab_obj)[0].update
	zab_obj = Template(**mock_data.template_do_request)
	assert not zab_obj.is_changed(zab_obj)[1]

	