
def openfile (fileName):
    try:
       file=open (fileName)
    except IOError:
       print("** File %s could not be opened!" % fileName)
       import sys
       sys.exit(2)

    return file

def filedata (file):
    for line in file.readlines():
        if line.startswith('#') or line.isspace():
            continue
        yield line
    file.close()

def degreesTohhMMss(angle, factor=15.0):


    if angle < 0.0:
      sign=-1.0
      angle=-angle
    else:
      sign=1.0

    hh= angle / factor
    hours= int(hh)

    mm= (hh - hours) * 60.0
    minutes= int(mm)

    seconds= (mm - minutes) * 60.0

    return "%d %d %.4f" % (sign*hours, minutes, seconds)

def stringIsDigits(s):
    try:
       int(s)
       return True
    except ValueError:
       return False

