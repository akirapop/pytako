#ifndef _MISC_AT_UTILITIES_H_
#define _MISC_AT_UTILITIES_H_

#include <atFunctions.h>

int copy_to_atvect (double *_from, AtVect _to);
void *copy_from_atvect (AtVect av);

void *copy_from_polarvect (AtPolarVect pv);
int copy_to_polarvect (double *_from, AtPolarVect _to);

#endif
