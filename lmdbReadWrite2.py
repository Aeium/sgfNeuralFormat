import numpy as np
import lmdb
import caffe_pb2
import os
import fnmatch
import sys
import struct
import random

import os


map_size_data = 13*(10**11)


class lmdbReadWrite2(object):


	@staticmethod
	def writeToDB(data, labels, startIndex, database):
        
		env = None
		
		env = lmdb.open(database, map_size=map_size_data)

		#print(database)
		#print(data[0])
		print(data[0].dtype)
		
		with env.begin(write=True) as txn:
			# txn is a Transaction object
			for i in range(len(labels)):
			  datum = caffe_pb2.Datum()
			  datum.channels = data.shape[1]
			  datum.height = data.shape[2]
			  datum.width = data.shape[3]
			  datum.data = data[i].tobytes()  # or .tostring() if numpy < 1.9
			  datum.label = int(labels[i])
			  str_id = '{0:08}'.format(startIndex + i)
	
				# The encode is only essential in Python 3
			  txn.put(str_id.encode('ascii'), datum.SerializeToString())
				


	@staticmethod
	def printArray(array1, array2):
		for i in range( 21 ):
			for j in range( 21 ):         
				idx = array1[i,j]
				id2 = array2[i,j]
				if idx == 0:
					print( 'O' ),
				elif idx == 255:
					print( 'X' ),
				elif idx == 2:
					print('W'),
				elif id2 == 0:
					print ('a'),
				elif id2 == 255:
					print ('b'),
				else:
					print( '-' ),
			print( '' )

	@staticmethod
	def readFromDB(index, size, database):
		
		env = lmdb.open(database, readonly=True)
		#with env.begin() as txn:
		#	cursor = txn.cursor()
		#	for i in range (index , size):
			
		#		str_id = '{0:08}'.format(i)
		#		value = cursor.get(str_id.encode('ascii'))
		#		output = '{0:08}'.format(value)
		#		print(i, value)
		
		datum = caffe_pb2.Datum()
		
		with env.begin() as txn:
			cursor = txn.cursor()
			for key, value in cursor:
				datum.proto.caffe_pb2.ParseFromString(value)
				label = datum.label
				channels = datum.channels
				height = datum.height
				width = datum.width
				
				short = 0
				#first = True
				
				readArray = np.zeros((channels, height, width), dtype=np.uint16)
				
				print(channels)
				print(height)
				print(width)
				
				count = 0;
				
				
				for c in datum.data:
					
						readArray[(count/(height*height)%channels),(count/height)%height,count%height ] = ord(struct.unpack('c',c)[0])
						#print(struct.unpack('H',short)[0])
						first = True
						count = count + 1
				
				print(label, "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
				#lmdbReadWrite2.printArray(readArray[1,:,:], readArray[0,:,:])
				#print readArray[2,:,:]
				print readArray[0,:,:]
				#print readArray[4,:,:]
				
			
				
				
				#readArray = struct.unpack('H',datum.data)
				#for element in readArray:
				#	print element
				#print(key, label)
		
		
	@staticmethod
	def getKeys(database):
	
		env = lmdb.open(database, readonly=True)
		#with env.begin() as txn:
		#	cursor = txn.cursor()
		#	for i in range (index , size):
			
		#		str_id = '{0:08}'.format(i)
		#		value = cursor.get(str_id.encode('ascii'))
		#		output = '{0:08}'.format(value)
		#		print(i, value)
		
		datum = caffe.proto.caffe_pb2.Datum()
		
		with env.begin() as txn:
			cursor = txn.cursor()
			
			count = 0
			for key, value in cursor:
			
				print(key)
				count = count + 1
				
				print(value)
				
				if count > 5:
					break
			cursor.close()
	
		
				
	@staticmethod
	def getDatum( index, database):
		env = lmdb.open(database, readonly=True)
		#with env.begin() as txn:
		#	cursor = txn.cursor()
		#	for i in range (index , size):
			
		#		str_id = '{0:08}'.format(i)
		#		value = cursor.get(str_id.encode('ascii'))
		#		output = '{0:08}'.format(value)
		#		print(i, value)
		
		datum = caffe.proto.caffe_pb2.Datum()
		
		
		
		with env.begin() as txn:
			cursor = txn.cursor()
			value = cursor.get(index)
			datum.ParseFromString(value)
			label = datum.label
			channels = datum.channels
			height = datum.height
			width = datum.width
				
			#print(channels)
				
			return datum
				
			short = 0
			#first = True
				
			readArray = np.zeros((channels, height, width), dtype=np.uint16)
				
			count = 0;
				
			for c in datum.data:
					
					readArray[(count/(height*height)%channels),(count/height)%height,count%height ] = ord(struct.unpack('c',c)[0])
					#print(struct.unpack('H',short)[0])
					first = True
					count = count + 1	
			
			cursor.close()
			
		return readArray
				
				
				#readArray = struct.unpack('H',datum.data)
				#for element in readArray:
				#	print element
				#print(key, label)
				
				
	@staticmethod
	def getDataPoint( index, database):
		env = lmdb.open(database, readonly=True)
		#with env.begin() as txn:
		#	cursor = txn.cursor()
		#	for i in range (index , size):
			
		#		str_id = '{0:08}'.format(i)
		#		value = cursor.get(str_id.encode('ascii'))
		#		output = '{0:08}'.format(value)
		#		print(i, value)
		
		datum = caffe.proto.caffe_pb2.Datum()
		
		
		
		with env.begin() as txn:
			cursor = txn.cursor()
			value = cursor.get(index)
			datum.ParseFromString(value)
			label = datum.label
			channels = datum.channels
			height = datum.height
			width = datum.width
				
			#print(channels)
				
			short = 0
			#first = True
				
			readArray = np.zeros((channels, height, width), dtype=np.uint16)
				
			count = 0;
				
			for c in datum.data:
					
					readArray[(count/(height*height)%channels),(count/height)%height,count%height ] = ord(struct.unpack('c',c)[0])
					#print(struct.unpack('H',short)[0])
					first = True
					count = count + 1	
			
			cursor.close()
			
		return [readArray, label]
				
				
				#readArray = struct.unpack('H',datum.data)
				#for element in readArray:
				#	print element
				#print(key, label)
				
	@staticmethod
	def getRandDataPoint( max, database):
	
		while(True):
		 try:
	
		  rand = random.randrange(max)
		
		  index = format((rand) , '08')
	
		  env = lmdb.open(database, readonly=True)
	  	  #with env.begin() as txn:
		  #	cursor = txn.cursor()
		  #	for i in range (index , size):
			
		  #		str_id = '{0:08}'.format(i)
		  #		value = cursor.get(str_id.encode('ascii'))
		  #		output = '{0:08}'.format(value)
		  #		print(i, value)
		
		  datum = caffe.proto.caffe_pb2.Datum()
		
		
		
		  with env.begin() as txn:
		  	  cursor = txn.cursor()
			  value = cursor.get(index)
			  datum.ParseFromString(value)
			  label = datum.label
			  channels = datum.channels
			  height = datum.height
			  width = datum.width
				
			  #print(channels)
				
			  short = 0
			  #first = True
				
			  readArray = np.zeros((channels, height, width), dtype=np.uint16)
				
			  count = 0;
				
			  for c in datum.data:
					
					  readArray[(count/(height*height)%channels),(count/height)%height,count%height ] = ord(struct.unpack('c',c)[0])
					  #print(struct.unpack('H',short)[0])
					  first = True
					  count = count + 1	
			
			  cursor.close()
			
		  return [readArray, label]
		 except:
		  format("missed lookup at" + index)
				
				#readArray = struct.unpack('H',datum.data)
				#for element in readArray:
				#	print element
				#print(key, label)
				
				
