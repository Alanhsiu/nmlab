# CC and CFLAGS are varilables
CC = g++
CFLAGS = -c
AR = ar
ARFLAGS = rcv
# -c option ask g++ to compile the source files, but do not link.
# -g option is for debugging version
# -O2 option is for optimized version
DBGFLAGS = -g -D_DEBUG_ON_
OPTFLAGS = -O3

all	: bin/nmlab
	@echo -n ""

# optimized version
bin/nmlab	: main_opt.o lib
			$(CC) $(OPTFLAGS)  main_opt.o -o bin/nmlab
main_opt.o 	   	: src/main.cpp lib/test.cpp
			$(CC) $(CFLAGS) $< -Ilib -o $@

	
# clean all the .o and executable files
clean:
		rm -rf *.o  bin/*