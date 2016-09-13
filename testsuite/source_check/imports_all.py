
if __name__ == '__main__':
	import os, sys, get_file_list
	stored_sys_path = list(sys.path)
	available_imports = {}
	used_imports = {}
	for (fn, fnrel) in get_file_list.get_file_list(showTypes = ['py'],
			showExternal = True, showAux = False, showTestsuite = False):

		if fn.endswith('go.py') or ('/requests/' in fn) or ('python_compat_' in fn):
			continue
		for line in open(fn):
			if ('import' in line) and ('from' in line):
				import_lines = list(map(str.strip, line.split('import')[1].split(',')))
				import_src = line.split('from')[1].split('import')[0].strip()
				used_imports.setdefault(import_src, set()).update(import_lines)

		module = None
		if ('/scripts/' in fn) and not fn.endswith('gcSupport.py'):
			continue
		elif fn.endswith('__init__.py'):
			sys.path.append(os.path.dirname(os.path.dirname(fn)))
			module = __import__(os.path.basename(os.path.dirname(fn)))
		else:
			sys.path.append(os.path.dirname(fn))
			module = __import__(os.path.basename(fn).split('.')[0])
		if hasattr(module, '__all__'):
			mod_all = list(module.__all__)
			mod_sort = sorted(mod_all, key = str.lower)
			available_imports[module] = mod_sort
			if mod_all != mod_sort:
				print "Unsorted", fn
				print "  -", mod_all
				print "  +", mod_sort
				print
		sys.path = list(stored_sys_path)

	for (import_src, imports) in used_imports.items():
		for module in available_imports:
#			if module.__name__.endswith(import_src):
				for item in imports:
					try:
						available_imports[module].remove(item)
					except:
						pass
	print '-'*20
	for module, module_x in available_imports.items():
		if module_x:
			print module.__name__, module_x
