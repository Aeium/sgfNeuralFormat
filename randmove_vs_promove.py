# first arg is sgf folder path
# second arg is train lmdb name (to be created)
# third is test lmdb name  (to be created)

import numpy as np
import os
import re
from dirtSimpleSGF import SGFsequence
from lmdbReadWrite2 import lmdbReadWrite2
import traceback
import random
import copy
import sys
import time

#  D:\GoGod_Sub\rotation-0\0\2015-03-22c_0.sgf

def getXY(string):

	print(type(string))
	#position = re.search('\[(..)\]', string)
	#return position;

LIBERTY = 'L'
GROUP = 'G'
	
#requires 21 x 21 array
def arrayPrint(array):
  	for i in range( 21 ):
		for j in range( 21 ):         
			idx = int(array[i,j][0])
			if idx > 0:
				print( idx ),
			elif idx == -1:
				print( '8' ),
			else:
				print( '-' ),

		print( '' )

	print( '' )
	
class Stone:
    def __init__(self, c, x, y):
		self.c = c
		self.x = x
		self.y = y

    def __repr__(self):
        return "<Stone c:%s x:%s y:%s>" % (self.c, self.x, self.y)

    def __str__(self):
        return "Stone: %s [ %s , %s ]" % (self.c, self.x, self.y)

