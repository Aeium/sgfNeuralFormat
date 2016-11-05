import string

class SGFsequence:

    moves = []

    def __init__(self, SGFstring):	
	
        self.moves = []
	
        moveCodes = SGFstring.strip().split(';')[2:]
		
        for move in moveCodes:
		  
           #print(move)
		
           x = ord(move[2]) - 97
           y = ord(move[3]) - 97
		   
           self.moves.append((x, y))