#include <stdio.h>
#include <string.h>

#include "memory.h"

void *allocate (size_t size)
{

    void *p;

    if (size <= 0) {
        fprintf (stderr, "\n\t%s: Non-sensical allocation requested: %d bytes\n\n", "allocate()", size);
        return NULL;
     }
    p= malloc (size);

    if (p == NULL) {
        fprintf (stderr, "\n\t%s: Malloc error! (%d bytes requested)\n\n", "allocate()", size);
        return NULL;
     }

    memset (p, 0, size);
    return p;

}

void *reallocate (void *p, size_t size)
{

    void *newp;

    if (size <= 0) {
        fprintf (stderr, "\n\t%s: Non-sensical allocation requested: %d bytes\n\n", "reallocate()", size);
        return NULL;
     }

    if (p == NULL) {
        fprintf (stderr, "\n\t%s: Attempt to reallocate space on a null pointer.\n\n", "reallocate()");
        return NULL;
     }

    newp= realloc (p, size);
    if (newp == NULL) {
        fprintf (stderr, "\n\t%s: Malloc error! (Reallocation to %d bytes requested)\n\n", "reallocate()", size);
        return NULL;
     }
    return newp;

}