class Board:
  def __init__(self, dim, symbols=None):
    self.dim = dim;
    self.libertySet = set(range(361))
    self.groups = [];
    self.stonesArray = np.zeros((21, 21), dtype=np.uint8)
    self.libertiesArray = np.zeros((21,21), dtype=np.uint8)
    self.heavyLibArray = np.zeros((21,21), dtype=np.uint8)
    self.invalid_moves = np.zeros((21,21), dtype=np.uint8)
    self.guidelines = np.zeros((21,21), dtype=np.uint8)
    self.other_info = None
	
    self.stonesArray.fill(127)
	
	#init invalid moves
    for i in range(441):
		x = i % 21
		y = i / 21
		if y == 0 or y == 20 or x == 0 or x == 20:
			self.invalid_moves[y,x] = 1
			
	#init guidelines
    for i in range(441):
		x = i % 21
		y = i / 21
		xline = x if x < 10 else 20 - x
		yline = y if y < 10 else 20 - y
		self.guidelines[y,x] = xline if xline < yline else yline
		
    for i in range(361):
        self.groups.append( None )
	
    self.symbols = symbols
      
	
  def print_board_pointer(self):
    count = 0
    for group in self.groups:
	    value = group.get_current_head().lbl
	    print(value),
	    if count % 19 == 0:
		   print(' ')
	    count = count + 1
		
    self.print_board_libG()
  def print_board_libG(self):
    count = 0
    for group in self.groups:
	    value = group.get_current_head().libertyGroup
	    if(value):
			print('O'),
	    else:
			print('.')
	    if count % 19 == 0:
		   print(' ')
	    count = count + 1
  def __board_to_ints__( self, brd_x, brd_y ):
    #print (brd_x, brd_y)
    #print (ord( brd_x.lower() ) - 97 , ord( brd_y.lower() ) - 97 )
    return ( ord( brd_x.lower() ) - 97 , ord( brd_y.lower() ) - 97 )  
	
  def __board_to_pos__(self, x, y ):
    return ( x + 19 * y )  

  def __check_for_captures__( self ):
    for group in self.groups:
      if not isinstance(group, int) and len( group.liberties ) == 0:
        group = self.groups[ 0 ]


  #backup board before putting down move
  #do move, then go back to backup
  def poof_stone(self, x, y , lbl, number):
  
    #these are the ones that might get messed up
    #backupLibertySet = copy.deepcopy(self.libertySet)
	
    backupLibertySet = set(self.libertySet)
    backupGroups = []
    for group in self.groups:
        if(group):
            backupGroups.append(group.copy())
        else:
            backupGroups.append(None)
	
    #backupGroups = 
    backupStonesArray = np.copy(self.stonesArray)
    backupLibertiesArray = np.copy (self.libertiesArray)
    backupHeavyLibArray = np.copy (self.heavyLibArray)
	
    stack = self.place_stone(x, y, lbl, number)

    if backupLibertySet == self.libertySet and False:
       print("backup lib set == lib set. shallow set copy???")
       print(x, y, y*19+x)
       self.print_board()
       self.print_info()
       print(backupLibertySet)
       print(number)
       exit()
	
	#rewind the clock
    self.libertySet = backupLibertySet
    self.groups = backupGroups
    self.stonesArray = backupStonesArray
    self.libertiesArray = backupLibertiesArray
    self.heavyLibArray = backupHeavyLibArray
	
    #return None
    return stack
  
  def place_stone(self, x, y, lbl, number):
  
    pos = self.__board_to_pos__( x, y )
  
    #x, y = self.__board_to_ints__( brd_x, brd_y )
    
    self.stonesArray[y+1, x+1] = lbl 
    self.libertySet.remove(pos)
	
    self.other_info = np.array(self.invalid_moves, copy=True)
    self.other_info[y+1,x+1] = -1
	
    newGroup = self.groups[pos] = Group(pos, lbl, self, True, False )
	
	#link in 4 directions
    if y + 1 < self.dim:
      north = newGroup.link( pos + 19, self)
    if y - 1 >= 0:
      south = newGroup.link( pos - 19, self)   
    if x + 1 < self.dim:
      east = newGroup.link( pos + 1, self)
    if x - 1 >= 0:
      west =  newGroup.link( pos - 1, self)
	  
    capture = False	
	  
    #  check for captures 4 directions
    if y + 1 < self.dim and north != None:
      checkGroup = north.get_current_head(self)  
      libs = checkGroup.check_liberties(self)
      if libs == 0 and (checkGroup != newGroup):
        checkGroup.remove_group(self)
        capture = True
		
    if y - 1 >= 0 and south != None:
      checkGroup = south.get_current_head(self)
      libs = checkGroup.check_liberties(self)
      if libs == 0 and (checkGroup != newGroup):
        checkGroup.remove_group(self)
        capture = True
		
    if x + 1 < self.dim and east != None:
      checkGroup = east.get_current_head(self)
      libs = checkGroup.check_liberties(self)
      if libs == 0 and (checkGroup != newGroup):
        checkGroup.remove_group(self)
        capture = True
		
    if x - 1 >= 0 and west != None: 
      checkGroup = west.get_current_head(self)
      libs = checkGroup.check_liberties(self)
      if libs == 0  and (checkGroup != newGroup):
        checkGroup.remove_group(self)
        capture = True
	   
	# get current stone on the map
    newGroup.check_liberties(self)
	
	#need to do that before we return the stack
    #self.calc_weights()
    if(capture):
        self.calc_weights()
    else:
        newGroup.weight_add(self)
	
    #if(not self.test_weights()):
    #    print("anomaly! detected!!")
    #    int = 1/0
		
	
    #print("stones" , self.stonesArray[0].dtype)
    #print("liberties" , self.libertiesArray[0].dtype)
    #print("weight" , self.heavyLibArray[0].dtype)
    #print("lines" , self.guidelines[0].dtype)
	
    return np.dstack((self.stonesArray, self.libertiesArray, self.heavyLibArray, self.guidelines))

  def print_board_liberty_test( self, checkGroup, libertySet ):
  
	matrix = np.zeros((self.dim, self.dim))
	
	for group in self.groups:
		if(group.visible):
			for element in group.elements:
				if(group == checkGroup):
					matrix[element/19, element%19] = 2
				else:
					matrix[element/19, element%19] = group.lbl

			
	for liberty in libertySet:
		matrix[liberty/19, liberty%19] = 3
 
	for i in range( self.dim ):
		for j in range( self.dim ):         
			idx = matrix[i,j]
			if idx == 1:
				print( 'B' ),
			elif idx == -1:
				print( 'W' ),
			elif idx == 2:
				print('X'),
			elif idx == 3:
				print('*'),
			else:
				print( '-' ),

		print( '' )
		
  def print_board_liberty( self  ):
  
	#matrix = np.zeros((self.dim, self.dim))
	
	#for group in self.groups:
	#	if(group.visible):
	#		group.check_liberties(self) 
	#		for element in group.elements:
	#				matrix[element/19, element%19] = group.liberties
 
	for i in range( self.dim +2):
		for j in range( self.dim + 2 ):
			if(i == 0 or j == 0 or i == 20 or j == 20):
				print(' '),
				continue
			idx = self.libertiesArray[i,j]
			if idx > 0:
				print( idx ),
			else:
				print( '-' ),

		print( '' )
	return self.libertiesArray
	
  def test_weights(  self ):
  
 	testheavyLibArray = np.zeros((21,21), dtype=np.uint8)
  	for group in self.groups:
		if(group != None and group.isPointer == False):
			libs = group.get_current_head(self).check_liberties(self)
			if (libs == 0):
				continue
			libertySet = group.borders & self.libertySet
			weight = int((len(group.elements) * 40) / libs) 
			for liberty in libertySet:
					x = liberty % 19
					y = liberty / 19
					testheavyLibArray[y + 1, x+1] += weight
	if(np.array_equal(testheavyLibArray, self.heavyLibArray)):
		return True
	else:
		self.print_board()
		print("DIFF ARRAY")
		self.print_weight(np.subtract(self.heavyLibArray, testheavyLibArray ))
		print("test ARRAY")
		self.print_weight(testheavyLibArray)
		print("board ARRAY")
		self.print_weight(self.heavyLibArray)
		return False

	
  def calc_weights(  self ):

	self.heavyLibArray = np.zeros((21,21), dtype=np.uint8)
  	for group in self.groups:
		if(group != None and group.isPointer == False):
			libs = group.get_current_head(self).check_liberties(self)
			if (libs == 0):
				continue
			libertySet = group.borders & self.libertySet
			weight = int((len(group.elements) * 40) / libs) 
			for liberty in libertySet:
					x = liberty % 19
					y = liberty / 19
					self.heavyLibArray[y + 1, x+1] += weight
		
	
  def print_weight( self, array):
  	for i in range( self.dim + 2 ):
		for j in range( self.dim + 2 ):
			if(i == 0 or j == 0 or i == 20 or j == 20):
				print(' '),
				continue			
			idx = array[i,j]#self.heavyLibArray[i,j]
			if idx > 0:
				print(repr(idx).rjust(3)),
			else:
				print( '  -' ),

		print( '' )

	print( '' )
	return self.heavyLibArray
	
  def print_info( self):
  	for i in range( self.dim + 2 ):
		for j in range( self.dim + 2 ):         
			idx = self.other_info[i,j]
			if idx != 0:
				print( idx ),
			else:
				print( ' - ' ),

		print( '' )

	print( '' )
	return self.other_info
	
  def print_guide( self):
  	for i in range( self.dim + 2 ):
		for j in range( self.dim + 2 ):         
			idx = self.guidelines[i,j]
			if idx != 0:
				print( idx ),
			else:
				print( ' - ' ),

		print( '' )

	print( '' )
	return self.guidelines
		
		
  def print_board( self ):
  
	#matrix = np.zeros((self.dim, self.dim))
	
	#for group in self.groups:
	#	if(group.visible):
	#		for element in group.elements:
	#				matrix[element/19, element%19] = group.lbl
 
	for i in range( self.dim + 2 ):
		for j in range( self.dim + 2 ):
			if(i == 0 or j == 0 or i == 20 or j == 20):
				print(' '),
				continue		
			idx = self.stonesArray[i,j]
			if idx == 1:
				print( 'W' ),
			elif idx == 255:
				print( 'B' ),
			elif idx == 2:
				print('X'),
			elif idx == 3:
				print('*'),
			else:
				print( '-' ),

		print( '' )
	return self.stonesArray

  def return_board_array( self ):
	array = np.zeros( (21,21) )
	
	for i in range (self.dim):
		for j in range (self.dim):
			idx = self.groups[ int( self.board[ i ][ j ] ) ]
			while isinstance( idx, int ): 
				idx = self.groups[ idx ]
			
			array[i+1,j+1] = idx.lbl
			
	return array
		
  def return_lib_array( self ):
  	array = np.zeros( (21,21) )
	
	for i in range (self.dim):
		for j in range (self.dim):
			idx = self.groups[ int( self.board[ i ][ j ] ) ]
			while isinstance( idx, int ): 
				idx = self.groups[ idx ]
			
			array[i+1,j+1] = len(idx.liberties)
			
	return array
  
	  
  def print_map( self ):
    print( self.groups ) 
    for i in range( self.dim ):
      for j in range( self.dim ):
        idx = self.board[ i ][ j ]
        while isinstance( idx, int ):
          idx = self.groups[ idx ]
        print( "%2d" % int( idx ) ),
      print( ' ' )

  def print_groups( self ):
    for group in self.groups:
      if not isinstance( group, int ):
        print( "GROUP " + str( group.idx ) + ":\n - liberties: " + str( len( group.liberties ) ) + "\n - size: " + str( len( group.elements ) ) + "\n----------------------------------" )

