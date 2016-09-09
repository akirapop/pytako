
"""  Implementation of the algorithm of Van Flandern and Pulkkinen,
     Ap J. Supp., 41:391 (1979), for calculating approximate (~ 10 arcminutes)
     right-ascension and declination for the sun, moon, planets and pluto.
"""

from SSOtable_py3 import SSOtable
from generic_py3 import openfile, filedata, degreesTohhMMss


import math

############## Module initialization ##############

## Globals

asin=math.asin
sqrt=math.sqrt
twoPi= 2.0 * math.pi

#dataDir="/home/baluta/Scheduling/bin/Data/SolarSystemVanFlandern/"
dataDir="SolarSystemVanFlandern/"

## Fundamental Arguments, reading & book-keeping
_fundamentalArgsFile="/".join( [ dataDir, "VanFlandern-Pulkkinen.Fundamental_Arguments"] )

####+
## The fundamental arguments dictionary contains, for each key, a
## two-element list: [closure to calculate the value, the current value]
####-

_fundamentalArguments={}
_activeArguments= []


# Initialization code: initialize the _fundamentalArguments
def __buildFundamentalArgsClosure(a,b):
    def func(t):
       val= a + b*t

       ## Return the fractional portion only. 
       dec = abs(val) % 1
       if val < 0.0:
         return -dec
       else:
         return dec
    return func

def __readFundamentalArgs(fundamentalArgsFile):

    global _fundamentalArguments
             
    file=openfile(fundamentalArgsFile)

    for line in filedata(file):
       ele, a, b= line.split()[0:3]
       _fundamentalArguments[ele]= [ __buildFundamentalArgsClosure (float(a), float(b)), 0.0 ]

__readFundamentalArgs(_fundamentalArgsFile)

############## End, module initialization ##############

def _truncate(val):
    decimal= abs(val) % 1
    if val < 0.0:
       return -decimal
    else:
       return decimal


def __sumSeries (T, series):
   fargs= _fundamentalArguments
   total=0.0

   ## Each element of the series contains a tuple: two "code references" and a tuple of terms
   for amp,sinOrCos,trigSeries in series:
       x= sum([ fargs[term][1] * val for term,val in trigSeries])
       total += amp(T) * sinOrCos ( twoPi * x )
   return total

######## Time globals  ######## 
jd=0.0
t=0.0
T=0.0
epsilon= 0.0416666667         # 1 hour

JD0 = 2451545.0

def _updateFundamentalArgs():
     global _fundamentalArguments
     global _activeArguments

     for term in _activeArguments:
         _updater= _fundamentalArguments[term][0]
         _fundamentalArguments[term][1]= _updater(t)


def __update_t (_jd, _epsilon=epsilon):

     global jd, t, T

     if (jd - epsilon) <= _jd <= (jd + epsilon):
       return

     jd=_jd
     t= jd - JD0
     T= 1.0 + t / 36525.0
 
     _updateFundamentalArgs()

def _calculateRaDec (_jd, Units, _sso):
    __update_t (_jd)

    uSeries= _sso.uSeries
    vSeries= _sso.vSeries
    wSeries= _sso.wSeries
    Lterm=_sso.longitudeTerm

    L= _fundamentalArguments[Lterm][1]

    U= __sumSeries(T, uSeries)
    V= __sumSeries(T, vSeries)
    W= __sumSeries(T, wSeries)

    alpha= 360.0 * ( L + asin( W / sqrt(U - V*V)) / twoPi )

    while True:
      if alpha < 0.0:
         alpha += 360.0
      else:
         break

    while True:
      if alpha > 360.0:
         alpha -= 360.0
      else:
         break

    sqrtU= sqrt(U)
    delta= 360.0 * asin (V/sqrtU) / twoPi

    if Units != "degrees":
      alpha, delta= degreesTohhMMss(alpha), degreesTohhMMss(delta, 1.0)

    rho=_sso.deltaBar * sqrtU
 
    return (alpha, delta, rho)

def _calculateDistanceFromSun (_jd, _sso):
    __update_t (_jd)

    rSeries= _sso.rSeries

    R= __sumSeries(T, rSeries)

    return R


