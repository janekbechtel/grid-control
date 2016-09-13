import astroid
from astroid import MANAGER


def register(linter):
	pass


def _add_enum(entry, enum_list):
	for attr in enum_list:
		entry.locals[attr] = [astroid.Const(0)]

	entry.locals['enum_value_list'] = [astroid.Const([])]
	entry.locals['enum_name_list'] = [astroid.Const([])]
	entry.locals['intstr2enum'] = [astroid.Const([])]


def transform_module(node):
	if node.name == 'logging':
		_add_enum(node, ['INFO1', 'INFO2', 'INFO3', 'DEBUG1', 'DEBUG2', 'DEBUG3', 'DEFAULT'])


def transform_class(node):
	if node.name == 'RestSession':
		_add_enum(node, ['GET', 'POST', 'DELETE', 'PUT'])
	elif node.name == 'VirtualFile':
		node.locals['getvalue'] = node.locals['get_tar_info']
		node.locals['close'] = node.locals['get_tar_info']
	elif node.name == 'Logger':
		node.locals['log_process'] = node.locals['log']
		node.locals['log_time'] = node.locals['log']
	elif node.name == 'DataProvider':
		_add_enum(node, ['NEntries', 'URL', 'FileList', 'Locations', 'Metadata',
			'Nickname', 'Dataset', 'BlockName', 'Provider'])
	elif node.name == 'Job':
		_add_enum(node, ['INIT', 'SUBMITTED', 'DISABLED', 'READY', 'WAITING', 'QUEUED', 'ABORTED',
			'RUNNING', 'CANCEL', 'UNKNOWN', 'CANCELLED', 'DONE', 'FAILED', 'SUCCESS'])
		node.locals['enum2str'] = node.locals['__init__']
		node.locals['str2enum'] = node.locals['get']
	elif node.name == 'DataSplitter':
		_add_enum(node, ['NEntries', 'FileList', 'Locations', 'BlockName',
			'Invalid', 'Comment', 'Nickname', 'Metadata', 'MetadataHeader',
			'Skipped', 'Dataset', 'CommonPrefix'])
	elif node.name == 'WMS':
		_add_enum(node, ['STORAGE', 'WALLTIME', 'CPUTIME', 'MEMORY', 'CPUS', 'SOFTWARE'])
	elif node.name == 'Console':
		_add_enum(node, ['RESET', 'COLOR_GREEN', 'COLOR_RED', 'COLOR_BLUE', 'COLOR_WHITE', 'BOLD'])
	elif node.name == 'FileInfoProcessor':
		_add_enum(node, ['Hash', 'NameLocal', 'NameDest', 'Path'])


MANAGER.register_transform(astroid.Module, transform_module)
MANAGER.register_transform(astroid.Class, transform_class)
