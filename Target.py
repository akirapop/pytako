from TargetSun_py3 import TargetView
import Constraint

"""
    The Target class encapsulates two separate groups of target-related information:

    (1) things explicitly related to the target -- ra, dec and exposure time
    (2) things related to the timeline of the target -- observing constraints

    The class itself is "passive": the target information encapsulated in an
instance are passed on to the scheduler. 

    Usage note: any constraints the target has must be registered via the register_constraint
method. Once all constraints have been registered, they ought to be 'consolidated' via the
consolidate_constraints method. This method 'chains' the constraints together.

"""

class Target:
     def __init__(self, ra_degrees, dec_degrees, exp_in_ks, name=None, **kwargs):
         self.ra=ra_degrees
         self.dec=dec_degrees
         self.exp=exp_in_ks

         if name is not None: self.tname=name

         self.constraints=[]
         self.calc_constraint=None       ## This will be a function of all constraints 'chained together'
         self.target_window=None

         self.__dict__.update(kwargs)

     def set_sun_constraint(self, mjd):
         """ Find the nearest target window for the target """
         self.tv=TargetView(self.ra, self.dec)
         self.targ_window= self.tv.target_window(mjd, step_size_in_days=0.1)

         sun_constraint= Constraint.Constraint("sun_constraint", "good", Constraint.window((self.targ_window,)))
         if len(self.constraints) > 0:
             self.constraints= [sun_constraint] +  self.constraints 
         else:
             self.constraints.append(sun_constraint)

     def target_within_window(self, mjd):
         """ Check to see whether (True) or not (False) the target is within its observable window on mjd """
         if self.target_window is None:
             self.set_sun_constraint(mjd)
         winopen, winclose= self.target_window

         return winopen <= mjd <= winclose

     def consolidate_constraints(self):
         """ Take the list of constraints registered for the target and combine them into a single _function_ """
         self.calc_constraint= Constraint.consolidate_constraints(self.constraints)

     def register_constraint(self, the_constraint):
         """ the_constraint is expected to be a Constraint instance! """
         self.constraints.append(the_constraint)

