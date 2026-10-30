/*
 * checker.c - a password-check reversing challenge (Project 09).
 * Build stripped so players must reverse it:  make
 * Players recover the password with `strings`, `ltrace`, or a decompiler (Ghidra/radare2),
 * then run it to print the flag. This teaches what a reverser looks for; it is not malware.
 */
#include <stdio.h>
#include <string.h>

int main(void) {
    char input[64];
    const char *secret = "r3verse_me_2026";   /* a reverser will find this */
    printf("Password: ");
    if (!fgets(input, sizeof input, stdin)) return 1;
    input[strcspn(input, "\n")] = '\0';
    if (strcmp(input, secret) == 0) {
        printf("Correct! flag{homelab_reversing_is_fun}\n");
        return 0;
    }
    printf("Nope.\n");
    return 1;
}
