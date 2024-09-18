from . import utils, writeutils, io_export_md5
from drodobyte.utils import *
from drodobyte.writeutils import *
import bpy
from . import version

def md5export(arm, meshes):
	filepath = 'c:/Users/Cani/development/projects/workspace/tests/TestAndroid/assets/md5/data.bin'
	md5name = ""
	md5exportList = 'mesh & anim'
	md5scale = 1.0
	settings = io_export_md5.md5Settings(savepath = filepath, scale = md5scale, exportMode = md5exportList)
	io_export_md5.save_md5(settings, arm, meshes)
	
def export(filename):
	import imp
	imp.reload(utils)
	imp.reload(writeutils)
	imp.reload(io_export_md5)
	utils.init()
	
	openPrinter(filename)
	test()

	bgo(bpy.data)
	closePrinter()

def bgo(data):
	meta(version.get())
	worlds(data.worlds)
	textures(data.textures)
	materials(data.materials)
	ipos(data.actions, False)
	paths(data.objects)
	skeletons(data.objects)
	meshes(data.meshes)
	entities(data.objects)
	lights(data.objects)
	cameras(data.objects)
	groups(data.groups)
	emitters(data.objects) # FIXME
	scenes(data.scenes)
	
def meta(version):
	integers(version)
	
def ipos(ips, compiled):
	used = getUsedIpos(ips)
	size(used)
	for i in used:
		ipo(i, compiled)
	
def ipo(i, compiled):
	bool(compiled)
	if not compiled:
		table = ipoTable(i.groups[0].channels) # group 0 FIXME?
		bool(table)
		if table:
			string(i.name)
			size(table)
			for curve in iter(table):
				string(curve)
				size(table[curve])
				for point in table[curve]:
					integer(point["frame"]) # frame
					real(point["value"]) # value
	else:
		table = compileIpo(i,20)
		bool(table)
		if table:
			string(i.name)
			bool(table['location'])
			if table['location']:
				size(table['location'])
				for step in table['location']:
					reals(step[0], step[1][0], step[1][1], step[1][2])
			bool(table['rotation'])
			if table['rotation']:
				size(table['rotation'])
				for step in table['rotation']:
					reals(step[0], step[1][0]*10, step[1][1]*10, step[1][2]*10) # ipo euler angles are divided by 10
			bool(table['quaternion'])
			if table['quaternion']:
				size(table['quaternion'])
				for step in table['quaternion']:
					reals(step[0], step[1][0]*10, step[1][1], step[1][2], step[1][3]) # divided by 10 ?

def paths(os):
	ps = getUsedPaths(os)
	size(ps)
	for p in ps:
		path(p)

def path(o):
	string(o.name)
	path = o.data
	real(path.path_duration)
	bool(path.splines[0].use_cyclic_u)
	matrix = transformMatrix(o.location, o.rotation_euler, o.scale)
	curve = path.splines[0].points # first curve in Nurbs set
	size(curve)
	for point in curve:
		wpoint = transform(point.co, matrix) # FIXME ver si transforma de verdad
		reals(wpoint[0], wpoint[2], -wpoint[1])

def worlds(ws):
	size(ws)
	for w in ws:
		world(w)

def world(w):
	string(w.name)
	reals(w.ambient_color[0], w.ambient_color[1], w.ambient_color[2]) # ambient
	reals(w.horizon_color[0], w.horizon_color[1], w.horizon_color[2]) # horizon
	fog(w)
	real(9.8) # gravity // FIXME!!
	
def fog(w):
	if hasFog(w):
		reals(w.mist_settings.start, w.mist_settings.depth)
	else:
		reals(0, 1000)
	
def scenes(ss):
	size(ss)
	for s in ss:
		scene(s)
		
def lights(os):
	ls = getUsedLamps(os)
	size(ls)
	for l in ls:
		light(l)
	
def light(o):
	l = o.data
	string(o.name)
	type = lampType(l.type)
	string(type)
	reals(l.color[0], l.color[1], l.color[2]) # color
	location(o)
	rotation(o)
	real(l.energy) # energy
	if type == 'spot':
		real(l.spot_size) # spotsize
		real(l.spot_blend) # spotblend
	else:
		real(0) # spotsize
		real(0) # spotblend
	if type == 'sun':
		string('constant') # falloff
	else:
		string(lampFalloff(l.falloff_type)) # falloff
	real(l.distance) # distance
	if type == 'sun':
		real(0) # linear attenuation
		real(0) # quadratic attenuation
	else:
		real(l.linear_attenuation) # linear attenuation
		real(l.quadratic_attenuation) # quadratic attenuation
	string(getZone(o))
	properties(o.game.properties)

	
def cameras(os):
	cs = getUsedCameras(os)
	size(cs)
	for c in cs:
		camera(c)
	
