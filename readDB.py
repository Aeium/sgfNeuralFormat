from lmdbReadWrite2 import lmdbReadWrite2
import numpy as np

import sys


class readDB():

	def prettyPrint(matrix):
	
		for i in range(matrix.shape[0]):
			for j in range(matrix.shape[1]):
				if(i == 0 or j == 0 or i == 20 or j == 20):
					print(' '),
					continue	
				idx = matrix[i,j]
				if idx < 80:
					print('O'),
				elif idx > 190:
					print('X'),
				elif idx == 127:
					print('-'),
				else:
				    error = 1/0
			print('')

	#lmdbReadWrite2.readFromDB(0, 100, sys.argv[1])
	
	#lmdbReadWrite2.getKeys(sys.argv[1])
	
	for i in range(1500,1600):
	
		np.set_printoptions(threshold=np.nan)
	
		point = lmdbReadWrite2.getDataPoint( format(i , '08'), sys.argv[1])
	
	
		print("NUMBER: %s" % i)
		print(point[1])
		prettyPrint( point[0][0])
		#print(point[0][0])
		print("\n")
		print(point[0][1])
		print("\n")
		print(point[0][2])
		print("\n")
		print(point[0][3])
		print("\n")
		
		#prettyPrint ( point[1][0])