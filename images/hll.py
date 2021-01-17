from hashlib import sha1
from math import ceil, log
from mpmath import inf, quad
from sys import getsizeof

h = lambda d: int(sha1(
	bytes(d.encode('utf8'))
	).hexdigest()[:16], 16)

rho = lambda s, shift: shift - s.bit_length() + 1

integrand = lambda u, m: log((2 + u) / (1 + u), 2) ** m
alpha = lambda m: 1 / (m * quad(
	lambda u: integrand(u, m),
	[0, inf]
	))

class HyperLogLog():

	def __init__(self, error):
		if not (0 < error < 1):
			raise ValueError('Error not in range 0 - 1.')

		self.b = int(ceil(log((1.04 / error) ** 2, 2)))
		self.m = 2 ** self.b
		self.M = [0 for i in range(self.m)]
		self.alpha = alpha(self.m)

	def add(self, v):
		x = h(v)

		j = x & (self.m - 1)
		w = x >> self.b

		self.M[j] = max(self.M[j], rho(w, 64 - self.b))
	
	def __len__(self):
		Z = 1 / sum(2.0 ** -i for i in self.M)
		E = self.alpha * self.m ** 2 * Z
		return round(E)
	
	def get_size(self, helpers=False):
		size = getsizeof(self.M)
		if helpers:
			size += getsizeof(self.b)
			size += getsizeof(self.m)
			size += getsizeof(self.alpha)
		return size