# Wrap the functions into closures
def _wrapRaDec(sso):
    def _pos(_jd, Units="degrees"):
        ra, dec, rho= _calculateRaDec(_jd, Units, sso)
        return ra, dec
    return _pos

def _wrapRaDecRearth(sso):
    def _pos(_jd, Units="degrees"):
        ra, dec, re= _calculateRaDec(_jd, Units, sso)
        return ra, dec, re
    return _pos

def _wrapDistanceFromSun(sso):
    def _rsun(_jd):
        return _calculateDistanceFromSun(_jd, sso)
    return _rsun

###############################################################################################

class SSO(object):
    def __init__(self, _sso):
        self.name=_sso.name

        self.raDec= _wrapRaDec(_sso)
        self.raDecRearth= _wrapRaDecRearth(_sso)
        self.rSun= _wrapDistanceFromSun(_sso)

    def __str__(self):
        return self.name

###############################################################################################
def _markActive (trigTerms, longitudeTerm):
     for term in trigTerms:
         if not term in _activeArguments:
              _activeArguments.append(term)

     if not longitudeTerm in _activeArguments:
         _activeArguments.append(longitudeTerm)


_activeSSO={}   # Dictionary of all objects that have been created/requested.
def _register(name):
    if name in _activeSSO:
       sso= _activeSSO[name]
    else:
       ssoData= SSOtable(name)
       sso= SSO(ssoData) 
       _markActive(ssoData.trigTerms, ssoData.longitudeTerm)
       _updateFundamentalArgs()
       _activeSSO[name]= sso
       
    return sso

ssoNameMap= {  "sun":"sun",
               "Sun":"sun",
               "SUN":"sun",
               "mercury":"mercury",
               "Mercury":"mercury",
               "MERCURY":"mercury",
               "venus":"venus",
               "Venus":"venus",
               "VENUS":"venus",
               "moon":"moon",
               "Moon":"moon",
               "MOON":"moon",
               "mars":"mars",
               "Mars":"mars",
               "MARS":"mars",
               "jupiter":"jupiter",
               "Jupiter":"jupiter",
               "JUPITER":"jupiter",
               "saturn":"saturn",
               "Saturn":"saturn",
               "SATURN":"saturn",
               "uranus":"uranus",
               "Uranus":"uranus",
               "URANUS":"uranus",
               "neptune":"neptune",
               "Neptune":"neptune",
               "NEPTUNE":"neptune",
               "pluto":"pluto",
               "Pluto":"pluto",
               "PLUTO":"pluto"     }


def lookupName(name):
   ''' Maps a given name to an SSO name '''
   return ssoNameMap[name]

####+ 
#
#    This is the principle (only!) part of the interface. The
# routine returns a _closure_ that will calculate the position
# of the given body.
#
# Example usage:
#
#    sunPos= solarSystem.Ephemeris('sun')
#
#    sun_alpha, sun_delta= sunPos(t) ; t = t + delta_t
#    sun_alpha, sun_delta= sunPos(t) ; t = t + delta_t
#    sun_alpha, sun_delta= sunPos(t) ; t = t + delta_t
#         .
#         .
#         .
#  sun_alpha & sun_delta are in _degrees_ by default. If the
#  user requires hh,mm,ss instead of degrees:
#
#    sunPos= solarSystem.Ephemeris('sun','hms')
#    sun_alpha, sun_delta= sunPos(t)
#
#
####-

def Ephemeris(obj_name):

     try:
         sso_name= lookupName (obj_name)
     except KeyError:
         print("** Unrecognized planet/object name: %s" % name)
         return None
    
     sso=_register(sso_name)

     return sso 


############################################################################################################

if __name__ == "__main__":

   testJd=2456469.0000


   for tgt in "mercury venus mars jupiter saturn uranus neptune pluto sun moon".split():
      print ("\n%s" % tgt)

      eph=Ephemeris(tgt)
      rSun= eph.rSun (testJd)

#     ra, dec, re=eph.raDecRearth (testJd)
#     print "On the given jd, rp=",rSun,  "re=", re

      raHH, decHH=eph.raDec (testJd, "hhmmss")
      print("In hhmmss: (%s %s) " % (raHH, decHH))

