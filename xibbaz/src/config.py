import yaml

def read_config(config, logger, output):
	try:
		with open(config, 'r') as config_file:
			return yaml.safe_load(config_file)
	except IOError: 
		output.error('Could not find config file')
	except yaml.YAMLError as error:
		output.error('Could not parse file, problem is: {prob}'.format(prob=str(error)))

# entry point
def build_config(config_file, logger, output):
	master_config = {}
	config = read_config(config, logger, output)
	if hasattr(config, 'include'):
		for file in config['include']:
			append_config = read_config(config, logger, output)
			config.update(append_config)
	master_config['zabbix_conf'] = config
	# build list of template names for reference
	master_config['templates'] = flatten_templates(master_config)
	master_config['triggers'] = flatten_triggers(master_config)
	check_template_issues(config)
	return master_config

def flatten_templates(config):
	return [x['name'] for x in config]

def flatten_triggers(config):
	trigs = []
	for template in config['zabbix_conf']['templates']:
		for trigger in template['triggers']:
			trigs.append('{template}:{trig}'.format(template=template['name'], trig=trigger['description']))
	return trigs

def check_template_issues(config, output):
	# TODO: add check for overridden triggers
	for template in config['zabbix_conf']['templates']:
		item_name_accum = [x['name'] for x in template['items']]
		item_key_accum = [x['key_'] for x in template['items']]
		#triggers
		template_run_list = template['templates'].copy()
		for cur_temp in template_run_list:
			cur_temp = config['zabbix_conf']['templates'][config['templates'].index(cur_temp)]
			if 'templates' in cur_temp.keys():
				# update loop var
				template_run_list = template_run_list + cur_temp['templates']
			for item in cur_temp['items']:
				if item['name'] in item_name_accum:
					output.error('Template: {base_temp} :item key {name} is in parent template {template}'.format(base_temp=template['name'], name=item['name'], cur_temp=cur_temp['name']))
				elif item['key_'] in item_key_accum:
					output.error('Template: {base_temp} :item key {key} is in parent template {template}'.format(base_temp=template['name'], key=item['key_'], cur_temp=cur_temp['name']))

			item_name_accum.append(item['name'])
			item_key_accum.append(item['key_'])
