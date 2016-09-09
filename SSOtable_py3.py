####+
#
# 03 June 2013
#
#    This class is intended to serve as an "internal" class
# to be used by the solarSystem.py module. In other words, it 
# is expected that users will *not* make direct use of this 
# class! 
#
#
#    Object instances of this class serve one fundamental
# purpose: To encapsulate the series of data needed to
# calculate approximate positions for given bodies in the
# solar system. It is therefore expected that the 'wrapper'
# module (solarSystem.py) will: (1) instantiate instances
# as requested and (2) access the data stored in the instances.
#
#   The data stored are taken from the paper "Low-Precision
# Formulae for Planetary Positions", Van Flandern and Pulkkinen, 
# Ap J. Supp., 41, 391-411 (1979).  Note that the so-called 
# "Fundamental Arguments" are _not_ encapsulated in this class!
# The solarSystem.py contains/reads this information.
#
####-

from generic_py3 import openfile, filedata

import math
sinCos= { "sin": math.sin,
          "cos": math.cos }

#dataDir="/home/baluta/Scheduling/bin/Data/SolarSystemVanFlandern/"
dataDir="SolarSystemVanFlandern/"

# "SSO" --> "Solar System Object"
class SSOtable (object):

    def __init__(self, name):
       self.name=name.title()
       self.__readUVW(dataDir)
       self.__readSunDistance(dataDir)
#      self.__readUVW("/home/baluta/Scheduling/bin/Data/SolarSystemVanFlandern/")
#      self.__readSunDistance("/home/baluta/Scheduling/bin/Data/SolarSystemVanFlandern/")

    def __str__(self):
       return self.name

    ## The routines that appear below here are initialization-related
    def __closePolyTerm(self, coeff, xp):
       ''' Form a closure of the form: coeff * T^(xp) or, if xp is 0, just coeff. '''
       if xp==0:
          def f(T):
             return coeff
       else:
          def f(T):
             return coeff * (T**xp)
       return f
 
    def __processSeriesString(self, dataString, norm):
       ''' Process the u/v/w portion of input. These should be strings
           that look something like this:
           "38966  0  sin  0  0  0  1  0  0  0 " ''' 
       parts=dataString.split()

       #####
       ## For the U, V, W series, the coefficients in the 
       ## data files been multiplied ## by 100,000, so we 
       ## must divide this term out. The series for the
       ## radius do not have this normalization applied.
       #####
       coeff= float(parts[0]) / norm
       exponent=float(parts[1])
       trigFunc= sinCos[parts[2]]
       series=[]
      
       #### 
       # Now process the trigonometric series: If the term is a 0, skip it.
       # Otherwise, prepare a tuple of the appropriate "fundamental element"
       # and the current term.  The "wrapper" library/module (solarSystem.py)
       # will then wrap this information into the appropriate closures.
       #### 
       for k, term in enumerate(parts[3:]):
          n=int(term)
          if n==0:
            continue
          series.append ( (self.trigTerms[k], n) ) 

       poly= self.__closePolyTerm(coeff, exponent)
       trigFunc= sinCos[parts[2]]

       if len(series) == 0:
         series= [ (self.trigTerms[0], 0) ]

       return (poly, trigFunc, tuple(series)) ## Make series a tuple -- don't allow anyone to mess it up!

    def __readUVW (self, dir="./"):
#      fileName= "".join([dir, self.name.lower(), "UVW"])
       file= openfile("".join([dir, self.name.lower(), "UVW"]))

       self.uSeries=[]
       self.vSeries=[]
       self.wSeries=[]

       norm=100000.0

       for line in filedata(file):
          if line.startswith("TrigSeriesTerms"):
              self.trigTerms=line.split()[1:]
          elif line.startswith("LongitudeTerm"):
              self.longitudeTerm=line.split()[1]
          elif line.startswith("DeltaBar"):
              self.deltaBar=float(line.split()[1])
          else:
              v, u, w= line.split("|")

              if not u.isspace():
                 self.uSeries.append ( self.__processSeriesString(u, norm) )
              if not v.isspace():
                 self.vSeries.append ( self.__processSeriesString(v, norm) )
              if not w.isspace():
                 self.wSeries.append ( self.__processSeriesString(w, norm) )

       ## The data encapsulated in this class must not be changed. tuple-ize! 
       self.uSeries= tuple(self.uSeries)
       self.vSeries= tuple(self.vSeries)
       self.wSeries= tuple(self.wSeries)

    def __readSunDistance (self, dir="./"):
#      fileName= "".join([dir, self.name.lower(), "Radius"])
       file= openfile("".join([dir, self.name.lower(), "Radius"]))
       self.rSeries=[]

       norm=1.0

       for line in filedata(file):
          if line.startswith("TrigSeriesTerms"):
              continue

          if not line.isspace():
             self.rSeries.append ( self.__processSeriesString(line, norm) )

       ## The data encapsulated in this class must not be changed. tuple-ize! 
       self.rSeries= tuple(self.rSeries)

if __name__ == "__main__":


     obj="jupiter"
     sso= SSOtable (obj)

     series=sso.__getattribute__('uSeries')
#    for k,s in enumerate(series):
     for k,s in enumerate(sso.uSeries):
        print ("%r: %r" % (k,s[2]))

#    name=sso.__getattribute__('name')
#    print "\nThe name is: ",name
     test= "".join(["blah! ", sso.__str__()])
     print("test: %s" % test)

     tterms=sso.trigTerms
     lterm=sso.longitudeTerm
     deltaBar=sso.deltaBar

     print("\nTrig terms: %r" % tterms)
     print("Longitude term: %r" % lterm)
     print("DeltaBar= %r" % deltaBar)
     print("\nR-Series:\n%r" % sso.rSeries)