class Group:
  def __init__( self, pos, lbl, board, visible, libertyGroup ):
  
    self.lbl = lbl	
    self.elements = set([pos]) 
    self.borders = set([])
    self.liberties = 0
    self.visible = visible
    self.pointer = None	
    self.isPointer = False
    self.weight = 0
    self.id = pos
    self.familiarGroups = set([])
	
  def copy(self):
  
    # the basic idea is that groups need to be pointers or have their full info but not both
	# so splitting them up that way might save copy time
  
    if(self.isPointer):
        copyGroup = Group(None, None, None, None, None)
        copyGroup.pointer = self.pointer  # this is still the old pointer
        copyGroup.isPointer = True
        copyGroup.id = self.id
        return copyGroup
  
    else: 
        copyGroup = Group(None, self.lbl, None, self.visible, None)
        copyGroup.elements = set(self.elements)
        copyGroup.borders = set(self.borders)
        copyGroup.liberties = self.liberties	
        copyGroup.pointer = None
        copyGroup.isPointer = False
        copyGroup.id = self.id
        return copyGroup
	
  def print_group(self):
     for i in range(361):
	    if i in self.elements:
		   print (self.liberties),
	    else:
		   print ('.'),
	    if i % 19 == 0:
		   print(' ')

  def print_libs(self, libertySet):
     for i in range(361):
	    if i in libertySet:
		   print ('0'),
	    else:
		   print ('.'),
	    if i % 19 == 0:
		   print(' ')
		   
  def weight_add(  self, board ):

	libs = (self.borders & board.libertySet)
	if(len(libs) > 0):
		weight = int((len(self.elements) * 40) / len(libs))
		for liberty in libs:
			x = liberty % 19
			y = liberty / 19
			board.heavyLibArray[y + 1, x+1] += weight
	
  #always called from new stone so we know where we are
  def link(self, localposition, board): 
	
	if (localposition in board.libertySet):
		self.borders.add(localposition)
		return None
	
	local = board.groups[localposition]
	local = local.get_current_head(board)

	if(local.id == self.id):
		return None #already done here
	
	# weights stuff
	# subtract weights from any group that might get changed
	if(local.id not in self.familiarGroups):
		prevLiberties = (local.borders & board.libertySet)
		prevLiberties.add(self.id)
		weight = len(local.elements) * 40 / len(prevLiberties)
		for liberty in prevLiberties:
			x = liberty % 19
			y = liberty / 19
			board.heavyLibArray[y + 1, x+1] -= weight
	
	
	if ((self.lbl == local.lbl) & (local != self)):
		
		self.elements |= local.elements
		self.borders |= local.borders
		self.borders -= self.elements
		local.pointer = self.id
		local.isPointer = True
		#local.visible = False

		
		# if the new stone does link we should wait
		# until all four link attempts have worked
	
	else:
		self.borders.add(localposition)
		
		# if the new stone doesn't link it's safe to write the modified
		# weight back now
		if(local.id not in self.familiarGroups):
			prevLiberties.remove(self.id)
			if(len(prevLiberties) > 0):
				weight = len(local.elements) * 40 / len(prevLiberties)
				for liberty in prevLiberties:
					x = liberty % 19
					y = liberty / 19
					board.heavyLibArray[y + 1, x+1] += weight
			self.familiarGroups.add(local.id)
		
	if(len(self.borders) == 0):
	    print("EMPTY BORDERS WTF HOW POSSIBLE")
	    print(self.elements)
	    traceback.print_exception()
	    exit()
	
	return local
  
  #returns the currently active group head  
  def get_current_head(self, board):
	if(self.isPointer):
		return board.groups[self.pointer].get_current_head(board)   #self.pointer.get_current_head()
	else:
		return self   

		
  # might be possible to subtract previous weight whenever removing
  # or merging parts of groups
  # and add weight whenever adding group
  # always adding from root of group
		
  def check_liberties(self, board):
	self.borders -= self.elements  
	libertySet = self.borders & board.libertySet
	self.liberties = len(libertySet)
	for element in self.elements:
		x = element % 19
		y = element / 19
		board.libertiesArray[y+1, x+1] = self.liberties
	return self.liberties
	
  def remove_group(self, board):
  
    for element in self.elements:
		x = element % 19
		y = element / 19
		board.stonesArray[y+1,x+1] = 0
		#board.libertySet.add(element)
    self.visible = False
	
	# update surrounding liberties after capture
    board.libertySet |= self.elements
	
    updateSet = self.borders - board.libertySet
	
    updateGroups = set([])
    for frontier in updateSet:
        updateGroups.add(board.groups[frontier].get_current_head(board).id)
    for id in updateGroups:
        if(board.groups[id]):
            board.groups[id].get_current_head(board).check_liberties(board)

	  # lets try adding fresh groups
	  # for i in range(361):
      #  self.groups.append( Group(i, 0, self, False, True ) )	
    for element in self.elements:
	   board.groups[element ] = None
   
   
   
    	
