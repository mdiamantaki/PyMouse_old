import datajoint as dj

dj.config['database.host'] = '139.91.171.210:3306'

behavior = dj.create_virtual_module('behavior.py', 'pipeline_behavior')
map = dj.create_virtual_module('map.py', 'pipeline_map')
obj = dj.create_virtual_module('obj.py', 'manolis_objects')
