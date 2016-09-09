#include <stdio.h>
#include <stdlib.h>

#include "memory.h"
#include "misc_at_utilities.h"

void *copy_from_atvect (AtVect av)
{

    unsigned int k;
    double *x= allocate (3 * sizeof (double));

    if (x == NULL) 
        return NULL;
 
    for (k=0; k<3; k++)
        x[k]=av[k];
    
    return (void *) x; 

}

int copy_to_atvect (double *_from, AtVect _to)
{

    if (_from == NULL) {
        fprintf (stderr, "\n\tNull pointer passed to copy_to_atvect()\n\n");
        return -1;
     }

    _to[0]= _from[0]; _to[1]= _from[1]; _to[2]= _from[2];

    return 0;

}

void *copy_from_polarvect (AtPolarVect pv)
{

    double *x= allocate (3 * sizeof (double));

    if (x == NULL) 
        return NULL;

    x[0]=pv.r;
    x[1]=pv.lon;
    x[2]=pv.lat;
 
    return (void *) x;

}

int copy_to_polarvect (double *_from, AtPolarVect _to)
{

    if (_from == NULL) {
        fprintf (stderr, "\n\tNull pointer passed to copy_to_atvect()\n\n");
        return -1;
     }

    _to.r= _from[0]; _to.lon= _from[1]; _to.lat= _from[2];

    return 0;

}
