#include <Python.h>

#include <atFunctions.h>
#include "orbit_wrappers.h"

/**
#include "Py_atMisc.h"
**/


/** Remove this in the future **/
    #include <stdio.h>



/**********************************************************************/ 
/*                                                                    */ 
/* Called from python as:                                             */
/*                                                                    */
/* Py_Orbit.py_atOrbInit (orbfile, mjd, nrows_cache, rigtable=rtable) */
/*                                                                    */ 
/**********************************************************************/ 
static PyObject *py_atOrbInit (PyObject *self, PyObject *args, PyObject *kwds)
{

    double mjd;
    unsigned int nrows_cache;
    char *orbfile, *rigtable;

    char *argnames[]= { "orbfile", "mjd", "nrows_cache", "rigtable", NULL};

    orbfile=rigtable=NULL;

    if (!PyArg_ParseTupleAndKeywords (args, kwds, "sdI|s", argnames, &orbfile, &mjd, 
          &nrows_cache, &rigtable))
      return NULL;

    if (-1 == _orbit_wrappers_init ( (const char *) orbfile, (const char *) rigtable, mjd, nrows_cache)) {
       PyErr_SetString (PyExc_RuntimeError, "Orbit initialization failed."); 
       return NULL;
     }

    Py_INCREF(Py_None);
    return Py_None;


} 

/**********************************************************************/ 
/*                                                                    */ 
/* Called from python as:                                             */
/*      xyz= Py_orbit.py_atSatPos3 (mjd, mjd_cache_row_number)        */
/*                                                                    */ 
/**********************************************************************/ 
static PyObject *py_atSatPos3 (PyObject *self, PyObject *args)
{

    double mjd;
    unsigned int cache_row_number;
    
    int status;
    AtVect xyz;

    if (!PyArg_ParseTuple (args, "dI", &mjd, &cache_row_number))
        return NULL;

    status= _atSatPos3 (mjd, cache_row_number, xyz);
    if (status != 0) {
        PyErr_Format (PyExc_RuntimeError, "Non-zero return status from _atSatPos3().");
        return NULL;
     }
    return Py_BuildValue ("(ddd)", xyz[0], xyz[1], xyz[2]);

}

/**********************************************************************/ 
/*                                                                    */ 
/* Called from python as:                                             */
/*  atgeod = Py_orbit.py_atGeodetic (mjd, cache_row_number)           */
/*                                                                    */
/*  atgeod is a tuple given the xyz values in geodetic coordinates.   */
/*                                                                    */ 
/**********************************************************************/ 
static PyObject *py_atGeodetic (PyObject *self, PyObject *args)
{

    AtVect xyz_geodetic;
    unsigned int cache_row;
    double mjd;

    int status;

    if (!PyArg_ParseTuple (args, "dI", &mjd, &cache_row))
        return NULL;

    status= _atGeodetic (mjd, cache_row, xyz_geodetic);
    if (status != 0) {
        PyErr_Format (PyExc_RuntimeError, "Non-zero return status from atGeodetic().");
        return NULL;
     }
    return Py_BuildValue ("(ddd)", xyz_geodetic[0], xyz_geodetic[1], xyz_geodetic[2]);

}

/**********************************************************************/ 
/*                                                                    */ 
/* Called from python as:                                             */
/*  atgeod = Py_orbit.py_pvGeodetic (mjd, cache_row_number)           */
/*                                                                    */
/*  o at_geog is a python dictionary with the following keys/values:  */ 
/*                                                                    */ 
/*     key           python value                                     */     
/*     ---           ------------                                     */
/*    HEIGHT      altitude (in km!) above the earth's surface         */ 
/*    LONGITUDE   longitude (in degrees) of the satellite             */ 
/*    LATITUDE    latitude (in degrees) of the satellite              */ 
/*                                                                    */ 
/**********************************************************************/ 
static PyObject *py_pvGeodetic (PyObject *self, PyObject *args)
{

    unsigned int cache_row;
    double mjd;

    AtPolarVect pvGeod;
    int status;

    if (!PyArg_ParseTuple (args, "dI", &mjd, &cache_row))
        return NULL;

    status= _pvGeodetic (mjd, cache_row, &pvGeod);
    if (status != 0) {
        PyErr_Format (PyExc_RuntimeError, "Non-zero return status from _pvGeodetic().");
        return NULL;
     }

    return Py_BuildValue ("{s:f,s:f,s:f}", "HEIGHT", pvGeod.r, "LONGITUDE", pvGeod.lon, 
        "LATITUDE", pvGeod.lat);

}

