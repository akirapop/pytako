#include <stdio.h>

#include <atError.h>
#include "orbit_wrappers.h"
#include "misc_at_utilities.h"
#include "cache.h"
#include "memory.h"

static const char *orbit_init_name    =  "_orbit_wrappers_init()";
static const char *atSatPos3_name     =  "_atSatPos3()";
static const char *atGeodetic_name    =  "_atGeodetic()";
static const char *pvGeodetic_name    =  "_pvGeodetic()";
static const char *atGeodcr_name      =  "_atGeodcr()";
static const char *atRigidity_name    =  "_atRigidity()";
static const char *atSaa_name         =  "_atSaa()";

static AtElement3 *_els=NULL;


/**** Cache setup information ****/
static short cache_slot=-1;       /** This will be assigned when we init/create the cache **/

static const short ncols_cache=2;
static const unsigned int    Cache_atSatpos3_col  =0;
static const unsigned int    Cache_pvGeodetic_col =1;   /** Polar vector version of atGeodetic vector **/

/**
static const unsigned int    Cache_atGeodcr_col   =2;
**/
 
/**** End, cache setup information ****/

int _orbit_wrappers_init(const char *orbfile, const char *rigfile, double mjd, unsigned int nrows_cache)
{

    int status=0;

    /*** _els is a *global* (see above) ***/
    if (_els != NULL) {
        fprintf (stderr, "\n\t%s: ** Orbit library has already been initialized!\n\n", orbit_init_name);
        return -1;
     }
    _els= allocate (sizeof (AtElement3));
    if (_els == NULL)
        return -1;

    if (NORMAL_END != atSetElement3 (_els, (char *) orbfile, mjd, 0)) {
        free ( _els );
        return -1;
     }

    /** Prepare for (possible) rigidity calculations **/
    if (rigfile != NULL) {
        status= atRigSet( (char *) rigfile);

        if (status != 0) {
            fprintf (stderr, "\n\t%s: Error in atRigSet. Error status: %d\n\n", orbit_init_name, status);
            return -1;
         }
     }

    /** Now set up the cache for this library **/
    if (cache_slot != -1) {
        fprintf (stderr, "\n\t%s: Cache has already been initialized for orbit code!\n", orbit_init_name);
        return -1;
     }
    cache_slot= cache_init (nrows_cache, ncols_cache);

    return status;

}

/** The calculated value is returned via the satPos variable **/
int _atSatPos3 (double mjd, unsigned int cache_row, AtVect satPos)
{

    int status=0;
    void *cache_value;

    if (_els == NULL) {
        fprintf (stderr, "\n\t%s: Orbit uninitialized! (Has _orbit_wrappers_init() been called?!)\n\n", atSatPos3_name);
        return -1;
     }

    cache_value= cache_retrieve(cache_slot, cache_row, Cache_atSatpos3_col, &status);
    if (cache_value == NULL) {       /** The value has not been cached. Calculate it, cache it **/

        if (status == -1)  /** There was an error within cache_retrieve(). **/
            return -1;

        if (NORMAL_END != atSatPos3 (_els, mjd,  satPos)) { 
            fprintf (stderr, "\n\t%s: Error in atSatPos3()\n\n", atSatPos3_name);
            return -1;
         }
        if (NULL == (cache_value =copy_from_atvect (satPos)))
            return -1;

        cache_put (cache_slot, cache_row, Cache_atSatpos3_col, cache_value);
     } else {    /** if (cache_value == NULL)  clause **/
        if (-1 == copy_to_atvect (cache_value, satPos))
            return -1;
     }

    return 0;

}

/** The calculated value is returned via the atGeod variable **/
int _atGeodetic (double mjd, unsigned int cache_row, AtVect atGeod)
{

    int status=0;
    AtVect satPos;

    if (-1 == _atSatPos3 (mjd,  cache_row, satPos)) 
        return -1;

    if (NORMAL_END != (status=atGeodetic (mjd,  satPos, atGeod))) { 
        fprintf (stderr, "\n\t%s: Error in atGeodetic(). Error status: %d\n\n", atGeodetic_name, status);
        return -1;
     }
    return 0;

}

/** Calculate the satellite pos. in geodetic coords. as a polar vector **/
int _pvGeodetic (double mjd, unsigned int cache_row, AtPolarVect *pvSatGeod)
{

    int status=0;
    void *cache_value;

    cache_value= cache_retrieve (cache_slot, cache_row, Cache_pvGeodetic_col, &status);
    if (cache_value == NULL) {
        AtVect _satGeod;

        if (status == -1)  /** There was an error within cache_retrieve(). **/
            return -1;

        if (-1 == (status=_atGeodetic (mjd,  cache_row, _satGeod))) { 
            fprintf (stderr, "\n\t%s: Error in atGeodetic(). Error status: %d\n\n", pvGeodetic_name, status);
            return -1;
         }
        atVectToPol (_satGeod, pvSatGeod);
        cache_value= copy_from_polarvect (*pvSatGeod);

        cache_put (cache_slot, cache_row, Cache_pvGeodetic_col, cache_value);
      } else {
        copy_to_polarvect (cache_value, *pvSatGeod);
      }

    return 0;

}

/** The calculated value for the rigidity is returned via the (input) pointer *rigidity **/
int _atRigidity (double mjd, unsigned int cache_row, float *rigidity)
{

    int status=0;
    AtPolarVect pv;

    if (rigidity == NULL) {
        fprintf (stderr, "%s: Null pointer passed to function!\n\n", atRigidity_name);
        return -1;
     }

    if (-1 == _pvGeodetic (mjd, cache_row, &pv))
        return -1;

    status= atRigidity (&pv, rigidity);
    if (status != NORMAL_END) {
        fprintf (stderr, "\n\t%s: Error in atRigidity(). Error status:%d\n\n", atRigidity_name, status);
        return -1;
     }

    return 0;

}

/** The calculated saa flag is returned via the (input) pointer *saa_flag **/
int _atSaa (double mjd, unsigned int cache_row, int *saa_flag)
{

    int status=0;
    AtPolarVect pv;

    if (saa_flag == NULL) {
        fprintf (stderr, "%s: Null pointer passed to function!\n\n", atSaa_name);
        return -1;
     }

    if (-1 == _pvGeodetic (mjd, cache_row, &pv))
        return -1;

    status= atBrazil (pv.lon, pv.lat, saa_flag);
    if (status != NORMAL_END) {
        fprintf (stderr, "\n\t%s: Error in atBrazil(). Error status:%d\n\n", atSaa_name, status);
        return -1;
     }
    return 0;

}


/** The calculated values are returned via the three (double *) values **/
int _atGeodcr (double mjd, unsigned int cache_row, double *hgt, double *lgtude, double *lat)
{

    int status=0;
    AtVect satPos;

    if ( hgt == NULL ||  lgtude == NULL  ||  lat == NULL) {
        fprintf (stderr, "\n\t%s : Null pointer(s) in argument list!\n\n", atGeodcr_name);
        return -1;
     }

    if (-1 == _atSatPos3 (mjd,  cache_row, satPos)) 
       return -1;

    status=atGeodcr (mjd,  satPos, hgt, lgtude, lat);
    if (status != NORMAL_END) { 
       fprintf (stderr, "\n\t%s: Error in atGeodecr(). Error status: %d\n\n", atGeodcr_name, status);
       return -1;
     }
    return 0;

}
