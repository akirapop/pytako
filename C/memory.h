#ifndef _MEMORY_H_
#define _MEMORY_H_

#include <stdlib.h>

void *allocate (size_t size);
void *reallocate (void *p, size_t size);

#endif

