import os
import numpy as np
from collections import namedtuple


class Config:

	def __init__(self):
		## Default
		self.DIGITS = 4
		self.CHARACTERS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
		self.N = 10

	def check(self):
		assert self.DIGITS <= self.N <= len(self.CHARACTERS)

config = Config()
config.check()


Transition = namedtuple('Transition',
                        ('state', 'action', 'next_state', 'reward'))


def init_candidates(digits=None):
	if digits is None:
		digits = config.DIGITS
	candidates = []
	for i in range(10**digits):
		x = int2str(i, digits)
		s = set(x)
		if len(s) < digits:
			continue

		t = False
		for c in s:
			if config.N < 10 and (int(c) > config.N or int(c) == 0):
				t = True
				break
		if t:
			continue
		candidates.append(x)
	return candidates

def separability(target, digits=None):
	for x in target:
		res = []
		for y in target:
			nA, nB = compare(x, y, digits)
			res.append(10*nA + nB)
		v, c = np.unique(res, return_counts=True)
		if np.max(c) == 1:
			return 'self-separable'

	for x in init_candidates(digits):
		res = []
		for y in target:
			nA, nB = compare(x, y, digits)
			res.append(10*nA + nB)
		v, c = np.unique(res, return_counts=True)
		if np.max(c) == 1:
			return 'self-unseparable'
	return 'hard-unseparable'

def compare(x, y, digits=None):
	if digits is None:
		digits = config.DIGITS
	assert len(x) == digits
	assert len(y) == digits

	nA = 0
	nB = 0
	for i in range(digits):
		if x[i] in y:
			if y[i] == x[i]:
				nA += 1
			else:
				nB += 1
	return nA, nB

def int2str(x, digits=None):
	if digits is None:
		digits = config.digits
	assert 0 <= x <= 10**digits

	if digits == 4:
			return '{:04d}'.format(x)
	elif digits == 3:
			return '{:03d}'.format(x)
	elif digits == 2:
			return '{:02d}'.format(x)
	elif digits == 1:
			return '{:01d}'.format(x)
	else:
		raise NotImplementedError("DIGITS Not implemented!")

def AB2str(nA, nB):
	if nB == 0:
		if nA == 0:
			return '0A0B'
		else:
			return '_{:d}A_'.format(nA)
	else:
		if nA == 0:
			return '_{:d}B_'.format(nB)
		else:
			return '{:d}A{:d}B'.format(nA, nB)

if __name__ == '__main__':
	target = ['132', '321', '213']
	target = ['134', '142', '421', '324', '413', '243']
	target = ['12', '13', '14', '15']
	print(target)
	print(separability(target, digits=2))
	'''
	candidates_set = init_candidates()
	n_candidates = len(candidates_set)
	compare_matrix = np.zeros([n_candidates, n_candidates], dtype=int)
	candidates_ID = {}
	for i in range(n_candidates):
		candidates_ID[candidates_set[i]] = i
		for j in range(n_candidates):
			nA, nB = compare(candidates_set[i], candidates_set[j])
			compare_matrix[i][j] = 10*nA + nB

	data = {
		'candidates': candidates_set,
		'candidates_ID': candidates_ID,
		'compare_matrix': compare_matrix,
	}

	np.save('BullsCows_{:d}_{:d}.npy'.format(config.DIGITS, config.N), data)
	'''

