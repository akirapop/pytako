from math import radians, degrees, cos, sin, sqrt, asin, acos, atan2, pi
import itertools

""" This module exports three primary 'objects':

    (1) alpha_delta_to_skyvector()

        This  routine. Given an input ra, dec pair (in _degrees_),
        the corresponding sky vector (as a tuple) is returned.

    (2) skyvector_to_alpha_delta()

        The inverse of routine (1): Given an input tuple (as a _single_ argument, in other
        words, a tuple object) representing a _normalized_ sky vector, the corresponding
        alpha, delta (in _degrees_) are returned

    (3) EulerMatrix

        This is a class representing a "Z-Y-Z" Euler rotation matrix. See the class for
        the routines it exports. (Its primary function is to rotate vectors from 
        sky->sc and sc->sky coordinates.)
"""

def _rationalize(angle_radians):
    """ Given an angle (in _radians_!) 'rationalizes' the angle to the range (0,2pi) """
    two_pi=2*pi

    while angle_radians < 0.000: angle_radians = angle_radians + two_pi
    while angle_radians > two_pi: angle_radians = angle_radians - two_pi

    return angle_radians

def _normalize(vec):
    length_squared= sum( [x*x for x in vec])

    try:
        length= sqrt(length_squared)
    except ValueError:
        print("\n\tDomain error (sqrt function) while normalizing...")

    if length == 0.000:
        return vec

    return [x/length for x in vec]

##########################################################################################################


def alpha_delta_to_skyvector(alpha_degrees, delta_degrees):
    """ Given an alpha, delta (in degrees), returns the sky vector (sidereral coordinates) as a 3-tuple """
    ra, dec= radians(alpha_degrees), radians(delta_degrees)

    return ( cos(ra) * cos (dec),  cos (dec) * sin (ra),  sin (dec) )

def skyvector_to_alpha_delta(sky_vector):
    """ Given a normalized sky vector (sidereal coordinates) as a tuple, returns the corresponding right-ascension, declination in degrees"""
    sky_x, sky_y, sky_z= sky_vector

    try:
        declination= asin(sky_z)
    except ValueError:
        raise ValueError("\n\tskyvector_to_alpha_delta(): Domain error in asin() calculation.\n\n")
#       return None

    right_ascension= _rationalize( atan2( sky_y, sky_x ) )

    return degrees(right_ascension), degrees(declination)    ## Degrees!!

class EulerMatrix:

    """ This class defines operations on "ZYZ" Euler rotation matrices. """

    def __init__(self, e1_degrees, e2_degrees, e3_degrees):
         self.e1= _rationalize(radians( e1_degrees ))
         self.e2= _rationalize(radians( e2_degrees ))
         self.e3= _rationalize(radians( e3_degrees ))

         self._calculateZYZ_rows()

    def _calculateZYZ_rows(self):

         s1, s2, s3= sin(self.e1), sin(self.e2), sin(self.e3)
         c1, c2, c3= cos(self.e1), cos(self.e2), cos(self.e3)

         row1= (c1*c2*c3 - s1*s3, -c2*s3*c1 - c3*s1, c1*s2)
         row2= (c1*s3 + c3*c2*s1, c1*c3 - c2*s1*s3, s2*s1)
         row3= (-c3*s2, s3*s2, c2 )

         self.sc_to_sky_matrix= [row1, row2, row3]
         self.sky_to_sc_matrix= [  (c1*c2*c3 - s1*s3, c1*s3 + c3*c2*s1, -c3*s2),
                             (-c2*s3*c1 - c3*s1,  c1*c3 - c2*s1*s3, s3*s2),
                             (c1*s2,  s2*s1, c2) ]

    def update_rows(self, row1,row2, row3):
         self.matrix[0]= row1
         self.matrix[1]= row2
         self.matrix[2]= row3

    def rotate_to_sky(self, xyz):
         mat=self.sc_to_sky_matrix
         return [ sum([x*y for x,y in itertools.izip(mat[0], xyz)]),\
                  sum([x*y for x,y in itertools.izip(mat[1], xyz)]),\
                  sum([x*y for x,y in itertools.izip(mat[2], xyz)]) ]

    def rotate_to_sc(self, xyz):
         mat=self.sky_to_sc_matrix
         return [ sum([x*y for x,y in itertools.izip(mat[0], xyz)]),\
                  sum([x*y for x,y in itertools.izip(mat[1], xyz)]),\
                  sum([x*y for x,y in itertools.izip(mat[2], xyz)]) ]


    #########################################################################################
    ###     It is sometimes necessary to calculate the angle between the sun vector and   ###
    ### sc+y repeatedly: We at times need to know the sun angle as a function of the      ###
    ### spacecraft roll angle. This calculation may be done efficienctly in the sc        ###
    ### coordinate system. The dot product in this case is simply the y-component of the  ###
    ### normalized sun vector in sc coordinates. As the only angle that changes as the    ###
    ### spacecraft is rolled is the roll angle / third euler angle, there is no sense in  ###
    ### re-calculating the sines/cosines of e1/e2.  Further, the only multiplication      ###
    ### needed is with the second row of the (sky_to_sc) matrix (which is the matrix      ###
    ### calculated/stored here as self.mat.)                                              ###
    ###                                                                                   ###
    ###     Note that this routine returns a _function_ that takes as input a vector      ###
    ### to the sun in _sky_ coordinates, and a roll angle in _degrees_ and returns the    ###
    ### angle between the sun vector and the sc+y axis. The returned angle is in          ###
    ### degrees.                                                                          ###
    #########################################################################################
    def fast_sun_sc_y_dot(self):
        """
             This routine returns a _closure_ which, given a sun vector (assumed to be in sc 
             coordinates and normalized) and a roll angle, calculates the angle between the
             spacecraft +y axis and the sun vector.  The return value is in _degrees_.
        """
        c1, c2= cos(self.e1), cos(self.e2)
        s1, s2= sin(self.e1), sin(self.e2)

        c1c2= c1 * c2
        s1c2= s1 * c2

        def _quick_dot(sun_sky, roll_in_degrees):
            e3= _rationalize(radians ( 90.0 - roll_in_degrees))
            c3, s3= cos(e3), sin(e3)

            row2= [ -c1c2 * s3 - s1 * c3,  
                     c1 * c3 - s1c2 * s3,
                     s2 * s3 ]

            dot= sum( [x*y for x,y in zip(row2, sun_sky)] )
            return degrees (acos (dot) )

        return _quick_dot
