#!/home/baluta/bin/python3

import tkinter as tk

from Target import Target
from Py_Tako import Scheduler
from list_boxes import ScrolledListbox
from dateTools_py3 import mjdToDateString


def read_targets(tfile):
    """ Lines in the file are assumed to have: 'name  ra  dec  exp <anything or nothing else>' """

    tlist=[]
    tobs=[]
    max_len=0

    def _mk_targ_obj(line):
        dat=line.split()
        nm=dat[0]
        ra, dec, exp= [float(x) for x in dat[1:4]]

        return Target(ra, dec, exp, name=nm)

    f=open(tfile)
    for line in f.readlines():
        tlist.append(line.rstrip('\n'))
        tobs.append(_mk_targ_obj(line))
 
        if len(line) > max_len:  max_len = len(line)
    
    return tlist, max_len, tobs

def mk_copy_cmd(lbox_from_widget, lbox_to_widget, scheduler, tgt_obj_list, already_scheduled_list):
    from_=lbox_from_widget
    to_=lbox_to_widget

    tlist=tgt_obj_list
    mjdStart= scheduler.mjdStart
    already_done=already_scheduled_list

    def _outline(s):
        _args=s.split()
        name = _args[0]

#       ra, dec, exp= [float(x) for x in _args[1:4]]
        return name

    def _sched(*args):
        #val=from_.get_selection()

        index, val=from_.get_index_and_selection()

        if index in already_done:
            return
        else:
            already_done.append(index)

        targ=tlist[int(index)]

        nm=_outline(val)

        ## Schedule!
        targ.set_sun_constraint(mjdStart)
        targ.consolidate_constraints()

        targ_num=scheduler.register_target(targ.ra, targ.dec, scheduler.mjdStart)
        cons_func=targ.calc_constraint

#       mjdEnd, nbins= scheduler.schedule_target(mjdStart, targ.exp, targ_num, cons_func)
        mjd_Start, mjdEnd, nbins= scheduler.schedule_target(targ.exp, targ_num, cons_func)

        eff = 100.0 * targ.exp / (  (mjdEnd - mjd_Start) * 86.4 )

        dateStart= mjdToDateString(mjd_Start)
        dateEnd= mjdToDateString(mjdEnd)

#       to_.add_item("%s : %.6f  (%d bins)" % (nm, mjdEnd, nbins))
#       to_.add_item("%s : Obs. ends %s  (%d bins)" % (nm, dateEnd, nbins))
        to_.add_item("%s : %s -- %s (%.1f ks   %.1f %%)" % (nm, dateStart, dateEnd, nbins * 60 / 1000, eff))

    return _sched

def get_scheduler():

    orbit_file='ae2_orbit.dat'
    mjdStart=57113.018

    binsize= 1.0 / 1440.
    nbins=1440*10
    ntargets=32

    return Scheduler (orbit_file, mjdStart, nbins, binsize, ntargets)

def mk_saver(sched_box):

    def _save(*args):
        full_sched=sched_box.get_all()
        if len(full_sched) == 0:
            return

        _out= open("out_sched.save", "w")
        _out.write(full_sched)
        _out.close()
    return _save

if __name__ == "__main__":

    import os, sys

    args=sys.argv
    if len(args) < 2:
        print ("\n\t%s target_file\n" % os.path.basename(args[0]))
        sys.exit(1)
    tfile=args[1]

    tlist, max_len, tgt_obs=read_targets(tfile)    

    scheduler= get_scheduler()

    root= tk.Tk()

    main= tk.Frame(root)
    main.pack(side=tk.TOP)

    lbox=ScrolledListbox(tlist, main) 
    rbox=ScrolledListbox(master=main) 

    copy_cmd= mk_copy_cmd(lbox, rbox, scheduler, tgt_obs,[])

    lbox.configure(width=max_len)
    rbox.configure(width=max_len*2)

    lbox.make_binding(copy_cmd)

    savebutt=tk.Button(main, text="Save", command=mk_saver(rbox))
    savebutt.pack(side=tk.TOP)
    quit=tk.Button(main, text="Quit", command=root.quit)
    quit.pack(side=tk.TOP)

    root.title("Test Scheduler")
    root.mainloop()

