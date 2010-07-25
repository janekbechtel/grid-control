import os
from grid_control import utils
from usermod import UserMod

class ROOTMod(UserMod):
	def __init__(self, config):
		# Determine ROOT path from previous settings / environment / config file
		taskInfo = utils.PersistentDict(os.path.join(config.workDir, 'task.dat'), ' = ')
		self._rootpath = taskInfo.get('root path', os.environ.get('ROOTSYS', None))
		self._rootpath = config.get(self.__class__.__name__, 'root path', self._rootpath)
		utils.vprint('Using the following ROOT path: %s' % self._rootpath, -1)
		taskInfo.write({'root path': self._rootpath})

		# Special handling for executables bundled with ROOT
		self.builtIn = False
		exe = config.get(self.__class__.__name__, 'executable')
		exeFull = os.path.join(self._rootpath, 'bin', exe)
		if os.path.exists(exeFull):
			self.builtIn = True
			config.set(self.__class__.__name__, 'send executable', 'False')
			config.set(self.__class__.__name__, 'executable', exeFull)

		# Apply default handling from UserMod
		UserMod.__init__(self, config)
		self.updateErrorDict(utils.pathGC('share', 'run.root.sh'))

		# Collect lib files needed by executable
		self.libFiles = []


	def getTaskConfig(self):
		data = UserMod.getTaskConfig(self)
		data['MY_ROOTSYS'] = self._rootpath
		return data


	def getCommand(self):
		cmd = './run.root.sh %s $@ > job.stdout 2> job.stderr' % self._executable
		return ('chmod u+x %s; ' % self._executable, '')[self.builtIn] + cmd


	def getInFiles(self):
		return UserMod.getInFiles(self) + self.libFiles + [utils.pathGC('share', 'run.root.sh')]
