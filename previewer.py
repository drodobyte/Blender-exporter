from . import exporter
import bpy
import os
	
def preview():
	import subprocess
	import imp
	imp.reload(exporter)
	
	cwd = norm(os.path.dirname(__file__))
	
	path = norm(cwd + '/_tmp/data/in/')
	if not os.path.exists(path):
		os.makedirs(path)

	filename = norm(path + '/data.bgo')
	exporter.export(filename)
	
	jar = norm(cwd + "/preview.jar")
	arg = norm(cwd + "/_tmp/")

	try:
		code = subprocess.call(['java', '-jar', jar, arg], shell=False) # shell=True for Windows
	except OSError as e:
		print("preview error " + e)

def norm(path):
	return os.path.abspath(os.path.normpath(path))