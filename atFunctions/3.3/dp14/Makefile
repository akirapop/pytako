#
# Makefile for atFunctions / dp14
#	13 Aug 1996	Y.Ishisaki

CFLAGS=	-O -I. -I$(INC)

INC = ../include
LIB = ../src/libatFunctions.a
OBJ = dp14.o
ALL = dp14

dp14: $(OBJ)
	$(CC) -o $@ $(OBJ) $(LIB) -lm

clean:
	${RM} $(ALL) $(OBJ)