class Board():

	#board = np.zeros((19,19))
  timeStart = time.time()
	
	#moves = [[Stone() for j in range(19)] for i in range(19)]

	#print (board)


	
  countTrain = 0
  countTest = 0
  
  max = 3672204

  rootDir = sys.argv[1]
  
  # name of DB:
  
  #inputDB = sys.argv[2]
  
  dbNameTrain = sys.argv[2]
  dbNameTest = sys.argv[3]
  
  
  train = True
  
 
  
  for dirName, subdirList, fileList in os.walk(rootDir):
    print('Found directory: %s' % dirName)
    for fname in fileList:
	
		
	
        if(True):
		
          print('\t%s' % fname)	

		  # /home/nathan/Go_Database/expanded-GoGod/rotation-7/69/1994-02-17g_7.sgf  new troublesome one
		  # 2015-03-23b_0.sgf is the troublesome one
          if fname.endswith('.sgf'):
            path = os.path.join(dirName, fname)
            f = open( path ,'r')
          else:
            continue
          sgfString = f.read()
	
          game = SGFsequence(sgfString)
          board = Board( 19 ) 
  
          onesA = np.ones((len(game.moves)))
          zerosA = np.zeros((len(game.moves)))
  
          sequence = np.append(onesA, (zerosA))
  
 
  
         #make a random sequence between random and pro moves
         #so we will know the total length
         #this is also the labels
 
          np.random.shuffle(sequence)
  
          batchLen = len(sequence)
  
          #lets write all the data for a game at once
          data = np.empty((batchLen, 4, 21, 21), dtype=np.uint8)
  
    # game[i].order[0][0][0] this is how you get X
    # game[i].order[0][0][1] this is how you get Y
    # process move by move

          i = 0
          j = 0
		  
          for item in sequence:  
 
			#just tring single stream learning so commenting out siamese thing for now
 
            #writeData2 = lmdbReadWrite2.getRandDataPoint(  max, inputDB)[0] #read from db
 
 
            #moves = random.randrange(280)
			
			
            if(not item):
              #randBoard = Board(19)
              #for randMove in range(0,moves):
                #randomPosition = random.sample((randBoard.libertySet),1)
                #x = randomPosition[0] % 19
                #y = randomPosition[0] / 19
                #randBoard.place_stone(x, y, 1 if randMove % 2 else -1, i-1)
				
              randomPosition = random.sample((board.libertySet),1)
              #print("randompos: %d" % randomPosition[0])
              x = randomPosition[0] % 19
              y = randomPosition[0] / 19
              writeData1 = board.poof_stone(x, y, 1 if i % 2 else -1, i)
	
            else:
              x = game.moves[ i ][0]
              y = game.moves[ i ][1]
              #x, y = board.__board_to_ints__(xchar, ychar)
              writeData1 = board.place_stone( x, y, 1 if i % 2 else -1, i) 
              i = i + 1
              #print("i = %s" % i)
              #array2 = board.print_board()
              #array3 = board.print_weight()
              #array1 = board.print_board_liberty()

            #print(writeData1[0,0,0].dtype)
	
            #transpose1 = writeData1.transpose((2, 0, 1))

            #transpose2 = writeData2 #.transpose((2, 0, 1))
	
            #concatedData = np.concatenate((transpose1, transpose2))
	
            #data[j,:,:,:] = transpose1  #concatedData

            #array2 = board.print_board()
            #array1 = board.print_board_liberty()

            #np.set_printoptions(threshold=np.nan)
            #print(transpose1)
            #print(transpose2)
            #print(concatedData)
			
            j = j + 1
	
          #	def writeToDB(data, label, index, database):


		  
          #print("writing")
          print(countTrain)
          print(countTest)
          #print(data.shape)
          #print(j)
          if(train < 50):
            lmdbReadWrite2.writeToDB(data, sequence, countTrain, dbNameTrain)
            countTrain = countTrain + len(sequence)
            train = train + 1;
          else:
            lmdbReadWrite2.writeToDB(data, sequence, countTest, dbNameTest)
            countTest = countTest + len(sequence)
            train = 0;
			
          	
	
        else:
		  print('Error in \t%s' % fname)
	

	
        #count = count + len(sequence)	
	
	#trainLabel = 'pro_vs_random_moves_train_data'
	
	
	
	   #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    #print("move")
    #print(count)
    #print("class")
    #print(label)
    #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    #a, b, c, d, e = np.dsplit(writeData, 5)
    #arrayPrint(a)
    #arrayPrint(b)
    #arrayPrint(c)
    #arrayPrint(d)
    #arrayPrint(e)
	

    
    #array3 = board.print_weight()
    #array4 = board.print_info()
    #array5 = board.print_guide()
	
	# 5 arrays

    #print(j)
	
    #print("first:")
    #print(data.shape[0])
	
    #print("second:")
    #print(data.shape[1])
	
    #print("third:")
    #print(data.shape[2])
	
    #print("fourth")
    #print(data.shape[3])
	
    #print(data[j][0])	
	
	#addmove()

  print(time.time()-timeStart)

class point:
    def __init__(self, obj): self.obj = obj
    def get(self):    return self.obj
    def set(self, obj):      self.obj = obj
