import xibbaz.src.config as config
from unittest.mock import MagicMock
test_output = MagicMock()
yml_config = config.read_config('tests/test_zabbix.yml', test_output)

def test_flatten_template():
	assert config.flatten_templates(yml_config) == ['test_template', 'test3_template']
	assert config.flatten_triggers(yml_config) == ['test_template:test_trigger', 'test3_template:test3_trigger']

def test_check_template_issues():
	master_config = {}
	master_config['zabbix_conf'] = yml_config
	master_config['templates'] = config.flatten_templates(yml_config)
	master_config['triggers'] = config.flatten_triggers(yml_config)
	assert not config.check_template_issues(master_config, test_output)

def test_build_config():
	master_conf = config.build_config('tests/test_zabbix.yml', test_output)
	assert master_conf['templates'] == ['test_template', 'test3_template', 'test2_template']
	assert master_conf['triggers'] == ['test_template:test_trigger', 'test3_template:test3_trigger', 'test2_template:test2_trigger']