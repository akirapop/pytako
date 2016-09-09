#ifndef _CACHE_H_
#define _CACHE_H_

#include "memory.h"

/**************************************************************************/
/** Using the cache                                                      **/
/**                                                                      **/
/**    The cache manager (cache.c) handles all interactions with caches. **/
/** The user requests a cache via cache_init(). This routine will return **/
/** a 'cache slot', which identifies the particular cache initialized    **/
/** for the user.                                                        **/
/**                                                                      **/
/**    Each cache stores data as pointers to void -- cache.c stores no   **/
/** information about the content of the data stored. It is therefore    **/
/** the responsibility of the user to: (1) appropriately de-reference    **/
/** the void * data returned from the cache via cache_retrieve(); and    **/
/** (2) pass a _pointer_ (allocated on the heap!!!) to any data that     **/ 
/** is to be cached.                                                     **/
/**                                                                      **/
/** Once the cache is no longer needed, cache_destroy() ought to be      **/
/** called.                                                              **/
/**                                                                      **/
/**************************************************************************/

int cache_init (unsigned int _nrows, unsigned int _ncols);
int cache_destroy(unsigned short cache_slot);
int cache_full_cache_destroy(void);
int cache_put (unsigned short cache_slot, unsigned int row, unsigned int col, void *val);
void *cache_retrieve (unsigned short cache_slot, unsigned int row, unsigned int col, int *status);

#endif
