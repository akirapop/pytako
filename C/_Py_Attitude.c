#include <Python.h>

#include <atFunctions.h>
#include "attitude_wrappers.h"


/** Remove this in the future **/
    #include <stdio.h>



/**********************************************************************/ 
/*                                                                    */ 
/* Called from python as:                                             */
/*                                                                    */
/* Py_Orbit.py_atAttInit (ntargets)                                   */
/*                                                                    */ 
/**********************************************************************/ 
static PyObject *py_atAttInit (PyObject *self, PyObject *args, PyObject *kwds)
{

    unsigned int nrows_cache;

    if (!PyArg_ParseTuple (args, "I", &nrows_cache))
      return NULL;

    if (-1 == attitude_wrappers_init (nrows_cache)) {
       PyErr_SetString (PyExc_RuntimeError, "Attitude library initialization failed."); 
       return NULL;
     }

    Py_INCREF(Py_None);
    return Py_None;


} 

/**********************************************************************/ 
/*                                                                    */ 
/* Called from python as:                                             */
/*      Py_att.py_addTarget (ra, dec, mjd, targ_number)               */
/*                                                                    */ 
/*    ra & dec must be in __degrees__                                 */ 
/**********************************************************************/ 
static PyObject *py_addTarget (PyObject *self, PyObject *args)
{

    double ra, dec, mjd;
    unsigned int cache_row_number;
    
    int status;
    AtVect xyz;

    if (!PyArg_ParseTuple (args, "dddI", &ra, &dec, &mjd, &cache_row_number))
        return NULL;

    status= targ_init (ra, dec, mjd, cache_row_number);
    if (status != 0) {
        PyErr_Format (PyExc_RuntimeError, "Error initializing new target.");
        return NULL;
     }

    Py_INCREF(Py_None);
    return Py_None;

}


/**********************************************************************/ 
/*                                                                    */ 
/* Called from python as:                                             */
/*  (flag, ele) = Py_att.py_atEarthOccult (mjd, cache_row, targ_num)  */
/*                                                                    */
/**********************************************************************/ 
static PyObject *py_atEarthOccult (PyObject *self, PyObject *args)
{

    unsigned int cache_row, target_cache_row;
    double mjd;

    double ele;
    int flag, status;

    flag=status=0;

    if (!PyArg_ParseTuple (args, "dII", &mjd, &cache_row, &target_cache_row))
        return NULL;

    status= _atEarthOccult (mjd, cache_row, target_cache_row, &flag, &ele);
    if (status != 0) {
        PyErr_Format (PyExc_RuntimeError, "Non-zero return status from _atEarthOccult().");
        return NULL;
     }
    return Py_BuildValue ("(id)", flag, ele);

}


/**********************************************************************/ 
/*                                                                    */ 
/* Called from python as:                                             */
/*  (flag, (ele)) = Py_att.py_atEarthElev (mjd, cache_row, targ_num)  */
/*                                                                    */
/* (ele) is a *tuple* containing the 3 elevation angles:              */
/*   (above earth limb, above bright/day limb, above dark/night limb) */
/*                                                                    */
/**********************************************************************/ 
static PyObject *py_atEarthElev (PyObject *self, PyObject *args)
{

    unsigned int cache_row, target_cache_row;
    double mjd;

    double ele[3];
    int flag, status;

    flag=status=0;

    if (!PyArg_ParseTuple (args, "dII", &mjd, &cache_row, &target_cache_row))
        return NULL;

    status= _atEarthElev (mjd, cache_row, target_cache_row, &flag, ele);
    if (status != 0) {
        PyErr_Format (PyExc_RuntimeError, "Non-zero return status from _atEarthElev().");
        return NULL;
     }
    return Py_BuildValue ("(i(ddd))", flag, ele[0], ele[1], ele[2]);

}


static PyMethodDef mod_methods[]= {
   { "py_atAttInit", (PyCFunction) py_atAttInit, METH_VARARGS, NULL},
   { "py_addTarget", (PyCFunction) py_addTarget, METH_VARARGS, NULL},
   { "py_atEarthOccult", (PyCFunction) py_atEarthOccult, METH_VARARGS, NULL},
   { "py_atEarthElev", (PyCFunction) py_atEarthElev, METH_VARARGS, NULL},
   { NULL, NULL, 0, NULL }
};

static struct PyModuleDef moduledef = {
     PyModuleDef_HEAD_INIT,
     "Py_orbit",
     "Python3 implementation of at-functions orbit code.",
     -1,
     mod_methods,
     NULL,
     NULL,
     NULL,
     NULL,
};

PyMODINIT_FUNC PyInit_Py_att(void)
{

    PyObject *m;

    m= PyModule_Create(&moduledef);
    if (m == NULL)
        return NULL;

    return m;
}
