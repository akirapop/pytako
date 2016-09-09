#ifndef _ATTITUDE_WRAPPERS_H_
#define _ATTITUDE_WRAPPERS_H_

#include <atFunctions.h>
#include <atError.h>

#include <stdio.h>

typedef struct {
    double ra, dec, roll;

    double mjd;        /** The mjd is 'linked' to the roll angle **/
/*
    double phi, theta, psi;
*/
/*  AtRotMat skyToSc; */   /** This is the matrix calculated from (phi, theta, psi) **/
/*  AtRotMat scToSky; */

    AtVect targVec;

} Target_Type;


int attitude_wrappers_init(unsigned int nrows_cache);

/** The right-ascension and declination must be in __degrees__. **/
int targ_init (double ra, double dec, double mjd, unsigned int cache_row);

/** Given an ra, dec (in __degrees__!), calculates an AtVect **/
int raDec_to_atVect (double ra, double dec, AtVect av);  /** ra & dec must be in __degrees__ **/

/**************************************************************************************************/
/**    Though the  _atEarthOccult & _atEarthElev routines have the same signature, they _do not_ **/
/** take the _exact_ same parameters! The final argument, a pointer to double in both cases,     **/
/** point to regions of different size: For the _atEarthOccult routine, this pointer should be   **/
/** to _one_ double type. For the _atEarthElev routine, this pointer should point to _three_     **/
/** double's. In the former, only a single elevation angle is returned. In the latter, three are **/
/** returned.                                                                                    **/
/**                                                                                              **/
/** The flag parameter has the followingmeanings:                                                **/
/**                                                                                              **/
/**  Flag        Meaning                                                                         **/    
/**   0       not occulted                                                                       **/
/**   1       occulted by __dark earth__                                                         **/
/**   2       occulted by __bright earth__                                                       **/
/**                                                                                              **/
/**************************************************************************************************/
int _atEarthOccult (double mjd, unsigned int cache_row, unsigned int target_cache_row, int *flag, double *elevation);
int _atEarthElev  (double mjd, unsigned int cache_row, unsigned int target_cache_row, int *flag, double *elevation);

int optimal_roll (unsigned int cache_row, double ra, double dec, double mjd);

#endif
