# Helper functions

import math
#from Blender import Window, Draw, BGL, Mesh, Material, Texture, Lamp, Ipo, Key, Mathutils, Object
import bpy
import array
import struct
import mathutils
from drodobyte.writeutils import *
from drodobyte import writeutils

# globals
#out = None
#outbin = None
RAD2DEG = 360.0/6.283185307179586476925286766559
X = mathutils.Vector((1,0,0))
Y = mathutils.Vector((0,1,0))
Z = mathutils.Vector((0,0,1))
validImageSizes = [1, 2, 4, 8, 16, 32, 64, 128, 256, 1024]
_armatures = None
_md5Ipos = None
_md5Meshes = None

def isMesh(object):
	return object.type == 'MESH'

def isArmature(object):
	return object.type == 'ARMATURE'

def isRoot(object):
	return not object.parent

def isLamp(object):
	return object.type == 'LAMP'

def isCamera(object):
	return object.type == 'CAMERA'

def isImage(texture):
	return texture.type == 'IMAGE'

def isEmpty(object):
	return object.type == 'EMPTY'

def isIpo(object):
	return object.type == 'IPO' and isUsed(object)

def isPath(object):
	return object.type == 'CURVE' # and (object.getData().getFlag() and 0x08) # 3 bit == CurvePath FIMXE

def isEmitter(object):
	return object.particle_systems

def isLattice(object):
	return object.type == 'LATTICE' and hasProperty(object, "zone", True)

def isZone(object):
	return isLattice(object)
	
def isSequence(object):
	return object.type == 'SCENE'
	
def isPlayableSequence(object):
	return isSequence(object) and object.name.upper().startswith('PLAYABLE')

def hasImage(texture):
	return isImage(texture) and texture.image and texture.users > 0

def isUsed(o):
	return (o.users == 1 and not o.use_fake_user) or o.users > 0

def isMd5Armature(object):
	return object in _armatures 
	
def isMd5Mesh(object):
	return object in _md5Meshes 

def isMd5Entity(object):
	return not isMd5Mesh(object) and isMd5Armature(object)
	
def isMd5Ipo(object):
	return object in _md5Ipos 
	
def getUsedMeshes(ms):
	usedm = []
	for m in ms:
		if isUsed(m):
			object = findMeshObject(m)
			if not isZone(object) and not isEmitter(object) and not isMd5Mesh(object):
				usedm.append(m)
	return usedm

def getUsedMd5Meshes():
	return getUsedMd5Armatures()
	
def getUsedEntities(objects):
	used = []
	for o in objects:
		if not isZone(o) and not isEmitter(o):
			if isEmpty(o) or isMd5Entity(o) or (isMesh(o) and not isMd5Mesh(o)):
				validateEntity(o)
				used.append(o)	
	return used

def getSceneEntities(objects):
	used = []
	for o in objects:
		if not isZone(o) and not isEmitter(o):
			if isEmpty(o) or isMd5Entity(o) or (isMesh(o)) and not isMd5Mesh(o) and (isRoot(o) or isArmature(o.parent)):
				used.append(o)
	return used

def getUsedEmpties(objects):
	used = []
	for o in objects:
		if isEmpty(o):
			used.append(o)
	return used
		
def getSceneLamps(objects):
	return getUsedLamps(objects)

def getUsedCameras(objects):
	used = []
	for o in objects:
		if isCamera(o): used.append(o)
	return used

def getUsedPaths(objects):
	used = []
	for o in objects:
		if isPath(o): used.append(o)
	return used

def getUsedMd5Armatures():
	return _armatures

def getMd5Meshes(armature):
	used = []
	for o in _md5Meshes:
		if o.parent == armature or o.parent_bone in armature.data.bones:
			used.append(o)
	return used

def getMd5Mesh(armature):
	for o in _md5Meshes:
		if o.parent == armature or o.parent_bone in armature.data.bones:
			return o
			
def getSceneCameras(objects):
	return getUsedCameras(objects)
	
def getFaceVertices(fs):
	used = []	
	for f in fs:
		if len(f.vertices) != 3:
			if len(f.vertices) == 4:
				used.append(f.vertices[0])
				used.append(f.vertices[1])
				used.append(f.vertices[3])
				used.append(f.vertices[1])
				used.append(f.vertices[2])
				used.append(f.vertices[3])
			if len(f.vertices) > 4:
				error('face with more than 4 vertices')
		else:	
			for vindex in f.vertices:
				used.append(vindex)
	return used

