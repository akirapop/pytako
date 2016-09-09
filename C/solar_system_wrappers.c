#include <stdio.h>

#include "solar_system_wrappers.h"
#include "misc_at_utilities.h"
#include "cache.h"
#include "memory.h"


static const char *ss_init_name       =  "_solar_system_wrappers_init()";
static const char *atSun_name         =  "_atSun()";
static const char *atMoon_name        =  "_atMoon()";
static const char *atVectToRaDec_name =  "_atVectToRaDec()";
static const char *sun_ra_dec_name    =  "sun_ra_dec()";
static const char *moon_ra_dec_name   =  "moon_ra_dec()";


/**** Cache setup information ****/
static short cache_slot=-1;       /** This will be assigned when we init/create the cache **/

static const short ncols_cache=2;
static const unsigned int    Cache_atSun_col      =0;
static const unsigned int    Cache_atMoon_col     =1;

/**********************************************************************************/
/**   The compression factors here define the grid on which the sun/moon/planets **/
/** will be calculated: (Do we need to calculate the sun (ra, dec) on one minute **/
/** intervals? for example.) If the positions are required to be calculated on   **/
/** the same grid, these factors are 1. Otherwise, they are set (in the init     **/
/** routine) accordingly.                                                        **/
/**********************************************************************************/
static unsigned int sun_compression   =1;
static unsigned int moon_compression  =1;
static unsigned int planet_compression=1;

/**** End, cache setup information ****/

int _solar_system_wrappers_init(unsigned int sun_comp, unsigned int moon_comp, unsigned int planet_comp, unsigned int nrows_cache)
{

    int status=0;

    sun_compression   =sun_comp;
    moon_compression  =moon_comp;
    planet_compression=planet_comp;
     
    /** Now set up the cache for this library **/
    if (cache_slot != -1) {
        fprintf (stderr, "\n\t%s: Cache has already been initialized for solar system code!\n", ss_init_name);
        return -1;
     }
    cache_slot= cache_init (nrows_cache, ncols_cache);

    return status;

}

int _atMoon(double mjd, unsigned int cache_row, AtVect moonPos)
{

    int status=0;
    void *cache_value;
    double size, phase, distance;  /** None of these are used -- but they are need by atMoon() **/


    cache_row /= moon_compression;

    cache_value= cache_retrieve(cache_slot, cache_row, Cache_atMoon_col, &status);
    if (cache_value == NULL) {       /** The value has not been cached. Calculate it, cache it **/

        if (status == -1)  /** There was an error within cache_retrieve(). **/
            return -1;

        if (NORMAL_END != atMoon (mjd,  moonPos, &size, &phase, &distance)) {
            fprintf (stderr, "\n\t%s: Error in atMoon()\n\n", atMoon_name);
            return -1;
         }
        if (NULL == (cache_value = copy_from_atvect (moonPos)))
            return -1;

        cache_put (cache_slot, cache_row, Cache_atMoon_col, cache_value);
     } else {    /** if (cache_value == NULL)  clause **/
        if (-1 == copy_to_atvect (cache_value, moonPos))
            return -1;
     }

    return 0;


}


/** Note that this routines *normalizes* the calculated vector. **/
static int _atSun_withCache(double mjd, unsigned int cache_row, AtVect sunPos)
{

    int status=0;
    void *cache_value;
    AtVect _sunPos;  /** Un-normalized **/

    cache_row /= sun_compression;

    cache_value= cache_retrieve(cache_slot, cache_row, Cache_atSun_col, &status);
    if (cache_value == NULL) {       /** The value has not been cached. Calculate it, cache it **/

        if (status == -1)  /** There was an error within cache_retrieve(). **/
            return -1;

        if (NORMAL_END != atSun (mjd,  _sunPos)) {
            fprintf (stderr, "\n\t%s: Error in atSun()\n\n", atSun_name);
            return -1;
         }
        if (NORMAL_END != atNormVect (_sunPos, sunPos)) {
            fprintf (stderr, "\n\t%s: Error in atNormVect()\n\n", atSun_name);
            return -1;
         }

        if (NULL == (cache_value =copy_from_atvect (sunPos)))
            return -1;

        cache_put (cache_slot, cache_row, Cache_atSun_col, cache_value);
     } else {    /** if (cache_value == NULL)  clause **/
        if (-1 == copy_to_atvect (cache_value, sunPos))
            return -1;
     }

    return 0;

}

int _atSun(double mjd, int cache_row, AtVect sunPos)
{

    /*****************************************************************************/
    /** Allow for the user to bypass the cache. This may be desirable for cases **/
    /** where the sun's position needs to be known for only a given mjd. (In    **/
    /** roll angle calculations, for example.                                   **/
    /*****************************************************************************/
    if (cache_row == -1) {
       if (-1 == atSun (mjd,  sunPos)) {
           fprintf (stderr, "\n\t%s: Error in atSun()\n\n", atSun_name);
           return -1;
        }
       return 0;
     }

    /** There is an implied 'else' here: 'else (cache_row != -1)' **/
    return _atSun_withCache(mjd, (unsigned) cache_row, sunPos);

}

/** Makes use of the atVectToPol60 routine to calculate ra, dec for a given AtVect **/
int _atVectToRaDec (AtVect pos, double *ra, double *dec)
{

    AtPolarVect60 pv;
    AtPolarVect pv_radians;

    if ( (ra == NULL)  ||  (dec == NULL)) {
        fprintf (stderr, "\n\t%s: Null ra/dec pointer!\n", atVectToRaDec_name);
        return -1;
     }

    if (NORMAL_END != atVectToPol60 (pos, &pv)) {
        fprintf (stderr, "\n\t%s: Error in  atVectToPol60()\n\n", atVectToRaDec_name);
        return -1;
     }
    if (NORMAL_END != atConvPol (&pv, &pv_radians)) {
        fprintf (stderr, "\n\t%s: Error in  atConvPol()\n\n", atVectToRaDec_name);
        return -1;
     }
    *ra =pv_radians.lon;
    *dec=pv_radians.lat;

    return 0;

}

int sun_ra_dec (double mjd, unsigned int cache_row, double *ra, double *dec)
{

    AtVect sunPos;

    if ( (ra == NULL) ||  (dec==NULL)) {
         fprintf (stderr, "\n\t%s: Null pointer(s) passed into routine.\n", sun_ra_dec_name);
         return -1;
     }

    if (-1 == _atSun (mjd, cache_row, sunPos))
       return -1;

    if (-1 == _atVectToRaDec (sunPos, ra, dec))
       return -1;

    return 0;

}

int moon_ra_dec (double mjd, unsigned int cache_row, double *ra, double *dec)
{

    AtVect moonPos;

    if ( (ra == NULL) ||  (dec==NULL)) {
         fprintf (stderr, "\n\t%s: Null pointer(s) passed into routine.\n", moon_ra_dec_name);
         return -1;
     }

    if (-1 == _atMoon (mjd, cache_row, moonPos))
       return -1;

    if (-1 == _atVectToRaDec (moonPos, ra, dec))
       return -1;

    return 0;

}
