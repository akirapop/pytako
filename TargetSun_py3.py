
import itertools

from math import radians, degrees, sin, cos, tan, acos

from CoordinateTransforms_py3 import EulerMatrix, alpha_delta_to_skyvector
from solarSystem_py3 import Ephemeris

"""     This module concerns various target/sun angle-related things. The
    principle services it offers are below. With the exception of the
    sso_ra_dec routine, all other services are accessed via the TargetView
    class:

    target_view= TargetView(ra_degrees, dec_degrees[, sun_limit_in_degrees])


    target_roll_info: Given an mjd, returns the nominal roll angle and the roll limits
                      for the date/mjd. The nominal roll angle is the "best" roll
                      angle, determined by minimizing the angle between the sc+y
                      axis and a vector in the direction of the sun.

           best_roll: Given an mjd, returns the "best" roll angle. Then angle is
                      determined by minimizing the angle between the sc+y axis
                      and a vector in the direction of the sun.

       target_window: Given an mjd, finds the next available observation window. A 
                      tuple giving the mjd start/end for the window is returned.

     targ_sun_vs_mjd: Given a starting mjd and the number of days to calculate, returns a 
                      list of (mjd, targ_sun_angle) values. If verbose=True is passed, 
                      (mjd, t_s_angle, sun_ra, sun_dec) is returned. An optional value
                      for the time resolution (delta_t_days) may be specified. The default
                      is 1.0: the target-sun angle is calculated for one-day intervals.

          sso_ra_dec: Given the name of a solar system object and an mjd, returns the 
                      (approximate) ra, dec in degrees along with the distance from
                      earth (a.u.). For the case of the moon, the distance is given in 
                      units of earth radii. The routine used is an implementation of the
                      method outlined in Van Flandern & Pulkkinen, Ap. J. Supp., 41:391 (1979)

  find_date_for_roll: Given a roll angle request (in degrees) and an mjd, finds the nearest
                      mjd where the requested roll angle is valid.

"""


def _mjd_to_jd(mjd):
    return mjd + 2400000.5

def sso_ra_dec(obj_name, mjd):
    ephem= Ephemeris(obj_name)

    jd= _mjd_to_jd(mjd)
    ra, dec, re= ephem.raDecRearth (jd)

    return (ra, dec)

def _spherical_triangle_solver(target_alpha_degrees, target_delta_degrees, verbose=False):
    """ This routine calculates a _closure_ for a given target ra, dec (in degrees). The """
    """ closure returns the angle in DEGREES between the sun and target for a given mjd. """

    sun_ephem= Ephemeris("sun")

    tra, tdec= radians(target_alpha_degrees), radians(target_delta_degrees)
    cos_tdec, sin_tdec= cos(tdec), sin(tdec)

    def sun_ra_dec(mjd):
        _ra, _dec, _ = sun_ephem.raDecRearth (_mjd_to_jd (mjd))
        return radians(_ra), radians(_dec)

    def _solve_triangle(mjd):
        sra, sdec= sun_ra_dec(mjd)

        deltaRa= tra-sra
        x= cos(deltaRa)*cos(sdec)*cos_tdec  +  sin(sdec)*sin_tdec

        if verbose:
            return mjd, degrees(acos(x)), sra, sdec
        else:
            return degrees(acos(x))
    return _solve_triangle 
        
