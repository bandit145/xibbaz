import yaml
import copy
import xibbaz.src.objects as objects

def read_config(config, output):
	try:
		with open(config, 'r') as config_file:
			return yaml.safe_load(config_file)
	except IOError: 
		output.error('Could not find config file')
	except yaml.YAMLError as error:
		output.error('Could not parse file, problem is: {prob}'.format(prob=str(error)))

def merge_config(old_config, new_config, filename, output):
	config = copy.deepcopy(old_config)
	del config['include']
	for item in new_config.keys():
		if item == 'actions' or item == 'templates':
			for setting in new_config[item]:
				check_section_conflict('name', item, setting, filename, config, output)
				if item not in config:
					config[item] = setting
				else:
					config[item].append(setting)
		elif item == 'global_macros':
			for macro in new_config['global_macros']:
				check_section_conflict('macro', item, setting, filename, config, output)
				if item not in config:
					config[item] = macro
				else:
					config[item].append(macro)
		elif item == 'host_groups':
			if item not in config.keys():
				config[item] = new_config[item]
			else:
				config[item] = config[item] + new_config[item]
	return config

def check_section_conflict(value, item, setting, filename, config, output):
	if setting[value] in [x[value] for x in config[item]]:
		output.error('{item} conflict in {file}'.format(item=item, file=filename))

# entry point
def build_config(config_file, api, logger, output):
	master_config = {}
	config = read_config(config_file, output)
	if 'include' in config.keys():
		for file in config['include']:
			append_config = read_config(file, output)
			config = merge_config(config, append_config, file, output)
	master_config['zabbix_conf'] = objectize_config(config)
	# build list of template names for reference
	master_config['template_names'] = flatten_templates(config)
	master_config['trigger_names'] = flatten_triggers(config)
	check_template_issues(master_config, output)
	return master_config

def objectize_config(config, api, logger):
	new_config = {}
	conf_keys = config.keys()
	new_config['host_groups'] = [objects.HostGroup(x, api, logger) for x in config['host_groups']]
	if 'global_macros' in conf_keys:
		new_config['global_macros'] = [objects.GlobalMacro(x['name'], x['macro'], api, logger) for x in config['global_macros']]
	if 'templates' in conf_keys:
		new_config['templates'] = [objectize_template(x, new_config, api, logger) for x in config['templates']]

def objectize_template(template, new_config, api, logger):
	temp_keys = template.keys()
	member_groups = [x.name for x in new_config['host_groups'] if x.name in template['host_groups']]
	new_temp = objects.Template(template['name'], member_groups)
	if 'macros' in temp_keys:
		new_temp.macros = [objects.Macro(x['macro'], x['value']) for x in template['macros']]
	if 'triggers' in temp_keys:
		new_temp.triggers = [objectize_trigger(x, api, logger) for x in template['triggers']]

# TODO: maybe look at rewriting the objects module to support kwargs everything in init	
def objectize_trigger(trigger, api, logger):
	# new_trig = objects.Trigger(trigger['name'])
	pass

def flatten_templates(config):
	return [x['name'] for x in config['templates']]

def flatten_triggers(config):
	trigs = []
	for template in config['templates']:
		for trigger in template['triggers']:
			trigs.append('{template}:{trig}'.format(template=template['name'], trig=trigger['description']))
	return trigs

def check_template_issues(config, output):
	# TODO: add check for overridden triggers
	for template in config['zabbix_conf']['template_names']:
		item_name_accum = [x['name'] for x in template['items']]
		item_key_accum = [x['key_'] for x in template['items']]
		# template check
		if 'templates' in template.keys():
			template_run_list = template['templates'].copy()
			for cur_temp in template_run_list:
				cur_temp = config['zabbix_conf']['templates'][config['templates'].index(cur_temp)]
				if 'templates' in cur_temp.keys():
					# update loop var
					template_run_list = template_run_list + cur_temp['templates']
				# check for parent item collisions
				for item in cur_temp['items']:
					if item['name'] in item_name_accum:
						output.error('Template: {base_temp} :item key {name} is in parent template {template}'.format(base_temp=template['name'], name=item['name'], cur_temp=cur_temp['name']))
						return True
					elif item['key_'] in item_key_accum:
						output.error('Template: {base_temp} :item key {key} is in parent template {template}'.format(base_temp=template['name'], key=item['key_'], cur_temp=cur_temp['name']))
						return True
				item_name_accum.append(item['name'])
				item_key_accum.append(item['key_'])
	return False