/**********************************************************************/ 
/*                                                                    */ 
/* Called from python as:                                             */
/*  xyz_geog = Py_orbit.py_atGeodcr (mjd, cache_row)                  */
/*                                                                    */ 
/*  o xyz_geog is a python dictionary with the following keys/values: */ 
/*                                                                    */ 
/*     key           python value                                     */     
/*     ---           ------------                                     */
/*    HEIGHT      altitude (in km!) above the earth's surface         */ 
/*    LONGITUDE   longitude (in degrees) of the satellite             */ 
/*    LATITUDE    latitude (in degrees) of the satellite              */ 
/*                                                                    */ 
/**********************************************************************/ 
static PyObject *py_atGeodcr (PyObject *self, PyObject *args)
{

    unsigned int cache_row;
    double mjd;

    double hgt, longitude, latitude;
    int status;

    if (!PyArg_ParseTuple (args, "dI", &mjd, &cache_row))
        return NULL;

    status= _atGeodcr (mjd, cache_row, &hgt, &longitude, &latitude);
    if (status != 0) {
        PyErr_Format (PyExc_RuntimeError, "Non-zero return status from _atGeodcr().");
        return NULL;
     }
    return Py_BuildValue ("{s:f,s:f,s:f}", "HEIGHT", hgt, "LONGITUDE", longitude, 
        "LATITUDE", latitude);

}

/**********************************************************************/ 
/*                                                                    */ 
/* Called from python as:                                             */
/*     saa = Py_orbit.py_atSaa (mjd, cache_row_number)                */
/*                                                                    */
/**********************************************************************/ 
static PyObject *py_atSaa (PyObject *self, PyObject *args)
{

    unsigned int cache_row;
    double mjd;

    int status, flag;

    flag=0;

    if (!PyArg_ParseTuple (args, "dI", &mjd, &cache_row))
        return NULL;

    status= _atSaa (mjd, cache_row, &flag);
    if (status != 0) {
        PyErr_Format (PyExc_RuntimeError, "Non-zero return status from _atSaa().");
        return NULL;
     }

    if (flag)
       Py_RETURN_TRUE;
    else
       Py_RETURN_FALSE;

}


/**********************************************************************/ 
/*                                                                    */ 
/* Called from python as:                                             */
/*   rigidity = Py_orbit.py_atRigidity (mjd, cache_row_number)        */
/*                                                                    */
/**********************************************************************/ 
static PyObject *py_atRigidity (PyObject *self, PyObject *args)
{

    unsigned int cache_row;
    double mjd;
    float rigidity;

    int status;

    status=0;

    if (!PyArg_ParseTuple (args, "dI", &mjd, &cache_row))
        return NULL;

    status= _atRigidity (mjd, cache_row, &rigidity);
    if (status != 0) {
        PyErr_Format (PyExc_RuntimeError, "Non-zero return status from _atRigidity().");
        return NULL;
     }

    return Py_BuildValue ("d", rigidity);

}

static PyMethodDef mod_methods[]= {
   { "py_atOrbInit", (PyCFunction) py_atOrbInit, METH_VARARGS, NULL},
   { "py_atSatPos3", (PyCFunction) py_atSatPos3, METH_VARARGS, NULL},
   { "py_atGeodetic", (PyCFunction) py_atGeodetic, METH_VARARGS, NULL},
   { "py_pvGeodetic", (PyCFunction) py_pvGeodetic, METH_VARARGS, NULL},
   { "py_atGeodcr", (PyCFunction) py_atGeodcr, METH_VARARGS, NULL},
   { "py_atSaa", (PyCFunction) py_atSaa, METH_VARARGS, NULL},
   { "py_atRigidity", (PyCFunction) py_atRigidity, METH_VARARGS, NULL},
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

PyMODINIT_FUNC PyInit_Py_orbit(void)
{

    PyObject *m;

    m= PyModule_Create(&moduledef);
    if (m == NULL)
        return NULL;

    return m;
}
