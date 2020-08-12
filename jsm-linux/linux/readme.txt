==============================================================

                   JSM (Jenet Script Manager)

==============================================================


    by ZP Engineering srl,  rel 1.0 (Jan 29, 2004)




PURPOSE

It interacts with a Jenet CAMAC Crate controller allowing script management.
Jenet contains a complete script interpreter engine based on Lua.
Script text can be transferred, started and stopped by means of JSM.
For implementation details please refer to Jenet User's Manual.

References:

www.zpeng.com/jenet     Jenet official web site
www.lua.org             Lua scripting language web site


COMMAND-LINE PARAMETERS

JSM is a command-line utility available for Windows and for Linux.
It accepts command-line parameters to determine which action to perform.

jsm -h 
   displays program version and a list of allowed parameters.

jsm -ip <IP addr> -u <filename.ext>
   uploads script text from specified file on host to Jenet

jsm -ip <IP addr> -run
   starts execution of current script

jsm -ip <IP addr> -stop
   halts execution of current script

jsm -ip <IP addr> -s
   stores current script on non volatile memory for Run-on-Boot option

jsm -ip <IP addr> -rob <value>
   sets rob (Run-on-Boot) flag to specified value (0 or 1)

jsm -ip <IP addr> -d <filename.ext>
   downloads script text from Jenet to specified file on host

jsm -ip <IP addr> -d stdout
   downloads script text from Jenet to stdout on host

jsm -ip <IP addr> -e <filename.ext>
   stores error message (if any) from Jenet to specified file on host

jsm -ip <IP addr> -e stdout
   stores error message (if any) from Jenet to stdout on host

jsm -ip <IP addr> -l <filename.ext>
   stores log message (if any) from Jenet to specified file on host

jsm -ip <IP addr> -l stdout
   stores log message (if any) from Jenet to stdout on host




 
       
