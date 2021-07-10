BIN=../bin
OBJ=../obj
CFLAGS=-g
#CFLAGS=-O2
CFLAGS+=-D_FILE_OFFSET_BITS=64 -Werror -Wuninitialized
CC=gcc

%.o: %.c 
	$(CC) -c -o $@ $< $(CFLAGS) -I../../zlib-1.2.11

read: read.o lists.o
	$(CC) -o $@ $^ $(CFLAGS) -L../../zlib-1.2.11 -lz

clean:
	rm -f *.o read
