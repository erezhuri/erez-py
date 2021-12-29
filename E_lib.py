#!/usr/bin/env python

class paintText:
	
	''' text colors'''
	def gray(self, text):
		return "\033[30m%s\033[1;0m" % text
	
	def red(self, text):
		return "\033[1;31m%s\033[1;0m" % text

	def green(self, text):
		return "\033[1;32m%s\033[1;0m" % text
		
	def yellow(self, text):
		return "\033[33m%s\033[1;0m" % text

	def blue(self, text):
		return "\033[34m%s\033[1;0m" % text	

	def purple(self, text):
		return "\033[1;35m%s\033[1;0m" % text

	def turquoise(self, text):
		return "\033[1;36m%s\033[1;0m" % text
	
	def darkRed(self, text):
		return "\033[1;38m%s\033[1;0m" % text	

	def maroon(self, text):#very dark red
		return "\033[1;91m%s\033[1;0m" % text
			
	def brown(self, text):
		return "\033[1;93m%s\033[1;0m" % text

	def darkGreen(self, text):
		return "\033[1;92m%s\033[1;0m" % text
	
	def darkPurple(self, text):
		return "\033[95m%s\033[1;0m" % text
	
	def darkBlue(self, text):
		return "\033[94m%s\033[1;0m" % text
	
	def black(self, text):
		return "\033[90m%s\033[1;0m" % text

	''' text effects'''
	def blink(self, text):
		return "\033[1;5m%s\033[1;0m" % text
	
	def underscore(self, text):
		return "\033[1;4m%s\033[1;0m" % text
	
	''' text back Ground '''
	def BR_red(self, text):
		return "\033[1;48m%s\033[1;0m" % text
	
	def BR_darkRed(self, text):
		return "\033[1;41m%s\033[1;0m" % text
		
	def BR_purple(self, text):
		return "\033[1;45m%s\033[1;0m" % text
		
	def BR_gray(self, text):
		return "\033[1;47m%s\033[1;0m" % text
	
	def BR_brown(self, text):
		return "\033[1;43m%s\033[1;0m" % text
	
	def BR_green(self, text):
		return "\033[1;42m%s\033[1;0m" % text
	
	def BR_blue(self, text):
		return "\033[44m%s\033[1;0m" % text

class skull():
	def __init__(self,value):
		out = '\n%s\n= WARNING: %s =\n%s' % ("="*(len("WARNING: " + value)+4), value, "="*(len("WARNING: " + value)+4))
		out +='''

       .... NO! ...                  ... MNO! ...
   ..... MNO!! ...................... MNNOO! ...
 ..... MMNO! ......................... MNNOO!! .
..... MNOONNOO!   MMMMMMMMMMPPPOII!   MNNO!!!! .
 ... !O! NNO! MMMMMMMMMMMMMPPPOOOII!! NO! ....
    ...... ! MMMMMMMMMMMMMPPPPOOOOIII! ! ...
   ........ MMMMMMMMMMMMPPPPPOOOOOOII!! .....
   ........ MMMMMOOOOOOPPPPPPPPOOOOMII! ...
    ....... MMMMM..    OPPMMP    .,OMI! ....
     ...... MMMM::   o.,OPMP,.o   ::I!! ...
         .... NNM:::.,,OOPM!P,.::::!! ....
          .. MMNNNNNOOOOPMO!!IIPPO!!O! .....
         ... MMMMMNNNNOO:!!:!!IPPPPOO! ....
           .. MMMMMNNOOMMNNIIIPPPOO!! ......
          ...... MMMONNMMNNNIIIOO!..........
       ....... MN MOMMMNNNIIIIIO! OO ..........
    ......... MNO! IiiiiiiiiiiiI OOOO ...........
  ...... NNN.MNO! . O!!!!!!!!!O . OONO NO! ........
   .... MNNNNNO! ...OOOOOOOOOOO .  MMNNON!........
   ...... MNNNNO! .. PPPPPPPPP .. MMNON!........
      ...... OO! ................. ON! .......
         ................................

'''
		self.value = out
	def __str__(self):
		return self.value
	
