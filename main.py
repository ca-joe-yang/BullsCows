import os
import numpy as np
from scipy.stats import entropy
from collections import namedtuple

from utils import *


class Teacher:

	def __init__(self):
		self.secret = np.random.permutation(config.CHARACTERS)[:config.DIGITS]

	def check(self, guess):
		nA, nB = compare(guess, self.secret)
		if nB == 0 and nA == config.DIGITS:
			return True, (nA, nB)
		else:
			return False, (nA, nB)

class Student:
	def __init__(self):
		self.candidates = init_candidates_set
		self.impossible = []

		# For rule based
		self.flag = 'random'
		self.N = len(config.CHARACTERS)
		self.C = list(np.random.permutation(config.CHARACTERS))

		self.compare_matrix = compare_matrix
		self.candidates_ID = candidates_ID

	def method_random(self):
		guess = self.candidates[np.random.randint(len(self.candidates))]
		return guess

	def method_entropy(self, lucky=True):
		if len(self.candidates) <= 2 or len(self.candidates) == len(init_candidates_set):
			return self.method_random()

		ID_2 = [ self.candidates_ID[c] for c in self.candidates]

		def compute_entropy(x):
			#x = list(np.random.permutation(x))
			E = []
			ID_1 = [ self.candidates_ID[g] for g in x ]
			M = self.compare_matrix[np.ix_(ID_1, ID_2)]
			for i in range(len(x)):
				values, counts = np.unique(M[i], return_counts=True)

				e = entropy(counts, base=None)
				#print(tmp, e)
				E.append(e)

			return x[np.argmax(E)], np.max(E)

		g1, e1 = compute_entropy(self.candidates)
		if lucky:
			return g1

		g2, e2 = compute_entropy(self.impossible)
		if e1 >= e2:
			return g1
		else:
			#print(g2, e2)
			#print(g1, e1)
			#print(self.candidates)
			return g2

	def method_rule_for_2(self, lucky=True):
		assert config.DIGITS == 2
		if len(self.candidates) <= 2:
			return self.method_random()
		def func_1():
			self.R = self.C[2:].copy()
			self.G = self.C[:2].copy()
			return self.C[0] + self.C[1]

		def func_2():
			if self.N == 3:
				return [self.C[0] + self.R[0], self.R[0] + self.C[1]][np.random.randint(1)]
			elif self.N == 4:
				self.flag = '1A-4'
				return self.C[0] + self.R[0]
			elif self.N == 5:
				self.flag = '1A-5'
				return self.C[0] + self.R[0]
			elif self.N >= 6:
				self.flag = '1A-6'
				return self.R[0] + self.R[1]


		if self.flag == 'random':
			self.flag = 'second'
			return func_1()
		elif self.flag == 'second':
			if self.last_clue == (0, 2):
				return self.G[::-1]
			elif self.last_clue == (0, 0):
				self.N -= 2
				self.C.remove(self.last_guess[0])
				self.C.remove(self.last_guess[1])
				return func_1()
			elif self.last_clue == (1, 0):
				return func_2()

			elif self.last_clue == (0, 1):
				self.G == self.G[::-1]
				return func_2()
		elif self.flag == '1A-4':
			if self.last_clue == (1, 0):
				return self.C[0] + self.R[1]
			elif self.last_clue == (0, 1):
				return self.R[0] + self.C[1]
			elif self.last_clue == (0, 0):
				return self.R[1] + self.C[1]
		elif self.flag == '1A-5':
			if self.last_clue == (1, 0):
				return [self.C[0] + self.R[1], self.C[0] + self.R[2]][np.random.randint(1)]
			elif self.last_clue == (0, 1):
				return self.R[0] + self.C[1]
			elif self.last_clue == (0, 0):
				return [self.R[1] + self.C[1], self.R[2] + self.C[1]][np.random.randint(1)]
		elif self.flag == '1A-6':
			if self.last_clue == (1, 0):
				return [self.C[0] + self.R[1], self.R[0] + self.C[1]][np.random.randint(1)]
			elif self.last_clue == (0, 1):
				return [self.C[0] + self.R[0], self.R[1] + self.C[1]][np.random.randint(1)]
			elif self.last_clue == (0, 0):
				self.N -= 2
				self.R.remove(self.last_guess[0])
				self.R.remove(self.last_guess[1])
				return func_2()

	def update(self, guess, clue):
		new_candidates = []
		for c in self.candidates:
			if compare(guess, c) == clue:
				new_candidates.append(c)
			else:
				self.impossible.append(c)
		self.candidates = new_candidates

		# For rule-based
		self.last_guess = guess
		self.last_clue = clue




if __name__ == '__main__':

	history = []
	verbose = True
	verbose = False

	config.DIGITS = 2
	config.CHARACTERS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
	config.N = 10
	config.check()

	if not os.path.exists('BullsCows_{:d}_{:d}.npy'.format(config.DIGITS, config.N)):
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
		init_candidates_set = candidates_set
		np.save('BullsCows_{:d}_{:d}.npy'.format(config.DIGITS, config.N), data)
	else:
		data = np.load('BullsCows_{:d}_{:d}.npy'.format(config.DIGITS, config.N), allow_pickle=True).item()
		init_candidates_set = data['candidates']
		candidates_ID = data['candidates_ID']
		compare_matrix = data['compare_matrix']
		n_candidates = len(init_candidates_set)

	n_game = 10000
	data = []
	for _ in range(n_game):
		print(_, end='\r')
		teacher = Teacher()
		student = Student()
		n_steps = 0
		next_state = np.zeros(n_candidates)
		while True:
			state = next_state
			for c in student.candidates:
				state[candidates_ID[c]] = 1
			n_steps += 1
			guess = student.method_random()
			action = np.zeros(n_candidates)
			action[candidates_ID[guess]] = 1
			#guess = student.method_entropy(True)
			#guess = student.method_rule_for_2()
			answer, clue = teacher.check(guess)
			nA, nB = clue
			student.update(guess, clue)
			next_state = np.zeros(n_candidates)
			for c in student.candidates:
				next_state[candidates_ID[c]] = 1
			reward = (2*nA + nB) / (2 * config.DIGITS)
			data.append(Transition(state, action, next_state, reward))
			if verbose:
				print(guess, AB2str(clue[0], clue[1]))
			if answer:
				break
			
		

		if verbose:
			print()
		history.append(n_steps)
	print()
	print(np.max(history), np.average(history))
	values, counts = np.unique(history, return_counts=True)
	H = dict(zip(values, counts))
	print(H)
