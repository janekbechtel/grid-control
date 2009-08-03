# Generic base class for workload management systems

import sys, os, time, shutil, tarfile
from grid_control import AbstractObject, ConfigError, RuntimeError, UserError, utils

class WMS(AbstractObject):
	INLINE_TAR_LIMIT = 256 * 1024
	reqTypes = ('MEMBER', 'WALLTIME', 'STORAGE', 'SITES', 'CPUTIME', 'MEMORY', 'OTHER')
	for id, reqType in enumerate(reqTypes):
		locals()[reqType] = id


	def __init__(self, config, module, backend):
		self.config = config
		self.module = module

		self._outputPath = os.path.join(config.workDir, 'output')

		if not os.path.exists(self._outputPath):
			if config.opts.init:
				try:
					os.mkdir(self._outputPath)
				except IOError, e:
					raise ConfigError("Problem creating work directory '%s': %s" % (self._outputPath, e))
			else:
				raise ConfigError("Not a properly initialized work directory '%s'." % config.workDir)

		tarFile = os.path.join(config.workDir, 'sandbox.tar.gz')

		self.sandboxIn = [ utils.atRoot('share', 'run.sh'), utils.atRoot('share', 'run.lib'), tarFile ]
		self.sandboxOut = self.module.getOutFiles() + [ 'stdout.txt', 'stderr.txt', 'jobinfo.txt' ]

		taskConfig = utils.DictFormat(escapeString = True).format(self.module.getTaskConfig(), format = 'export %s%s%s\n')
		varMapping = map(lambda (x,y): "%s %s\n" % (x,y), self.module.getVarMapping().items())
		inFiles = self.module.getInFiles() + [ utils.VirtualFile('_config.sh', utils.sorted(taskConfig)),
			utils.VirtualFile('_varmap.dat', str.join('', utils.sorted(varMapping))) ]

		utils.vprint("Packing sandbox:")
		if config.opts.init:
			utils.vprint("\t%s" % tarFile)
			tar = tarfile.TarFile.open(tarFile, 'w:gz')

		for file in inFiles:
			if type(file) == str:
				# Path to filename given
				if not os.path.exists(file):
					raise UserError("File %s does not exist!" % file)

				# Put file in sandbox instead of tar file
				if os.path.getsize(file) > self.INLINE_TAR_LIMIT and file.endswith('.gz') or file.endswith('.bz2'):
					self.sandboxIn.append(file)
					continue

			if config.opts.init:
				# Package sandbox tar file
				if type(file) == str:
					utils.vprint("\t\t%s" % file)
					info = tarfile.TarInfo(os.path.basename(file))
					info.size = os.path.getsize(file)
					handle = open(file, 'rb')
				else:
					utils.vprint("\t\t%s" % file.name)
					info, handle = file.getTarInfo()

				if info.name.endswith('.sh'):
					info.mode = 0755
				elif info.name.endswith('.py'):
					info.mode = 0755
				else:
					info.mode = 0644
				info.mtime = time.time()

				tar.addfile(info, handle)
				handle.close()

		if config.opts.init:
			tar.close()
		for file in self.sandboxIn:
			if file != tarFile or not config.opts.init:
				utils.vprint("\t%s" % file)


	def getTimings(self):
		return (60, 10)


	def getRequirements(self, jobNum):
		return self.module.getRequirements(jobNum)


	def bulkSubmissionBegin(self, nJobs):
		return True


	def bulkSubmissionEnd(self):
		pass


	def submitJobs(self, jobNumList):
		for jobNum in jobNumList:
			if self.config.opts.abort:
				raise StopIteration
			jobNum, wmsId, data = self.submitJob(jobNum)
			if wmsId == None:
				continue # FIXME
			yield (jobNum, wmsId, data)


	def retrieveJobs(self, ids):
		def readJobFile(info):
			data = utils.DictFormat().parse(open(info, 'r'), lowerCaseKey = False)
			return (data['JOBID'], data['EXITCODE'], data)

		for inJobNum, dir in self.getJobsOutput(ids):
			if dir == None:
				yield (inJobNum, -1, {})
				continue

			accepted = False
			info = os.path.join(dir, 'jobinfo.txt')
			try:
				jobNum, retCode, data = readJobFile(info)
				if jobNum != inJobNum:
					raise RuntimeError("Invalid job id in job file")
				dst = os.path.join(self._outputPath, 'job_%d' % jobNum)
				accepted = True
			except:
				sys.stderr.write("Warning: '%s' seems broken.\n" % info)
#				# Try to extract jobinfo from stdout file
#				if not os.path.exists(dir):
#					continue
#				try:
#					info = os.path.join(dir, 'stdout.txt')
#					id, retCode, data = readJobFile(open(info, 'r').readlines()[-3:])
#					sys.stderr.write("Recovered job %d with exit code %d...\n" % (id, retCode))
#				except:
					# Move corrupted output to fail directory

				try:
					os.rmdir(dir)
					# No files were retrieved...
					continue
				except:
					pass

				failpath = os.path.join(self.config.workDir, 'fail')
				if not os.path.exists(failpath):
					os.mkdir(failpath)
				dst = os.path.join(failpath, os.path.basename(dir))
				sys.stderr.write("Moving output sandbox to %s\n" % dst)

			try:
				if os.path.exists(dst):
					shutil.rmtree(dst)
			except IOError, e:
				sys.stderr.write("Warning: '%s' cannot be removed: %s" % (dst, str(e)))
				continue

			try:
				shutil.move(dir, dst)
			except IOError, e:
				sys.stderr.write("Warning: Error moving job output directory from '%s' to '%s': %s" % (dir, dst, str(e)))
				continue

			if accepted:
				yield (jobNum, retCode, data)
