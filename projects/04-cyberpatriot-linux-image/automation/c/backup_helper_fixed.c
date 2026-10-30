/*
 * backup_helper_fixed.c - the hardened version of the Project 04 C exercise.
 *
 * The buggy original (described in answer-key.md) was made SUID root and called the C library
 * `system()` with a RELATIVE command name, so the shell resolved "tar" using the caller's PATH
 * while running as root. That is the classic PATH-hijacking privilege escalation and is why one
 * of your hardening controls is "no unexpected SUID binaries" (see GTFOBins).
 *
 * This version fixes it:
 *   1. Absolute program path (/usr/bin/tar) via execv(): no PATH lookup.
 *   2. No shell at all, so shell metacharacters cannot be injected.
 *   3. A fixed, minimal environment instead of inheriting the caller's.
 *   4. Output into a root-owned directory with safe permissions, not a predictable
 *      world-writable /tmp name (which invites symlink attacks).
 *   5. Note in the comments: the cleanest fix is usually NOT to be SUID at all. Run backups from
 *      a root systemd service/cron job and let users trigger them through a narrowly scoped
 *      sudoers rule.
 *
 * Build:  make           (or: gcc -Wall -Wextra -o backup-helper backup_helper_fixed.c)
 * This program is safe to compile and read anywhere; do NOT make it SUID in production.
 */
#include <errno.h>
#include <stdio.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <unistd.h>

#define BACKUP_DIR "/var/backups/home"

int main(void) {
    if (mkdir(BACKUP_DIR, 0700) != 0 && errno != EEXIST) {
        perror("mkdir " BACKUP_DIR);
        return 1;
    }

    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        return 1;
    }

    if (pid == 0) {
        /* Child: a minimal, trusted environment. No caller-controlled PATH. */
        char *const args[] = {
            "/usr/bin/tar", "-czf", BACKUP_DIR "/home.tgz", "/home", (char *)0
        };
        char *const env[] = {
            "PATH=/usr/bin:/bin", "LANG=C", (char *)0
        };
        execve(args[0], args, env);   /* absolute path, explicit argv, fixed env */
        perror("execve");             /* only reached if execve fails */
        _exit(127);
    }

    int status = 0;
    if (waitpid(pid, &status, 0) < 0) {
        perror("waitpid");
        return 1;
    }
    if (WIFEXITED(status) && WEXITSTATUS(status) == 0) {
        printf("Backup written to %s/home.tgz\n", BACKUP_DIR);
        return 0;
    }
    fprintf(stderr, "backup failed\n");
    return 1;
}
