#ifndef _ORBIT_WRAPPERS_H_
#define _ORBIT_WRAPPERS_H_

#include <atFunctions.h>

int _orbit_wrappers_init(const char *orbfile, const char *rigfile, double mjd, unsigned int nrows_cache);
int _atSatPos3 (double mjd, unsigned int cache_row, AtVect satPos);
int _atGeodetic (double mjd, unsigned int cache_row, AtVect returnValue);
int _pvGeodetic (double mjd, unsigned int cache_row, AtPolarVect *returnValue);  /** Geodetic vec. as polar vec. **/
int _atGeodcr (double mjd, unsigned int cache_row, double *hgt, double *lgtude, double *lat);

int _atRigidity (double mjd, unsigned int cache_row, float *returned_rigidity);
int _atSaa (double mjd, unsigned int cache_row, int *returned_saa_flag);

#endif
