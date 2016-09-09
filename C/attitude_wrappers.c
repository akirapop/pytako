#include "attitude_wrappers.h"
#include "orbit_wrappers.h"
#include "solar_system_wrappers.h"
#include "cache.h"
#include "memory.h"

static const char *raDec_to_atVect_name= "raDec_to_atVect_name()";
static const char *atEarthOccult_name  = "_atEarthOccult()";
static const char *atEarthElev_name    = "_atEarthElev()";
static const char *att_init_name       = "attitude_wrappers_init()";
static const char *targ_init_name      = "targ_init()";

/**** Cache setup information ****/
static short cache_slot=-1;       /** This will be assigned when we init/create the cache **/

static const short ncols_cache=1;
static const unsigned int    Cache_targets_col    =0;

/**** End, cache setup information ****/

int attitude_wrappers_init(unsigned int nrows_cache)
{

    /** Now set up the cache for this library **/
    if (cache_slot != -1) {
        fprintf (stderr, "\n\t%s: Cache has already been initialized for the attitude code!\n", att_init_name);
        return -1;
     }
    cache_slot= cache_init (nrows_cache, ncols_cache);

    return 0;

}

static int _ra_dec_degrees_toAtPolarVect60 (double ra, double dec, AtPolarVect60 *_pv)
{

    if (_pv == NULL) {
        fprintf (stderr, "\n\tNull pointer passed to _ra_dec_degrees_toAtPolarVect60 ()\n");
        return -1;
     }

    atDegToRA (ra, &(_pv->ra)); 
    atDegToDec (dec, &(_pv->dec)); 

    return 0;

}

/** The atFunctions atPol60ToVect() routine has a bug: AtPolarVect pv.r is _not_ set! **/
static int _atPol60ToVect (AtPolarVect60 *pv60, AtVect x)
{

    AtPolarVect pv;
    int status=0;

    pv.lon= atRAToRadian (pv60->ra);
    pv.lat= atDecToRadian (pv60->dec);
    pv.r=1.0;             /** This is not done in the at-func. atPol60ToVect() routine **/

    status = atPolToVect (&pv, x);
    if (status != 0) {
        fprintf (stderr, "\n\tNon-zero error status from atPolToVect()\n");
        return -1;
     }
 
    return 0;
 
}

/** ra & dec must be in __degrees__ **/
int raDec_to_atVect (double ra, double dec, AtVect tvec)
{

    AtPolarVect60 pv;

    if (-1 == _ra_dec_degrees_toAtPolarVect60( ra, dec, &pv)) {
        fprintf (stderr, "\n\t%s: Error converting ra/dec\n", raDec_to_atVect_name);
        return -1;
     }
    if (NORMAL_END != _atPol60ToVect (&pv, tvec)) {
        fprintf (stderr, "\n\t%s: Error in atPol60ToVect()\n", raDec_to_atVect_name); 
        return -1;
     }
    return 0;    

}

int _atEarthOccult (double mjd, unsigned int cache_row, unsigned int target_cache_row, int *flag, double *ele)
{

    AtVect vSun;
    AtVect satPos;
    Target_Type *t;

    int status=0;

    if ( (flag==NULL)  ||  (ele==NULL) ){
        fprintf (stderr, "\n\t%s: Null pointer(s) passed\n", atEarthOccult_name);
        return -1;
     }

    if (-1 == _atSatPos3 (mjd, cache_row, satPos)) {
        fprintf (stderr, "\n\t%s: Error calculating satellite position.\n", atEarthOccult_name);
        return -1;
     }
    if (-1 == _atSun(mjd, cache_row, vSun)) {
        fprintf (stderr, "\n\t%s: Error calculating solar position.\n", atEarthOccult_name);
        return -1;
     }
  
    t= cache_retrieve (cache_slot, target_cache_row, Cache_targets_col, &status); 
    if ( (status != 0)  ||  (t==NULL) ) {
        fprintf (stderr, "\n\t%s: Error retrieving information for target #%d.\n", atEarthOccult_name, target_cache_row);
        return -1;
     }
    
    if (0 != atEarthOccult (satPos, t->targVec, vSun, flag, ele)) {
        fprintf (stderr, "\n\t%s: Error in atEarthOccult().\n", atEarthOccult_name);
        return -1;
     }
 
    return 0;

}

int _atEarthElev (double mjd, unsigned int cache_row, unsigned int target_cache_row, int *flag, double *ele)
{

    AtVect vSun;
    AtVect satPos;
    Target_Type *t;

    double _ele[3];
    int status=0;

    if ( (flag==NULL)  ||  (ele==NULL) ){
        fprintf (stderr, "\n\t%s: Null pointer(s) passed\n", atEarthElev_name);
        return -1;
     }

    if (-1 == _atSatPos3 (mjd, cache_row, satPos)) {
        fprintf (stderr, "\n\t%s: Error calculating satellite position.\n", atEarthElev_name);
        return -1;
     }
    if (-1 == _atSun(mjd, cache_row, vSun)) {
        fprintf (stderr, "\n\t%s: Error calculating solar position.\n", atEarthElev_name);
        return -1;
     }
  
    t= cache_retrieve (cache_slot, target_cache_row, Cache_targets_col, &status); 
    if ( (status != 0)  ||  (t==NULL) ) {
        fprintf (stderr, "\n\t%s: Error retrieving information for target #%d.\n", atEarthElev_name, target_cache_row);
        return -1;
     }
    
    if (0 != atEarthElev (satPos, t->targVec, vSun, flag, _ele)) {
        fprintf (stderr, "\n\t%s: Error in atEarthElev().\n", atEarthElev_name);
        return -1;
     }
    ele[0]=_ele[0]; ele[1]=_ele[1]; ele[2]=_ele[2];
 
    return 0;

}

/** ra & dec are assumed to be in __degrees__ **/
int targ_init (double ra, double dec, double mjd, unsigned int cache_row)
{

    Target_Type *_targ;
    int status=0;
    void *p;

    p=cache_retrieve (cache_slot, cache_row, Cache_targets_col, &status);
    if (status != 0) {
        fprintf (stderr, "\n\t%s: Cache error.\n", targ_init_name);
        return -1;
     }
    if (p != NULL) {
        fprintf (stderr, "\n\t%s: Cache slot already taken! (Bad target number?)\n", targ_init_name);
        return -1;
     }

    _targ= allocate (sizeof (Target_Type));
    if (_targ == NULL)
        return -1;

    _targ->ra=ra;  _targ->dec=dec;  _targ->roll=0.0;   /** For now, roll is a 'stub' **/ 
    _targ->mjd=mjd;

    if (-1 == raDec_to_atVect (ra, dec, _targ->targVec))
        return -1; 

    if (-1 == cache_put (cache_slot, cache_row, Cache_targets_col, (void *) _targ)) {
        fprintf (stderr, "\n\t%s: Caching error.\n", targ_init_name);
        free ( (void *) _targ);
        return -1;
     }

    return 0;

}


/*********************************************************************/
/** Implements the roll angle calculation outlined in:              **/
/**                                                                 **/
/**  http://archive.stsci.edu/iue/newsletters/Vol09/ORIENT.pdf      **/
/**  http://archive.stsci.edu/iue/instrument/obs_guide/node18.html  **/
/**                                                                 **/
/**  ra & dec must be in __degrees__                                **/
/*********************************************************************/
/**
int optimal_roll (double ra, double dec, double mjd);
{



}
**/
