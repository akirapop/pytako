import Py_sched as psched

from os.path import isfile
from itertools import groupby
from math import degrees, floor, ceil

def file_does_not_exist(fname):
    return not isfile(fname) 

"""


"""

######################################################################################## 
class TargetLimitReached(Exception): pass
class IntervalLimitExceeded(Exception): pass
class IntervalTooSmallForTarget(Exception): pass
class BadBinNumber(Exception): pass

class Timeline:
    def __init__(self, nbins):
        """ This class in intended to act as a 'book-keeping' class, maintaining a list of available time intervals.
            The intervals are represented as simple tuples giving the start & end bins of the available interval. 
            Once an interval has been 'used', the interval must be updated to reflect the number of bins that were
            'used' (scheduled) for that given interval!

            Note that this class contains *no* information linking a given bin to its corresponding mjd! It is the
            responsibility of the Scheduler class instance to make this connection.

        """

        self.open_intervals=[ (0, nbins) ]
        self.current_interval_in_use=0

    def next_interval(self):
        index=self.current_interval_in_use 
        return self.open_intervals[index]

    def update_interval(self, new_start_bin):
        index=self.current_interval_in_use 
       
        interval=self.open_intervals[index]
        end_bin= interval[1] 

        if new_start_bin > end_bin:
             raise IntervalLimitExceeded("\n\t** Target scheduled has exceeded allotted time interval!\n")
        elif new_start_bin == end_bin: 
             del(self.open_intervals[index])
#            self.current_interval_in_use += 1
        else:
             self.open_intervals[index]= (new_start_bin, end_bin)

    def unordered_access(self, start_bin_needed):
        sb=start_bin_needed

        for k,oi in enumerate(self.open_intervals):
            if oi[0] <=  sb  <= oi[1]:
                self.current_interval_in_use=k
                return oi
        return None


class Scheduler:
    ksec_per_day= 86.4

    def __init__(self, orbit_file, mjdStart, nbins, bin_size, ntargets):
        """ mjdStart & nbins are needed to initialize the orbit code and cache """

        if file_does_not_exist(orbit_file):
            raise RuntimeError("\n\tOrbit file ('%s') could not be found." % orbit_file)
 
        try:
            psched.py_atOrbInit (orbit_file, mjdStart, nbins)
            psched.py_atSSInit(1, 1, 1, nbins)
            psched.py_atAttInit(ntargets)
        except Exception as e:
            mess="\n\tScheduler initialization failed. Exception: '%s'\n" % e
            raise RuntimeError(mess)

        self.mjdStart=mjdStart
        self.nbins=nbins
        self.bin_size=bin_size

        self.ntargets_allocated=ntargets
        self.current_target_pointer=-1

        self.timeline= Timeline (nbins)
        self.current_mjd=mjdStart

        #######################################################################################
        ## The saa cache is a simple list - each (time) bin is True (sat. in saa) or False.  ##
        ## For occultations, the cache is a two-dimensional list -- each registered target   ##
        ## has a list (cache) of occultation values. These lists are the same as for saa:    ##
        ## True (target is occulted) or False (not occulted).                                ##
        #######################################################################################
        self.cache= { "saa":[None] * nbins, "occult":[None]*ntargets }

    def ksec(self, bins):
        """ For a given number of bins, calculates the number of kiloseconds """
        return bins * self.bin_size * Scheduler.ksec_per_day

    def register_target (self, ra_degrees, dec_degrees, mjd):
        """ Register a given target (ra, dec): This is needed as the target will be cached inside the C code! """

        self.current_target_pointer += 1 
        if self.current_target_pointer >= self.ntargets_allocated:
             raise TargetLimitReached("Number of targets requested exceeds original request!")

        psched.py_addTarget (ra_degrees, dec_degrees, mjd, self.current_target_pointer)

        return self.current_target_pointer

    def bin_to_mjd(self, bin):
        if bin < 0  or  bin > self.nbins:
            raise BadBinNumber("\n\tBin number outside range given in Scheduler init.: %d <-> %d" % (bin, self.nbins))

        return self.mjdStart + self.bin_size * bin

#   def schedule_target(self, from_mjd, exp_in_ks, targ_num, time_constrained=None):
    def schedule_target(self, exp_in_ks, targ_num, time_constrained=None):
        """ 
                This routine is used when *sequentially* scheduling a target/targets. In other words, schedule
            one target, then another -- immediately after the previous target. 

            * Scheduling begins at the beginning of the timeline given when initializing the Scheduler class * 

            A note about the parameters: time_constrained, if given, is a constraint _function_ that, given an 
            mjd, returns True (mjd is 'bad' time) or False 
        """

        if targ_num > self.current_target_pointer:
            raise RuntimeError("\tGiven target number (%d) > the number of targets registered!\n" % targ_num)

        exp_in_bins=  (exp_in_ks / Scheduler.ksec_per_day)  /  self.bin_size

        nbins_needed= ceil(exp_in_bins)

        ## Schedule the target within the next available interval! FUTURE: we need to 
        ## add logic here to allow the user to split the target over multiple intervals.
        open_int= self.timeline.next_interval()

        if open_int[1]-open_int[0] < exp_in_bins:
             raise IntervalTooSmallForTarget("** Cannot schedule target within the given interval!")

        next_k= self._next_bin(open_int[0], open_int[1])

        total_bins=0
