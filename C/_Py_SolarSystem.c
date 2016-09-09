#include <Python.h>

#include <atFunctions.h>
#include "solar_system_wrappers.h"


/** Remove this in the future **/
    #include <stdio.h>


/**********************************************************************/ 
/*                                                                    */ 
/* Called from python as:                                             */
/*                                                                    */
/* Py_Orbit.py_atAttInit (sun_compression, moon_compression,          */
/*    planets_compression, nrows_cache)                               */ 
/*                                                                    */ 
/* The _compression factors determine how often to calculate the      */ 
/* given position, in comparison to the number of bins on the         */ 
/* timeline.                                                          */ 
/*                                                                    */ 
/**********************************************************************/ 
static PyObject *py_atSSInit (PyObject *self, PyObject *args, PyObject *kwds)
{

    unsigned int sun_comp, moon_comp, planet_comp;
    unsigned int nrows_cache;

    if (!PyArg_ParseTuple (args, "IIII", &sun_comp, &moon_comp, &planet_comp, &nrows_cache))
      return NULL;

    if (-1 == _solar_system_wrappers_init (sun_comp, moon_comp, planet_comp, nrows_cache)) {
       PyErr_SetString (PyExc_RuntimeError, "Solar system library initialization failed."); 
       return NULL;
     }

    Py_INCREF(Py_None);
    return Py_None;


} 

/**********************************************************************/ 
/*                                                                    */ 
/* Called from python as:                                             */
/*  (ra, dec)= Py_ss.py_sun_ra_dec (mjd, cache_row)                   */
/*                                                                    */
/**********************************************************************/ 
static PyObject *py_sun_ra_dec (PyObject *self, PyObject *args)
{

    unsigned int cache_row;
    double mjd;

    double ra, dec;
    int status;

    status=0;

    if (!PyArg_ParseTuple (args, "dI", &mjd, &cache_row))
        return NULL;

    status= sun_ra_dec (mjd, cache_row, &ra, &dec);
    if (status != 0) {
        PyErr_Format (PyExc_RuntimeError, "Non-zero return status from sun_ra_dec().");
        return NULL;
     }
    return Py_BuildValue ("(dd)", ra, dec);

}


/**********************************************************************/ 
/*                                                                    */ 
/* Called from python as:                                             */
/*  (ra, dec)= Py_ss.py_moon_ra_dec (mjd, cache_row)                  */
/*                                                                    */
/**********************************************************************/ 
static PyObject *py_moon_ra_dec (PyObject *self, PyObject *args)
{

    unsigned int cache_row;
    double mjd;

    double ra, dec;
    int status;

    status=0;

    if (!PyArg_ParseTuple (args, "dI", &mjd, &cache_row))
        return NULL;

    status= moon_ra_dec (mjd, cache_row, &ra, &dec);
    if (status != 0) {
        PyErr_Format (PyExc_RuntimeError, "Non-zero return status from moon_ra_dec().");
        return NULL;
     }
    return Py_BuildValue ("(dd)", ra, dec);

}