class TreeConfigError(Exception):
	def __init__(self, tree = ""):
		errorStr = skull("TreeConfig was not set on this shell.")
		if tree:
			self.value = str(errorStr) + "Run the following: \033[1;32mcd %s; source `mbk root`/ME.Develop/BuildSys/TreeConfig.sh; cd -\033[1;0m" % tree
		else:
			self.value = str(errorStr) + "Run the following in the tree: \033[1;32msource `mbk root`/ME.Develop/BuildSys/TreeConfig.sh\033[1;0m"
	def __str__(self):
		return self.value

class QaError(Exception):
    # color = paintText() 
    def __init__(self, appName = "General"):
        self.value = paintText().red("\n== %s Error ==\n" % appName)
    def __str__(self):
        return self.value

def mkdirs(newdir): # this will make a new dir in the path given
	import os
	""" Create a directory and all parent folders.
        Features:
        - parent directoryies will be created
        - if directory already exists, then do nothing
        - if there is another filsystem object with the same name, raise an exception
	"""
	if os.path.isdir(newdir):
        	return
	elif os.path.isfile(newdir):
        	raise OSError("cannot create directory, file already exists: '%s'" % newdir)
	else:
        	head, tail = os.path.split(newdir)
	if head and not os.path.isdir(head):
		mkdirs(head)
	if tail:
		os.mkdir(newdir)
 
# def IsTreePath(Path): # This function will check if "path" is a tree path
	# '''This function will check if "path" is a tree path
	# if True it return the path to the root of the tree
	# otherwise return False  
	# '''
	# import commands
	# tempCommand = "cd %s ; /mobileye/shared/Tools/mbk/mbk.py root; cd -" % (Path)
	# a = commands.getoutput(tempCommand)
	# return (a.split("\n")[0] + '/') if ("is not a subdirectory of an mbk repository" not in a) else False

def getKey(dic, val):# This function will return list of keys from a dictionary by given value
	'''This function will return list of keys from a dictionary by given value'''
	return [k for k, v in dic.iteritems() if v == val]

def is_number(s): # This function will return true if 's' is a number
    try:
        float(s)
        return True
    except ValueError:
        return False

def min_max(val, minVal, maxVal):
	return min(maxVal, max(minVal, val)) if minVal < maxVal else min(minVal, max(maxVal, val))

def scale_round_min_max( val, scale, minVal, maxVal):
    ival = round(scale * val)
    ival = min_max(ival, minVal, maxVal)
    return ival

def getAboutValue(name, destDir = '.'):# This function will returns value from about.txt given about attribute name, if not exist return None.
    try:
        aboutF = open("%s/about.txt" % destDir,'r')
        about = aboutF.readlines()
        aboutF.close()
    except IOError:
        return 
    for line in about:
    	curName, value = line.split(' ->> ')
    	if curName == name:
    		return value.split('\n')[0]
def setAboutValue(name, value, destDir = '.', update = False):
# This function will add about attribute name and value if not exist. if exist and update is True it will update about attribute value.
	# mkdirs("%s/runlog/" % destDir)
	if not getAboutValue(name, destDir): # If new parameter
		open("%s/about.txt" % destDir,'a').write(name + ' ->> ' + str(value) + '\n')
	elif update:
		about = open("%s/about.txt" % destDir,'r').readlines()
		aboutF = open("%s/about.txt" % destDir,'w')
		for line in about:
			curName, oldValue = line.split(' ->> ')
			if curName == name:
				oldValue = value
			aboutF.write(curName + ' ->> ' + str(oldValue) + '\n')
		aboutF.close()

def TreeConfigCheck(tree = ""):
	color = paintText()
	import sys, commands
	a = commands.getoutput("echo $VMP_ROOT")
	if not a:
	    raise TreeConfigError(tree)
	else:
		return a

if(__name__ == "__main__"):
	color = paintText()      
	skull1 = skull("You've Enetered my Domain!")
	print (skull1)
	# TreeConfigCheck()