class TargetView:

    one_minute= 1.0 / 1440       ## one minute, as a fraction of a day

    def __init__(self, ra_degrees, dec_degrees, sun_limit=25.0):
        self.ra, self.dec= radians(ra_degrees), radians(dec_degrees)

        self.ra_deg=ra_degrees
        self.dec_deg=dec_degrees

        self.sun_limit=sun_limit
        self.target_sun_angle_calc= _spherical_triangle_solver(ra_degrees, dec_degrees)

    def _nominal_roll(self, sun_alpha, sun_delta):
        """ Given an mjd, computes the 'best' (nominal) roll angle. Note that """
        """ no check is made to see whether or not the target is observable!  """

        alpha= self.ra
        delta= self.dec

        sun_alpha = radians(sun_alpha)
        sun_delta = radians(sun_delta)

        delta_alpha= sin (alpha - sun_alpha)

        beta= acos(  -sin(delta)*sin(sun_delta) -
                     cos(delta)*cos(sun_delta)*cos(alpha-sun_alpha ) )

        gamma= acos( -tan(delta)/tan(beta)  -sin(sun_delta) / (sin(beta)*cos(delta)) )

        gamma= degrees(gamma)

        if delta_alpha < 0.0:
            sign= -1.0
        else:
            sign= 1.0

        roll= 180.0 + sign*gamma

        return roll

    def _find_roll_limits(self, roll0, dot, sun_in_sky, step_size_in_degrees=1.0):

        sun_limit= self.sun_limit

        initial_sun_angle= dot(sun_in_sky, roll0)
        if initial_sun_angle > sun_limit:
            print("\n\t*** Target is outside of sun angle limits! Sun angle: %.1f, Sun limit: %.1f\n" % (initial_sun_angle, sun_limit))
            return None

        step_size=step_size_in_degrees

        sun_angle=initial_sun_angle
        roll=roll0
        while sun_angle < sun_limit:
             roll= roll - step_size
             sun_angle= dot(sun_in_sky, roll)        

        roll_min=roll

        sun_angle=initial_sun_angle
        roll=roll0

        while sun_angle < sun_limit:
             roll= roll + step_size
             sun_angle= dot(sun_in_sky, roll)        
        roll_max=roll

        return (roll_min, roll_max)

    def targ_sun_vs_mjd(self, mjd_start, ndays, step_size_days=1.0, verbose=False):
        """ Given an mjd and number of days, returns mjd vs. target/sun angle at an interval given by step_size_days """
        delta_t= step_size_days

        angle_info=[]

        ra_degrees= self.ra_deg
        dec_degrees= self.dec_deg

        targ_sun_solver= _spherical_triangle_solver(ra_degrees, dec_degrees, verbose)

        mjd=mjd_start
        for _ in range(ndays):
            retval=targ_sun_solver(mjd)

            if verbose:
                angle_info.append(retval)
            else:
                angle_info.append( (mjd,retval))
            mjd += delta_t

        return angle_info

    def _find_window_open(self, mjd_start, sun_targ_angle_code, critical_angle, step_size_days):

        step_size=step_size_days

        ## Hacky clutter. (This is what happens when you don't think quite long enough ahead of time!)
        ## We could get stuck in an infinite recursion (below) as we try to zero-in on the mjd when the
        ## window closes. If the step_size is below one minute ... we're done!
        if step_size <= TargetView.one_minute:
            return mjd_start

        mjd=mjd_start
        angle= sun_targ_angle_code(mjd)
        dphi= abs(90.0 - angle)

        if dphi <= critical_angle:
            return mjd

        while dphi > critical_angle:

            mjd += step_size
            angle=sun_targ_angle_code(mjd)

            dphi= abs(90.0 - angle)
            if dphi <= critical_angle:
                return self._find_window_open(mjd - step_size, sun_targ_angle_code, critical_angle, step_size/100.0)

    def _find_window_close(self, mjd_start, sun_targ_angle_code, critical_angle, step_size_days):

        step_size=step_size_days

        ## Hacky clutter. (This is what happens when you don't think quite long enough ahead of time!)
        ## We could get stuck in an infinite recursion (below) as we try to zero-in on the mjd when the
        ## window closes. If the step_size is below one minute ... we're done!
        if step_size <= TargetView.one_minute:
            return mjd_start

        mjd=mjd_start
        angle= sun_targ_angle_code(mjd)
        dphi= abs(90.0 - angle)
         
        if dphi >= critical_angle:
            return mjd

        while dphi < critical_angle:

            mjd += step_size

            if mjd-mjd_start >= 365.:
                return mjd

            angle=sun_targ_angle_code(mjd)
            dphi= abs(90.0 - angle)

            ## The reason for the recursion: We've (very likely) gone past the actual mjd for the
            ## time that the window closed: Backtrack by one step size, and calculate again, using
            ## a much smaller time interval.
            if dphi >= critical_angle:
                return self._find_window_close(mjd - step_size, sun_targ_angle_code, critical_angle, step_size/100.0)

    def _target_window(self, sun_targ_angle_code, mjd, step_size_in_days=1.0):

        step_size=step_size_in_days

        sun_limit=self.sun_limit

        mjd_window_open  = self._find_window_open(mjd, sun_targ_angle_code, sun_limit, step_size)
        mjd_window_close = self._find_window_close (mjd_window_open, sun_targ_angle_code, sun_limit, step_size)

        return mjd_window_open, mjd_window_close

    def target_window(self, mjd_start, step_size_in_days=1.0):

        sun_limit=self.sun_limit

        ra_degrees= self.ra_deg
        dec_degrees= self.dec_deg

        sun_targ_separation_routine= self.target_sun_angle_calc
