char *help_all= "\n\
 Available commands\n\n\
   Angle    : calculate the angle between two vectors\n\
   Convert  : conversion coordinate\n\
   ENd      : terminate program\n\
   EUler    : set euler angle\n\
   Help     : help\n\
   Rotate   : rotate around satellite axis\n\
   TIme     : set time\n\
   TArget   : set target\n\n\
   to obtain information about these commands\n\
   enter help [command]";

char *help_angle= "\n\
   Command:   Angle\n\n\
   Purpose:   calculate the angle between two vectors\n\n\
   Syntax:    ANGLE   alpha1 delta1  alpha2 delta2\n\n\
   Example:   angle   230.155 8.785  229.847 7.878\n\
              angle   10h34m30.0s 23d15m45s  4h31m30.0s -13d21m0s\n";

char *help_convert= "\n\
   Command:   Convert\n\n\
   Purpose:   conversion coordinate\n\n\
   Syntax:    CONVERT  [coord] alpha delta\n\
              coord : coordinate system of alpha and delta\n\
                  E1950 : Equatorial Coordinate (Epoch 1950)\n\
                  E2000 : Equatorial Coordinate (Epoch 2000)\n\
                  G     : Galactic Coordinate\n\
                  default : E2000\n\n\
   Example    convert e1950  10h34m30.0s 23d15m45s\n\
              convert g      230.5 -23.4\n";

char *help_end="\n\
   Command:   ENd\n\n\
   Purpose:   terminate program\n\n\
   Syntax:    END";

char *help_euler="\n\
   Command:   EUler\n\n\
   Purpose:   input euler angle\n\n\
   Syntax:    Euler  phai theta psi\n\n\
   Example:   euler 10.0 120.0 20.0\n";

char *help_help="\n\
   Command:   Help\n\n\
   Purpose:   help\n\n\
   Syntax:    HELP [command name]\n\
              if you omit command name, avalable commands are displayed";

char *help_qpara="\n\
   Command:   QPara\n\n\
   Purpose:   input q-parameters\n\n\
   Syntax:    QPARA param1 param2 param3 param4\n\n\
   Example:   qpara  0.0 0.0 0.707107 0.707107\n";

char *help_rotate="\n\
   Command:   Rotate\n\n\
   Purpose:   rotate satelite along x,y,z axis\n\n\
   Syntax:    Rotate axis angle\n\
                     axis : X,Y,Z\n\n\
   Example:   rotate x 90.0\n";

char *help_target="\n\
   Command:   TArget\n\n\
   Purpose:   input target\n\n\
   Syntax:    TARGET [option] name alpha delata\n\
              option = e1950: Equatorial Coordinate (Epoch 1950)\n\
                       e2000: Equatorial Coordinate (Epoch 2000)\n\
                       g    : Galactic Coordinate\n\
                       [1-6]: column\n\n\
   Example    target  e1950 a2256 17h6m36s 78d47m0s\n\
              target  3  g  a2256 111.09 31.73\n";

char *help_time="\n\
   Command:   TIme\n\n\
   Purpose:   input UT\n\n\
   Syntax:    TIME yy/mm/dd hh:mm:ss.sss\n\n\
   Example:  time 92/12/25 11:12:05.0\n";

char *prompt=" att> ";
char *version=" ATT ver1.0";
char *err_memory="  ERROR: not enough memory\n";
