OFILES = crate_lib.o CrateHandle.o

PROGRAMS = 

HFILES = CrateHandle.hh crate_lib_defs.h crate_lib.h
SWIGFILES = numpy.i stddecls.i CrateHandle.i crate_lib_defs.i

OPTIMIZE = -g -O0

CAEN_INC = /usr/include
GENERS_INC = /usr/local/include
PYTHON_INC = /usr/local/anaconda3/include/python3.6m
NUMPY_INC := $(shell python3 -c "import numpy; print(numpy.get_include())")
INCLUDES = -I. -I$(GENERS_INC) -I$(CAEN_INC) -I$(NUMPY_INC) -I$(PYTHON_INC)

CFLAGS = $(OPTIMIZE) $(INCLUDES) -pthread -DLINUX -Wall -W -Werror
CPPFLAGS = -std=c++11 $(CFLAGS)

LIBS = -pthread -L/usr/local/lib -L/usr/lib64 -L/usr/lib -lpthread -ldl -lm

%.o : %.c
	gcc -c $(CFLAGS) -fPIC -MD $< -o $@
	@sed -i 's,\($*\.o\)[:]*\(.*\),$@: $$\(wildcard\2\)\n\1:\2,g' $*.d

%.o : %.cc
	g++ -c $(CPPFLAGS) -fPIC -MD $< -o $@
	@sed -i 's,\($*\.o\)[:]*\(.*\),$@: $$\(wildcard\2\)\n\1:\2,g' $*.d

%.o : %.cxx
	g++ -c -Wno-unused-parameter $(CPPFLAGS) -fPIC -MD $< -o $@
	@sed -i 's,\($*\.o\)[:]*\(.*\),$@: $$\(wildcard\2\)\n\1:\2,g' $*.d

BINARIES = $(PROGRAMS:.cc=)
PYTHONMODULES = _caencamac.so

all: $(BINARIES) $(PYTHONMODULES)

$(BINARIES): % : %.o $(OFILES); g++ $(OPTIMIZE) -fPIC -o $@ $^ $(LIBS)

clean:
	rm -f $(BINARIES) caencamac.py caencamac_wrap.cxx core.* *.o *.pyc *.so *.d *~
	rm -fr __pycache__

_caencamac.so: caencamac_wrap.o $(OFILES)
	rm -f $@
	g++ $(OPTIMIZE) -shared -o $@ $^ $(LIBS)

caencamac_wrap.cxx: caencamac.i $(SWIGFILES) $(HFILES)
	rm -f $@
	swig $(INCLUDES) -DLINUX -builtin -python -py3 -c++ -o $@ $<

-include $(OFILES:.o=.d)
-include $(PROGRAMS:.cc=.d)
-include caencamac_wrap.d
