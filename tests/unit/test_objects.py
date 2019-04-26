from xibbaz.src.objects import *
import mock_data
import logging


def test_template_object():
	zab_obj = Template(**mock_data.template_do_request)
	new_zab_obj = Template(**mock_data.template_do_request)
	unchanged_obj = Template(**mock_data.template_do_request)
	new_zab_obj.description = 'test'
	assert zab_obj.host == 'test_template1'
	assert zab_obj.items[0]['itemid'] == "28533"
	assert zab_obj.items[1]['itemid'] == "28534"
	assert zab_obj.is_changed(new_zab_obj)
	assert not zab_obj.is_changed(unchanged_obj)

	