def camera(o):
	c = o.data
	string(o.name)
	string(c.type.lower())
	location(o)
	rotation(o)
	real(fov(c))
	real(c.clip_start)
	real(c.clip_end)
	animation(o)
	properties(o.game.properties)

	
def scene(sc):	
	string(sc.name)
	string(sceneCamera(sc))
	integer(sc.frame_start)
	integer(sc.frame_end)
	bool(sc.world)
	if sc.world:
		string(sc.world.name)
	os = getSceneEntities(sc.objects)
	size(os)
	for o in os:
		string(o.name)
	ls = getSceneLamps(sc.objects)
	size(ls)
	for o in ls:
		string(o.name)
	cs = getSceneCameras(sc.objects)
	size(cs)
	for c in cs:
		string(c.name)
	gs = getSceneGroups(sc)
	size(gs)
	for g in gs:
		string(g.name)
	zs = getSceneZones(sc)
	size(zs)
	for z in zs:
		string(z.name)
		grid = zoneGrid(z)
		integers(grid[0], grid[2], grid[1])
		latticeBounds(z)
	es = getSceneEmitters(sc)
	size(es)
	for e in es:
		string(e.name)
	sp = getUsedPaths(sc.objects)
	size(sp)
	for p in sp:
		string(p.name)
	sequences(getSceneSequences(sc))

def sequences(ss):
	size(ss)
	for s in ss:
		sequence(s)
	
def sequence(s):
	string(s.name)
	string(getSequenceType(s))
	integer(s.channel)
	string(s.scene.name)
	bool(s.scene_camera)
	if s.scene_camera:
		string(s.scene_camera.name)
	integer(s.frame_final_start) # Still Start
	integer(s.frame_final_start+s.frame_still_start) # Animation Start 
	integer(s.frame_final_end-s.frame_still_end) # Animation End
	integer(s.frame_final_end) # Still End
	integer(s.animation_offset_start) # Animation offset
#	print('')
#	print(s.name)	
#	print('frame duration ' + str(s.frame_duration))
#	print('fram final duration ' + str(s.frame_final_duration))
#	print('frame final end ' + str(s.frame_final_end))
#	print('frame final start ' + str(s.frame_final_start))
#	print('fram offset end ' + str(s.frame_offset_end))
#	print('frame offset start ' + str(s.frame_offset_start))
#	print('frame start ' + str(s.frame_start))
#	print('frame still end ' + str(s.frame_still_end))
#	print('frame still start ' + str(s.frame_still_start))

def textures(ts):
	used = getUsedTextures(ts)
	size(used)
	for t in used:
		texture(t)			

def texture(t):
	string(t.name)
	string(bpy.path.abspath(t.image.filepath))
	
def materials(ms):
	size(ms)
	for m in ms:
		string(m.name)
		ts = getMaterialTextures(m)
		size(ts)
		for t in ts:
			string(t.name)
			checkBlendType(m, t)
			string(t.blend_type); # blend type: Mix/Multiply
			real(t.diffuse_color_factor); # blend factors
			bool(t.texture.use_alpha); # alpha for decaling
			reals(t.offset.x, 1-t.offset.y, 0)
			reals(t.scale.x, t.scale.y, 1)
		col = m.diffuse_color
		real(m.ambient) # ambient
		if m.use_transparency:
			alpha = m.alpha
		else:
			alpha = 1
		reals(m.diffuse_intensity, col[0], col[1], col[2], alpha) # color
		col = m.specular_color
		reals(m.specular_intensity, col[0], col[1], col[2]) # specular
		real(m.specular_hardness) # shininess
		real(m.emit) # emission

def skeletons(os):
	arms = getUsedArmatures(os)
	size(arms)
	for a in arms:
		skeleton(a)
	
def skeleton(a):
	string(a.name)
	location(a)
	rotation(a)
#	if a.getAction(): p('action {%s}', a.getAction().name)
	bones = a.data.bones.values();
	size(bones)
	for b in bones:
		ipo = boneIpo(a, b)
		string(b.name)
		bool(b.parent)
		if b.parent: string(b.parent.name)
#		t = tail(b)
#		p('head {%f %f %f}', loc[0], loc[1], loc[2])
#		p('tail {%f %f %f}', loc[0], loc[1], loc[2])
#		p('roll {%f}', b.roll)
		h = head(b,False)
		reals(h.x, h.y, h.z) # location
		quat = boneQuaternion(b,False)
		reals(quat.x, quat.y, quat.z, quat.w) # quaternion
#		if t: p('rotation {%f %f %f}', t[0], t[1], t[2])
#		p('rotation {%f %f %f}', rot[0], rot[1], rot[2])
#		if ipo: p('ipo {%s}', ipo.name)

def emitters(os):
	es = getUsedEmitters(os)
	size(es)
	for o in es:
		emitter(o)

def emitter(o):
	string(o.name)
	parent(o)
	location(o)
	direction(o)
	real(o.scale[0])
	string(o.particle_systems[0].name)
	bool(isEmitter3d(o))
	string(getZone(o))
	properties(o.game.properties)
	
