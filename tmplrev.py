import difflib

class Symbol:
	def __init__(self,symbol):
		self.symbol = symbol
	
	def __repr__(self):
		return '%s()' % type(self).__name__

	def __str__(self):
		return self.symbol

	def __eq__(self,other):
		if isinstance(other,Symbol):
			return self.symbol == other.symbol
		return False

class BOF(Symbol):
	def __init__(self):
		Symbol.__init__(self,'BOF')

class EOF(Symbol):
	def __init__(self):
		Symbol.__init__(self,'EOF')

class ANY(Symbol):
	def __init__(self):
		Symbol.__init__(self,'ANY')

class Template(list):
    def __init__(self, arr):
        for item in arr:
        	self.append(Chunk(item))
			
    def __str__(self):
    	return  ", ".join( (str(item) for item in self) )

class Chunk:
    def __init__(self, arr):
        self.left = arr[0]
        self.right = arr[2]

    def __str__(self):
        return " ".join((str(item) for item in self.left if not isinstance(item,Symbol))) + " ... " + "".join((str(item) for item in self.right if not isinstance(item,Symbol)))


def diff(a, b):
	if isinstance(a, str):
		a = tuple(c for c in a)
	if isinstance(b, str):
		b = tuple(c for c in b)

	_ANY = ANY()

	before = 0
	yield BOF()
	for d in difflib.ndiff(a, b):
		if not d.startswith('+') and not d.startswith('?'):
			if d[0] == '-':
				if before == 0:
					yield _ANY
					before = 1
			else:
				yield d[2:]
				before = 0
	yield EOF()


def partition(seq, length, step=None):
	if step is None or step <= 0:
		step = length
	seq = tuple(seq)
	for i in range(0, len(seq) - length + step, step):
		yield seq[i:i + length]


def partition_by(seq, val):
	part = []
	for item in seq:
		if item != val:
			part.append(item)
		else:
			if part:
				yield part
			part = []
			yield val
	if part:
		yield part


def detect(a, b, sidelen=10):
	return partition(partition_by(diff(a, b), ANY()), 3, 2)


import unittest


class TestSequenceFunctions(unittest.TestCase):
	def test_partition(self):
		p = list(partition([1, 2, 3, 4, 5, 6, 7], 2, 1))
		self.assertEqual(p, [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7)])
		p = list(partition([1, 2, 3, 4, 5, 6, 7], 2))
		self.assertEqual(p, [(1, 2), (3, 4), (5, 6), (7,)])
		p = list(partition([1, 2, 3, 4, 5, 6, 7], 2, 3))
		self.assertEqual(p, [(1, 2), (4, 5), (7,)])

	def test_partition_by(self):
		self.assertEqual(tuple(partition_by([1, 2, 3], 2)), ([1],2,[3]))

class TestMain(unittest.TestCase):

	def test_symbol(self):
		self.assertEqual(ANY(), Symbol('ANY'))
		self.assertEqual(ANY(), ANY())
		self.assertNotEqual(EOF(), ANY())
		self.assertEqual(str(ANY()), 'ANY')
		self.assertIsInstance(ANY(), Symbol)

	def test_diff(self):
		self.assertEqual(tuple(diff(('a', 'b', 'c'), ('a', 'd', 'c'))), (BOF(), 'a', ANY(), 'c', EOF()))

		d = diff("Hello I am khs".split(), "Hello I was in there khs".split())
		self.assertEqual(tuple(partition(d, 2, 1)),((BOF(), 'Hello'), ('Hello', 'I'), ('I', ANY()), (ANY(), 'khs'), ('khs', EOF())))

		d = diff("Hello there, I was been there aaa".split(),
		         "Hello there, he was in there khs".split())
		self.assertEqual( tuple(partition_by(d, ANY())),
						  ([BOF(), 'Hello', 'there,'], ANY(), ['was'], ANY(), ['there'], ANY(), [EOF()]) )

		d = diff("Hello! there, I was been there aaa".split(),
		         "Hello there, he was in there khs".split())
		self.assertEqual( tuple(partition_by(d, ANY())), 
						  ([BOF()], ANY(), ['there,'], ANY(), ['was'], ANY(), ['there'], ANY(), [EOF()]) )

		d = diff("Hello! there, I was been there aaa".split(),
		         "Hello there, he was in there khs".split())
		self.assertEqual( tuple(d),
						  (BOF(), ANY(), 'there,', ANY(), 'was', ANY(), 'there', ANY(), EOF()) )

		d = diff("Hello! there, I was been there aaa".split(),
		         "Hello there, he was in there khs".split())
		self.assertEqual( tuple(partition(partition_by(d, ANY()), 3, 2)), 
						  (([BOF()], ANY(), ['there,']), (['there,'], ANY(), ['was']), (['was'], ANY(), ['there']), (['there'], ANY(), [EOF()])) )

	
	def test_detect(self):
		d = detect("Hello! there, I was been there aaa".split(),
		           "Hello there, he was in there khs".split())
		self.assertEqual( tuple(d),
						  (([BOF()], ANY(), ['there,']), (['there,'], ANY(), ['was']), (['was'], ANY(), ['there']), (['there'], ANY(), [EOF()])) )

		d = detect("Hello there, I was been there aaa".split(),
				   "Hello there, he was in there khs".split())
		self.assertEqual( tuple(d),
						  (([BOF(), 'Hello', 'there,'], ANY(), ['was']), (['was'], ANY(), ['there']), (['there'], ANY(), [EOF()])) )

		d = detect("Hello there, I was been there aaa".split(),
				   "Hello there, he was in there khs".split())
		self.assertEqual( str(Template(d)), "Hello there, ... was, was ... there, there ... ")


if __name__ == '__main__':
	unittest.main()

	

	
