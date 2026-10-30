CC     ?= gcc
CFLAGS ?= -O2 -s
# -s strips the symbol table so the challenge is a little harder to read

checker: checker.c
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -f checker

.PHONY: clean