#       mjd_end=self.bin_to_mjd(open_int[0])
        mjd_end=self.current_mjd

        if time_constrained is None:
            time_constrained= lambda mjd: False

        while nbins_needed > 0:

             try:
                 k, mjd = next(next_k)
             except StopIteration:
                 break

             total_bins += 1
             mjd_end= mjd

             if time_constrained(mjd):
                 continue
 
             if self._in_saa(mjd, k):
                 continue

             if self._targ_occulted(mjd, k, targ_num):
                 continue

             nbins_needed -= 1

        if nbins_needed > 0:
            print ("\tTarget could not be fit into the timeline! %d bins (%.1f ks) left over." % (nbins_needed,
                     self.ksec(nbins_needed)))

        self.timeline.update_interval(open_int[0] + total_bins - 1)

        _mjdStart=self.current_mjd
        self.current_mjd=mjd_end

#       return mjd_end, total_bins
        return _mjdStart, mjd_end, total_bins

    def _next_bin(self, start_bin, end_bin):
        mjd0=self.mjdStart
        bsize=self.bin_size

        current_bin=start_bin
        mjd = mjd0 + bsize * current_bin
        while current_bin <= end_bin:
            yield current_bin, mjd
            current_bin += 1
            mjd += bsize
 
    def schedule_targetFirst(self, from_mjd, exp_in_ks, targ_num, time_constrained=None):
        """ time_constrained - if given - is a constraint _function_ that, given an mjd, returns True (mjd is 'bad' time) or False """

        if targ_num > self.current_target_pointer:
            raise RuntimeError("\tGiven target number (%d) > the number of targets registered!\n" % targ_num)

        exp_in_bins=  (exp_in_ks / Scheduler.ksec_per_day)  /  self.bin_size

        nbins_needed= ceil(exp_in_bins)
        next_k= self._next_binFirst(from_mjd)

        total_bins=0
        mjd_end=from_mjd

        if time_constrained is None:
            time_constrained= lambda mjd: False

        while nbins_needed > 0:

             try:
                 k, mjd = next(next_k)
             except StopIteration:
                 break

             total_bins += 1
             mjd_end= mjd

             if time_constrained(mjd):
                 continue
 
             if self._in_saa(mjd, k):
                 continue

             if self._targ_occulted(mjd, k, targ_num):
                 continue

             nbins_needed -= 1

        if nbins_needed > 0:
            print ("\tTarget could not be fit into the timeline! %d bins (%.1f ks) left over." % (nbins_needed,
                     self.ksec(nbins_needed)))

        return mjd_end, total_bins

    def _next_binFirst(self, from_mjd, start_bin=None):
        mjd0=self.mjdStart
        bsize=self.bin_size

        ## We make an assumption here: If the user gives a start_bin,
        ## we _assume_ it corresponds to the bin for from_mjd!
        if start_bin is None:
            _from_mjd_bin= floor( (from_mjd - mjd0) / bsize)
            start_bin=_from_mjd_bin

        current_bin=start_bin
        mjd= from_mjd
        max_bins= self.nbins

        while current_bin < max_bins:
            yield current_bin, mjd
            current_bin += 1
            mjd += bsize
 
    def _targ_occulted(self, mjd, k, targ_num, Brightlimit=20.0, Darklimit=5.0):
  
        _cache=self.cache["occult"]
 
        if _cache[targ_num] is None:
            _cache[targ_num]= [None] * self.nbins

        _occult= _cache[targ_num]

        if _occult[k] is not None:
            return _occult[k]

        flag, eles= psched.py_atEarthElev (mjd, k, targ_num)
        eles = [degrees(x) for x in eles]

        val=None    
        if flag == 0:
#           return False 
            val=False 
    
        if eles[0] < Darklimit  or   eles[1] < Brightlimit:
#           return True
            val=True 
        else:
#           return False
            val=False 
        _occult[k]=val

        return val
 

    def _in_saa(self, mjd, k):

        _saa= self.cache["saa"][k]
        if _saa is not None:
            return _saa

        if psched.py_atSaa(mjd, k) > 0:
            _saa=True
        else:
            _saa=False
        self.cache["saa"][k]=_saa

        return _saa