def getFaceUVs(m):
	used = []
	if not m.uv_textures or isSticky(m):
		return used
	if len(m.uv_textures) > 1:
		error('mesh ' + m.name + ' must have at most 1 UV set')

	faces = m.uv_textures[0].data
	for face in faces:
		uv = face.uv1, face.uv2, face.uv3, face.uv4
		if len(face.uv) == 4: # 4 vertices
			used.append(uv[0].x)
			used.append(1-uv[0].y)
			used.append(uv[1].x)
			used.append(1-uv[1].y) 
			used.append(uv[3].x) 
			used.append(1-uv[3].y)
			
			used.append(uv[1].x)
			used.append(1-uv[1].y)
			used.append(uv[2].x)
			used.append(1-uv[2].y)
			used.append(uv[3].x)
			used.append(1-uv[3].y) 
		else:
			used.append(uv[0].x)
			used.append(1-uv[0].y)
			used.append(uv[1].x)
			used.append(1-uv[1].y) 
			used.append(uv[2].x) 
			used.append(1-uv[2].y)

	return used

def isSticky(mesh):
	return len(mesh.sticky) != 0

def hasUVSet(mesh):
	return mesh.uv_textures or len(mesh.uv_textures) > 0

def getUsedTextures(ts):
	used = []
	for t in ts: 
		if hasImage(t):
			validateTexture(t) 
			used.append(t)
	return used

def getUsedMaterials(o):
	used = []
	for mat in o.material_slots:
		if mat.link == 'DATA':
			error(o.name + ' object material must be linked to Object (set as default in blender preferences)')
		if mat: used.append(mat)
	return used

def getMaterialTextures(m):
	used = []
	for t in m.texture_slots:
		if t and hasImage(t.texture) and t.use: 
			validateTextureMapping(m.name, t)
			used.append(t)
	return used
	
def getUsedLamps(objects):
	used = []
	for o in objects:
		if isUsed(o) and isLamp(o): used.append(o)
	return used
	
def getUsedIpos(ips):
	used = []
	for i in ips:
		if isUsed(i) and not isMd5Ipo(i) and i.groups: used.append(i)
	return used

def getUsedArmatures(arms):
	used = []
	for a in arms:
		if isArmature(a) and not isMd5Armature(a) and isUsed(a): used.append(a)
	return used

def getUsedEmitters(objects):
	used = []
	for o in objects:
		if o.particle_systems:
			used.append(o)
	return used
	
def getUsedZones(objects):
	used = []
	for o in objects:
		if isZone(o):
			used.append(o)
	return used
	
def isEmitter3d(object):
	return hasProperty(object, "particle.mode", "3d")

def isDecal(object):
	return hasProperty(object, "decal", True)

def parentName(o):
	if o.parent:
		if isArmature(o.parent):
			name = o.parent.name
			if o.parent_bone:
				name += '@' + o.parent_bone
		else:
			name = o.parent.name
		return name
	
def findMeshObject(mesh):
	for o in bpy.data.objects:
		if isMesh(o):
			if o.data.name == mesh.name: # FIXME usa bpy
				return o
			
def findMeshObjects(mesh):
	found = []
	for o in bpy.data.objects:
		if isMesh(o):
			if o.data.name == mesh.name:
				found.append(o)
	return found

def getMaterialTexturesCount(mesh):
	os = findMeshObjects(mesh);
	count = 0
	for o in os:
		ms = getUsedMaterials(o)
		for m in ms:
			ts = len(getMaterialTextures(m.material))
			if ts > count:
				count = ts
	return count

def sceneCamera(scene):
	if not isCamera(scene.camera):
		error(scene.camera.name + ': not valid camera for scene ' + scene.name)
	return scene.camera.name
	
def lampType(value):
	if 'POINT' == value:
		return 'point'
	if 'SUN' == value:
		return 'sun'
	if 'SPOT' == value:
		return 'spot'
	error('only Lamp/Sun/Spot lamps supported')

def lampFalloff(value):
	if 'CONSTANT' == value:
		return 'constant'
	if 'INVERSE_LINEAR' == value:
		return 'linear'
	if 'INVERSE_SQUARE' == value:
		return 'square'
	if 'LINEAR_QUADRATIC_WEIGHTED' == value:
		return 'user'
	error('only \"Constant, InvLinear, InvSquare, LinQuad\" lamp falloffs are supported')

def getProperties(object, pattern):
	found = []
	properties = object.getAllProperties()
	for property in properties:
		if match(pattern, property.getName()):
			found.append(property)
	return found

def getProperty(object, key):
	data = object.game.properties.get(key)
	if data: return data.value
	else: return None

def hasProperty(object, key, value):
	return getProperty(object, key) == value
	