#       sun_targ_separation_routine= _spherical_triangle_solver(ra_degrees, dec_degrees)
        next_window= self._target_window (sun_targ_separation_routine, mjd_start, step_size_in_days)

        return next_window
   
    def target_roll_info (self, mjd):
        """ Returns the nominal roll + (roll min, roll max) for the given mjd. """

        sun_angle_limit=self.sun_limit

        target_alpha=self.ra_deg
        target_delta=self.dec_deg

        sun_alpha, sun_delta=  sso_ra_dec("sun", mjd)

        nominal_roll= self._nominal_roll(sun_alpha, sun_delta) 

        roll0=nominal_roll

        sun_in_sky= alpha_delta_to_skyvector(sun_alpha, sun_delta)

        ## Euler angles (in degrees) are expected by the EulerMatrix constructor.
        matrix= EulerMatrix( target_alpha, 90.0 - target_delta, 90.0 - roll0 )

        dot= matrix.fast_sun_sc_y_dot()

        sun_at_roll0= dot(sun_in_sky, roll0)
        roll_limits= self._find_roll_limits(roll0, dot, sun_in_sky)

        if roll_limits is None:
            return None, None

        return nominal_roll, roll_limits 

    def best_roll (self, mjd):
        """ Given a sun angle limit, a target ra, target dec, and an mjd, returns the
            "best" roll angle for the mjd.) The input angles are assumed to be in _DEGREES_. 
        """

        sun_angle_limit=self.sun_limit
        target_alpha=self.ra_deg
        target_delta=self.dec_deg

        best_roll, _ = self.target_roll_info (mjd)

        return best_roll

    def find_date_for_roll(self, roll_request_in_degrees, from_mjd):
        """ Given a requested roll angle and an mjd, finds the mjd for when the roll is possible (if it's possible!) """
        step_size=1.0   ## Try a step size of 1.0 days

        req_roll = roll_request_in_degrees

        obs_windows=[]

        first_window=self.target_window(from_mjd)

        obs_windows.append(first_window)
        if first_window[1]-first_window[0] < 365.:
            obs_windows.append(self.target_window(first_window[1] + 20.))   ## + 20 days (arbitrary choice)

        for wnum, obs_window in enumerate(obs_windows):
            if obs_window[0] < from_mjd < obs_window[1]:
                mjd=from_mjd
            else:
                mjd=obs_window[0] + .01    ## "It's time to go home" hack -- sometimes the window routine
                                           ## has a time for which the target/sun angle = sum_limit + epsilon.
                                           ## This results in the target_roll_info routine leaving with an
                                           ## error message: "target outside observing window!"

            def target_observable(mjd):
                ang= self.target_sun_angle_calc (mjd)
                return abs(90.0 - ang) < self.sun_limit

            while True:
                roll, roll_limits= self.target_roll_info(mjd)

                if roll_limits is None:
                    if wnum==1:
                        print ("*** Roll angle not available for target.")
                        return None
                    else:
                        break

                if roll_limits[0] <= req_roll <= roll_limits[1]:
                    if target_observable(mjd):
                        return mjd
                    else:
                        if wnum == 1:
                            print ("*** Target not observable on date for requested roll angle!")
                            return None

                if mjd-from_mjd > 365.0:
                    return None

                mjd += step_size

####################################################################################################################
if __name__ == "__main__":

    import os, sys

    args=sys.argv

    if len(args) < 4:
        print("\n\t%s mjd targ_alpha targ_delta [sunlimit]\n\n" % os.path.basename(args[0]))
        sys.exit(1)
    mjd, targ_alpha, targ_delta= [float(x) for x in args[1:4]]

    if len(args) == 5:
        slimit=float(args[4])
    else:
        slimit=25.0


    tv=TargetView(targ_alpha, targ_delta, sun_limit=slimit)

    window=tv.target_window(mjd)

    print ("\n\tFor a sunlimit of %.1f degrees, target visible from %f ... %f" % (slimit, window[0], window[1]))

    best_roll, roll_limits= tv.target_roll_info(mjd)

    if roll_limits is None:
        print ("\n\t** Target is not observable on the given date!")
        sys.exit(2)
    else:
        print ("\tBest roll: %.1f,  roll range: (%.1f -- %.1f)   sunlimit=%.1f" % (best_roll, roll_limits[0], roll_limits[1], slimit))


    





