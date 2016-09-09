#
# Makefile for atFunctions / att
#	13 Aug 1996	Y.Ishisaki

CURSES_LNK = -lcurses -ltermcap

CFLAGS=	-O -I. -I$(INC)

INC = ../include
LIB = ../src/libatFunctions.a
OBJ = att.o
ALL = att

att: $(OBJ)
	$(CC) -o $@ $(OBJ) $(LIB) $(CURSES_LNK) -lm

clean:
	${RM} $(ALL) $(OBJ)
