# Helper functions
import array
import tempfile
import io
import os

# globals
out = None
outbin = None
_raw = None
		
def openPrinter(path):
	global out
	global outbin
	dir = os.path.dirname(path)
	if not os.path.exists(dir):
		os.makedirs(dir)
	out = open(path, 'w')
	outbin = open(path+'.bin', 'wb')
	
def closePrinter():
	out.close()
	outbin.close()
	
# write to a tmp memory buffer - useful for MD5 raw data
def beginRaw():
	global _raw
	_raw = io.BytesIO()
#	tmp = NamedTemporaryFile(prefix='bgo.tmp')

def getRaw():
	return _raw.getvalue()
#	os.path.getsize(tmp-)
		
def endRaw():
	global _raw
	_raw.close()
	_raw = None
	
def n():
	p('')
	
def p(s, *args):
	out.write((s+'\n')%tuple(args))

def s(s, *args):
	out.write(s%tuple(args))

def w(*args):
	for arg in tuple(args):
		getWriteMethod(arg)(arg)

def writes(list):
	if len(list) > 0:
		typ = getType(list[0])
		if typ == 'int':
			integersa(list)
		elif typ == 'float':
			realsa(list)
		elif typ == 'str':
			stringsa(list)
		
def integer(i):
	a = array.array('i')
	a.append(i)
	a.byteswap()
	if _raw:
		_raw.write(a)
	else:
		a.tofile(outbin)
	
def short(i):
	a = array.array('h')
	a.append(i)
	a.byteswap()
	if _raw:
		_raw.write(a)
	else:
		a.tofile(outbin)
	
def real(r):
	a = array.array('f')
	a.append(r)
	a.byteswap()
	if _raw:
		_raw.write(a)
	else:
		a.tofile(outbin)
	
def string(str):
	bytes = str.encode('utf8')
	bs = array.array('h')
	bs.append(len(bytes))
	bs.byteswap()
	if _raw:
		_raw.write(bs)
		_raw.write(bytes)
	else:
		bs.tofile(outbin)
		outbin.write(bytes)

def bool(b):
	if b == None or b == 0 or b == False or b == [] or b == {}:
		integer(0)
	else:
		integer(1)

def raws(bindata):
	outbin.write(bindata)

def integersa(i):
	a = array.array('i')
	a.extend(i)
	a.byteswap()
	if _raw:
		_raw.write(a)
	else:
		a.tofile(outbin)
	
def integers(*i):
	if len(i) == 1:
		integersa(i[0])
	else:
		integersa(tuple(i))
		
def realsa(r):
	a = array.array('f')
	a.extend(r)
	a.byteswap()
	if _raw:
		_raw.write(a)
	else:
		a.tofile(outbin)
	
def reals(*rs):
	if len(rs) == 1:
		realsa(rs[0])
	else:
		realsa(tuple(rs))
	
def stringsa(str):
	for s in str: string(s)

def size(objects):
	integer(len(objects))

def getWriteMethod(elem):
	return getMethodByType(getType(elem))
	
def getMethodByType(typ):
	if typ == 'int': return integer;
	elif typ == 'float': return real;
	elif typ == 'str': return string;
	elif typ == 'list': return writes;
	
def getType(e):
	if isinstance(e, type(4)):
		return 'int'
	elif isinstance(e, type(4.4)):
		return 'float'
	elif isinstance(e, type('')):
		return 'str'
	elif isinstance(e, type([])):
		return 'list'
	else:
		error('write: %s not recognized type'%elem)
	
def message(s):
	t = Draw.Create(s)
	block = []
	block.append(('', t, 10, 100, ''))
	Draw.PupBlock(s, block)
	
def error(s):
	e = '### ERROR : '
	out.write(e + s)
	raise Exception(e+s)
		
def abort(s):
	message(s)
	Draw.Exit()
	return