def meshes(ms):
	used = getUsedMeshes(ms)
	size(used)
	for m in used:
		mesh(m)
	used = getUsedMd5Meshes()
	size(used)
	for m in used:
		md5mesh(m)

def mesh(m):
	string(m.name)
	textureCount = getMaterialTexturesCount(m)
	if textureCount > 0 and not hasUVSet(m):
		error(m.name + 'mesh must have UV coordinates')
	vertices(m.vertices, m, m.faces)
	faces(m.faces, m)
	edges(m.edges)
	integer(textureCount)
	o = findMeshObject(m)
	vertexgroups(o)
	bool(o.hide_render)
	bounds(boundType(o), localBounds(o))

def md5mesh(arm):
	string(arm.data.name)
	md5export(arm, getMd5Meshes(arm))
	
def vertexgroups(o):
	gs = o.vertex_groups
	size(gs)
	for g in gs:
		vertexgroup(o,g)
			
def vertexgroup(o, group):
	string(group.name)
	vertices = [] # FIXME falta la lista de vertices
	size(vertices)
	integers(vertices) # vertex indexes
	
def entities(os):
	es = getUsedEntities(os)
	size(es)
	for e in es:
		entity(e)	
		
def entity(o):
	# object: parent object, mass, friction
	# rigid/soft/dinamyc/static... body
	string(o.name)
	parent(o)
	location(o)
	rotation(o)
	string(getZone(o))
	empty = isEmpty(o)
	bool(empty)
	if empty:
		animation(o)
	if not empty:
		scale(o)
		if (isMd5Entity(o)):
			string(o.data.name)
			material(getMd5Mesh(o))
			bool(False) # no animation FIXME
		else:
			string(o.data.name) # mesh name
			material(o)
			animation(o)
		physics(o)
		if isDecal(o): # Render pass
			integer(1)
		else:
			integer(o.pass_index)
		properties(o.game.properties)

def animation(o):
	anim = getAnimation(o)
	bool(anim)
	if anim:
		string(anim)
	
def groups(gs):
	size(gs)
	for g in gs:
		group(g)
	
def group(g):
	string(g.name)
	size(g.objects)
	for o in g.objects:
		string(o.name) # group object name
	
def parent(o):
	bool(o.parent)
	if o.parent:
		string(parentName(o))
		
def location(ob):
	l = ob.location
	reals(l[0], l[2], -l[1])
	
def rotation(ob):
	r = ob.rotation_euler
	reals(r[0], r[2], -r[1])
	
def direction(ob):
	d = toDirection(ob.rotation_euler)
	reals(d.x, d.z, -d.y)

def scale(ob):
	checkPositiveScale(ob)
	s = ob.scale
	reals(s[0], s[2], s[1])
		
def color(ob):
	c = ob.color
	reals(c[0], c[1], c[2], c[3])
	
def bounds(type, b):
	string(type)
	size(b)
	bound(b)

def bound(b):
	for v in b:
		reals(v[0], v[2], -v[1])

def boundWorld(b, location, rotation, scale):
	bound(transforms(b, location, rotation, scale))

def latticeBounds(l):
	checkNoRotation(l)
	boundWorld(unitBounds(), l.location, l.rotation_euler, l.scale)
		
def vertices(vs, m, fs):
	size(vs)
	sticky = isSticky(m)
	bool(sticky)
	for v in vs:
		reals(v.co[0], v.co[2], -v.co[1]) # coords
		reals(v.normal[0], v.normal[2], -v.normal[1]) # normals
		if sticky:
			reals(m.sticky[v.index].co.x, 1-m.sticky[v.index].co.y)

def faces(fs, m):
	indexes = getFaceVertices(fs) # indexes
	integer(int(len(indexes)/3)) # face count
	integers(indexes)
	uvs = getFaceUVs(m)
	bool(uvs) 
	if uvs: 
		reals(uvs) 

def edges(es):
	pass # e.v1.index, e.v2.index

def material(m):
	used = getUsedMaterials(m)
	size(used)
	for mat in used:
		string(mat.name)
	
def physics(o):
#	checkColliderUntransformed(o)
	string(physicProperty(o))
	
def properties(ps):
	size(ps)
	for pr in ps:
		string(pr.name)
		string(str(pr.value))

# This lets you can import the script without running it
if __name__ == '__main__':
	in_emode = Window.EditMode()
	if in_emode: Window.EditMode(0)
	export('c:/Users/Cani/development/projects/workspace/Drodobyte/trunk/desktop.tool/BGOTool/data/in/data.bgo')
	print ('BGO export sucess: (test data)')
	print ('openGL adaptation not finished (bones/quaternions...): http://wiki.blender.org/index.php/Extensions:Uni-Verse/BlenderVsVerse')
	if in_emode: Window.EditMode(1)