#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cache.h"

#define MAX_CACHES   5

static void ***full_cache[MAX_CACHES];   /* The full cache consists of MAX_CACHES individual caches */
static unsigned int nrows[MAX_CACHES];   /* nrows & ncols give the dimensions for each cache        */
static unsigned int ncols[MAX_CACHES];

static unsigned short next_cache=-1;
static unsigned short __full_cache_initialized__ = 0;

/**************************************************************************/
/*    This library is a relatively simple cache implementation. The cache */
/* stores the data as void * data-types which are passed in by the user.  */
/*                                                                        */
/*            !!! All data (pointers to void) ought                       */
/*            !!! to have been allocated on the heap!                     */
/*                                                                        */
/**************************************************************************/

static void _cache_manager_init(void)
{

    unsigned short k;

    if (__full_cache_initialized__ == 1)
        return;

    for (k=0; k<MAX_CACHES; k++)
        full_cache[k]=NULL;

    __full_cache_initialized__ = 1;

    return;

}

static int _full_cache_bounds_check (unsigned short cache_slot)
{
    if (cache_slot >= MAX_CACHES) {
        fprintf (stderr, "\n\tRequest to access non-existent cache.\n");
        fprintf (stderr, "\trequested cache: %d, Number of caches: %d\n\n", cache_slot, MAX_CACHES);
        return -1;
     }
    return 0;
}

static int _bounds_check (unsigned short cache_slot, unsigned int row, unsigned int col)
{

    unsigned int _cache_nrows, _cache_ncols;

    if (_full_cache_bounds_check (cache_slot) == -1)
        return -1;
     
    _cache_nrows= nrows[cache_slot]; 
    _cache_ncols= ncols[cache_slot];

    if ( (row >= _cache_nrows)  ||  (col >= _cache_ncols) ){
        fprintf (stderr, "\n\trow/col outside cache bounds!\n");
        fprintf (stderr, "\trow=%d/col=%d, cache dimensions: %d / %d\n\n", row, col,
                 _cache_nrows, _cache_ncols);
        return -1;
     }
    return 0;

}

int cache_init (unsigned int _nrows, unsigned int _ncols)
{

    void ***_cache;
    size_t size_per_row= _ncols * sizeof (void *);
    unsigned int k;

    if (__full_cache_initialized__ == 0)
        _cache_manager_init();
        
    if ( (_nrows == 0)  ||  (_ncols == 0) ){
        fprintf (stderr, "\n\nZero-sized cache requested: nrows=%d, ncols=%d\n\n", _nrows, _ncols);
        return -1;
     }

    next_cache++;
    if (next_cache == MAX_CACHES) {
        fprintf (stderr, "\n\tMaximum allowable caches reached!\n\n");
        return -1;
     }

    _cache= allocate ( _nrows * sizeof (void **));
    if (_cache == NULL)
      return -1;

    for (k=0; k<_nrows;k++)
     {
         _cache[k]= allocate (size_per_row);

         if (_cache[k] == NULL)
             return -1;
     }

    full_cache[next_cache]=_cache;
    nrows[next_cache]=_nrows;
    ncols[next_cache]=_ncols;

    return next_cache;

}

static int cache_removeline (unsigned short cache_slot, unsigned int row)
{

    unsigned int k;
    void ***_cache;
    unsigned int _cache_ncols;

    /*******************************************************************************/
    /**    The second argument here -- 0 -- is a 'dummy' value. The _bounds_check **/
    /** requires a row number and a column number, but we're only interested in   **/
    /** checking the row number.                                                  **/
    /*******************************************************************************/
    if (-1 == _bounds_check (cache_slot, row, 0)) {
        fprintf (stderr, "\n\tRequest to remove cache line ignored.\n\n");
        return -1;
     }

    _cache= full_cache[cache_slot];
    _cache_ncols= ncols[cache_slot];

    for (k=0; k < _cache_ncols; k++) {
        if (_cache[row][k] != NULL)
            free (_cache[row][k]);        /** This is controversial: Should we warn the **/ 
                                          /** user and abort, or just free it up???     **/ 
     }   
    free (_cache[row]),  _cache[row]=NULL;

    return 0;

}

int cache_destroy (unsigned short cache_slot)
{

    unsigned int k, _cache_nrows;

    if (-1 == _full_cache_bounds_check (cache_slot))
        return -1;

    _cache_nrows= nrows[cache_slot];

    for (k=0; k<_cache_nrows; k++)
        cache_removeline (cache_slot, k);

    free (full_cache[cache_slot]),  full_cache[cache_slot]=NULL;

    return 0;

}


int cache_full_cache_destroy(void)
{

    unsigned short k;

    for (k=0; k< next_cache; k++)
        cache_destroy(k);

    return 0;

}

int cache_put (unsigned short cache_slot, unsigned int row, unsigned int col, void *val)
{

    void ***_cache;

    if (_full_cache_bounds_check (cache_slot) == -1)
        return -1;

    if ( -1 == _bounds_check(cache_slot, row, col))
        return -1;

    _cache=full_cache[cache_slot];
    if (_cache == NULL) {
        fprintf (stderr, "\n\tAttempt to put to uninitialized cache.\n\n");
        return -1;
     }

    if (_cache[row] == NULL) {
        fprintf (stderr, "\n\tAttempt to put to uninitialized line in cache. (row=%d)\n\n", row);
        return -1;
     }
    _cache[row][col]= val;

    return 0;

}
 

void *cache_retrieve (unsigned short cache_slot, unsigned int row, unsigned int col, int *status)
{

    void ***_cache;
    void *_val;

    if (status == NULL) {
        fprintf (stderr, "\n\t%s: Null pointer for status variable!\n\n", "cache_retrieve()");
        return NULL;
     }

    *status=-1;

    if (_full_cache_bounds_check (cache_slot) == -1)
        return NULL;

    if ( -1 == _bounds_check(cache_slot, row, col))
        return NULL;

    _cache=full_cache[cache_slot];
    if (_cache == NULL) {
        fprintf (stderr, "\n\tAttempt to retrieve from uninitialized cache.\n\n");
        return NULL;
     }

    if (status == NULL) {
        fprintf (stderr, "\n\tNULL *status pointer passed to cache_retrieve().\n\n");
        return NULL;
     }

    if ( -1 == _bounds_check (cache_slot, row, col))
        return NULL;

    _val= _cache[row][col], *status=0;

    return _val;

}