def match(pattern, str):
	post = pre = False
	if pattern.startswith('*'):
		post = True
	if pattern.endswith('*'):
		pre = True
	p = pattern.replace('*','')
	if post and pre:
		return str.contains(p)
	if pre:
		return str.startswith(p)
	if post:
		return str.endswith(p)
	return str == p

def ipoTable(channels):
	return collectPoints(channels)
			
def collectPoints(channels):
	table = {}
	for channel in channels:
		if not channel.mute:
			table[channelId(channel)] = [{"frame":int(keyframe.co[0]), "value":keyframe.co[1]} for keyframe in channel.keyframe_points]
	toOpenGLCoords(table)
	return table

def channelId(channel):
	path = stripChannelPath(channel)
	if channel.array_index == 0: return path+'X'
	if channel.array_index == 1: return path+'Y'
	if channel.array_index == 2: return path+'Z'
	if channel.array_index == 3: return path+'W'
	return path+channel.array_index

def stripChannelPath(ch):
	ns = ch.data_path.split('.')
	return ns[len(ns)-1]
	
def toOpenGLCoords(table):
	swapCurves(table, "locationY", "locationZ")
	swapCurves(table, "rotation_eulerY", "rotation_eulerZ")
	swapCurves(table, "scaleY", "scaleZ")
	negateCurve(table, "locationZ")
	negateCurve(table, "rotation_eulerZ")
#	negateCurve(table, "scaleZ")
	scaleCurve(table, "rotation_eulerX", RAD2DEG) # to degrees
	scaleCurve(table, "rotation_eulerY", RAD2DEG)
	scaleCurve(table, "rotation_eulerZ", RAD2DEG)
	
def swapCurves(table, curve1, curve2):
	swapTableKeys(table, curve1, curve2)
	
def negateCurve(table, curve):
	scaleCurve(table, curve, -1)
	
def scaleCurve(table, curve, factor):
	if curve in table:
		for pair in table[curve]:
			pair["value"] = factor*pair["value"]
	
def compileIpo(ipo, fps):
	extents = getFrameRange(filterCurves(ipo, CURVES))
	if extents:
		table = {}
		table['location'] = evalCurves(filterCurves(ipo, CURVES_LOC), extents, fps)
		table['rotation'] = evalCurves(filterCurves(ipo, CURVES_ROT), extents, fps)
		table['quaternion'] = evalCurves(filterCurves(ipo, CURVES_QUAT), extents, fps)
		return table

def filterCurves(ipo, curves):
	valid = []
	for id in ipo.curveConsts.values():
		if id in curves and ipo[id]: valid.append(ipo[id])
	return valid
	
def getFrameRange(curves):
	range = None
	for curve in curves:
		if curve:
			c = len(curve.bezierPoints)
			if c > 0:
				if range:
					range = (min(time(curve,0), range[0]), max(time(curve,c-1), range[1]))
				else:
					range = (time(curve,0), time(curve,c-1))
	return range

def time(curve, point):
	return curve.bezierPoints[point].vec[1][0]

def evalCurves(curves, extents, fps):
	sequence = []
	frame = extents[0]
	while frame <= extents[1]:
		values = [eval(curve, frame) for curve in curves]
		if values: sequence.append((frame/25.0, values)) # euler angles divided by 10
		frame += 25.0/fps
	return sequence
		
def eval(curve, frame):
	if curve: return curve[frame]

def getAnimation(o):
	anim = o.animation_data
	if not anim: return None
	if o.parent: return o.parent.name
	elif o.constraints: return o.constraints.name
	elif o.motion_path: return o.motion_path.name
	elif anim.nla_tracks: return anim.nla_tracks.name
	elif anim.drivers: return anim.drivers.name
	elif anim.action: return anim.action.name
	return None

def boneQuaternion(bone, local=True):
	if local: return bone.matrix_local.to_quaternion() 
	else: return bone.matrix.to_quaternion()

def head(bone, local=True):
	if local: return bone.head_local 
	else: return bone.head
	
def tail(bone, local=True):
	if local: return bone.tail_local 
	else: return bone.tail

def boneIpo(armature, bone):
	return armature.getAction().getChannelIpo(bone.name) # FIXME cuidado con try:catch

def localBounds(object):
	return object.bound_box
#	im = object.getInverseMatrix()
#	return [Mathutils.Vector(v)*im for v in object.boundingBox]

def boundType(object):
	value = object.game.collision_bounds_type 
	if 'BOX' == value: return 'box'
	if 'SPHERE' == value: return 'sphere'
	if 'CYLINDER' == value: return 'cylinder'
	if 'CONE' == value: return 'cone'
	if 'CONVEX_HULL' == value: return 'hull'
	if 'TRIANGLE_MESH' == value: return 'poly'

