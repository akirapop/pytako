#ifndef _SOLAR_SYSTEM_WRAPPERS_H_
#define _SOLAR_SYSTEM_WRAPPERS_H_

#include <atFunctions.h>
#include <atError.h>

/****************************************************************************************/
/*   The sun/moon/planet_comp factors determine how often the sun/moon/position vectors */
/* are calculated in comparison with the satellite postion/time line grid. (It might be */
/* considered unnecessary to calculate the sun's position every minute, say.) The       */
/* factors are given as multiples of the timeline grid: If the sun's position should be */
/* calculated every 30 minutes, compared to 1-minute bins for the satellite position,   */
/* sun_comp=30.                                                                         */
/*                                                                                      */       
/* Usage notes:                                                                         */       
/*                                                                                      */       
/* _atSun:  The user may need to calculate the sun's position at a given mjd without    */       
/*          necessarily needing to cache the value. Passing cache_row=-1 to the         */       
/*          _atSun() routine will allow for this.                                       */       
/*                                                                                      */       
/*                                                                                      */       
/****************************************************************************************/

int _solar_system_wrappers_init(unsigned int sun_comp, unsigned int moon_comp, unsigned int planet_comp, unsigned int nrows_cache);

int _atMoon(double mjd, unsigned int cache_row, AtVect moonPos);
int _atSun(double mjd, int cache_row, AtVect sunPos);
int _atVectToRaDec (AtVect x, double *ra, double *dec);         /** Values returned _in radians_ **/
int sun_ra_dec (double mjd, unsigned int cache_row, double *ra, double *dec);
int moon_ra_dec (double mjd, unsigned int cache_row, double *ra, double *dec);


#endif
