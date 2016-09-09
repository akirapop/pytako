from math import fmod

def phase(period, ephemeris, phase_min, phase_max):

    if phase_max < phase_min:
        phase_ranges=[ (0, phase_max), (phase_min,1.0)]
    else:
        phase_ranges=[ (phase_min, phase_max) ]

    def _phase(mjd, *args):
        ph= fmod( mjd - ephemeris, period) / period

        if ph < 0.0: ph += 1.0

        for _plo,_phi in phase_ranges:
            if _plo  <=  ph <= _phi:
                return True
        return False
    return _phase         

def window(inclusion_windows):
    """ inclusion_windows is a list/tuple of two-element lists/tuples giving windows    
        defining the good times: ( (start, stop)[, (start, stop), (start,stop)...]).    
        As ought to be clear -- at least *one* window must be specified! Further,       
        for the case of only a single window, be careful: a tuple of *tuples* (or a     
        list or lists) is expected:  wndow_func= window( (start, stop),)             
    """
    def _window(mjd, *args):
        for wbegin,wend in inclusion_windows:
            if wbegin <= mjd <= wend:
                return True
        return False
    return _window

def consolidate_constraints(constraint_list):
    """ Given a list of Constraint types/instances, consolidates the constraints into one constraint function """
    if len(constraint_list) == 0:
        return None

    def _bin_is_bad_time(mjd):
        for c in constraint_list:
           if c.is_bad_time(mjd):
               return True
        return False
    return _bin_is_bad_time


class Constraint:
    def __init__(self, name, constraint_type, constraint_func, **kwargs):
        """ constraint_type: "bad"-time or "good"-time """

        constraint_type = constraint_type.lower()

        if constraint_type not in "bad"  and  constraint_type not in "good":
             raise ValueError("\tUnknown constraint type: '%s'. Only 'good' and 'bad' recognized." % constraint_type)

        self.cstr_type=constraint_type
        self.cstr_func=constraint_func
        self.name=name

        self.__dict__.update(kwargs)

        if self.cstr_type == "good":
            def _bad_time(mjd, *args):
                return not self.cstr_func(mjd, *args)
            self.is_bad_time= _bad_time
        else:
            self.is_bad_time= self.cstr_func

    def show_bad(self, mjdStart, nbins, binsize):
        good_or_bad= [ self.is_bad_time(k*binsize + mjdStart) for k in range(nbins)] 

        return good_or_bad



##########################################################################################################
if __name__ == "__main__":


    import os, sys

    jd2mjd= lambda jd: jd - 2400000.5

    wuma_phase= phase(0.3336, jd2mjd(2452500.179), 0.2, 0.5)

    wuma= Constraint("wuma-phase", "good", wuma_phase)


    nbins=24
    bsize=1.0 / 24
    mjdStart=53000.0

    phase_info= wuma.show_bad(mjdStart, nbins, bsize)

    for k,bad in enumerate(phase_info):
        t=k*bsize + mjdStart

        if bad:
            print ("Time %f is *outside* phase 0.2-0.5." % t) 
        else:
            print ("Time %f is GOOD!" % t)