def unitBounds():
	bv = 0.5
	return [[-bv, -bv, -bv], [-bv, -bv, bv], [-bv, bv, bv], [-bv, bv, -bv], [bv, -bv, -bv], [bv, -bv, bv], [bv, bv, bv], [bv, bv, -bv]]
	
def checkColliderUntransformed(object):
	if isSensor(object) or isStatic(object):
		r = object.rotation_euler
		s = object.scale
		if r[0] != 0 or r[1] != 0 or r[2] != 0 or s[0] != 1 or s[1] != 1 or s[2] != 1:
			raise Exception("Collider must be unrotated and unscaled: " + object.name)
	
def physicProperty(object):
	if isNonCollider(object): return 'noncollider'
	if isStatic(object): return 'statical'
	if isSensor(object): return 'sensor'
	if isRigid(object): return 'rigid'
	if isSoft(object): return 'soft'
	if isDynamic(object): return 'dynamic'

def isNonCollider(object): return rbf(object, 'NO_COLLISION')
def isSensor(object): return rbf(object, 'SENSOR')
def isStatic(object): return not (isDynamic(object) or isRigid(object) or isSoft(object) or isSensor(object) or isNonCollider(object))
def isDynamic(object): return rbf(object, 'DYNAMIC')
def isRigid(object): return rbf(object, 'RIGID_BODY')
def isSoft(object): return rbf(object, 'SOFT_BODY')
def isOccluder(object): return rbf(object, 'OCCLUDER')
	
def rbf(object, key): 
#flags: GHOST,RIGIDBODY,USEFH,COLLISION,ROTFH,DYNAMIC,BOUNDS,ACTOR,PROP,OCCLUDER,SOFTBODY,CHILD,ANISOTROPIC,SECTOR,MAINACTOR,SENSOR,COLLISION_RESPONSE
	return object.game.physics_type == key 
		
def isClockwise(face):
	v1 = toVector(f.verts[0].co)
	v2 = toVector(f.verts[1].co)
	v3 = toVector(f.verts[2].co)
	normal = toVector(f.no)
	e1 = v2 - v1
	e2 = v3 - v1
	dot = Mathutils.DotVecs(normal, Mathutils.CrossVecs(e1, e2))
	if dot > 0: return True
	elif dot < 0: return False
	else: return None

def toVector(vertex):
	return Mathutils.Vector(vertex.x, vertex.y, vertex.z)

def arrayToVector(array):
	return mathutils.Vector((array[0], array[1], array[2]))

def checkPositiveScale(object):
	size = object.scale
	if size[0] < 0 or size[1] < 0 or size[2] < 0: raise Exception("Negative Scale on object " + object.name)

def checkNoRotation(object):
	rot = object.rotation_euler
	if not (rot[0] == 0 and rot[1] == 0 and rot[2] == 0): raise Exception("Must not be rotated " + object.type + " " + object.name)

def checkBlendType(material, slot):
	if not (slot.blend_type == 'MIX' or slot.blend_type == 'MULTIPLY' or slot.blend_type == 'ADD'):
		error(slot.texture.name + ' texture in material ' + material.name + ' must have blend type "Mix", "Multiply" or "Add"')

def hasFog(world):
	return world.mist_settings.use_mist
	
def getGroups(object):
	groups = []
	for g in bpy.data.groups:
		if object.name in g.objects: # FIXME?
			groups.append(g)
	return groups

def getSceneGroups(scene):
	groups = []
	for object in scene.objects:
		for group in getGroups(object):
			if group not in groups:
				groups.append(group)
	return sorted(groups, key=idCompare)

def getSceneEmitters(scene):
	emitters = []
	for object in scene.objects:
		if isEmitter(object):
			emitters.append(object)
	return emitters

def getSceneZones(scene):
	return getUsedZones(scene.objects)

def getSceneSequences(scene):
	sequences = []
	if scene.sequence_editor:
		for s in scene.sequence_editor.sequences:
			if isSequence(s):
				sequences.append(s)
	return sequences
	
	
def isAllZones(object):
	return hasProperty(object, "zone", "all")

def getZone(object):
	zone = getProperty(object, "zone")
	if zone == None: return "subzone"
	else: return zone
	
def zoneGrid(z):
	return [z.data.points_u-1, z.data.points_v-1, z.data.points_w-1]

def getSequenceType(sequence):
	if isPlayableSequence(sequence): return 'PLAYABLE'
	else: return sequence.type
	
