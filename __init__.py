bl_info = {
	"name": "Bgo exporter",
	"description": "Exports to Drodobyte.",
	"author": "DrodoByte: Antonio Salido Urbaneja",
	"version": (1,3,4),
	"blender": (2, 59, 0),
	"api": 39257,
	"location": "File > Export > DrodoByte (.bgo)",
	"warning": '', # used for warning icon and text in addons panel
	"wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/Scripts/My_Script",
	"tracker_url": "http://projects.blender.org/tracker/index.php?func=detail&aid=<number>",
	"category": "Import-Export"}

if "bpy" in locals():
    import imp
    imp.reload(version)
    imp.reload(exporter)
    imp.reload(previewer)
else:
    from . import version
    from . import exporter
    from . import previewer
    
import bpy
import os

class BgoExporter(bpy.types.Operator):
	bl_idname = "export_game.modeldata"
	bl_label = "Export DrodoMalord data"
		
	def invoke(self, context, event):
		return export(False)

class BgoPreview(bpy.types.Operator):
	bl_idname = "preview_game.modeldata"
	bl_label = "Preview DrodoMalord data"
		
	def invoke(self, context, event):
		return export(True)


def export(preview):
	try:
		editmode = (bpy.context.active_object.mode == 'EDIT')
	except:
		editmode = False
		
	if editmode:
		bpy.ops.object.editmode_toggle()

	version.set(bl_info['version'])
	
	try:
		if preview:
			previewer.preview()
		else:
			if os.getlogin() == 'cani':
				filename = os.path.expanduser('~') + '/development/drodobyte/tools/bgo.tool/data/in/data.bgo'
			else:
				path = norm(norm(os.path.dirname(__file__)) + '/_tmp/data/in/')
				if not os.path.exists(path):
					os.makedirs(path)
				filename = norm(path + '/data.bgo')
				
			print ('exporting to ' + filename)
			exporter.export(filename)
	except:
		print ('export error!')
		raise
	else:
		print ('export successful')
		
	if editmode:
		bpy.ops.object.editmode_toggle()
	
	return {'RUNNING_MODAL'}

def norm(path):
	return os.path.abspath(os.path.normpath(path))

def register():
	bpy.utils.register_module(__name__)

def unregister():
	bpy.utils.unregister_module(__name__)

if __name__ == "__main__": # only for live edit
	register()
