#!/usr/bin/env python
import os


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

    def maroon(self, text):  # very dark red
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


class skull:
    def __init__(self, value):
        out = '\n%s\n= WARNING: %s =\n%s' % (
            "=" * (len("WARNING: " + value) + 4), value, "=" * (len("WARNING: " + value) + 4))
        out += '''

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
    def __init__(self, tree=""):
        errorStr = skull("TreeConfig was not set on this shell.")
        if tree:
            self.value = str(
                errorStr) + "Run the following: \033[1;32mcd %s; source `mbk root`/ME.Develop/BuildSys/TreeConfig.sh; cd -\033[1;0m" % tree
        else:
            self.value = str(
                errorStr) + "Run the following in the tree: \033[1;32msource `mbk root`/ME.Develop/BuildSys/TreeConfig.sh\033[1;0m"

    def __str__(self):
        return self.value


class QaError(Exception):
    # color = paintText() 
    def __init__(self, appName="General"):
        self.value = paintText().red("\n== %s Error ==\n" % appName)

    def __str__(self):
        return self.value


def mkdirs(newdir):  # this will make a new dir in the path given
    """
    Create a directory and all parent folders.
    Features:
        - parent directories will be created
        - if directory already exists, then do nothing
        - if there is another filesystem object with the same name, raise an exception
    :param newdir: Dir name and path
    :return: None
    """
    import os

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

def getKey(dic, val):  # This function will return list of keys from a dictionary by given value
    """
    This function will return list of keys from a dictionary by given value
    :param dic: a dictionary
    :param val: given value
    :return: list of keys
    """
    return [k for k, v in dic.iteritems() if v == val]


def is_number(val):  # This function will return true if 's' is a number
    """
    This function will return true if 's' is a number
    :param val: value to check
    :return: Boolean
    """
    try:
        float(val)
        return True
    except ValueError:
        return False


def min_max(val, minVal, maxVal):
    """
    returns normalized number between min / max
    :param val: Value
    :param minVal: Minimum value
    :param maxVal: Maximum value
    :return: normalized number
    """
    return min(maxVal, max(minVal, val)) if minVal < maxVal else min(minVal, max(maxVal, val))


def scale_round_min_max(val, scale, minVal, maxVal):
    """
    returns rounded and normalized number between min / max
    :param val: Value
    :param scale: Scale of round
    :param minVal: Minimum value
    :param maxVal: Maximum value
    :return: Rounded and normalized
    """
    ival = round(scale * val)
    ival = min_max(ival, minVal, maxVal)
    return ival


def getAboutValue(key, file_name="about.cfg", destDir='.',
                  delimiter='='):  # This function will returns value from about.txt given about attribute name, if not exist return None.
    """
    Returns value from about.txt given about attribute name, if not exist return None.
    :param file_name:
    :param delimiter:
    :param key:
    :param destDir:
    :return: Value or None
    """
    try:
        with open(destDir + '/' + file_name, 'r') as aboutF:
            # aboutF = open("%s/about.txt" % destDir, 'r')
            about = aboutF.readlines()
            # aboutF.close()
            # except IOError:
            #     return
            for line in about:
                curName, value = line.split(delimiter)
                curName = curName.rstrip().lstrip()
                value = value.rstrip().lstrip()
                if curName == key:
                    return value.rstrip('\n')
            return None
    except FileNotFoundError:
        return None


def setConfigValue(key, value, file_name="about.cfg", destDir='.', delimiter='=', update=True):
    """
    This function will add 'about' attribute key and value if not exist.
        Update it if exist and 'update=True'.
    :param key: Key of attribute
    :param value: Value of attribute
    :param file_name:
    :param destDir: Path of file
    :param delimiter:
    :param update: Default true - if set to False will not update value of existing key
    :return: True if set completed, False if not
    """

    # if getAboutValue(key, destDir, file_name, delimiter):  # If new parameter
    #     if not update: return False
    try:
        with open(f'{destDir}/{file_name}', 'r') as f:
            about = f.readlines()
        count = 0
        # for i in range(len(about)):
        for line in about:
            # curName, curValue = about[i].split(delimiter)
            curName, curValue = line.split(delimiter)
            curName = curName.rstrip().lstrip()
            curValue = curValue.rstrip().lstrip()
            if curName == key:
                if not update:
                    return False
                about[count] = f'{key} {delimiter} {value}\n'
                with open(f'{destDir}/{file_name}','w') as f:
                    f.writelines(about)
                return True
            count += 1
    except FileNotFoundError:
        pass
    with open(f'{destDir}/{file_name}','a') as f:
        f.write(f'{key} {delimiter} {value}\n')
    return True
    # aboutF = open("%s/about.txt" % destDir, 'w')
    # for line in about:
    #     curName, oldValue = line.split(' ->> ')
    #     if curName == key:
    #         oldValue = value
    #     aboutF.write(curName + ' ->> ' + str(oldValue) + '\n')
    # aboutF.close()
    # else return False

    # open("%s/about.txt" % destDir, 'a').write(key + ' ->> ' + str(value) + '\n')


def TreeConfigCheck(tree=""):
    import os
    a = os.getenv("VMP_ROOT")
    if not a:
        raise TreeConfigError(tree)
    else:
        return a


if __name__ == "__main__":
    color = paintText()
    skull1 = skull("You've Entered my Domain!")
    print(skull1)
    setConfigValue("key1", "value1", delimiter='-->')
    print(getAboutValue("key1", delimiter='-->'))
    setConfigValue("key1", "value4", delimiter='-->')
    setConfigValue("key2", "value2", delimiter='-->')
    print(getAboutValue("key1", delimiter='-->'))
    print(os.listdir())

# TreeConfigCheck()