def idCompare(group1, group2):
	p1 = splitId(group1.name)
	p2 = splitId(group2.name)
	if p1[0] > p2[0]:
		return 1
	elif p2[0] > p1[0]:
		return -1
	else:
		n1 = int(p1[1])
		n2 = int(p2[1])
		if n1 > n2:
			return 1
		elif n1 < n2:
			return -1
		else:
			return 0

def splitId(id):
	i = 0
	for c in id:
		if c.isdigit(): break
		i+=1
	return (id[:i],id[i:])

# appends new elements to set (not duplicates)
def addToSet(set, elements):
	for e in elements: 
		if e not in set: set.append(e)

def collectNames(os):
	return [o.getName() for o in os]

def findByName(name, objects):
	for object in objects:
		if name == object.getName():
			return object
	return None

def getObjectsByName(objects, names):
	matches = []
	for object in objects:
		if object.getName() in names: matches.append(o)
	return matches

def toDirection(euler):
	d = mathutils.Vector((0,0,1))
	d = mathutils.Matrix.Rotation(euler[2],3,Z) * d
	d = mathutils.Matrix.Rotation(euler[0],3,X) * d
	d = mathutils.Matrix.Rotation(euler[1],3,Y) * d
	return d

def rotationMatrix(eulerVector):
	matrix = mathutils.Matrix()
	matrix = matrix * mathutils.Matrix.Rotation(eulerVector[2],4,Z)
	matrix = matrix * mathutils.Matrix.Rotation(eulerVector[0],4,X)
	matrix = matrix * mathutils.Matrix.Rotation(eulerVector[1],4,Y)
	return matrix
	
def scaleMatrix(scaleVector):
	matrix = mathutils.Matrix()
	matrix = matrix * mathutils.Matrix.Scale(scaleVector[0],4,X)
	matrix = matrix * mathutils.Matrix.Scale(scaleVector[1],4,Y)
	matrix = matrix * mathutils.Matrix.Scale(scaleVector[2],4,Z)
	return matrix
	
def toMatrix(locationVector, rotationVector, scaleVector):
	matrix = mathutils.Matrix()
	matrix = matrix * mathutils.Matrix.Translation(locationVector)
	matrix = matrix * scaleMatrix(scaleVector)
	matrix = matrix * rotationMatrix(rotationVector)
	return matrix;

def transformMatrix(location, rotation, scale):
	return toMatrix(arrayToVector(location), arrayToVector(rotation), arrayToVector(scale))
	
def transform(point, location, rotation, scale):
	return transform(point, transformMatrix(location, rotation, scale))

def transforms(points, location, rotation, scale):
	matrix = transformMatrix(location, rotation, scale)
	return [transform(point, matrix) for point in points]

def transform(point, matrix):
	return matrix * arrayToVector(point)
	
def swapTableKeys(table, key1, key2):
	has1 = key1 in table
	has2 = key2 in table
	tmp = None
	if has1:
		tmp = table[key1]
	if has2:
		table[key1] = table[key2]
	else:
		if has1: del table[key1]
	if has1:
		table[key2] = tmp
	else:
		if has2: del table[key2]

# adaptation of http://en.wikipedia.org/wiki/Angle_of_view
def fov(camera):
	return (2 * math.atan(35/(2*camera.lens))) * RAD2DEG

# Validate utilities
def validateEntity(object):
	if not isEmpty(object) and not object.rotation_mode == 'YXZ':
		error(object.name + ' object in scene ' + object.users_scene[0].name + ' has illegal rotation mode: must be YXZ') 
	
def validateTexture(texture):
	if texture.image.size[0] not in validImageSizes or texture.image.size[1] not in validImageSizes:
		error(texture.name + " texture has illegal size: must be power of two") 
	if ' ' in texture.image.filepath:
		error(texture.name + " texture has illegal path-name: must not contain spaces") 

def validateTextureMapping(materialName, slot):
	if not slot.texture_coords == 'UV':
		error(slot.texture.name + ' texture mapping coordinates in material ' + materialName + ' must be UV')

def init():
	# cache some items
	global _armatures
	global _md5Ipos 
	global _md5Meshes 
	_armatures = []
	_md5Ipos = []
	_md5Meshes = []
	parented = []
	for object in bpy.data.objects:
		if object.parent or object.parent_bone:
			parented.append(object)
	for object in bpy.data.objects:
		if object.type == 'ARMATURE':
			_armatures.append(object)
	for armature in _armatures:
		for action in bpy.data.actions:
			if armature.animation_data and armature.animation_data.action == action:
				_md5Ipos.append(armature.animation_data.action)
		for object in parented:
			if object.parent == armature or object.parent_bone in armature.data.bones:
				_md5Meshes.append(object)
# testing purposes
def test():
	pass
