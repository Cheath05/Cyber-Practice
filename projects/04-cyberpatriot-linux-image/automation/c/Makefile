CC       ?= gcc
CFLAGS   ?= -std=c11 -O2 -Wall -Wextra -Wpedantic

backup-helper: backup_helper_fixed.c
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -f backup-helper

.PHONY: clean
