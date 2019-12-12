# Linux System Call Table

These are the system call numbers (NR) and their corresponding symbolic names.

These vary significantly across architectures/ABIs, both in mappings and in
actual name.

This is a quick reference for people debugging things (e.g. seccomp failures).

For more details on syscalls in general, see the
[syscall(2)](http://man7.org/linux/man-pages/man2/syscall.2.html) man page.

[TOC]

## Random Names {#naming}

Depending on the environment you're in, syscall names might use slightly
different naming conventions.

The kernel headers (e.g. `asm/unistd.h`) use names like `__NR_xxx`, but don't
provide any other utility code.
The C library headers (e.g. `syscall.h` & `sys/syscall.h`) use names like
`SYS_xxx` with the intention they be used with `syscall(...)`.
These defines will be exactly the same -- so `__NR_foo` will have the same
value as `SYS_foo`.

Which one a developer chooses to use is a bit arbitrary, and most likely belies
their background (with kernel developers tending towards `__NR_xxx`).
If you're writing userland C code and the `syscall(...)` function, you probably
should stick to `SYS_xxx` instead.

The short name "NR" itself just refers to "number".
You might see "syscall number" and "NR" and "syscall NR" used interchangeably.

Another fun difference is that some architectures namespace syscalls that are
specific to their port in some way.
Or they don't.
It's another situation of different kernel maintainers making different choices
and there not being a central authority who noticed & enforced things.
For example, ARM has a few `__ARM_NR_xxx` syscalls that they consider "private",
and they have a few `__NR_arm_xxx` syscalls to indicate that they have a custom
wrapper around the `xxx` syscall!

Another edge case to keep in mind is that different architectures might use the
same name for different entry points.
It's uncommon, but can come up when looking at syscalls with variants.
For example, an older architecture port might have `setuid` & `setuid32` while
newer ones only have `setuid`.
The older port's `setuid` takes a 16-bit argument while the newer port's
`setuid` takes a 32-bit argument and is equivalent to `setuid32`.
There are many parallels with filesystem calls like `statfs` & `statfs64`.

## Kernel Implementations

The cs/ links to kernel sources are mostly best effort.
They focus on the common C entry point, but depending on your execution
environment, that might not be the first place the kernel executes.
Unfortunately, they're Google-internal only currently as we haven't found any
good public indexes to point to instead.

Every architecture may point a syscall from its initial entry point to custom
trampoline code.
For example, ARM's fstatfs64 implementation starts execution in
sys_fstatfs64_wrapper which lives under arch/arm/ as assembly code.
That in turn calls sys_fstatfs64 which is C code in the common fs/ tree.
Usually these trampolines are not complicated, but they might add an extra check
to overall execution.
If you're seeing confusing behavior related to the C code, you might want to
dive deeper.

When working with 32-bit ABIs on 64-bit kernels, you might run into the syscall
compat layers which try to swizzle structures.
This shows up a lot on x86 & ARM systems where the userland is 32-bit but the
kernel is 64-bit.
These will use conventions like compat_sys_xxx instead of sys_xxx, and
COMPAT_SYSCALL_XXX wrappers instead of SYSCALL_XXX.
They're responsible for taking the 32-bit structures from userland, converting
them to the 64-bit structures the kernel uses, then calling the 64-bit C code.
Normally this conversion is not a problem, but if the code detects issues with
the data structures, it'll error out before the common implementation of the
syscall is ever executed.

The Android/ARC++ container executes under the alt-syscall layer.
This allows defining of a custom syscall table for the purpose of hard disabling
any syscalls for all processes (without needing seccomp), or for adding extra
checks to the entry/exit points of the common implementation, or stubbing things
out regardless of any arguments.
All of this code will run before the common implementation of the syscall is
ever executed.
Since the tables are hand maintained in our kernel (and not upstream), new
syscalls aren't added to the whitelist automatically, so you might see confusing
errors like ENOSYS, but only when run inside of the container.
If you're seeing misbehavior, you should check to see if alt-syscall is enabled
for the process, and if so, look at the wrappers under security/chromiumos/.

## Calling Conventions

Here's a cheat sheet for the syscall calling convention for arches supported
by Chrome OS.
These are useful when looking at seccomp failures in minidumps.

This is only meant as a cheat sheet for people writing seccomp filters, or
similar low level tools.
It is *not* a complete reference for the entire calling convention for each
architecture as that can be extremely nuanced & complicated.
If you need that level of detail, you should start with the [syscall(2) notes],
and then check out the respective psABI (Processor Specific Application Binary
Interface) supplemental chapters.

[syscall(2) notes]: http://man7.org/linux/man-pages/man2/syscall.2.html#NOTES

*** note
The `arg0` names below match minijail's seccomp filter syntax.
It's not uncommon for source code to count from 1 instead of 0, so be aware as
you go spelunking into implementations.
***

| arch   | syscall NR | return | arg0 | arg1 | arg2 | arg3 | arg4 | arg5 |
|:------:|:----------:|:------:|:----:|:----:|:----:|:----:|:----:|:----:|
| arm    | r7         | r0     | r0   | r1   | r2   | r3   | r4   | r5   |
| arm64  | x8         | x0     | x0   | x1   | x2   | x3   | x4   | x5   |
| x86    | eax        | eax    | ebx  | ecx  | edx  | esi  | edi  | ebp  |
| x86_64 | rax        | rax    | rdi  | rsi  | rdx  | r10  | r8   | r9   |

<!--
Note: These tables are generated by the syscalls.py helper script.
Do not hand edit.
-->

[linux-headers]: https://chromium.googlesource.com/chromiumos/overlays/chromiumos-overlay/+/HEAD/sys-kernel/linux-headers/

## Tables

### x86_64 (64-bit)

Compiled from [Linux 4.14.0 headers][linux-headers].

| NR | syscall name | references | %rax | arg0 (%rdi) | arg1 (%rsi) | arg2 (%rdx) | arg3 (%r10) | arg4 (%r8) | arg5 (%r9) |
|:---:|---|:---:|:---:|---|---|---|---|---|---|
| 0 | read | [man/](http://man7.org/linux/man-pages/man2/read.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*read+package:^chromeos_public$) | 0x00 | unsigned int fd | char \*buf | size\_t count | - | - | - |
| 1 | write | [man/](http://man7.org/linux/man-pages/man2/write.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*write+package:^chromeos_public$) | 0x01 | unsigned int fd | const char \*buf | size\_t count | - | - | - |
| 2 | open | [man/](http://man7.org/linux/man-pages/man2/open.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*open+package:^chromeos_public$) | 0x02 | const char \*filename | int flags | umode\_t mode | - | - | - |
| 3 | close | [man/](http://man7.org/linux/man-pages/man2/close.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*close+package:^chromeos_public$) | 0x03 | unsigned int fd | - | - | - | - | - |
| 4 | stat | [man/](http://man7.org/linux/man-pages/man2/stat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*stat+package:^chromeos_public$) | 0x04 | const char \*filename | struct \_\_old\_kernel\_stat \*statbuf | - | - | - | - |
| 5 | fstat | [man/](http://man7.org/linux/man-pages/man2/fstat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fstat+package:^chromeos_public$) | 0x05 | unsigned int fd | struct \_\_old\_kernel\_stat \*statbuf | - | - | - | - |
| 6 | lstat | [man/](http://man7.org/linux/man-pages/man2/lstat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*lstat+package:^chromeos_public$) | 0x06 | const char \*filename | struct \_\_old\_kernel\_stat \*statbuf | - | - | - | - |
| 7 | poll | [man/](http://man7.org/linux/man-pages/man2/poll.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*poll+package:^chromeos_public$) | 0x07 | struct pollfd \*ufds | unsigned int nfds | int timeout | - | - | - |
| 8 | lseek | [man/](http://man7.org/linux/man-pages/man2/lseek.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*lseek+package:^chromeos_public$) | 0x08 | unsigned int fd | off\_t offset | unsigned int whence | - | - | - |
| 9 | mmap | [man/](http://man7.org/linux/man-pages/man2/mmap.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mmap+package:^chromeos_public$) | 0x09 | ? | ? | ? | ? | ? | ? |
| 10 | mprotect | [man/](http://man7.org/linux/man-pages/man2/mprotect.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mprotect+package:^chromeos_public$) | 0x0a | unsigned long start | size\_t len | unsigned long prot | - | - | - |
| 11 | munmap | [man/](http://man7.org/linux/man-pages/man2/munmap.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*munmap+package:^chromeos_public$) | 0x0b | unsigned long addr | size\_t len | - | - | - | - |
| 12 | brk | [man/](http://man7.org/linux/man-pages/man2/brk.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*brk+package:^chromeos_public$) | 0x0c | unsigned long brk | - | - | - | - | - |
| 13 | rt_sigaction | [man/](http://man7.org/linux/man-pages/man2/rt_sigaction.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rt_sigaction+package:^chromeos_public$) | 0x0d | int | const struct sigaction \* | struct sigaction \* | size\_t | - | - |
| 14 | rt_sigprocmask | [man/](http://man7.org/linux/man-pages/man2/rt_sigprocmask.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rt_sigprocmask+package:^chromeos_public$) | 0x0e | int how | sigset\_t \*set | sigset\_t \*oset | size\_t sigsetsize | - | - |
| 15 | rt_sigreturn | [man/](http://man7.org/linux/man-pages/man2/rt_sigreturn.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rt_sigreturn+package:^chromeos_public$) | 0x0f | ? | ? | ? | ? | ? | ? |
| 16 | ioctl | [man/](http://man7.org/linux/man-pages/man2/ioctl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ioctl+package:^chromeos_public$) | 0x10 | unsigned int fd | unsigned int cmd | unsigned long arg | - | - | - |
| 17 | pread64 | [man/](http://man7.org/linux/man-pages/man2/pread64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pread64+package:^chromeos_public$) | 0x11 | unsigned int fd | char \*buf | size\_t count | loff\_t pos | - | - |
| 18 | pwrite64 | [man/](http://man7.org/linux/man-pages/man2/pwrite64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pwrite64+package:^chromeos_public$) | 0x12 | unsigned int fd | const char \*buf | size\_t count | loff\_t pos | - | - |
| 19 | readv | [man/](http://man7.org/linux/man-pages/man2/readv.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*readv+package:^chromeos_public$) | 0x13 | unsigned long fd | const struct iovec \*vec | unsigned long vlen | - | - | - |
| 20 | writev | [man/](http://man7.org/linux/man-pages/man2/writev.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*writev+package:^chromeos_public$) | 0x14 | unsigned long fd | const struct iovec \*vec | unsigned long vlen | - | - | - |
| 21 | access | [man/](http://man7.org/linux/man-pages/man2/access.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*access+package:^chromeos_public$) | 0x15 | const char \*filename | int mode | - | - | - | - |
| 22 | pipe | [man/](http://man7.org/linux/man-pages/man2/pipe.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pipe+package:^chromeos_public$) | 0x16 | int \*fildes | - | - | - | - | - |
| 23 | select | [man/](http://man7.org/linux/man-pages/man2/select.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*select+package:^chromeos_public$) | 0x17 | int n | fd\_set \*inp | fd\_set \*outp | fd\_set \*exp | struct timeval \*tvp | - |
| 24 | sched_yield | [man/](http://man7.org/linux/man-pages/man2/sched_yield.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_yield+package:^chromeos_public$) | 0x18 | - | - | - | - | - | - |
| 25 | mremap | [man/](http://man7.org/linux/man-pages/man2/mremap.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mremap+package:^chromeos_public$) | 0x19 | unsigned long addr | unsigned long old\_len | unsigned long new\_len | unsigned long flags | unsigned long new\_addr | - |
| 26 | msync | [man/](http://man7.org/linux/man-pages/man2/msync.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*msync+package:^chromeos_public$) | 0x1a | unsigned long start | size\_t len | int flags | - | - | - |
| 27 | mincore | [man/](http://man7.org/linux/man-pages/man2/mincore.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mincore+package:^chromeos_public$) | 0x1b | unsigned long start | size\_t len | unsigned char \* vec | - | - | - |
| 28 | madvise | [man/](http://man7.org/linux/man-pages/man2/madvise.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*madvise+package:^chromeos_public$) | 0x1c | unsigned long start | size\_t len | int behavior | - | - | - |
| 29 | shmget | [man/](http://man7.org/linux/man-pages/man2/shmget.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*shmget+package:^chromeos_public$) | 0x1d | key\_t key | size\_t size | int flag | - | - | - |
| 30 | shmat | [man/](http://man7.org/linux/man-pages/man2/shmat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*shmat+package:^chromeos_public$) | 0x1e | int shmid | char \*shmaddr | int shmflg | - | - | - |
| 31 | shmctl | [man/](http://man7.org/linux/man-pages/man2/shmctl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*shmctl+package:^chromeos_public$) | 0x1f | int shmid | int cmd | struct shmid\_ds \*buf | - | - | - |
| 32 | dup | [man/](http://man7.org/linux/man-pages/man2/dup.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*dup+package:^chromeos_public$) | 0x20 | unsigned int fildes | - | - | - | - | - |
| 33 | dup2 | [man/](http://man7.org/linux/man-pages/man2/dup2.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*dup2+package:^chromeos_public$) | 0x21 | unsigned int oldfd | unsigned int newfd | - | - | - | - |
| 34 | pause | [man/](http://man7.org/linux/man-pages/man2/pause.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pause+package:^chromeos_public$) | 0x22 | - | - | - | - | - | - |
| 35 | nanosleep | [man/](http://man7.org/linux/man-pages/man2/nanosleep.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*nanosleep+package:^chromeos_public$) | 0x23 | struct \_\_kernel\_timespec \*rqtp | struct \_\_kernel\_timespec \*rmtp | - | - | - | - |
| 36 | getitimer | [man/](http://man7.org/linux/man-pages/man2/getitimer.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getitimer+package:^chromeos_public$) | 0x24 | int which | struct itimerval \*value | - | - | - | - |
| 37 | alarm | [man/](http://man7.org/linux/man-pages/man2/alarm.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*alarm+package:^chromeos_public$) | 0x25 | unsigned int seconds | - | - | - | - | - |
| 38 | setitimer | [man/](http://man7.org/linux/man-pages/man2/setitimer.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setitimer+package:^chromeos_public$) | 0x26 | int which | struct itimerval \*value | struct itimerval \*ovalue | - | - | - |
| 39 | getpid | [man/](http://man7.org/linux/man-pages/man2/getpid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getpid+package:^chromeos_public$) | 0x27 | - | - | - | - | - | - |
| 40 | sendfile | [man/](http://man7.org/linux/man-pages/man2/sendfile.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sendfile+package:^chromeos_public$) | 0x28 | int out\_fd | int in\_fd | off\_t \*offset | size\_t count | - | - |
| 41 | socket | [man/](http://man7.org/linux/man-pages/man2/socket.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*socket+package:^chromeos_public$) | 0x29 | int | int | int | - | - | - |
| 42 | connect | [man/](http://man7.org/linux/man-pages/man2/connect.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*connect+package:^chromeos_public$) | 0x2a | int | struct sockaddr \* | int | - | - | - |
| 43 | accept | [man/](http://man7.org/linux/man-pages/man2/accept.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*accept+package:^chromeos_public$) | 0x2b | int | struct sockaddr \* | int \* | - | - | - |
| 44 | sendto | [man/](http://man7.org/linux/man-pages/man2/sendto.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sendto+package:^chromeos_public$) | 0x2c | int | void \* | size\_t | unsigned | struct sockaddr \* | int |
| 45 | recvfrom | [man/](http://man7.org/linux/man-pages/man2/recvfrom.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*recvfrom+package:^chromeos_public$) | 0x2d | int | void \* | size\_t | unsigned | struct sockaddr \* | int \* |
| 46 | sendmsg | [man/](http://man7.org/linux/man-pages/man2/sendmsg.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sendmsg+package:^chromeos_public$) | 0x2e | int fd | struct user\_msghdr \*msg | unsigned flags | - | - | - |
| 47 | recvmsg | [man/](http://man7.org/linux/man-pages/man2/recvmsg.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*recvmsg+package:^chromeos_public$) | 0x2f | int fd | struct user\_msghdr \*msg | unsigned flags | - | - | - |
| 48 | shutdown | [man/](http://man7.org/linux/man-pages/man2/shutdown.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*shutdown+package:^chromeos_public$) | 0x30 | int | int | - | - | - | - |
| 49 | bind | [man/](http://man7.org/linux/man-pages/man2/bind.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*bind+package:^chromeos_public$) | 0x31 | int | struct sockaddr \* | int | - | - | - |
| 50 | listen | [man/](http://man7.org/linux/man-pages/man2/listen.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*listen+package:^chromeos_public$) | 0x32 | int | int | - | - | - | - |
| 51 | getsockname | [man/](http://man7.org/linux/man-pages/man2/getsockname.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getsockname+package:^chromeos_public$) | 0x33 | int | struct sockaddr \* | int \* | - | - | - |
| 52 | getpeername | [man/](http://man7.org/linux/man-pages/man2/getpeername.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getpeername+package:^chromeos_public$) | 0x34 | int | struct sockaddr \* | int \* | - | - | - |
| 53 | socketpair | [man/](http://man7.org/linux/man-pages/man2/socketpair.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*socketpair+package:^chromeos_public$) | 0x35 | int | int | int | int \* | - | - |
| 54 | setsockopt | [man/](http://man7.org/linux/man-pages/man2/setsockopt.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setsockopt+package:^chromeos_public$) | 0x36 | int fd | int level | int optname | char \*optval | int optlen | - |
| 55 | getsockopt | [man/](http://man7.org/linux/man-pages/man2/getsockopt.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getsockopt+package:^chromeos_public$) | 0x37 | int fd | int level | int optname | char \*optval | int \*optlen | - |
| 56 | clone | [man/](http://man7.org/linux/man-pages/man2/clone.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*clone+package:^chromeos_public$) | 0x38 | unsigned long | unsigned long | int \* | int \* | unsigned long | - |
| 57 | fork | [man/](http://man7.org/linux/man-pages/man2/fork.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fork+package:^chromeos_public$) | 0x39 | - | - | - | - | - | - |
| 58 | vfork | [man/](http://man7.org/linux/man-pages/man2/vfork.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*vfork+package:^chromeos_public$) | 0x3a | - | - | - | - | - | - |
| 59 | execve | [man/](http://man7.org/linux/man-pages/man2/execve.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*execve+package:^chromeos_public$) | 0x3b | const char \*filename | const char \*const \*argv | const char \*const \*envp | - | - | - |
| 60 | exit | [man/](http://man7.org/linux/man-pages/man2/exit.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*exit+package:^chromeos_public$) | 0x3c | int error\_code | - | - | - | - | - |
| 61 | wait4 | [man/](http://man7.org/linux/man-pages/man2/wait4.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*wait4+package:^chromeos_public$) | 0x3d | pid\_t pid | int \*stat\_addr | int options | struct rusage \*ru | - | - |
| 62 | kill | [man/](http://man7.org/linux/man-pages/man2/kill.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*kill+package:^chromeos_public$) | 0x3e | pid\_t pid | int sig | - | - | - | - |
| 63 | uname | [man/](http://man7.org/linux/man-pages/man2/uname.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*uname+package:^chromeos_public$) | 0x3f | struct old\_utsname \* | - | - | - | - | - |
| 64 | semget | [man/](http://man7.org/linux/man-pages/man2/semget.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*semget+package:^chromeos_public$) | 0x40 | key\_t key | int nsems | int semflg | - | - | - |
| 65 | semop | [man/](http://man7.org/linux/man-pages/man2/semop.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*semop+package:^chromeos_public$) | 0x41 | int semid | struct sembuf \*sops | unsigned nsops | - | - | - |
| 66 | semctl | [man/](http://man7.org/linux/man-pages/man2/semctl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*semctl+package:^chromeos_public$) | 0x42 | int semid | int semnum | int cmd | unsigned long arg | - | - |
| 67 | shmdt | [man/](http://man7.org/linux/man-pages/man2/shmdt.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*shmdt+package:^chromeos_public$) | 0x43 | char \*shmaddr | - | - | - | - | - |
| 68 | msgget | [man/](http://man7.org/linux/man-pages/man2/msgget.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*msgget+package:^chromeos_public$) | 0x44 | key\_t key | int msgflg | - | - | - | - |
| 69 | msgsnd | [man/](http://man7.org/linux/man-pages/man2/msgsnd.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*msgsnd+package:^chromeos_public$) | 0x45 | int msqid | struct msgbuf \*msgp | size\_t msgsz | int msgflg | - | - |
| 70 | msgrcv | [man/](http://man7.org/linux/man-pages/man2/msgrcv.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*msgrcv+package:^chromeos_public$) | 0x46 | int msqid | struct msgbuf \*msgp | size\_t msgsz | long msgtyp | int msgflg | - |
| 71 | msgctl | [man/](http://man7.org/linux/man-pages/man2/msgctl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*msgctl+package:^chromeos_public$) | 0x47 | int msqid | int cmd | struct msqid\_ds \*buf | - | - | - |
| 72 | fcntl | [man/](http://man7.org/linux/man-pages/man2/fcntl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fcntl+package:^chromeos_public$) | 0x48 | unsigned int fd | unsigned int cmd | unsigned long arg | - | - | - |
| 73 | flock | [man/](http://man7.org/linux/man-pages/man2/flock.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*flock+package:^chromeos_public$) | 0x49 | unsigned int fd | unsigned int cmd | - | - | - | - |
| 74 | fsync | [man/](http://man7.org/linux/man-pages/man2/fsync.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fsync+package:^chromeos_public$) | 0x4a | unsigned int fd | - | - | - | - | - |
| 75 | fdatasync | [man/](http://man7.org/linux/man-pages/man2/fdatasync.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fdatasync+package:^chromeos_public$) | 0x4b | unsigned int fd | - | - | - | - | - |
| 76 | truncate | [man/](http://man7.org/linux/man-pages/man2/truncate.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*truncate+package:^chromeos_public$) | 0x4c | const char \*path | long length | - | - | - | - |
| 77 | ftruncate | [man/](http://man7.org/linux/man-pages/man2/ftruncate.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ftruncate+package:^chromeos_public$) | 0x4d | unsigned int fd | unsigned long length | - | - | - | - |
| 78 | getdents | [man/](http://man7.org/linux/man-pages/man2/getdents.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getdents+package:^chromeos_public$) | 0x4e | unsigned int fd | struct linux\_dirent \*dirent | unsigned int count | - | - | - |
| 79 | getcwd | [man/](http://man7.org/linux/man-pages/man2/getcwd.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getcwd+package:^chromeos_public$) | 0x4f | char \*buf | unsigned long size | - | - | - | - |
| 80 | chdir | [man/](http://man7.org/linux/man-pages/man2/chdir.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*chdir+package:^chromeos_public$) | 0x50 | const char \*filename | - | - | - | - | - |
| 81 | fchdir | [man/](http://man7.org/linux/man-pages/man2/fchdir.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fchdir+package:^chromeos_public$) | 0x51 | unsigned int fd | - | - | - | - | - |
| 82 | rename | [man/](http://man7.org/linux/man-pages/man2/rename.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rename+package:^chromeos_public$) | 0x52 | const char \*oldname | const char \*newname | - | - | - | - |
| 83 | mkdir | [man/](http://man7.org/linux/man-pages/man2/mkdir.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mkdir+package:^chromeos_public$) | 0x53 | const char \*pathname | umode\_t mode | - | - | - | - |
| 84 | rmdir | [man/](http://man7.org/linux/man-pages/man2/rmdir.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rmdir+package:^chromeos_public$) | 0x54 | const char \*pathname | - | - | - | - | - |
| 85 | creat | [man/](http://man7.org/linux/man-pages/man2/creat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*creat+package:^chromeos_public$) | 0x55 | const char \*pathname | umode\_t mode | - | - | - | - |
| 86 | link | [man/](http://man7.org/linux/man-pages/man2/link.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*link+package:^chromeos_public$) | 0x56 | const char \*oldname | const char \*newname | - | - | - | - |
| 87 | unlink | [man/](http://man7.org/linux/man-pages/man2/unlink.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*unlink+package:^chromeos_public$) | 0x57 | const char \*pathname | - | - | - | - | - |
| 88 | symlink | [man/](http://man7.org/linux/man-pages/man2/symlink.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*symlink+package:^chromeos_public$) | 0x58 | const char \*old | const char \*new | - | - | - | - |
| 89 | readlink | [man/](http://man7.org/linux/man-pages/man2/readlink.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*readlink+package:^chromeos_public$) | 0x59 | const char \*path | char \*buf | int bufsiz | - | - | - |
| 90 | chmod | [man/](http://man7.org/linux/man-pages/man2/chmod.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*chmod+package:^chromeos_public$) | 0x5a | const char \*filename | umode\_t mode | - | - | - | - |
| 91 | fchmod | [man/](http://man7.org/linux/man-pages/man2/fchmod.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fchmod+package:^chromeos_public$) | 0x5b | unsigned int fd | umode\_t mode | - | - | - | - |
| 92 | chown | [man/](http://man7.org/linux/man-pages/man2/chown.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*chown+package:^chromeos_public$) | 0x5c | const char \*filename | uid\_t user | gid\_t group | - | - | - |
| 93 | fchown | [man/](http://man7.org/linux/man-pages/man2/fchown.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fchown+package:^chromeos_public$) | 0x5d | unsigned int fd | uid\_t user | gid\_t group | - | - | - |
| 94 | lchown | [man/](http://man7.org/linux/man-pages/man2/lchown.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*lchown+package:^chromeos_public$) | 0x5e | const char \*filename | uid\_t user | gid\_t group | - | - | - |
| 95 | umask | [man/](http://man7.org/linux/man-pages/man2/umask.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*umask+package:^chromeos_public$) | 0x5f | int mask | - | - | - | - | - |
| 96 | gettimeofday | [man/](http://man7.org/linux/man-pages/man2/gettimeofday.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*gettimeofday+package:^chromeos_public$) | 0x60 | struct timeval \*tv | struct timezone \*tz | - | - | - | - |
| 97 | getrlimit | [man/](http://man7.org/linux/man-pages/man2/getrlimit.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getrlimit+package:^chromeos_public$) | 0x61 | unsigned int resource | struct rlimit \*rlim | - | - | - | - |
| 98 | getrusage | [man/](http://man7.org/linux/man-pages/man2/getrusage.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getrusage+package:^chromeos_public$) | 0x62 | int who | struct rusage \*ru | - | - | - | - |
| 99 | sysinfo | [man/](http://man7.org/linux/man-pages/man2/sysinfo.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sysinfo+package:^chromeos_public$) | 0x63 | struct sysinfo \*info | - | - | - | - | - |
| 100 | times | [man/](http://man7.org/linux/man-pages/man2/times.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*times+package:^chromeos_public$) | 0x64 | struct tms \*tbuf | - | - | - | - | - |
| 101 | ptrace | [man/](http://man7.org/linux/man-pages/man2/ptrace.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ptrace+package:^chromeos_public$) | 0x65 | long request | long pid | unsigned long addr | unsigned long data | - | - |
| 102 | getuid | [man/](http://man7.org/linux/man-pages/man2/getuid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getuid+package:^chromeos_public$) | 0x66 | - | - | - | - | - | - |
| 103 | syslog | [man/](http://man7.org/linux/man-pages/man2/syslog.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*syslog+package:^chromeos_public$) | 0x67 | int type | char \*buf | int len | - | - | - |
| 104 | getgid | [man/](http://man7.org/linux/man-pages/man2/getgid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getgid+package:^chromeos_public$) | 0x68 | - | - | - | - | - | - |
| 105 | setuid | [man/](http://man7.org/linux/man-pages/man2/setuid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setuid+package:^chromeos_public$) | 0x69 | uid\_t uid | - | - | - | - | - |
| 106 | setgid | [man/](http://man7.org/linux/man-pages/man2/setgid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setgid+package:^chromeos_public$) | 0x6a | gid\_t gid | - | - | - | - | - |
| 107 | geteuid | [man/](http://man7.org/linux/man-pages/man2/geteuid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*geteuid+package:^chromeos_public$) | 0x6b | - | - | - | - | - | - |
| 108 | getegid | [man/](http://man7.org/linux/man-pages/man2/getegid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getegid+package:^chromeos_public$) | 0x6c | - | - | - | - | - | - |
| 109 | setpgid | [man/](http://man7.org/linux/man-pages/man2/setpgid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setpgid+package:^chromeos_public$) | 0x6d | pid\_t pid | pid\_t pgid | - | - | - | - |
| 110 | getppid | [man/](http://man7.org/linux/man-pages/man2/getppid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getppid+package:^chromeos_public$) | 0x6e | - | - | - | - | - | - |
| 111 | getpgrp | [man/](http://man7.org/linux/man-pages/man2/getpgrp.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getpgrp+package:^chromeos_public$) | 0x6f | - | - | - | - | - | - |
| 112 | setsid | [man/](http://man7.org/linux/man-pages/man2/setsid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setsid+package:^chromeos_public$) | 0x70 | - | - | - | - | - | - |
| 113 | setreuid | [man/](http://man7.org/linux/man-pages/man2/setreuid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setreuid+package:^chromeos_public$) | 0x71 | uid\_t ruid | uid\_t euid | - | - | - | - |
| 114 | setregid | [man/](http://man7.org/linux/man-pages/man2/setregid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setregid+package:^chromeos_public$) | 0x72 | gid\_t rgid | gid\_t egid | - | - | - | - |
| 115 | getgroups | [man/](http://man7.org/linux/man-pages/man2/getgroups.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getgroups+package:^chromeos_public$) | 0x73 | int gidsetsize | gid\_t \*grouplist | - | - | - | - |
| 116 | setgroups | [man/](http://man7.org/linux/man-pages/man2/setgroups.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setgroups+package:^chromeos_public$) | 0x74 | int gidsetsize | gid\_t \*grouplist | - | - | - | - |
| 117 | setresuid | [man/](http://man7.org/linux/man-pages/man2/setresuid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setresuid+package:^chromeos_public$) | 0x75 | uid\_t ruid | uid\_t euid | uid\_t suid | - | - | - |
| 118 | getresuid | [man/](http://man7.org/linux/man-pages/man2/getresuid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getresuid+package:^chromeos_public$) | 0x76 | uid\_t \*ruid | uid\_t \*euid | uid\_t \*suid | - | - | - |
| 119 | setresgid | [man/](http://man7.org/linux/man-pages/man2/setresgid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setresgid+package:^chromeos_public$) | 0x77 | gid\_t rgid | gid\_t egid | gid\_t sgid | - | - | - |
| 120 | getresgid | [man/](http://man7.org/linux/man-pages/man2/getresgid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getresgid+package:^chromeos_public$) | 0x78 | gid\_t \*rgid | gid\_t \*egid | gid\_t \*sgid | - | - | - |
| 121 | getpgid | [man/](http://man7.org/linux/man-pages/man2/getpgid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getpgid+package:^chromeos_public$) | 0x79 | pid\_t pid | - | - | - | - | - |
| 122 | setfsuid | [man/](http://man7.org/linux/man-pages/man2/setfsuid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setfsuid+package:^chromeos_public$) | 0x7a | uid\_t uid | - | - | - | - | - |
| 123 | setfsgid | [man/](http://man7.org/linux/man-pages/man2/setfsgid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setfsgid+package:^chromeos_public$) | 0x7b | gid\_t gid | - | - | - | - | - |
| 124 | getsid | [man/](http://man7.org/linux/man-pages/man2/getsid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getsid+package:^chromeos_public$) | 0x7c | pid\_t pid | - | - | - | - | - |
| 125 | capget | [man/](http://man7.org/linux/man-pages/man2/capget.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*capget+package:^chromeos_public$) | 0x7d | cap\_user\_header\_t header | cap\_user\_data\_t dataptr | - | - | - | - |
| 126 | capset | [man/](http://man7.org/linux/man-pages/man2/capset.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*capset+package:^chromeos_public$) | 0x7e | cap\_user\_header\_t header | const cap\_user\_data\_t data | - | - | - | - |
| 127 | rt_sigpending | [man/](http://man7.org/linux/man-pages/man2/rt_sigpending.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rt_sigpending+package:^chromeos_public$) | 0x7f | sigset\_t \*set | size\_t sigsetsize | - | - | - | - |
| 128 | rt_sigtimedwait | [man/](http://man7.org/linux/man-pages/man2/rt_sigtimedwait.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rt_sigtimedwait+package:^chromeos_public$) | 0x80 | const sigset\_t \*uthese | siginfo\_t \*uinfo | const struct timespec \*uts | size\_t sigsetsize | - | - |
| 129 | rt_sigqueueinfo | [man/](http://man7.org/linux/man-pages/man2/rt_sigqueueinfo.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rt_sigqueueinfo+package:^chromeos_public$) | 0x81 | pid\_t pid | int sig | siginfo\_t \*uinfo | - | - | - |
| 130 | rt_sigsuspend | [man/](http://man7.org/linux/man-pages/man2/rt_sigsuspend.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rt_sigsuspend+package:^chromeos_public$) | 0x82 | sigset\_t \*unewset | size\_t sigsetsize | - | - | - | - |
| 131 | sigaltstack | [man/](http://man7.org/linux/man-pages/man2/sigaltstack.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sigaltstack+package:^chromeos_public$) | 0x83 | const struct sigaltstack \*uss | struct sigaltstack \*uoss | - | - | - | - |
| 132 | utime | [man/](http://man7.org/linux/man-pages/man2/utime.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*utime+package:^chromeos_public$) | 0x84 | char \*filename | struct utimbuf \*times | - | - | - | - |
| 133 | mknod | [man/](http://man7.org/linux/man-pages/man2/mknod.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mknod+package:^chromeos_public$) | 0x85 | const char \*filename | umode\_t mode | unsigned dev | - | - | - |
| 134 | uselib | [man/](http://man7.org/linux/man-pages/man2/uselib.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*uselib+package:^chromeos_public$) | 0x86 | const char \*library | - | - | - | - | - |
| 135 | personality | [man/](http://man7.org/linux/man-pages/man2/personality.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*personality+package:^chromeos_public$) | 0x87 | unsigned int personality | - | - | - | - | - |
| 136 | ustat | [man/](http://man7.org/linux/man-pages/man2/ustat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ustat+package:^chromeos_public$) | 0x88 | unsigned dev | struct ustat \*ubuf | - | - | - | - |
| 137 | statfs | [man/](http://man7.org/linux/man-pages/man2/statfs.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*statfs+package:^chromeos_public$) | 0x89 | const char \* path | struct statfs \*buf | - | - | - | - |
| 138 | fstatfs | [man/](http://man7.org/linux/man-pages/man2/fstatfs.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fstatfs+package:^chromeos_public$) | 0x8a | unsigned int fd | struct statfs \*buf | - | - | - | - |
| 139 | sysfs | [man/](http://man7.org/linux/man-pages/man2/sysfs.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sysfs+package:^chromeos_public$) | 0x8b | int option | unsigned long arg1 | unsigned long arg2 | - | - | - |
| 140 | getpriority | [man/](http://man7.org/linux/man-pages/man2/getpriority.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getpriority+package:^chromeos_public$) | 0x8c | int which | int who | - | - | - | - |
| 141 | setpriority | [man/](http://man7.org/linux/man-pages/man2/setpriority.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setpriority+package:^chromeos_public$) | 0x8d | int which | int who | int niceval | - | - | - |
| 142 | sched_setparam | [man/](http://man7.org/linux/man-pages/man2/sched_setparam.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_setparam+package:^chromeos_public$) | 0x8e | pid\_t pid | struct sched\_param \*param | - | - | - | - |
| 143 | sched_getparam | [man/](http://man7.org/linux/man-pages/man2/sched_getparam.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_getparam+package:^chromeos_public$) | 0x8f | pid\_t pid | struct sched\_param \*param | - | - | - | - |
| 144 | sched_setscheduler | [man/](http://man7.org/linux/man-pages/man2/sched_setscheduler.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_setscheduler+package:^chromeos_public$) | 0x90 | pid\_t pid | int policy | struct sched\_param \*param | - | - | - |
| 145 | sched_getscheduler | [man/](http://man7.org/linux/man-pages/man2/sched_getscheduler.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_getscheduler+package:^chromeos_public$) | 0x91 | pid\_t pid | - | - | - | - | - |
| 146 | sched_get_priority_max | [man/](http://man7.org/linux/man-pages/man2/sched_get_priority_max.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_get_priority_max+package:^chromeos_public$) | 0x92 | int policy | - | - | - | - | - |
| 147 | sched_get_priority_min | [man/](http://man7.org/linux/man-pages/man2/sched_get_priority_min.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_get_priority_min+package:^chromeos_public$) | 0x93 | int policy | - | - | - | - | - |
| 148 | sched_rr_get_interval | [man/](http://man7.org/linux/man-pages/man2/sched_rr_get_interval.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_rr_get_interval+package:^chromeos_public$) | 0x94 | pid\_t pid | struct timespec \*interval | - | - | - | - |
| 149 | mlock | [man/](http://man7.org/linux/man-pages/man2/mlock.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mlock+package:^chromeos_public$) | 0x95 | unsigned long start | size\_t len | - | - | - | - |
| 150 | munlock | [man/](http://man7.org/linux/man-pages/man2/munlock.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*munlock+package:^chromeos_public$) | 0x96 | unsigned long start | size\_t len | - | - | - | - |
| 151 | mlockall | [man/](http://man7.org/linux/man-pages/man2/mlockall.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mlockall+package:^chromeos_public$) | 0x97 | int flags | - | - | - | - | - |
| 152 | munlockall | [man/](http://man7.org/linux/man-pages/man2/munlockall.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*munlockall+package:^chromeos_public$) | 0x98 | - | - | - | - | - | - |
| 153 | vhangup | [man/](http://man7.org/linux/man-pages/man2/vhangup.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*vhangup+package:^chromeos_public$) | 0x99 | - | - | - | - | - | - |
| 154 | modify_ldt | [man/](http://man7.org/linux/man-pages/man2/modify_ldt.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*modify_ldt+package:^chromeos_public$) | 0x9a | ? | ? | ? | ? | ? | ? |
| 155 | pivot_root | [man/](http://man7.org/linux/man-pages/man2/pivot_root.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pivot_root+package:^chromeos_public$) | 0x9b | const char \*new\_root | const char \*put\_old | - | - | - | - |
| 156 | _sysctl | [man/](http://man7.org/linux/man-pages/man2/_sysctl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*_sysctl+package:^chromeos_public$) | 0x9c | ? | ? | ? | ? | ? | ? |
| 157 | prctl | [man/](http://man7.org/linux/man-pages/man2/prctl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*prctl+package:^chromeos_public$) | 0x9d | int option | unsigned long arg2 | unsigned long arg3 | unsigned long arg4 | unsigned long arg5 | - |
| 158 | arch_prctl | [man/](http://man7.org/linux/man-pages/man2/arch_prctl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*arch_prctl+package:^chromeos_public$) | 0x9e | ? | ? | ? | ? | ? | ? |
| 159 | adjtimex | [man/](http://man7.org/linux/man-pages/man2/adjtimex.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*adjtimex+package:^chromeos_public$) | 0x9f | struct timex \*txc\_p | - | - | - | - | - |
| 160 | setrlimit | [man/](http://man7.org/linux/man-pages/man2/setrlimit.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setrlimit+package:^chromeos_public$) | 0xa0 | unsigned int resource | struct rlimit \*rlim | - | - | - | - |
| 161 | chroot | [man/](http://man7.org/linux/man-pages/man2/chroot.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*chroot+package:^chromeos_public$) | 0xa1 | const char \*filename | - | - | - | - | - |
| 162 | sync | [man/](http://man7.org/linux/man-pages/man2/sync.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sync+package:^chromeos_public$) | 0xa2 | - | - | - | - | - | - |
| 163 | acct | [man/](http://man7.org/linux/man-pages/man2/acct.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*acct+package:^chromeos_public$) | 0xa3 | const char \*name | - | - | - | - | - |
| 164 | settimeofday | [man/](http://man7.org/linux/man-pages/man2/settimeofday.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*settimeofday+package:^chromeos_public$) | 0xa4 | struct timeval \*tv | struct timezone \*tz | - | - | - | - |
| 165 | mount | [man/](http://man7.org/linux/man-pages/man2/mount.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mount+package:^chromeos_public$) | 0xa5 | char \*dev\_name | char \*dir\_name | char \*type | unsigned long flags | void \*data | - |
| 166 | umount2 | [man/](http://man7.org/linux/man-pages/man2/umount2.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*umount2+package:^chromeos_public$) | 0xa6 | ? | ? | ? | ? | ? | ? |
| 167 | swapon | [man/](http://man7.org/linux/man-pages/man2/swapon.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*swapon+package:^chromeos_public$) | 0xa7 | const char \*specialfile | int swap\_flags | - | - | - | - |
| 168 | swapoff | [man/](http://man7.org/linux/man-pages/man2/swapoff.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*swapoff+package:^chromeos_public$) | 0xa8 | const char \*specialfile | - | - | - | - | - |
| 169 | reboot | [man/](http://man7.org/linux/man-pages/man2/reboot.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*reboot+package:^chromeos_public$) | 0xa9 | int magic1 | int magic2 | unsigned int cmd | void \*arg | - | - |
| 170 | sethostname | [man/](http://man7.org/linux/man-pages/man2/sethostname.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sethostname+package:^chromeos_public$) | 0xaa | char \*name | int len | - | - | - | - |
| 171 | setdomainname | [man/](http://man7.org/linux/man-pages/man2/setdomainname.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setdomainname+package:^chromeos_public$) | 0xab | char \*name | int len | - | - | - | - |
| 172 | iopl | [man/](http://man7.org/linux/man-pages/man2/iopl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*iopl+package:^chromeos_public$) | 0xac | ? | ? | ? | ? | ? | ? |
| 173 | ioperm | [man/](http://man7.org/linux/man-pages/man2/ioperm.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ioperm+package:^chromeos_public$) | 0xad | unsigned long from | unsigned long num | int on | - | - | - |
| 174 | create_module | [man/](http://man7.org/linux/man-pages/man2/create_module.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*create_module+package:^chromeos_public$) | 0xae | ? | ? | ? | ? | ? | ? |
| 175 | init_module | [man/](http://man7.org/linux/man-pages/man2/init_module.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*init_module+package:^chromeos_public$) | 0xaf | void \*umod | unsigned long len | const char \*uargs | - | - | - |
| 176 | delete_module | [man/](http://man7.org/linux/man-pages/man2/delete_module.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*delete_module+package:^chromeos_public$) | 0xb0 | const char \*name\_user | unsigned int flags | - | - | - | - |
| 177 | get_kernel_syms | [man/](http://man7.org/linux/man-pages/man2/get_kernel_syms.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*get_kernel_syms+package:^chromeos_public$) | 0xb1 | ? | ? | ? | ? | ? | ? |
| 178 | query_module | [man/](http://man7.org/linux/man-pages/man2/query_module.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*query_module+package:^chromeos_public$) | 0xb2 | ? | ? | ? | ? | ? | ? |
| 179 | quotactl | [man/](http://man7.org/linux/man-pages/man2/quotactl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*quotactl+package:^chromeos_public$) | 0xb3 | unsigned int cmd | const char \*special | qid\_t id | void \*addr | - | - |
| 180 | nfsservctl | [man/](http://man7.org/linux/man-pages/man2/nfsservctl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*nfsservctl+package:^chromeos_public$) | 0xb4 | ? | ? | ? | ? | ? | ? |
| 181 | getpmsg | [man/](http://man7.org/linux/man-pages/man2/getpmsg.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getpmsg+package:^chromeos_public$) | 0xb5 | ? | ? | ? | ? | ? | ? |
| 182 | putpmsg | [man/](http://man7.org/linux/man-pages/man2/putpmsg.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*putpmsg+package:^chromeos_public$) | 0xb6 | ? | ? | ? | ? | ? | ? |
| 183 | afs_syscall | [man/](http://man7.org/linux/man-pages/man2/afs_syscall.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*afs_syscall+package:^chromeos_public$) | 0xb7 | ? | ? | ? | ? | ? | ? |
| 184 | tuxcall | [man/](http://man7.org/linux/man-pages/man2/tuxcall.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*tuxcall+package:^chromeos_public$) | 0xb8 | ? | ? | ? | ? | ? | ? |
| 185 | security | [man/](http://man7.org/linux/man-pages/man2/security.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*security+package:^chromeos_public$) | 0xb9 | ? | ? | ? | ? | ? | ? |
| 186 | gettid | [man/](http://man7.org/linux/man-pages/man2/gettid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*gettid+package:^chromeos_public$) | 0xba | - | - | - | - | - | - |
| 187 | readahead | [man/](http://man7.org/linux/man-pages/man2/readahead.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*readahead+package:^chromeos_public$) | 0xbb | int fd | loff\_t offset | size\_t count | - | - | - |
| 188 | setxattr | [man/](http://man7.org/linux/man-pages/man2/setxattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setxattr+package:^chromeos_public$) | 0xbc | const char \*path | const char \*name | const void \*value | size\_t size | int flags | - |
| 189 | lsetxattr | [man/](http://man7.org/linux/man-pages/man2/lsetxattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*lsetxattr+package:^chromeos_public$) | 0xbd | const char \*path | const char \*name | const void \*value | size\_t size | int flags | - |
| 190 | fsetxattr | [man/](http://man7.org/linux/man-pages/man2/fsetxattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fsetxattr+package:^chromeos_public$) | 0xbe | int fd | const char \*name | const void \*value | size\_t size | int flags | - |
| 191 | getxattr | [man/](http://man7.org/linux/man-pages/man2/getxattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getxattr+package:^chromeos_public$) | 0xbf | const char \*path | const char \*name | void \*value | size\_t size | - | - |
| 192 | lgetxattr | [man/](http://man7.org/linux/man-pages/man2/lgetxattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*lgetxattr+package:^chromeos_public$) | 0xc0 | const char \*path | const char \*name | void \*value | size\_t size | - | - |
| 193 | fgetxattr | [man/](http://man7.org/linux/man-pages/man2/fgetxattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fgetxattr+package:^chromeos_public$) | 0xc1 | int fd | const char \*name | void \*value | size\_t size | - | - |
| 194 | listxattr | [man/](http://man7.org/linux/man-pages/man2/listxattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*listxattr+package:^chromeos_public$) | 0xc2 | const char \*path | char \*list | size\_t size | - | - | - |
| 195 | llistxattr | [man/](http://man7.org/linux/man-pages/man2/llistxattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*llistxattr+package:^chromeos_public$) | 0xc3 | const char \*path | char \*list | size\_t size | - | - | - |
| 196 | flistxattr | [man/](http://man7.org/linux/man-pages/man2/flistxattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*flistxattr+package:^chromeos_public$) | 0xc4 | int fd | char \*list | size\_t size | - | - | - |
| 197 | removexattr | [man/](http://man7.org/linux/man-pages/man2/removexattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*removexattr+package:^chromeos_public$) | 0xc5 | const char \*path | const char \*name | - | - | - | - |
| 198 | lremovexattr | [man/](http://man7.org/linux/man-pages/man2/lremovexattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*lremovexattr+package:^chromeos_public$) | 0xc6 | const char \*path | const char \*name | - | - | - | - |
| 199 | fremovexattr | [man/](http://man7.org/linux/man-pages/man2/fremovexattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fremovexattr+package:^chromeos_public$) | 0xc7 | int fd | const char \*name | - | - | - | - |
| 200 | tkill | [man/](http://man7.org/linux/man-pages/man2/tkill.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*tkill+package:^chromeos_public$) | 0xc8 | pid\_t pid | int sig | - | - | - | - |
| 201 | time | [man/](http://man7.org/linux/man-pages/man2/time.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*time+package:^chromeos_public$) | 0xc9 | time\_t \*tloc | - | - | - | - | - |
| 202 | futex | [man/](http://man7.org/linux/man-pages/man2/futex.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*futex+package:^chromeos_public$) | 0xca | u32 \*uaddr | int op | u32 val | struct timespec \*utime | u32 \*uaddr2 | u32 val3 |
| 203 | sched_setaffinity | [man/](http://man7.org/linux/man-pages/man2/sched_setaffinity.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_setaffinity+package:^chromeos_public$) | 0xcb | pid\_t pid | unsigned int len | unsigned long \*user\_mask\_ptr | - | - | - |
| 204 | sched_getaffinity | [man/](http://man7.org/linux/man-pages/man2/sched_getaffinity.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_getaffinity+package:^chromeos_public$) | 0xcc | pid\_t pid | unsigned int len | unsigned long \*user\_mask\_ptr | - | - | - |
| 205 | set_thread_area | [man/](http://man7.org/linux/man-pages/man2/set_thread_area.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*set_thread_area+package:^chromeos_public$) | 0xcd | ? | ? | ? | ? | ? | ? |
| 206 | io_setup | [man/](http://man7.org/linux/man-pages/man2/io_setup.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*io_setup+package:^chromeos_public$) | 0xce | unsigned nr\_reqs | aio\_context\_t \*ctx | - | - | - | - |
| 207 | io_destroy | [man/](http://man7.org/linux/man-pages/man2/io_destroy.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*io_destroy+package:^chromeos_public$) | 0xcf | aio\_context\_t ctx | - | - | - | - | - |
| 208 | io_getevents | [man/](http://man7.org/linux/man-pages/man2/io_getevents.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*io_getevents+package:^chromeos_public$) | 0xd0 | aio\_context\_t ctx\_id | long min\_nr | long nr | struct io\_event \*events | struct timespec \*timeout | - |
| 209 | io_submit | [man/](http://man7.org/linux/man-pages/man2/io_submit.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*io_submit+package:^chromeos_public$) | 0xd1 | aio\_context\_t | long | struct iocb \* \* | - | - | - |
| 210 | io_cancel | [man/](http://man7.org/linux/man-pages/man2/io_cancel.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*io_cancel+package:^chromeos_public$) | 0xd2 | aio\_context\_t ctx\_id | struct iocb \*iocb | struct io\_event \*result | - | - | - |
| 211 | get_thread_area | [man/](http://man7.org/linux/man-pages/man2/get_thread_area.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*get_thread_area+package:^chromeos_public$) | 0xd3 | ? | ? | ? | ? | ? | ? |
| 212 | lookup_dcookie | [man/](http://man7.org/linux/man-pages/man2/lookup_dcookie.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*lookup_dcookie+package:^chromeos_public$) | 0xd4 | u64 cookie64 | char \*buf | size\_t len | - | - | - |
| 213 | epoll_create | [man/](http://man7.org/linux/man-pages/man2/epoll_create.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*epoll_create+package:^chromeos_public$) | 0xd5 | int size | - | - | - | - | - |
| 214 | epoll_ctl_old | [man/](http://man7.org/linux/man-pages/man2/epoll_ctl_old.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*epoll_ctl_old+package:^chromeos_public$) | 0xd6 | ? | ? | ? | ? | ? | ? |
| 215 | epoll_wait_old | [man/](http://man7.org/linux/man-pages/man2/epoll_wait_old.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*epoll_wait_old+package:^chromeos_public$) | 0xd7 | ? | ? | ? | ? | ? | ? |
| 216 | remap_file_pages | [man/](http://man7.org/linux/man-pages/man2/remap_file_pages.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*remap_file_pages+package:^chromeos_public$) | 0xd8 | unsigned long start | unsigned long size | unsigned long prot | unsigned long pgoff | unsigned long flags | - |
| 217 | getdents64 | [man/](http://man7.org/linux/man-pages/man2/getdents64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getdents64+package:^chromeos_public$) | 0xd9 | unsigned int fd | struct linux\_dirent64 \*dirent | unsigned int count | - | - | - |
| 218 | set_tid_address | [man/](http://man7.org/linux/man-pages/man2/set_tid_address.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*set_tid_address+package:^chromeos_public$) | 0xda | int \*tidptr | - | - | - | - | - |
| 219 | restart_syscall | [man/](http://man7.org/linux/man-pages/man2/restart_syscall.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*restart_syscall+package:^chromeos_public$) | 0xdb | - | - | - | - | - | - |
| 220 | semtimedop | [man/](http://man7.org/linux/man-pages/man2/semtimedop.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*semtimedop+package:^chromeos_public$) | 0xdc | int semid | struct sembuf \*sops | unsigned nsops | const struct \_\_kernel\_timespec \*timeout | - | - |
| 221 | fadvise64 | [man/](http://man7.org/linux/man-pages/man2/fadvise64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fadvise64+package:^chromeos_public$) | 0xdd | int fd | loff\_t offset | size\_t len | int advice | - | - |
| 222 | timer_create | [man/](http://man7.org/linux/man-pages/man2/timer_create.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*timer_create+package:^chromeos_public$) | 0xde | clockid\_t which\_clock | struct sigevent \*timer\_event\_spec | timer\_t \* created\_timer\_id | - | - | - |
| 223 | timer_settime | [man/](http://man7.org/linux/man-pages/man2/timer_settime.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*timer_settime+package:^chromeos_public$) | 0xdf | timer\_t timer\_id | int flags | const struct \_\_kernel\_itimerspec \*new\_setting | struct itimerspec \*old\_setting | - | - |
| 224 | timer_gettime | [man/](http://man7.org/linux/man-pages/man2/timer_gettime.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*timer_gettime+package:^chromeos_public$) | 0xe0 | timer\_t timer\_id | struct \_\_kernel\_itimerspec \*setting | - | - | - | - |
| 225 | timer_getoverrun | [man/](http://man7.org/linux/man-pages/man2/timer_getoverrun.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*timer_getoverrun+package:^chromeos_public$) | 0xe1 | timer\_t timer\_id | - | - | - | - | - |
| 226 | timer_delete | [man/](http://man7.org/linux/man-pages/man2/timer_delete.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*timer_delete+package:^chromeos_public$) | 0xe2 | timer\_t timer\_id | - | - | - | - | - |
| 227 | clock_settime | [man/](http://man7.org/linux/man-pages/man2/clock_settime.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*clock_settime+package:^chromeos_public$) | 0xe3 | clockid\_t which\_clock | const struct \_\_kernel\_timespec \*tp | - | - | - | - |
| 228 | clock_gettime | [man/](http://man7.org/linux/man-pages/man2/clock_gettime.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*clock_gettime+package:^chromeos_public$) | 0xe4 | clockid\_t which\_clock | struct \_\_kernel\_timespec \*tp | - | - | - | - |
| 229 | clock_getres | [man/](http://man7.org/linux/man-pages/man2/clock_getres.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*clock_getres+package:^chromeos_public$) | 0xe5 | clockid\_t which\_clock | struct \_\_kernel\_timespec \*tp | - | - | - | - |
| 230 | clock_nanosleep | [man/](http://man7.org/linux/man-pages/man2/clock_nanosleep.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*clock_nanosleep+package:^chromeos_public$) | 0xe6 | clockid\_t which\_clock | int flags | const struct \_\_kernel\_timespec \*rqtp | struct \_\_kernel\_timespec \*rmtp | - | - |
| 231 | exit_group | [man/](http://man7.org/linux/man-pages/man2/exit_group.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*exit_group+package:^chromeos_public$) | 0xe7 | int error\_code | - | - | - | - | - |
| 232 | epoll_wait | [man/](http://man7.org/linux/man-pages/man2/epoll_wait.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*epoll_wait+package:^chromeos_public$) | 0xe8 | int epfd | struct epoll\_event \*events | int maxevents | int timeout | - | - |
| 233 | epoll_ctl | [man/](http://man7.org/linux/man-pages/man2/epoll_ctl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*epoll_ctl+package:^chromeos_public$) | 0xe9 | int epfd | int op | int fd | struct epoll\_event \*event | - | - |
| 234 | tgkill | [man/](http://man7.org/linux/man-pages/man2/tgkill.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*tgkill+package:^chromeos_public$) | 0xea | pid\_t tgid | pid\_t pid | int sig | - | - | - |
| 235 | utimes | [man/](http://man7.org/linux/man-pages/man2/utimes.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*utimes+package:^chromeos_public$) | 0xeb | char \*filename | struct timeval \*utimes | - | - | - | - |
| 236 | vserver | [man/](http://man7.org/linux/man-pages/man2/vserver.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*vserver+package:^chromeos_public$) | 0xec | ? | ? | ? | ? | ? | ? |
| 237 | mbind | [man/](http://man7.org/linux/man-pages/man2/mbind.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mbind+package:^chromeos_public$) | 0xed | unsigned long start | unsigned long len | unsigned long mode | const unsigned long \*nmask | unsigned long maxnode | unsigned flags |
| 238 | set_mempolicy | [man/](http://man7.org/linux/man-pages/man2/set_mempolicy.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*set_mempolicy+package:^chromeos_public$) | 0xee | int mode | const unsigned long \*nmask | unsigned long maxnode | - | - | - |
| 239 | get_mempolicy | [man/](http://man7.org/linux/man-pages/man2/get_mempolicy.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*get_mempolicy+package:^chromeos_public$) | 0xef | int \*policy | unsigned long \*nmask | unsigned long maxnode | unsigned long addr | unsigned long flags | - |
| 240 | mq_open | [man/](http://man7.org/linux/man-pages/man2/mq_open.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mq_open+package:^chromeos_public$) | 0xf0 | const char \*name | int oflag | umode\_t mode | struct mq\_attr \*attr | - | - |
| 241 | mq_unlink | [man/](http://man7.org/linux/man-pages/man2/mq_unlink.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mq_unlink+package:^chromeos_public$) | 0xf1 | const char \*name | - | - | - | - | - |
| 242 | mq_timedsend | [man/](http://man7.org/linux/man-pages/man2/mq_timedsend.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mq_timedsend+package:^chromeos_public$) | 0xf2 | mqd\_t mqdes | const char \*msg\_ptr | size\_t msg\_len | unsigned int msg\_prio | const struct \_\_kernel\_timespec \*abs\_timeout | - |
| 243 | mq_timedreceive | [man/](http://man7.org/linux/man-pages/man2/mq_timedreceive.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mq_timedreceive+package:^chromeos_public$) | 0xf3 | mqd\_t mqdes | char \*msg\_ptr | size\_t msg\_len | unsigned int \*msg\_prio | const struct \_\_kernel\_timespec \*abs\_timeout | - |
| 244 | mq_notify | [man/](http://man7.org/linux/man-pages/man2/mq_notify.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mq_notify+package:^chromeos_public$) | 0xf4 | mqd\_t mqdes | const struct sigevent \*notification | - | - | - | - |
| 245 | mq_getsetattr | [man/](http://man7.org/linux/man-pages/man2/mq_getsetattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mq_getsetattr+package:^chromeos_public$) | 0xf5 | mqd\_t mqdes | const struct mq\_attr \*mqstat | struct mq\_attr \*omqstat | - | - | - |
| 246 | kexec_load | [man/](http://man7.org/linux/man-pages/man2/kexec_load.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*kexec_load+package:^chromeos_public$) | 0xf6 | unsigned long entry | unsigned long nr\_segments | struct kexec\_segment \*segments | unsigned long flags | - | - |
| 247 | waitid | [man/](http://man7.org/linux/man-pages/man2/waitid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*waitid+package:^chromeos_public$) | 0xf7 | int which | pid\_t pid | struct siginfo \*infop | int options | struct rusage \*ru | - |
| 248 | add_key | [man/](http://man7.org/linux/man-pages/man2/add_key.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*add_key+package:^chromeos_public$) | 0xf8 | const char \*\_type | const char \*\_description | const void \*\_payload | size\_t plen | key\_serial\_t destringid | - |
| 249 | request_key | [man/](http://man7.org/linux/man-pages/man2/request_key.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*request_key+package:^chromeos_public$) | 0xf9 | const char \*\_type | const char \*\_description | const char \*\_callout\_info | key\_serial\_t destringid | - | - |
| 250 | keyctl | [man/](http://man7.org/linux/man-pages/man2/keyctl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*keyctl+package:^chromeos_public$) | 0xfa | int cmd | unsigned long arg2 | unsigned long arg3 | unsigned long arg4 | unsigned long arg5 | - |
| 251 | ioprio_set | [man/](http://man7.org/linux/man-pages/man2/ioprio_set.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ioprio_set+package:^chromeos_public$) | 0xfb | int which | int who | int ioprio | - | - | - |
| 252 | ioprio_get | [man/](http://man7.org/linux/man-pages/man2/ioprio_get.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ioprio_get+package:^chromeos_public$) | 0xfc | int which | int who | - | - | - | - |
| 253 | inotify_init | [man/](http://man7.org/linux/man-pages/man2/inotify_init.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*inotify_init+package:^chromeos_public$) | 0xfd | - | - | - | - | - | - |
| 254 | inotify_add_watch | [man/](http://man7.org/linux/man-pages/man2/inotify_add_watch.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*inotify_add_watch+package:^chromeos_public$) | 0xfe | int fd | const char \*path | u32 mask | - | - | - |
| 255 | inotify_rm_watch | [man/](http://man7.org/linux/man-pages/man2/inotify_rm_watch.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*inotify_rm_watch+package:^chromeos_public$) | 0xff | int fd | \_\_s32 wd | - | - | - | - |
| 256 | migrate_pages | [man/](http://man7.org/linux/man-pages/man2/migrate_pages.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*migrate_pages+package:^chromeos_public$) | 0x100 | pid\_t pid | unsigned long maxnode | const unsigned long \*from | const unsigned long \*to | - | - |
| 257 | openat | [man/](http://man7.org/linux/man-pages/man2/openat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*openat+package:^chromeos_public$) | 0x101 | int dfd | const char \*filename | int flags | umode\_t mode | - | - |
| 258 | mkdirat | [man/](http://man7.org/linux/man-pages/man2/mkdirat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mkdirat+package:^chromeos_public$) | 0x102 | int dfd | const char \* pathname | umode\_t mode | - | - | - |
| 259 | mknodat | [man/](http://man7.org/linux/man-pages/man2/mknodat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mknodat+package:^chromeos_public$) | 0x103 | int dfd | const char \* filename | umode\_t mode | unsigned dev | - | - |
| 260 | fchownat | [man/](http://man7.org/linux/man-pages/man2/fchownat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fchownat+package:^chromeos_public$) | 0x104 | int dfd | const char \*filename | uid\_t user | gid\_t group | int flag | - |
| 261 | futimesat | [man/](http://man7.org/linux/man-pages/man2/futimesat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*futimesat+package:^chromeos_public$) | 0x105 | int dfd | const char \*filename | struct timeval \*utimes | - | - | - |
| 262 | newfstatat | [man/](http://man7.org/linux/man-pages/man2/newfstatat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*newfstatat+package:^chromeos_public$) | 0x106 | int dfd | const char \*filename | struct stat \*statbuf | int flag | - | - |
| 263 | unlinkat | [man/](http://man7.org/linux/man-pages/man2/unlinkat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*unlinkat+package:^chromeos_public$) | 0x107 | int dfd | const char \* pathname | int flag | - | - | - |
| 264 | renameat | [man/](http://man7.org/linux/man-pages/man2/renameat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*renameat+package:^chromeos_public$) | 0x108 | int olddfd | const char \* oldname | int newdfd | const char \* newname | - | - |
| 265 | linkat | [man/](http://man7.org/linux/man-pages/man2/linkat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*linkat+package:^chromeos_public$) | 0x109 | int olddfd | const char \*oldname | int newdfd | const char \*newname | int flags | - |
| 266 | symlinkat | [man/](http://man7.org/linux/man-pages/man2/symlinkat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*symlinkat+package:^chromeos_public$) | 0x10a | const char \* oldname | int newdfd | const char \* newname | - | - | - |
| 267 | readlinkat | [man/](http://man7.org/linux/man-pages/man2/readlinkat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*readlinkat+package:^chromeos_public$) | 0x10b | int dfd | const char \*path | char \*buf | int bufsiz | - | - |
| 268 | fchmodat | [man/](http://man7.org/linux/man-pages/man2/fchmodat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fchmodat+package:^chromeos_public$) | 0x10c | int dfd | const char \* filename | umode\_t mode | - | - | - |
| 269 | faccessat | [man/](http://man7.org/linux/man-pages/man2/faccessat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*faccessat+package:^chromeos_public$) | 0x10d | int dfd | const char \*filename | int mode | - | - | - |
| 270 | pselect6 | [man/](http://man7.org/linux/man-pages/man2/pselect6.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pselect6+package:^chromeos_public$) | 0x10e | int | fd\_set \* | fd\_set \* | fd\_set \* | struct timespec \* | void \* |
| 271 | ppoll | [man/](http://man7.org/linux/man-pages/man2/ppoll.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ppoll+package:^chromeos_public$) | 0x10f | struct pollfd \* | unsigned int | struct timespec \* | const sigset\_t \* | size\_t | - |
| 272 | unshare | [man/](http://man7.org/linux/man-pages/man2/unshare.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*unshare+package:^chromeos_public$) | 0x110 | unsigned long unshare\_flags | - | - | - | - | - |
| 273 | set_robust_list | [man/](http://man7.org/linux/man-pages/man2/set_robust_list.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*set_robust_list+package:^chromeos_public$) | 0x111 | struct robust\_list\_head \*head | size\_t len | - | - | - | - |
| 274 | get_robust_list | [man/](http://man7.org/linux/man-pages/man2/get_robust_list.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*get_robust_list+package:^chromeos_public$) | 0x112 | int pid | struct robust\_list\_head \* \*head\_ptr | size\_t \*len\_ptr | - | - | - |
| 275 | splice | [man/](http://man7.org/linux/man-pages/man2/splice.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*splice+package:^chromeos_public$) | 0x113 | int fd\_in | loff\_t \*off\_in | int fd\_out | loff\_t \*off\_out | size\_t len | unsigned int flags |
| 276 | tee | [man/](http://man7.org/linux/man-pages/man2/tee.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*tee+package:^chromeos_public$) | 0x114 | int fdin | int fdout | size\_t len | unsigned int flags | - | - |
| 277 | sync_file_range | [man/](http://man7.org/linux/man-pages/man2/sync_file_range.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sync_file_range+package:^chromeos_public$) | 0x115 | int fd | loff\_t offset | loff\_t nbytes | unsigned int flags | - | - |
| 278 | vmsplice | [man/](http://man7.org/linux/man-pages/man2/vmsplice.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*vmsplice+package:^chromeos_public$) | 0x116 | int fd | const struct iovec \*iov | unsigned long nr\_segs | unsigned int flags | - | - |
| 279 | move_pages | [man/](http://man7.org/linux/man-pages/man2/move_pages.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*move_pages+package:^chromeos_public$) | 0x117 | pid\_t pid | unsigned long nr\_pages | const void \* \*pages | const int \*nodes | int \*status | int flags |
| 280 | utimensat | [man/](http://man7.org/linux/man-pages/man2/utimensat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*utimensat+package:^chromeos_public$) | 0x118 | int dfd | const char \*filename | struct timespec \*utimes | int flags | - | - |
| 281 | epoll_pwait | [man/](http://man7.org/linux/man-pages/man2/epoll_pwait.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*epoll_pwait+package:^chromeos_public$) | 0x119 | int epfd | struct epoll\_event \*events | int maxevents | int timeout | const sigset\_t \*sigmask | size\_t sigsetsize |
| 282 | signalfd | [man/](http://man7.org/linux/man-pages/man2/signalfd.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*signalfd+package:^chromeos_public$) | 0x11a | int ufd | sigset\_t \*user\_mask | size\_t sizemask | - | - | - |
| 283 | timerfd_create | [man/](http://man7.org/linux/man-pages/man2/timerfd_create.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*timerfd_create+package:^chromeos_public$) | 0x11b | int clockid | int flags | - | - | - | - |
| 284 | eventfd | [man/](http://man7.org/linux/man-pages/man2/eventfd.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*eventfd+package:^chromeos_public$) | 0x11c | unsigned int count | - | - | - | - | - |
| 285 | fallocate | [man/](http://man7.org/linux/man-pages/man2/fallocate.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fallocate+package:^chromeos_public$) | 0x11d | int fd | int mode | loff\_t offset | loff\_t len | - | - |
| 286 | timerfd_settime | [man/](http://man7.org/linux/man-pages/man2/timerfd_settime.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*timerfd_settime+package:^chromeos_public$) | 0x11e | int ufd | int flags | const struct \_\_kernel\_itimerspec \*utmr | struct \_\_kernel\_itimerspec \*otmr | - | - |
| 287 | timerfd_gettime | [man/](http://man7.org/linux/man-pages/man2/timerfd_gettime.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*timerfd_gettime+package:^chromeos_public$) | 0x11f | int ufd | struct \_\_kernel\_itimerspec \*otmr | - | - | - | - |
| 288 | accept4 | [man/](http://man7.org/linux/man-pages/man2/accept4.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*accept4+package:^chromeos_public$) | 0x120 | int | struct sockaddr \* | int \* | int | - | - |
| 289 | signalfd4 | [man/](http://man7.org/linux/man-pages/man2/signalfd4.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*signalfd4+package:^chromeos_public$) | 0x121 | int ufd | sigset\_t \*user\_mask | size\_t sizemask | int flags | - | - |
| 290 | eventfd2 | [man/](http://man7.org/linux/man-pages/man2/eventfd2.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*eventfd2+package:^chromeos_public$) | 0x122 | unsigned int count | int flags | - | - | - | - |
| 291 | epoll_create1 | [man/](http://man7.org/linux/man-pages/man2/epoll_create1.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*epoll_create1+package:^chromeos_public$) | 0x123 | int flags | - | - | - | - | - |
| 292 | dup3 | [man/](http://man7.org/linux/man-pages/man2/dup3.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*dup3+package:^chromeos_public$) | 0x124 | unsigned int oldfd | unsigned int newfd | int flags | - | - | - |
| 293 | pipe2 | [man/](http://man7.org/linux/man-pages/man2/pipe2.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pipe2+package:^chromeos_public$) | 0x125 | int \*fildes | int flags | - | - | - | - |
| 294 | inotify_init1 | [man/](http://man7.org/linux/man-pages/man2/inotify_init1.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*inotify_init1+package:^chromeos_public$) | 0x126 | int flags | - | - | - | - | - |
| 295 | preadv | [man/](http://man7.org/linux/man-pages/man2/preadv.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*preadv+package:^chromeos_public$) | 0x127 | unsigned long fd | const struct iovec \*vec | unsigned long vlen | unsigned long pos\_l | unsigned long pos\_h | - |
| 296 | pwritev | [man/](http://man7.org/linux/man-pages/man2/pwritev.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pwritev+package:^chromeos_public$) | 0x128 | unsigned long fd | const struct iovec \*vec | unsigned long vlen | unsigned long pos\_l | unsigned long pos\_h | - |
| 297 | rt_tgsigqueueinfo | [man/](http://man7.org/linux/man-pages/man2/rt_tgsigqueueinfo.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rt_tgsigqueueinfo+package:^chromeos_public$) | 0x129 | pid\_t tgid | pid\_t pid | int sig | siginfo\_t \*uinfo | - | - |
| 298 | perf_event_open | [man/](http://man7.org/linux/man-pages/man2/perf_event_open.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*perf_event_open+package:^chromeos_public$) | 0x12a | struct perf\_event\_attr \*attr\_uptr | pid\_t pid | int cpu | int group\_fd | unsigned long flags | - |
| 299 | recvmmsg | [man/](http://man7.org/linux/man-pages/man2/recvmmsg.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*recvmmsg+package:^chromeos_public$) | 0x12b | int fd | struct mmsghdr \*msg | unsigned int vlen | unsigned flags | struct timespec \*timeout | - |
| 300 | fanotify_init | [man/](http://man7.org/linux/man-pages/man2/fanotify_init.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fanotify_init+package:^chromeos_public$) | 0x12c | unsigned int flags | unsigned int event\_f\_flags | - | - | - | - |
| 301 | fanotify_mark | [man/](http://man7.org/linux/man-pages/man2/fanotify_mark.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fanotify_mark+package:^chromeos_public$) | 0x12d | int fanotify\_fd | unsigned int flags | u64 mask | int fd | const char \*pathname | - |
| 302 | prlimit64 | [man/](http://man7.org/linux/man-pages/man2/prlimit64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*prlimit64+package:^chromeos_public$) | 0x12e | pid\_t pid | unsigned int resource | const struct rlimit64 \*new\_rlim | struct rlimit64 \*old\_rlim | - | - |
| 303 | name_to_handle_at | [man/](http://man7.org/linux/man-pages/man2/name_to_handle_at.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*name_to_handle_at+package:^chromeos_public$) | 0x12f | int dfd | const char \*name | struct file\_handle \*handle | int \*mnt\_id | int flag | - |
| 304 | open_by_handle_at | [man/](http://man7.org/linux/man-pages/man2/open_by_handle_at.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*open_by_handle_at+package:^chromeos_public$) | 0x130 | int mountdirfd | struct file\_handle \*handle | int flags | - | - | - |
| 305 | clock_adjtime | [man/](http://man7.org/linux/man-pages/man2/clock_adjtime.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*clock_adjtime+package:^chromeos_public$) | 0x131 | clockid\_t which\_clock | struct timex \*tx | - | - | - | - |
| 306 | syncfs | [man/](http://man7.org/linux/man-pages/man2/syncfs.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*syncfs+package:^chromeos_public$) | 0x132 | int fd | - | - | - | - | - |
| 307 | sendmmsg | [man/](http://man7.org/linux/man-pages/man2/sendmmsg.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sendmmsg+package:^chromeos_public$) | 0x133 | int fd | struct mmsghdr \*msg | unsigned int vlen | unsigned flags | - | - |
| 308 | setns | [man/](http://man7.org/linux/man-pages/man2/setns.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setns+package:^chromeos_public$) | 0x134 | int fd | int nstype | - | - | - | - |
| 309 | getcpu | [man/](http://man7.org/linux/man-pages/man2/getcpu.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getcpu+package:^chromeos_public$) | 0x135 | unsigned \*cpu | unsigned \*node | struct getcpu\_cache \*cache | - | - | - |
| 310 | process_vm_readv | [man/](http://man7.org/linux/man-pages/man2/process_vm_readv.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*process_vm_readv+package:^chromeos_public$) | 0x136 | pid\_t pid | const struct iovec \*lvec | unsigned long liovcnt | const struct iovec \*rvec | unsigned long riovcnt | unsigned long flags |
| 311 | process_vm_writev | [man/](http://man7.org/linux/man-pages/man2/process_vm_writev.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*process_vm_writev+package:^chromeos_public$) | 0x137 | pid\_t pid | const struct iovec \*lvec | unsigned long liovcnt | const struct iovec \*rvec | unsigned long riovcnt | unsigned long flags |
| 312 | kcmp | [man/](http://man7.org/linux/man-pages/man2/kcmp.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*kcmp+package:^chromeos_public$) | 0x138 | pid\_t pid1 | pid\_t pid2 | int type | unsigned long idx1 | unsigned long idx2 | - |
| 313 | finit_module | [man/](http://man7.org/linux/man-pages/man2/finit_module.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*finit_module+package:^chromeos_public$) | 0x139 | int fd | const char \*uargs | int flags | - | - | - |
| 314 | sched_setattr | [man/](http://man7.org/linux/man-pages/man2/sched_setattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_setattr+package:^chromeos_public$) | 0x13a | pid\_t pid | struct sched\_attr \*attr | unsigned int flags | - | - | - |
| 315 | sched_getattr | [man/](http://man7.org/linux/man-pages/man2/sched_getattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_getattr+package:^chromeos_public$) | 0x13b | pid\_t pid | struct sched\_attr \*attr | unsigned int size | unsigned int flags | - | - |
| 316 | renameat2 | [man/](http://man7.org/linux/man-pages/man2/renameat2.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*renameat2+package:^chromeos_public$) | 0x13c | int olddfd | const char \*oldname | int newdfd | const char \*newname | unsigned int flags | - |
| 317 | seccomp | [man/](http://man7.org/linux/man-pages/man2/seccomp.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*seccomp+package:^chromeos_public$) | 0x13d | unsigned int op | unsigned int flags | const char \*uargs | - | - | - |
| 318 | getrandom | [man/](http://man7.org/linux/man-pages/man2/getrandom.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getrandom+package:^chromeos_public$) | 0x13e | char \*buf | size\_t count | unsigned int flags | - | - | - |
| 319 | memfd_create | [man/](http://man7.org/linux/man-pages/man2/memfd_create.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*memfd_create+package:^chromeos_public$) | 0x13f | const char \*uname\_ptr | unsigned int flags | - | - | - | - |
| 320 | kexec_file_load | [man/](http://man7.org/linux/man-pages/man2/kexec_file_load.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*kexec_file_load+package:^chromeos_public$) | 0x140 | int kernel\_fd | int initrd\_fd | unsigned long cmdline\_len | const char \*cmdline\_ptr | unsigned long flags | - |
| 321 | bpf | [man/](http://man7.org/linux/man-pages/man2/bpf.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*bpf+package:^chromeos_public$) | 0x141 | int cmd | union bpf\_attr \*attr | unsigned int size | - | - | - |
| 322 | execveat | [man/](http://man7.org/linux/man-pages/man2/execveat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*execveat+package:^chromeos_public$) | 0x142 | int dfd | const char \*filename | const char \*const \*argv | const char \*const \*envp | int flags | - |
| 323 | userfaultfd | [man/](http://man7.org/linux/man-pages/man2/userfaultfd.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*userfaultfd+package:^chromeos_public$) | 0x143 | int flags | - | - | - | - | - |
| 324 | membarrier | [man/](http://man7.org/linux/man-pages/man2/membarrier.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*membarrier+package:^chromeos_public$) | 0x144 | int cmd | int flags | - | - | - | - |
| 325 | mlock2 | [man/](http://man7.org/linux/man-pages/man2/mlock2.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mlock2+package:^chromeos_public$) | 0x145 | unsigned long start | size\_t len | int flags | - | - | - |
| 326 | copy_file_range | [man/](http://man7.org/linux/man-pages/man2/copy_file_range.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*copy_file_range+package:^chromeos_public$) | 0x146 | int fd\_in | loff\_t \*off\_in | int fd\_out | loff\_t \*off\_out | size\_t len | unsigned int flags |
| 327 | preadv2 | [man/](http://man7.org/linux/man-pages/man2/preadv2.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*preadv2+package:^chromeos_public$) | 0x147 | unsigned long fd | const struct iovec \*vec | unsigned long vlen | unsigned long pos\_l | unsigned long pos\_h | rwf\_t flags |
| 328 | pwritev2 | [man/](http://man7.org/linux/man-pages/man2/pwritev2.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pwritev2+package:^chromeos_public$) | 0x148 | unsigned long fd | const struct iovec \*vec | unsigned long vlen | unsigned long pos\_l | unsigned long pos\_h | rwf\_t flags |
| 329 | pkey_mprotect | [man/](http://man7.org/linux/man-pages/man2/pkey_mprotect.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pkey_mprotect+package:^chromeos_public$) | 0x149 | unsigned long start | size\_t len | unsigned long prot | int pkey | - | - |
| 330 | pkey_alloc | [man/](http://man7.org/linux/man-pages/man2/pkey_alloc.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pkey_alloc+package:^chromeos_public$) | 0x14a | unsigned long flags | unsigned long init\_val | - | - | - | - |
| 331 | pkey_free | [man/](http://man7.org/linux/man-pages/man2/pkey_free.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pkey_free+package:^chromeos_public$) | 0x14b | int pkey | - | - | - | - | - |
| 332 | statx | [man/](http://man7.org/linux/man-pages/man2/statx.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*statx+package:^chromeos_public$) | 0x14c | int dfd | const char \*path | unsigned flags | unsigned mask | struct statx \*buffer | - |

### arm (32-bit/EABI)

Compiled from [Linux 4.14.0 headers][linux-headers].

| NR | syscall name | references | %r7 | arg0 (%r0) | arg1 (%r1) | arg2 (%r2) | arg3 (%r3) | arg4 (%r4) | arg5 (%r5) |
|:---:|---|:---:|:---:|---|---|---|---|---|---|
| 0 | restart_syscall | [man/](http://man7.org/linux/man-pages/man2/restart_syscall.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*restart_syscall+package:^chromeos_public$) | 0x00 | - | - | - | - | - | - |
| 1 | exit | [man/](http://man7.org/linux/man-pages/man2/exit.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*exit+package:^chromeos_public$) | 0x01 | int error\_code | - | - | - | - | - |
| 2 | fork | [man/](http://man7.org/linux/man-pages/man2/fork.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fork+package:^chromeos_public$) | 0x02 | - | - | - | - | - | - |
| 3 | read | [man/](http://man7.org/linux/man-pages/man2/read.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*read+package:^chromeos_public$) | 0x03 | unsigned int fd | char \*buf | size\_t count | - | - | - |
| 4 | write | [man/](http://man7.org/linux/man-pages/man2/write.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*write+package:^chromeos_public$) | 0x04 | unsigned int fd | const char \*buf | size\_t count | - | - | - |
| 5 | open | [man/](http://man7.org/linux/man-pages/man2/open.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*open+package:^chromeos_public$) | 0x05 | const char \*filename | int flags | umode\_t mode | - | - | - |
| 6 | close | [man/](http://man7.org/linux/man-pages/man2/close.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*close+package:^chromeos_public$) | 0x06 | unsigned int fd | - | - | - | - | - |
| 7 | *not implemented* | | 0x07 ||
| 8 | creat | [man/](http://man7.org/linux/man-pages/man2/creat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*creat+package:^chromeos_public$) | 0x08 | const char \*pathname | umode\_t mode | - | - | - | - |
| 9 | link | [man/](http://man7.org/linux/man-pages/man2/link.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*link+package:^chromeos_public$) | 0x09 | const char \*oldname | const char \*newname | - | - | - | - |
| 10 | unlink | [man/](http://man7.org/linux/man-pages/man2/unlink.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*unlink+package:^chromeos_public$) | 0x0a | const char \*pathname | - | - | - | - | - |
| 11 | execve | [man/](http://man7.org/linux/man-pages/man2/execve.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*execve+package:^chromeos_public$) | 0x0b | const char \*filename | const char \*const \*argv | const char \*const \*envp | - | - | - |
| 12 | chdir | [man/](http://man7.org/linux/man-pages/man2/chdir.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*chdir+package:^chromeos_public$) | 0x0c | const char \*filename | - | - | - | - | - |
| 13 | *not implemented* | | 0x0d ||
| 14 | mknod | [man/](http://man7.org/linux/man-pages/man2/mknod.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mknod+package:^chromeos_public$) | 0x0e | const char \*filename | umode\_t mode | unsigned dev | - | - | - |
| 15 | chmod | [man/](http://man7.org/linux/man-pages/man2/chmod.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*chmod+package:^chromeos_public$) | 0x0f | const char \*filename | umode\_t mode | - | - | - | - |
| 16 | lchown | [man/](http://man7.org/linux/man-pages/man2/lchown.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*lchown+package:^chromeos_public$) | 0x10 | const char \*filename | uid\_t user | gid\_t group | - | - | - |
| 17 | *not implemented* | | 0x11 ||
| 18 | *not implemented* | | 0x12 ||
| 19 | lseek | [man/](http://man7.org/linux/man-pages/man2/lseek.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*lseek+package:^chromeos_public$) | 0x13 | unsigned int fd | off\_t offset | unsigned int whence | - | - | - |
| 20 | getpid | [man/](http://man7.org/linux/man-pages/man2/getpid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getpid+package:^chromeos_public$) | 0x14 | - | - | - | - | - | - |
| 21 | mount | [man/](http://man7.org/linux/man-pages/man2/mount.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mount+package:^chromeos_public$) | 0x15 | char \*dev\_name | char \*dir\_name | char \*type | unsigned long flags | void \*data | - |
| 22 | *not implemented* | | 0x16 ||
| 23 | setuid | [man/](http://man7.org/linux/man-pages/man2/setuid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setuid+package:^chromeos_public$) | 0x17 | uid\_t uid | - | - | - | - | - |
| 24 | getuid | [man/](http://man7.org/linux/man-pages/man2/getuid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getuid+package:^chromeos_public$) | 0x18 | - | - | - | - | - | - |
| 25 | *not implemented* | | 0x19 ||
| 26 | ptrace | [man/](http://man7.org/linux/man-pages/man2/ptrace.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ptrace+package:^chromeos_public$) | 0x1a | long request | long pid | unsigned long addr | unsigned long data | - | - |
| 27 | *not implemented* | | 0x1b ||
| 28 | *not implemented* | | 0x1c ||
| 29 | pause | [man/](http://man7.org/linux/man-pages/man2/pause.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pause+package:^chromeos_public$) | 0x1d | - | - | - | - | - | - |
| 30 | *not implemented* | | 0x1e ||
| 31 | *not implemented* | | 0x1f ||
| 32 | *not implemented* | | 0x20 ||
| 33 | access | [man/](http://man7.org/linux/man-pages/man2/access.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*access+package:^chromeos_public$) | 0x21 | const char \*filename | int mode | - | - | - | - |
| 34 | nice | [man/](http://man7.org/linux/man-pages/man2/nice.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*nice+package:^chromeos_public$) | 0x22 | int increment | - | - | - | - | - |
| 35 | *not implemented* | | 0x23 ||
| 36 | sync | [man/](http://man7.org/linux/man-pages/man2/sync.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sync+package:^chromeos_public$) | 0x24 | - | - | - | - | - | - |
| 37 | kill | [man/](http://man7.org/linux/man-pages/man2/kill.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*kill+package:^chromeos_public$) | 0x25 | pid\_t pid | int sig | - | - | - | - |
| 38 | rename | [man/](http://man7.org/linux/man-pages/man2/rename.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rename+package:^chromeos_public$) | 0x26 | const char \*oldname | const char \*newname | - | - | - | - |
| 39 | mkdir | [man/](http://man7.org/linux/man-pages/man2/mkdir.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mkdir+package:^chromeos_public$) | 0x27 | const char \*pathname | umode\_t mode | - | - | - | - |
| 40 | rmdir | [man/](http://man7.org/linux/man-pages/man2/rmdir.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rmdir+package:^chromeos_public$) | 0x28 | const char \*pathname | - | - | - | - | - |
| 41 | dup | [man/](http://man7.org/linux/man-pages/man2/dup.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*dup+package:^chromeos_public$) | 0x29 | unsigned int fildes | - | - | - | - | - |
| 42 | pipe | [man/](http://man7.org/linux/man-pages/man2/pipe.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pipe+package:^chromeos_public$) | 0x2a | int \*fildes | - | - | - | - | - |
| 43 | times | [man/](http://man7.org/linux/man-pages/man2/times.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*times+package:^chromeos_public$) | 0x2b | struct tms \*tbuf | - | - | - | - | - |
| 44 | *not implemented* | | 0x2c ||
| 45 | brk | [man/](http://man7.org/linux/man-pages/man2/brk.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*brk+package:^chromeos_public$) | 0x2d | unsigned long brk | - | - | - | - | - |
| 46 | setgid | [man/](http://man7.org/linux/man-pages/man2/setgid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setgid+package:^chromeos_public$) | 0x2e | gid\_t gid | - | - | - | - | - |
| 47 | getgid | [man/](http://man7.org/linux/man-pages/man2/getgid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getgid+package:^chromeos_public$) | 0x2f | - | - | - | - | - | - |
| 48 | *not implemented* | | 0x30 ||
| 49 | geteuid | [man/](http://man7.org/linux/man-pages/man2/geteuid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*geteuid+package:^chromeos_public$) | 0x31 | - | - | - | - | - | - |
| 50 | getegid | [man/](http://man7.org/linux/man-pages/man2/getegid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getegid+package:^chromeos_public$) | 0x32 | - | - | - | - | - | - |
| 51 | acct | [man/](http://man7.org/linux/man-pages/man2/acct.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*acct+package:^chromeos_public$) | 0x33 | const char \*name | - | - | - | - | - |
| 52 | umount2 | [man/](http://man7.org/linux/man-pages/man2/umount2.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*umount2+package:^chromeos_public$) | 0x34 | ? | ? | ? | ? | ? | ? |
| 53 | *not implemented* | | 0x35 ||
| 54 | ioctl | [man/](http://man7.org/linux/man-pages/man2/ioctl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ioctl+package:^chromeos_public$) | 0x36 | unsigned int fd | unsigned int cmd | unsigned long arg | - | - | - |
| 55 | fcntl | [man/](http://man7.org/linux/man-pages/man2/fcntl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fcntl+package:^chromeos_public$) | 0x37 | unsigned int fd | unsigned int cmd | unsigned long arg | - | - | - |
| 56 | *not implemented* | | 0x38 ||
| 57 | setpgid | [man/](http://man7.org/linux/man-pages/man2/setpgid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setpgid+package:^chromeos_public$) | 0x39 | pid\_t pid | pid\_t pgid | - | - | - | - |
| 58 | *not implemented* | | 0x3a ||
| 59 | *not implemented* | | 0x3b ||
| 60 | umask | [man/](http://man7.org/linux/man-pages/man2/umask.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*umask+package:^chromeos_public$) | 0x3c | int mask | - | - | - | - | - |
| 61 | chroot | [man/](http://man7.org/linux/man-pages/man2/chroot.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*chroot+package:^chromeos_public$) | 0x3d | const char \*filename | - | - | - | - | - |
| 62 | ustat | [man/](http://man7.org/linux/man-pages/man2/ustat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ustat+package:^chromeos_public$) | 0x3e | unsigned dev | struct ustat \*ubuf | - | - | - | - |
| 63 | dup2 | [man/](http://man7.org/linux/man-pages/man2/dup2.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*dup2+package:^chromeos_public$) | 0x3f | unsigned int oldfd | unsigned int newfd | - | - | - | - |
| 64 | getppid | [man/](http://man7.org/linux/man-pages/man2/getppid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getppid+package:^chromeos_public$) | 0x40 | - | - | - | - | - | - |
| 65 | getpgrp | [man/](http://man7.org/linux/man-pages/man2/getpgrp.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getpgrp+package:^chromeos_public$) | 0x41 | - | - | - | - | - | - |
| 66 | setsid | [man/](http://man7.org/linux/man-pages/man2/setsid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setsid+package:^chromeos_public$) | 0x42 | - | - | - | - | - | - |
| 67 | sigaction | [man/](http://man7.org/linux/man-pages/man2/sigaction.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sigaction+package:^chromeos_public$) | 0x43 | int | const struct old\_sigaction \* | struct old\_sigaction \* | - | - | - |
| 68 | *not implemented* | | 0x44 ||
| 69 | *not implemented* | | 0x45 ||
| 70 | setreuid | [man/](http://man7.org/linux/man-pages/man2/setreuid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setreuid+package:^chromeos_public$) | 0x46 | uid\_t ruid | uid\_t euid | - | - | - | - |
| 71 | setregid | [man/](http://man7.org/linux/man-pages/man2/setregid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setregid+package:^chromeos_public$) | 0x47 | gid\_t rgid | gid\_t egid | - | - | - | - |
| 72 | sigsuspend | [man/](http://man7.org/linux/man-pages/man2/sigsuspend.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sigsuspend+package:^chromeos_public$) | 0x48 | int unused1 | int unused2 | old\_sigset\_t mask | - | - | - |
| 73 | sigpending | [man/](http://man7.org/linux/man-pages/man2/sigpending.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sigpending+package:^chromeos_public$) | 0x49 | old\_sigset\_t \*uset | - | - | - | - | - |
| 74 | sethostname | [man/](http://man7.org/linux/man-pages/man2/sethostname.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sethostname+package:^chromeos_public$) | 0x4a | char \*name | int len | - | - | - | - |
| 75 | setrlimit | [man/](http://man7.org/linux/man-pages/man2/setrlimit.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setrlimit+package:^chromeos_public$) | 0x4b | unsigned int resource | struct rlimit \*rlim | - | - | - | - |
| 76 | *not implemented* | | 0x4c ||
| 77 | getrusage | [man/](http://man7.org/linux/man-pages/man2/getrusage.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getrusage+package:^chromeos_public$) | 0x4d | int who | struct rusage \*ru | - | - | - | - |
| 78 | gettimeofday | [man/](http://man7.org/linux/man-pages/man2/gettimeofday.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*gettimeofday+package:^chromeos_public$) | 0x4e | struct timeval \*tv | struct timezone \*tz | - | - | - | - |
| 79 | settimeofday | [man/](http://man7.org/linux/man-pages/man2/settimeofday.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*settimeofday+package:^chromeos_public$) | 0x4f | struct timeval \*tv | struct timezone \*tz | - | - | - | - |
| 80 | getgroups | [man/](http://man7.org/linux/man-pages/man2/getgroups.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getgroups+package:^chromeos_public$) | 0x50 | int gidsetsize | gid\_t \*grouplist | - | - | - | - |
| 81 | setgroups | [man/](http://man7.org/linux/man-pages/man2/setgroups.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setgroups+package:^chromeos_public$) | 0x51 | int gidsetsize | gid\_t \*grouplist | - | - | - | - |
| 82 | *not implemented* | | 0x52 ||
| 83 | symlink | [man/](http://man7.org/linux/man-pages/man2/symlink.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*symlink+package:^chromeos_public$) | 0x53 | const char \*old | const char \*new | - | - | - | - |
| 84 | *not implemented* | | 0x54 ||
| 85 | readlink | [man/](http://man7.org/linux/man-pages/man2/readlink.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*readlink+package:^chromeos_public$) | 0x55 | const char \*path | char \*buf | int bufsiz | - | - | - |
| 86 | uselib | [man/](http://man7.org/linux/man-pages/man2/uselib.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*uselib+package:^chromeos_public$) | 0x56 | const char \*library | - | - | - | - | - |
| 87 | swapon | [man/](http://man7.org/linux/man-pages/man2/swapon.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*swapon+package:^chromeos_public$) | 0x57 | const char \*specialfile | int swap\_flags | - | - | - | - |
| 88 | reboot | [man/](http://man7.org/linux/man-pages/man2/reboot.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*reboot+package:^chromeos_public$) | 0x58 | int magic1 | int magic2 | unsigned int cmd | void \*arg | - | - |
| 89 | *not implemented* | | 0x59 ||
| 90 | *not implemented* | | 0x5a ||
| 91 | munmap | [man/](http://man7.org/linux/man-pages/man2/munmap.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*munmap+package:^chromeos_public$) | 0x5b | unsigned long addr | size\_t len | - | - | - | - |
| 92 | truncate | [man/](http://man7.org/linux/man-pages/man2/truncate.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*truncate+package:^chromeos_public$) | 0x5c | const char \*path | long length | - | - | - | - |
| 93 | ftruncate | [man/](http://man7.org/linux/man-pages/man2/ftruncate.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ftruncate+package:^chromeos_public$) | 0x5d | unsigned int fd | unsigned long length | - | - | - | - |
| 94 | fchmod | [man/](http://man7.org/linux/man-pages/man2/fchmod.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fchmod+package:^chromeos_public$) | 0x5e | unsigned int fd | umode\_t mode | - | - | - | - |
| 95 | fchown | [man/](http://man7.org/linux/man-pages/man2/fchown.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fchown+package:^chromeos_public$) | 0x5f | unsigned int fd | uid\_t user | gid\_t group | - | - | - |
| 96 | getpriority | [man/](http://man7.org/linux/man-pages/man2/getpriority.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getpriority+package:^chromeos_public$) | 0x60 | int which | int who | - | - | - | - |
| 97 | setpriority | [man/](http://man7.org/linux/man-pages/man2/setpriority.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setpriority+package:^chromeos_public$) | 0x61 | int which | int who | int niceval | - | - | - |
| 98 | *not implemented* | | 0x62 ||
| 99 | statfs | [man/](http://man7.org/linux/man-pages/man2/statfs.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*statfs+package:^chromeos_public$) | 0x63 | const char \* path | struct statfs \*buf | - | - | - | - |
| 100 | fstatfs | [man/](http://man7.org/linux/man-pages/man2/fstatfs.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fstatfs+package:^chromeos_public$) | 0x64 | unsigned int fd | struct statfs \*buf | - | - | - | - |
| 101 | *not implemented* | | 0x65 ||
| 102 | *not implemented* | | 0x66 ||
| 103 | syslog | [man/](http://man7.org/linux/man-pages/man2/syslog.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*syslog+package:^chromeos_public$) | 0x67 | int type | char \*buf | int len | - | - | - |
| 104 | setitimer | [man/](http://man7.org/linux/man-pages/man2/setitimer.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setitimer+package:^chromeos_public$) | 0x68 | int which | struct itimerval \*value | struct itimerval \*ovalue | - | - | - |
| 105 | getitimer | [man/](http://man7.org/linux/man-pages/man2/getitimer.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getitimer+package:^chromeos_public$) | 0x69 | int which | struct itimerval \*value | - | - | - | - |
| 106 | stat | [man/](http://man7.org/linux/man-pages/man2/stat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*stat+package:^chromeos_public$) | 0x6a | const char \*filename | struct \_\_old\_kernel\_stat \*statbuf | - | - | - | - |
| 107 | lstat | [man/](http://man7.org/linux/man-pages/man2/lstat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*lstat+package:^chromeos_public$) | 0x6b | const char \*filename | struct \_\_old\_kernel\_stat \*statbuf | - | - | - | - |
| 108 | fstat | [man/](http://man7.org/linux/man-pages/man2/fstat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fstat+package:^chromeos_public$) | 0x6c | unsigned int fd | struct \_\_old\_kernel\_stat \*statbuf | - | - | - | - |
| 109 | *not implemented* | | 0x6d ||
| 110 | *not implemented* | | 0x6e ||
| 111 | vhangup | [man/](http://man7.org/linux/man-pages/man2/vhangup.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*vhangup+package:^chromeos_public$) | 0x6f | - | - | - | - | - | - |
| 112 | *not implemented* | | 0x70 ||
| 113 | *not implemented* | | 0x71 ||
| 114 | wait4 | [man/](http://man7.org/linux/man-pages/man2/wait4.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*wait4+package:^chromeos_public$) | 0x72 | pid\_t pid | int \*stat\_addr | int options | struct rusage \*ru | - | - |
| 115 | swapoff | [man/](http://man7.org/linux/man-pages/man2/swapoff.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*swapoff+package:^chromeos_public$) | 0x73 | const char \*specialfile | - | - | - | - | - |
| 116 | sysinfo | [man/](http://man7.org/linux/man-pages/man2/sysinfo.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sysinfo+package:^chromeos_public$) | 0x74 | struct sysinfo \*info | - | - | - | - | - |
| 117 | *not implemented* | | 0x75 ||
| 118 | fsync | [man/](http://man7.org/linux/man-pages/man2/fsync.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fsync+package:^chromeos_public$) | 0x76 | unsigned int fd | - | - | - | - | - |
| 119 | sigreturn | [man/](http://man7.org/linux/man-pages/man2/sigreturn.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sigreturn+package:^chromeos_public$) | 0x77 | ? | ? | ? | ? | ? | ? |
| 120 | clone | [man/](http://man7.org/linux/man-pages/man2/clone.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*clone+package:^chromeos_public$) | 0x78 | unsigned long | unsigned long | int \* | int \* | unsigned long | - |
| 121 | setdomainname | [man/](http://man7.org/linux/man-pages/man2/setdomainname.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setdomainname+package:^chromeos_public$) | 0x79 | char \*name | int len | - | - | - | - |
| 122 | uname | [man/](http://man7.org/linux/man-pages/man2/uname.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*uname+package:^chromeos_public$) | 0x7a | struct old\_utsname \* | - | - | - | - | - |
| 123 | *not implemented* | | 0x7b ||
| 124 | adjtimex | [man/](http://man7.org/linux/man-pages/man2/adjtimex.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*adjtimex+package:^chromeos_public$) | 0x7c | struct timex \*txc\_p | - | - | - | - | - |
| 125 | mprotect | [man/](http://man7.org/linux/man-pages/man2/mprotect.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mprotect+package:^chromeos_public$) | 0x7d | unsigned long start | size\_t len | unsigned long prot | - | - | - |
| 126 | sigprocmask | [man/](http://man7.org/linux/man-pages/man2/sigprocmask.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sigprocmask+package:^chromeos_public$) | 0x7e | int how | old\_sigset\_t \*set | old\_sigset\_t \*oset | - | - | - |
| 127 | *not implemented* | | 0x7f ||
| 128 | init_module | [man/](http://man7.org/linux/man-pages/man2/init_module.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*init_module+package:^chromeos_public$) | 0x80 | void \*umod | unsigned long len | const char \*uargs | - | - | - |
| 129 | delete_module | [man/](http://man7.org/linux/man-pages/man2/delete_module.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*delete_module+package:^chromeos_public$) | 0x81 | const char \*name\_user | unsigned int flags | - | - | - | - |
| 130 | *not implemented* | | 0x82 ||
| 131 | quotactl | [man/](http://man7.org/linux/man-pages/man2/quotactl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*quotactl+package:^chromeos_public$) | 0x83 | unsigned int cmd | const char \*special | qid\_t id | void \*addr | - | - |
| 132 | getpgid | [man/](http://man7.org/linux/man-pages/man2/getpgid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getpgid+package:^chromeos_public$) | 0x84 | pid\_t pid | - | - | - | - | - |
| 133 | fchdir | [man/](http://man7.org/linux/man-pages/man2/fchdir.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fchdir+package:^chromeos_public$) | 0x85 | unsigned int fd | - | - | - | - | - |
| 134 | bdflush | [man/](http://man7.org/linux/man-pages/man2/bdflush.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*bdflush+package:^chromeos_public$) | 0x86 | int func | long data | - | - | - | - |
| 135 | sysfs | [man/](http://man7.org/linux/man-pages/man2/sysfs.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sysfs+package:^chromeos_public$) | 0x87 | int option | unsigned long arg1 | unsigned long arg2 | - | - | - |
| 136 | personality | [man/](http://man7.org/linux/man-pages/man2/personality.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*personality+package:^chromeos_public$) | 0x88 | unsigned int personality | - | - | - | - | - |
| 137 | *not implemented* | | 0x89 ||
| 138 | setfsuid | [man/](http://man7.org/linux/man-pages/man2/setfsuid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setfsuid+package:^chromeos_public$) | 0x8a | uid\_t uid | - | - | - | - | - |
| 139 | setfsgid | [man/](http://man7.org/linux/man-pages/man2/setfsgid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setfsgid+package:^chromeos_public$) | 0x8b | gid\_t gid | - | - | - | - | - |
| 140 | _llseek | [man/](http://man7.org/linux/man-pages/man2/_llseek.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*_llseek+package:^chromeos_public$) | 0x8c | ? | ? | ? | ? | ? | ? |
| 141 | getdents | [man/](http://man7.org/linux/man-pages/man2/getdents.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getdents+package:^chromeos_public$) | 0x8d | unsigned int fd | struct linux\_dirent \*dirent | unsigned int count | - | - | - |
| 142 | _newselect | [man/](http://man7.org/linux/man-pages/man2/_newselect.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*_newselect+package:^chromeos_public$) | 0x8e | ? | ? | ? | ? | ? | ? |
| 143 | flock | [man/](http://man7.org/linux/man-pages/man2/flock.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*flock+package:^chromeos_public$) | 0x8f | unsigned int fd | unsigned int cmd | - | - | - | - |
| 144 | msync | [man/](http://man7.org/linux/man-pages/man2/msync.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*msync+package:^chromeos_public$) | 0x90 | unsigned long start | size\_t len | int flags | - | - | - |
| 145 | readv | [man/](http://man7.org/linux/man-pages/man2/readv.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*readv+package:^chromeos_public$) | 0x91 | unsigned long fd | const struct iovec \*vec | unsigned long vlen | - | - | - |
| 146 | writev | [man/](http://man7.org/linux/man-pages/man2/writev.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*writev+package:^chromeos_public$) | 0x92 | unsigned long fd | const struct iovec \*vec | unsigned long vlen | - | - | - |
| 147 | getsid | [man/](http://man7.org/linux/man-pages/man2/getsid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getsid+package:^chromeos_public$) | 0x93 | pid\_t pid | - | - | - | - | - |
| 148 | fdatasync | [man/](http://man7.org/linux/man-pages/man2/fdatasync.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fdatasync+package:^chromeos_public$) | 0x94 | unsigned int fd | - | - | - | - | - |
| 149 | _sysctl | [man/](http://man7.org/linux/man-pages/man2/_sysctl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*_sysctl+package:^chromeos_public$) | 0x95 | ? | ? | ? | ? | ? | ? |
| 150 | mlock | [man/](http://man7.org/linux/man-pages/man2/mlock.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mlock+package:^chromeos_public$) | 0x96 | unsigned long start | size\_t len | - | - | - | - |
| 151 | munlock | [man/](http://man7.org/linux/man-pages/man2/munlock.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*munlock+package:^chromeos_public$) | 0x97 | unsigned long start | size\_t len | - | - | - | - |
| 152 | mlockall | [man/](http://man7.org/linux/man-pages/man2/mlockall.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mlockall+package:^chromeos_public$) | 0x98 | int flags | - | - | - | - | - |
| 153 | munlockall | [man/](http://man7.org/linux/man-pages/man2/munlockall.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*munlockall+package:^chromeos_public$) | 0x99 | - | - | - | - | - | - |
| 154 | sched_setparam | [man/](http://man7.org/linux/man-pages/man2/sched_setparam.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_setparam+package:^chromeos_public$) | 0x9a | pid\_t pid | struct sched\_param \*param | - | - | - | - |
| 155 | sched_getparam | [man/](http://man7.org/linux/man-pages/man2/sched_getparam.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_getparam+package:^chromeos_public$) | 0x9b | pid\_t pid | struct sched\_param \*param | - | - | - | - |
| 156 | sched_setscheduler | [man/](http://man7.org/linux/man-pages/man2/sched_setscheduler.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_setscheduler+package:^chromeos_public$) | 0x9c | pid\_t pid | int policy | struct sched\_param \*param | - | - | - |
| 157 | sched_getscheduler | [man/](http://man7.org/linux/man-pages/man2/sched_getscheduler.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_getscheduler+package:^chromeos_public$) | 0x9d | pid\_t pid | - | - | - | - | - |
| 158 | sched_yield | [man/](http://man7.org/linux/man-pages/man2/sched_yield.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_yield+package:^chromeos_public$) | 0x9e | - | - | - | - | - | - |
| 159 | sched_get_priority_max | [man/](http://man7.org/linux/man-pages/man2/sched_get_priority_max.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_get_priority_max+package:^chromeos_public$) | 0x9f | int policy | - | - | - | - | - |
| 160 | sched_get_priority_min | [man/](http://man7.org/linux/man-pages/man2/sched_get_priority_min.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_get_priority_min+package:^chromeos_public$) | 0xa0 | int policy | - | - | - | - | - |
| 161 | sched_rr_get_interval | [man/](http://man7.org/linux/man-pages/man2/sched_rr_get_interval.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_rr_get_interval+package:^chromeos_public$) | 0xa1 | pid\_t pid | struct timespec \*interval | - | - | - | - |
| 162 | nanosleep | [man/](http://man7.org/linux/man-pages/man2/nanosleep.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*nanosleep+package:^chromeos_public$) | 0xa2 | struct \_\_kernel\_timespec \*rqtp | struct \_\_kernel\_timespec \*rmtp | - | - | - | - |
| 163 | mremap | [man/](http://man7.org/linux/man-pages/man2/mremap.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mremap+package:^chromeos_public$) | 0xa3 | unsigned long addr | unsigned long old\_len | unsigned long new\_len | unsigned long flags | unsigned long new\_addr | - |
| 164 | setresuid | [man/](http://man7.org/linux/man-pages/man2/setresuid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setresuid+package:^chromeos_public$) | 0xa4 | uid\_t ruid | uid\_t euid | uid\_t suid | - | - | - |
| 165 | getresuid | [man/](http://man7.org/linux/man-pages/man2/getresuid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getresuid+package:^chromeos_public$) | 0xa5 | uid\_t \*ruid | uid\_t \*euid | uid\_t \*suid | - | - | - |
| 166 | *not implemented* | | 0xa6 ||
| 167 | *not implemented* | | 0xa7 ||
| 168 | poll | [man/](http://man7.org/linux/man-pages/man2/poll.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*poll+package:^chromeos_public$) | 0xa8 | struct pollfd \*ufds | unsigned int nfds | int timeout | - | - | - |
| 169 | nfsservctl | [man/](http://man7.org/linux/man-pages/man2/nfsservctl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*nfsservctl+package:^chromeos_public$) | 0xa9 | ? | ? | ? | ? | ? | ? |
| 170 | setresgid | [man/](http://man7.org/linux/man-pages/man2/setresgid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setresgid+package:^chromeos_public$) | 0xaa | gid\_t rgid | gid\_t egid | gid\_t sgid | - | - | - |
| 171 | getresgid | [man/](http://man7.org/linux/man-pages/man2/getresgid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getresgid+package:^chromeos_public$) | 0xab | gid\_t \*rgid | gid\_t \*egid | gid\_t \*sgid | - | - | - |
| 172 | prctl | [man/](http://man7.org/linux/man-pages/man2/prctl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*prctl+package:^chromeos_public$) | 0xac | int option | unsigned long arg2 | unsigned long arg3 | unsigned long arg4 | unsigned long arg5 | - |
| 173 | rt_sigreturn | [man/](http://man7.org/linux/man-pages/man2/rt_sigreturn.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rt_sigreturn+package:^chromeos_public$) | 0xad | ? | ? | ? | ? | ? | ? |
| 174 | rt_sigaction | [man/](http://man7.org/linux/man-pages/man2/rt_sigaction.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rt_sigaction+package:^chromeos_public$) | 0xae | int | const struct sigaction \* | struct sigaction \* | size\_t | - | - |
| 175 | rt_sigprocmask | [man/](http://man7.org/linux/man-pages/man2/rt_sigprocmask.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rt_sigprocmask+package:^chromeos_public$) | 0xaf | int how | sigset\_t \*set | sigset\_t \*oset | size\_t sigsetsize | - | - |
| 176 | rt_sigpending | [man/](http://man7.org/linux/man-pages/man2/rt_sigpending.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rt_sigpending+package:^chromeos_public$) | 0xb0 | sigset\_t \*set | size\_t sigsetsize | - | - | - | - |
| 177 | rt_sigtimedwait | [man/](http://man7.org/linux/man-pages/man2/rt_sigtimedwait.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rt_sigtimedwait+package:^chromeos_public$) | 0xb1 | const sigset\_t \*uthese | siginfo\_t \*uinfo | const struct timespec \*uts | size\_t sigsetsize | - | - |
| 178 | rt_sigqueueinfo | [man/](http://man7.org/linux/man-pages/man2/rt_sigqueueinfo.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rt_sigqueueinfo+package:^chromeos_public$) | 0xb2 | pid\_t pid | int sig | siginfo\_t \*uinfo | - | - | - |
| 179 | rt_sigsuspend | [man/](http://man7.org/linux/man-pages/man2/rt_sigsuspend.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rt_sigsuspend+package:^chromeos_public$) | 0xb3 | sigset\_t \*unewset | size\_t sigsetsize | - | - | - | - |
| 180 | pread64 | [man/](http://man7.org/linux/man-pages/man2/pread64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pread64+package:^chromeos_public$) | 0xb4 | unsigned int fd | char \*buf | size\_t count | loff\_t pos | - | - |
| 181 | pwrite64 | [man/](http://man7.org/linux/man-pages/man2/pwrite64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pwrite64+package:^chromeos_public$) | 0xb5 | unsigned int fd | const char \*buf | size\_t count | loff\_t pos | - | - |
| 182 | chown | [man/](http://man7.org/linux/man-pages/man2/chown.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*chown+package:^chromeos_public$) | 0xb6 | const char \*filename | uid\_t user | gid\_t group | - | - | - |
| 183 | getcwd | [man/](http://man7.org/linux/man-pages/man2/getcwd.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getcwd+package:^chromeos_public$) | 0xb7 | char \*buf | unsigned long size | - | - | - | - |
| 184 | capget | [man/](http://man7.org/linux/man-pages/man2/capget.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*capget+package:^chromeos_public$) | 0xb8 | cap\_user\_header\_t header | cap\_user\_data\_t dataptr | - | - | - | - |
| 185 | capset | [man/](http://man7.org/linux/man-pages/man2/capset.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*capset+package:^chromeos_public$) | 0xb9 | cap\_user\_header\_t header | const cap\_user\_data\_t data | - | - | - | - |
| 186 | sigaltstack | [man/](http://man7.org/linux/man-pages/man2/sigaltstack.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sigaltstack+package:^chromeos_public$) | 0xba | const struct sigaltstack \*uss | struct sigaltstack \*uoss | - | - | - | - |
| 187 | sendfile | [man/](http://man7.org/linux/man-pages/man2/sendfile.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sendfile+package:^chromeos_public$) | 0xbb | int out\_fd | int in\_fd | off\_t \*offset | size\_t count | - | - |
| 188 | *not implemented* | | 0xbc ||
| 189 | *not implemented* | | 0xbd ||
| 190 | vfork | [man/](http://man7.org/linux/man-pages/man2/vfork.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*vfork+package:^chromeos_public$) | 0xbe | - | - | - | - | - | - |
| 191 | ugetrlimit | [man/](http://man7.org/linux/man-pages/man2/ugetrlimit.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ugetrlimit+package:^chromeos_public$) | 0xbf | ? | ? | ? | ? | ? | ? |
| 192 | mmap2 | [man/](http://man7.org/linux/man-pages/man2/mmap2.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mmap2+package:^chromeos_public$) | 0xc0 | ? | ? | ? | ? | ? | ? |
| 193 | truncate64 | [man/](http://man7.org/linux/man-pages/man2/truncate64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*truncate64+package:^chromeos_public$) | 0xc1 | const char \*path | loff\_t length | - | - | - | - |
| 194 | ftruncate64 | [man/](http://man7.org/linux/man-pages/man2/ftruncate64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ftruncate64+package:^chromeos_public$) | 0xc2 | unsigned int fd | loff\_t length | - | - | - | - |
| 195 | stat64 | [man/](http://man7.org/linux/man-pages/man2/stat64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*stat64+package:^chromeos_public$) | 0xc3 | const char \*filename | struct stat64 \*statbuf | - | - | - | - |
| 196 | lstat64 | [man/](http://man7.org/linux/man-pages/man2/lstat64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*lstat64+package:^chromeos_public$) | 0xc4 | const char \*filename | struct stat64 \*statbuf | - | - | - | - |
| 197 | fstat64 | [man/](http://man7.org/linux/man-pages/man2/fstat64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fstat64+package:^chromeos_public$) | 0xc5 | unsigned long fd | struct stat64 \*statbuf | - | - | - | - |
| 198 | lchown32 | [man/](http://man7.org/linux/man-pages/man2/lchown32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*lchown32+package:^chromeos_public$) | 0xc6 | ? | ? | ? | ? | ? | ? |
| 199 | getuid32 | [man/](http://man7.org/linux/man-pages/man2/getuid32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getuid32+package:^chromeos_public$) | 0xc7 | ? | ? | ? | ? | ? | ? |
| 200 | getgid32 | [man/](http://man7.org/linux/man-pages/man2/getgid32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getgid32+package:^chromeos_public$) | 0xc8 | ? | ? | ? | ? | ? | ? |
| 201 | geteuid32 | [man/](http://man7.org/linux/man-pages/man2/geteuid32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*geteuid32+package:^chromeos_public$) | 0xc9 | ? | ? | ? | ? | ? | ? |
| 202 | getegid32 | [man/](http://man7.org/linux/man-pages/man2/getegid32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getegid32+package:^chromeos_public$) | 0xca | ? | ? | ? | ? | ? | ? |
| 203 | setreuid32 | [man/](http://man7.org/linux/man-pages/man2/setreuid32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setreuid32+package:^chromeos_public$) | 0xcb | ? | ? | ? | ? | ? | ? |
| 204 | setregid32 | [man/](http://man7.org/linux/man-pages/man2/setregid32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setregid32+package:^chromeos_public$) | 0xcc | ? | ? | ? | ? | ? | ? |
| 205 | getgroups32 | [man/](http://man7.org/linux/man-pages/man2/getgroups32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getgroups32+package:^chromeos_public$) | 0xcd | ? | ? | ? | ? | ? | ? |
| 206 | setgroups32 | [man/](http://man7.org/linux/man-pages/man2/setgroups32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setgroups32+package:^chromeos_public$) | 0xce | ? | ? | ? | ? | ? | ? |
| 207 | fchown32 | [man/](http://man7.org/linux/man-pages/man2/fchown32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fchown32+package:^chromeos_public$) | 0xcf | ? | ? | ? | ? | ? | ? |
| 208 | setresuid32 | [man/](http://man7.org/linux/man-pages/man2/setresuid32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setresuid32+package:^chromeos_public$) | 0xd0 | ? | ? | ? | ? | ? | ? |
| 209 | getresuid32 | [man/](http://man7.org/linux/man-pages/man2/getresuid32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getresuid32+package:^chromeos_public$) | 0xd1 | ? | ? | ? | ? | ? | ? |
| 210 | setresgid32 | [man/](http://man7.org/linux/man-pages/man2/setresgid32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setresgid32+package:^chromeos_public$) | 0xd2 | ? | ? | ? | ? | ? | ? |
| 211 | getresgid32 | [man/](http://man7.org/linux/man-pages/man2/getresgid32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getresgid32+package:^chromeos_public$) | 0xd3 | ? | ? | ? | ? | ? | ? |
| 212 | chown32 | [man/](http://man7.org/linux/man-pages/man2/chown32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*chown32+package:^chromeos_public$) | 0xd4 | ? | ? | ? | ? | ? | ? |
| 213 | setuid32 | [man/](http://man7.org/linux/man-pages/man2/setuid32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setuid32+package:^chromeos_public$) | 0xd5 | ? | ? | ? | ? | ? | ? |
| 214 | setgid32 | [man/](http://man7.org/linux/man-pages/man2/setgid32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setgid32+package:^chromeos_public$) | 0xd6 | ? | ? | ? | ? | ? | ? |
| 215 | setfsuid32 | [man/](http://man7.org/linux/man-pages/man2/setfsuid32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setfsuid32+package:^chromeos_public$) | 0xd7 | ? | ? | ? | ? | ? | ? |
| 216 | setfsgid32 | [man/](http://man7.org/linux/man-pages/man2/setfsgid32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setfsgid32+package:^chromeos_public$) | 0xd8 | ? | ? | ? | ? | ? | ? |
| 217 | getdents64 | [man/](http://man7.org/linux/man-pages/man2/getdents64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getdents64+package:^chromeos_public$) | 0xd9 | unsigned int fd | struct linux\_dirent64 \*dirent | unsigned int count | - | - | - |
| 218 | pivot_root | [man/](http://man7.org/linux/man-pages/man2/pivot_root.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pivot_root+package:^chromeos_public$) | 0xda | const char \*new\_root | const char \*put\_old | - | - | - | - |
| 219 | mincore | [man/](http://man7.org/linux/man-pages/man2/mincore.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mincore+package:^chromeos_public$) | 0xdb | unsigned long start | size\_t len | unsigned char \* vec | - | - | - |
| 220 | madvise | [man/](http://man7.org/linux/man-pages/man2/madvise.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*madvise+package:^chromeos_public$) | 0xdc | unsigned long start | size\_t len | int behavior | - | - | - |
| 221 | fcntl64 | [man/](http://man7.org/linux/man-pages/man2/fcntl64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fcntl64+package:^chromeos_public$) | 0xdd | unsigned int fd | unsigned int cmd | unsigned long arg | - | - | - |
| 222 | *not implemented* | | 0xde ||
| 223 | *not implemented* | | 0xdf ||
| 224 | gettid | [man/](http://man7.org/linux/man-pages/man2/gettid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*gettid+package:^chromeos_public$) | 0xe0 | - | - | - | - | - | - |
| 225 | readahead | [man/](http://man7.org/linux/man-pages/man2/readahead.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*readahead+package:^chromeos_public$) | 0xe1 | int fd | loff\_t offset | size\_t count | - | - | - |
| 226 | setxattr | [man/](http://man7.org/linux/man-pages/man2/setxattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setxattr+package:^chromeos_public$) | 0xe2 | const char \*path | const char \*name | const void \*value | size\_t size | int flags | - |
| 227 | lsetxattr | [man/](http://man7.org/linux/man-pages/man2/lsetxattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*lsetxattr+package:^chromeos_public$) | 0xe3 | const char \*path | const char \*name | const void \*value | size\_t size | int flags | - |
| 228 | fsetxattr | [man/](http://man7.org/linux/man-pages/man2/fsetxattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fsetxattr+package:^chromeos_public$) | 0xe4 | int fd | const char \*name | const void \*value | size\_t size | int flags | - |
| 229 | getxattr | [man/](http://man7.org/linux/man-pages/man2/getxattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getxattr+package:^chromeos_public$) | 0xe5 | const char \*path | const char \*name | void \*value | size\_t size | - | - |
| 230 | lgetxattr | [man/](http://man7.org/linux/man-pages/man2/lgetxattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*lgetxattr+package:^chromeos_public$) | 0xe6 | const char \*path | const char \*name | void \*value | size\_t size | - | - |
| 231 | fgetxattr | [man/](http://man7.org/linux/man-pages/man2/fgetxattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fgetxattr+package:^chromeos_public$) | 0xe7 | int fd | const char \*name | void \*value | size\_t size | - | - |
| 232 | listxattr | [man/](http://man7.org/linux/man-pages/man2/listxattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*listxattr+package:^chromeos_public$) | 0xe8 | const char \*path | char \*list | size\_t size | - | - | - |
| 233 | llistxattr | [man/](http://man7.org/linux/man-pages/man2/llistxattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*llistxattr+package:^chromeos_public$) | 0xe9 | const char \*path | char \*list | size\_t size | - | - | - |
| 234 | flistxattr | [man/](http://man7.org/linux/man-pages/man2/flistxattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*flistxattr+package:^chromeos_public$) | 0xea | int fd | char \*list | size\_t size | - | - | - |
| 235 | removexattr | [man/](http://man7.org/linux/man-pages/man2/removexattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*removexattr+package:^chromeos_public$) | 0xeb | const char \*path | const char \*name | - | - | - | - |
| 236 | lremovexattr | [man/](http://man7.org/linux/man-pages/man2/lremovexattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*lremovexattr+package:^chromeos_public$) | 0xec | const char \*path | const char \*name | - | - | - | - |
| 237 | fremovexattr | [man/](http://man7.org/linux/man-pages/man2/fremovexattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fremovexattr+package:^chromeos_public$) | 0xed | int fd | const char \*name | - | - | - | - |
| 238 | tkill | [man/](http://man7.org/linux/man-pages/man2/tkill.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*tkill+package:^chromeos_public$) | 0xee | pid\_t pid | int sig | - | - | - | - |
| 239 | sendfile64 | [man/](http://man7.org/linux/man-pages/man2/sendfile64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sendfile64+package:^chromeos_public$) | 0xef | int out\_fd | int in\_fd | loff\_t \*offset | size\_t count | - | - |
| 240 | futex | [man/](http://man7.org/linux/man-pages/man2/futex.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*futex+package:^chromeos_public$) | 0xf0 | u32 \*uaddr | int op | u32 val | struct timespec \*utime | u32 \*uaddr2 | u32 val3 |
| 241 | sched_setaffinity | [man/](http://man7.org/linux/man-pages/man2/sched_setaffinity.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_setaffinity+package:^chromeos_public$) | 0xf1 | pid\_t pid | unsigned int len | unsigned long \*user\_mask\_ptr | - | - | - |
| 242 | sched_getaffinity | [man/](http://man7.org/linux/man-pages/man2/sched_getaffinity.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_getaffinity+package:^chromeos_public$) | 0xf2 | pid\_t pid | unsigned int len | unsigned long \*user\_mask\_ptr | - | - | - |
| 243 | io_setup | [man/](http://man7.org/linux/man-pages/man2/io_setup.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*io_setup+package:^chromeos_public$) | 0xf3 | unsigned nr\_reqs | aio\_context\_t \*ctx | - | - | - | - |
| 244 | io_destroy | [man/](http://man7.org/linux/man-pages/man2/io_destroy.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*io_destroy+package:^chromeos_public$) | 0xf4 | aio\_context\_t ctx | - | - | - | - | - |
| 245 | io_getevents | [man/](http://man7.org/linux/man-pages/man2/io_getevents.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*io_getevents+package:^chromeos_public$) | 0xf5 | aio\_context\_t ctx\_id | long min\_nr | long nr | struct io\_event \*events | struct timespec \*timeout | - |
| 246 | io_submit | [man/](http://man7.org/linux/man-pages/man2/io_submit.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*io_submit+package:^chromeos_public$) | 0xf6 | aio\_context\_t | long | struct iocb \* \* | - | - | - |
| 247 | io_cancel | [man/](http://man7.org/linux/man-pages/man2/io_cancel.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*io_cancel+package:^chromeos_public$) | 0xf7 | aio\_context\_t ctx\_id | struct iocb \*iocb | struct io\_event \*result | - | - | - |
| 248 | exit_group | [man/](http://man7.org/linux/man-pages/man2/exit_group.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*exit_group+package:^chromeos_public$) | 0xf8 | int error\_code | - | - | - | - | - |
| 249 | lookup_dcookie | [man/](http://man7.org/linux/man-pages/man2/lookup_dcookie.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*lookup_dcookie+package:^chromeos_public$) | 0xf9 | u64 cookie64 | char \*buf | size\_t len | - | - | - |
| 250 | epoll_create | [man/](http://man7.org/linux/man-pages/man2/epoll_create.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*epoll_create+package:^chromeos_public$) | 0xfa | int size | - | - | - | - | - |
| 251 | epoll_ctl | [man/](http://man7.org/linux/man-pages/man2/epoll_ctl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*epoll_ctl+package:^chromeos_public$) | 0xfb | int epfd | int op | int fd | struct epoll\_event \*event | - | - |
| 252 | epoll_wait | [man/](http://man7.org/linux/man-pages/man2/epoll_wait.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*epoll_wait+package:^chromeos_public$) | 0xfc | int epfd | struct epoll\_event \*events | int maxevents | int timeout | - | - |
| 253 | remap_file_pages | [man/](http://man7.org/linux/man-pages/man2/remap_file_pages.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*remap_file_pages+package:^chromeos_public$) | 0xfd | unsigned long start | unsigned long size | unsigned long prot | unsigned long pgoff | unsigned long flags | - |
| 254 | *not implemented* | | 0xfe ||
| 255 | *not implemented* | | 0xff ||
| 256 | set_tid_address | [man/](http://man7.org/linux/man-pages/man2/set_tid_address.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*set_tid_address+package:^chromeos_public$) | 0x100 | int \*tidptr | - | - | - | - | - |
| 257 | timer_create | [man/](http://man7.org/linux/man-pages/man2/timer_create.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*timer_create+package:^chromeos_public$) | 0x101 | clockid\_t which\_clock | struct sigevent \*timer\_event\_spec | timer\_t \* created\_timer\_id | - | - | - |
| 258 | timer_settime | [man/](http://man7.org/linux/man-pages/man2/timer_settime.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*timer_settime+package:^chromeos_public$) | 0x102 | timer\_t timer\_id | int flags | const struct \_\_kernel\_itimerspec \*new\_setting | struct itimerspec \*old\_setting | - | - |
| 259 | timer_gettime | [man/](http://man7.org/linux/man-pages/man2/timer_gettime.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*timer_gettime+package:^chromeos_public$) | 0x103 | timer\_t timer\_id | struct \_\_kernel\_itimerspec \*setting | - | - | - | - |
| 260 | timer_getoverrun | [man/](http://man7.org/linux/man-pages/man2/timer_getoverrun.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*timer_getoverrun+package:^chromeos_public$) | 0x104 | timer\_t timer\_id | - | - | - | - | - |
| 261 | timer_delete | [man/](http://man7.org/linux/man-pages/man2/timer_delete.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*timer_delete+package:^chromeos_public$) | 0x105 | timer\_t timer\_id | - | - | - | - | - |
| 262 | clock_settime | [man/](http://man7.org/linux/man-pages/man2/clock_settime.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*clock_settime+package:^chromeos_public$) | 0x106 | clockid\_t which\_clock | const struct \_\_kernel\_timespec \*tp | - | - | - | - |
| 263 | clock_gettime | [man/](http://man7.org/linux/man-pages/man2/clock_gettime.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*clock_gettime+package:^chromeos_public$) | 0x107 | clockid\_t which\_clock | struct \_\_kernel\_timespec \*tp | - | - | - | - |
| 264 | clock_getres | [man/](http://man7.org/linux/man-pages/man2/clock_getres.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*clock_getres+package:^chromeos_public$) | 0x108 | clockid\_t which\_clock | struct \_\_kernel\_timespec \*tp | - | - | - | - |
| 265 | clock_nanosleep | [man/](http://man7.org/linux/man-pages/man2/clock_nanosleep.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*clock_nanosleep+package:^chromeos_public$) | 0x109 | clockid\_t which\_clock | int flags | const struct \_\_kernel\_timespec \*rqtp | struct \_\_kernel\_timespec \*rmtp | - | - |
| 266 | statfs64 | [man/](http://man7.org/linux/man-pages/man2/statfs64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*statfs64+package:^chromeos_public$) | 0x10a | const char \*path | size\_t sz | struct statfs64 \*buf | - | - | - |
| 267 | fstatfs64 | [man/](http://man7.org/linux/man-pages/man2/fstatfs64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fstatfs64+package:^chromeos_public$) | 0x10b | unsigned int fd | size\_t sz | struct statfs64 \*buf | - | - | - |
| 268 | tgkill | [man/](http://man7.org/linux/man-pages/man2/tgkill.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*tgkill+package:^chromeos_public$) | 0x10c | pid\_t tgid | pid\_t pid | int sig | - | - | - |
| 269 | utimes | [man/](http://man7.org/linux/man-pages/man2/utimes.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*utimes+package:^chromeos_public$) | 0x10d | char \*filename | struct timeval \*utimes | - | - | - | - |
| 270 | arm_fadvise64_64 | [man/](http://man7.org/linux/man-pages/man2/arm_fadvise64_64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*arm_fadvise64_64+package:^chromeos_public$) | 0x10e | ? | ? | ? | ? | ? | ? |
| 271 | pciconfig_iobase | [man/](http://man7.org/linux/man-pages/man2/pciconfig_iobase.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pciconfig_iobase+package:^chromeos_public$) | 0x10f | long which | unsigned long bus | unsigned long devfn | - | - | - |
| 272 | pciconfig_read | [man/](http://man7.org/linux/man-pages/man2/pciconfig_read.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pciconfig_read+package:^chromeos_public$) | 0x110 | unsigned long bus | unsigned long dfn | unsigned long off | unsigned long len | void \*buf | - |
| 273 | pciconfig_write | [man/](http://man7.org/linux/man-pages/man2/pciconfig_write.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pciconfig_write+package:^chromeos_public$) | 0x111 | unsigned long bus | unsigned long dfn | unsigned long off | unsigned long len | void \*buf | - |
| 274 | mq_open | [man/](http://man7.org/linux/man-pages/man2/mq_open.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mq_open+package:^chromeos_public$) | 0x112 | const char \*name | int oflag | umode\_t mode | struct mq\_attr \*attr | - | - |
| 275 | mq_unlink | [man/](http://man7.org/linux/man-pages/man2/mq_unlink.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mq_unlink+package:^chromeos_public$) | 0x113 | const char \*name | - | - | - | - | - |
| 276 | mq_timedsend | [man/](http://man7.org/linux/man-pages/man2/mq_timedsend.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mq_timedsend+package:^chromeos_public$) | 0x114 | mqd\_t mqdes | const char \*msg\_ptr | size\_t msg\_len | unsigned int msg\_prio | const struct \_\_kernel\_timespec \*abs\_timeout | - |
| 277 | mq_timedreceive | [man/](http://man7.org/linux/man-pages/man2/mq_timedreceive.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mq_timedreceive+package:^chromeos_public$) | 0x115 | mqd\_t mqdes | char \*msg\_ptr | size\_t msg\_len | unsigned int \*msg\_prio | const struct \_\_kernel\_timespec \*abs\_timeout | - |
| 278 | mq_notify | [man/](http://man7.org/linux/man-pages/man2/mq_notify.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mq_notify+package:^chromeos_public$) | 0x116 | mqd\_t mqdes | const struct sigevent \*notification | - | - | - | - |
| 279 | mq_getsetattr | [man/](http://man7.org/linux/man-pages/man2/mq_getsetattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mq_getsetattr+package:^chromeos_public$) | 0x117 | mqd\_t mqdes | const struct mq\_attr \*mqstat | struct mq\_attr \*omqstat | - | - | - |
| 280 | waitid | [man/](http://man7.org/linux/man-pages/man2/waitid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*waitid+package:^chromeos_public$) | 0x118 | int which | pid\_t pid | struct siginfo \*infop | int options | struct rusage \*ru | - |
| 281 | socket | [man/](http://man7.org/linux/man-pages/man2/socket.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*socket+package:^chromeos_public$) | 0x119 | int | int | int | - | - | - |
| 282 | bind | [man/](http://man7.org/linux/man-pages/man2/bind.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*bind+package:^chromeos_public$) | 0x11a | int | struct sockaddr \* | int | - | - | - |
| 283 | connect | [man/](http://man7.org/linux/man-pages/man2/connect.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*connect+package:^chromeos_public$) | 0x11b | int | struct sockaddr \* | int | - | - | - |
| 284 | listen | [man/](http://man7.org/linux/man-pages/man2/listen.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*listen+package:^chromeos_public$) | 0x11c | int | int | - | - | - | - |
| 285 | accept | [man/](http://man7.org/linux/man-pages/man2/accept.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*accept+package:^chromeos_public$) | 0x11d | int | struct sockaddr \* | int \* | - | - | - |
| 286 | getsockname | [man/](http://man7.org/linux/man-pages/man2/getsockname.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getsockname+package:^chromeos_public$) | 0x11e | int | struct sockaddr \* | int \* | - | - | - |
| 287 | getpeername | [man/](http://man7.org/linux/man-pages/man2/getpeername.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getpeername+package:^chromeos_public$) | 0x11f | int | struct sockaddr \* | int \* | - | - | - |
| 288 | socketpair | [man/](http://man7.org/linux/man-pages/man2/socketpair.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*socketpair+package:^chromeos_public$) | 0x120 | int | int | int | int \* | - | - |
| 289 | send | [man/](http://man7.org/linux/man-pages/man2/send.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*send+package:^chromeos_public$) | 0x121 | int | void \* | size\_t | unsigned | - | - |
| 290 | sendto | [man/](http://man7.org/linux/man-pages/man2/sendto.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sendto+package:^chromeos_public$) | 0x122 | int | void \* | size\_t | unsigned | struct sockaddr \* | int |
| 291 | recv | [man/](http://man7.org/linux/man-pages/man2/recv.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*recv+package:^chromeos_public$) | 0x123 | int | void \* | size\_t | unsigned | - | - |
| 292 | recvfrom | [man/](http://man7.org/linux/man-pages/man2/recvfrom.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*recvfrom+package:^chromeos_public$) | 0x124 | int | void \* | size\_t | unsigned | struct sockaddr \* | int \* |
| 293 | shutdown | [man/](http://man7.org/linux/man-pages/man2/shutdown.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*shutdown+package:^chromeos_public$) | 0x125 | int | int | - | - | - | - |
| 294 | setsockopt | [man/](http://man7.org/linux/man-pages/man2/setsockopt.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setsockopt+package:^chromeos_public$) | 0x126 | int fd | int level | int optname | char \*optval | int optlen | - |
| 295 | getsockopt | [man/](http://man7.org/linux/man-pages/man2/getsockopt.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getsockopt+package:^chromeos_public$) | 0x127 | int fd | int level | int optname | char \*optval | int \*optlen | - |
| 296 | sendmsg | [man/](http://man7.org/linux/man-pages/man2/sendmsg.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sendmsg+package:^chromeos_public$) | 0x128 | int fd | struct user\_msghdr \*msg | unsigned flags | - | - | - |
| 297 | recvmsg | [man/](http://man7.org/linux/man-pages/man2/recvmsg.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*recvmsg+package:^chromeos_public$) | 0x129 | int fd | struct user\_msghdr \*msg | unsigned flags | - | - | - |
| 298 | semop | [man/](http://man7.org/linux/man-pages/man2/semop.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*semop+package:^chromeos_public$) | 0x12a | int semid | struct sembuf \*sops | unsigned nsops | - | - | - |
| 299 | semget | [man/](http://man7.org/linux/man-pages/man2/semget.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*semget+package:^chromeos_public$) | 0x12b | key\_t key | int nsems | int semflg | - | - | - |
| 300 | semctl | [man/](http://man7.org/linux/man-pages/man2/semctl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*semctl+package:^chromeos_public$) | 0x12c | int semid | int semnum | int cmd | unsigned long arg | - | - |
| 301 | msgsnd | [man/](http://man7.org/linux/man-pages/man2/msgsnd.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*msgsnd+package:^chromeos_public$) | 0x12d | int msqid | struct msgbuf \*msgp | size\_t msgsz | int msgflg | - | - |
| 302 | msgrcv | [man/](http://man7.org/linux/man-pages/man2/msgrcv.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*msgrcv+package:^chromeos_public$) | 0x12e | int msqid | struct msgbuf \*msgp | size\_t msgsz | long msgtyp | int msgflg | - |
| 303 | msgget | [man/](http://man7.org/linux/man-pages/man2/msgget.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*msgget+package:^chromeos_public$) | 0x12f | key\_t key | int msgflg | - | - | - | - |
| 304 | msgctl | [man/](http://man7.org/linux/man-pages/man2/msgctl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*msgctl+package:^chromeos_public$) | 0x130 | int msqid | int cmd | struct msqid\_ds \*buf | - | - | - |
| 305 | shmat | [man/](http://man7.org/linux/man-pages/man2/shmat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*shmat+package:^chromeos_public$) | 0x131 | int shmid | char \*shmaddr | int shmflg | - | - | - |
| 306 | shmdt | [man/](http://man7.org/linux/man-pages/man2/shmdt.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*shmdt+package:^chromeos_public$) | 0x132 | char \*shmaddr | - | - | - | - | - |
| 307 | shmget | [man/](http://man7.org/linux/man-pages/man2/shmget.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*shmget+package:^chromeos_public$) | 0x133 | key\_t key | size\_t size | int flag | - | - | - |
| 308 | shmctl | [man/](http://man7.org/linux/man-pages/man2/shmctl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*shmctl+package:^chromeos_public$) | 0x134 | int shmid | int cmd | struct shmid\_ds \*buf | - | - | - |
| 309 | add_key | [man/](http://man7.org/linux/man-pages/man2/add_key.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*add_key+package:^chromeos_public$) | 0x135 | const char \*\_type | const char \*\_description | const void \*\_payload | size\_t plen | key\_serial\_t destringid | - |
| 310 | request_key | [man/](http://man7.org/linux/man-pages/man2/request_key.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*request_key+package:^chromeos_public$) | 0x136 | const char \*\_type | const char \*\_description | const char \*\_callout\_info | key\_serial\_t destringid | - | - |
| 311 | keyctl | [man/](http://man7.org/linux/man-pages/man2/keyctl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*keyctl+package:^chromeos_public$) | 0x137 | int cmd | unsigned long arg2 | unsigned long arg3 | unsigned long arg4 | unsigned long arg5 | - |
| 312 | semtimedop | [man/](http://man7.org/linux/man-pages/man2/semtimedop.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*semtimedop+package:^chromeos_public$) | 0x138 | int semid | struct sembuf \*sops | unsigned nsops | const struct \_\_kernel\_timespec \*timeout | - | - |
| 313 | vserver | [man/](http://man7.org/linux/man-pages/man2/vserver.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*vserver+package:^chromeos_public$) | 0x139 | ? | ? | ? | ? | ? | ? |
| 314 | ioprio_set | [man/](http://man7.org/linux/man-pages/man2/ioprio_set.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ioprio_set+package:^chromeos_public$) | 0x13a | int which | int who | int ioprio | - | - | - |
| 315 | ioprio_get | [man/](http://man7.org/linux/man-pages/man2/ioprio_get.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ioprio_get+package:^chromeos_public$) | 0x13b | int which | int who | - | - | - | - |
| 316 | inotify_init | [man/](http://man7.org/linux/man-pages/man2/inotify_init.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*inotify_init+package:^chromeos_public$) | 0x13c | - | - | - | - | - | - |
| 317 | inotify_add_watch | [man/](http://man7.org/linux/man-pages/man2/inotify_add_watch.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*inotify_add_watch+package:^chromeos_public$) | 0x13d | int fd | const char \*path | u32 mask | - | - | - |
| 318 | inotify_rm_watch | [man/](http://man7.org/linux/man-pages/man2/inotify_rm_watch.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*inotify_rm_watch+package:^chromeos_public$) | 0x13e | int fd | \_\_s32 wd | - | - | - | - |
| 319 | mbind | [man/](http://man7.org/linux/man-pages/man2/mbind.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mbind+package:^chromeos_public$) | 0x13f | unsigned long start | unsigned long len | unsigned long mode | const unsigned long \*nmask | unsigned long maxnode | unsigned flags |
| 320 | get_mempolicy | [man/](http://man7.org/linux/man-pages/man2/get_mempolicy.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*get_mempolicy+package:^chromeos_public$) | 0x140 | int \*policy | unsigned long \*nmask | unsigned long maxnode | unsigned long addr | unsigned long flags | - |
| 321 | set_mempolicy | [man/](http://man7.org/linux/man-pages/man2/set_mempolicy.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*set_mempolicy+package:^chromeos_public$) | 0x141 | int mode | const unsigned long \*nmask | unsigned long maxnode | - | - | - |
| 322 | openat | [man/](http://man7.org/linux/man-pages/man2/openat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*openat+package:^chromeos_public$) | 0x142 | int dfd | const char \*filename | int flags | umode\_t mode | - | - |
| 323 | mkdirat | [man/](http://man7.org/linux/man-pages/man2/mkdirat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mkdirat+package:^chromeos_public$) | 0x143 | int dfd | const char \* pathname | umode\_t mode | - | - | - |
| 324 | mknodat | [man/](http://man7.org/linux/man-pages/man2/mknodat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mknodat+package:^chromeos_public$) | 0x144 | int dfd | const char \* filename | umode\_t mode | unsigned dev | - | - |
| 325 | fchownat | [man/](http://man7.org/linux/man-pages/man2/fchownat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fchownat+package:^chromeos_public$) | 0x145 | int dfd | const char \*filename | uid\_t user | gid\_t group | int flag | - |
| 326 | futimesat | [man/](http://man7.org/linux/man-pages/man2/futimesat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*futimesat+package:^chromeos_public$) | 0x146 | int dfd | const char \*filename | struct timeval \*utimes | - | - | - |
| 327 | fstatat64 | [man/](http://man7.org/linux/man-pages/man2/fstatat64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fstatat64+package:^chromeos_public$) | 0x147 | int dfd | const char \*filename | struct stat64 \*statbuf | int flag | - | - |
| 328 | unlinkat | [man/](http://man7.org/linux/man-pages/man2/unlinkat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*unlinkat+package:^chromeos_public$) | 0x148 | int dfd | const char \* pathname | int flag | - | - | - |
| 329 | renameat | [man/](http://man7.org/linux/man-pages/man2/renameat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*renameat+package:^chromeos_public$) | 0x149 | int olddfd | const char \* oldname | int newdfd | const char \* newname | - | - |
| 330 | linkat | [man/](http://man7.org/linux/man-pages/man2/linkat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*linkat+package:^chromeos_public$) | 0x14a | int olddfd | const char \*oldname | int newdfd | const char \*newname | int flags | - |
| 331 | symlinkat | [man/](http://man7.org/linux/man-pages/man2/symlinkat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*symlinkat+package:^chromeos_public$) | 0x14b | const char \* oldname | int newdfd | const char \* newname | - | - | - |
| 332 | readlinkat | [man/](http://man7.org/linux/man-pages/man2/readlinkat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*readlinkat+package:^chromeos_public$) | 0x14c | int dfd | const char \*path | char \*buf | int bufsiz | - | - |
| 333 | fchmodat | [man/](http://man7.org/linux/man-pages/man2/fchmodat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fchmodat+package:^chromeos_public$) | 0x14d | int dfd | const char \* filename | umode\_t mode | - | - | - |
| 334 | faccessat | [man/](http://man7.org/linux/man-pages/man2/faccessat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*faccessat+package:^chromeos_public$) | 0x14e | int dfd | const char \*filename | int mode | - | - | - |
| 335 | pselect6 | [man/](http://man7.org/linux/man-pages/man2/pselect6.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pselect6+package:^chromeos_public$) | 0x14f | int | fd\_set \* | fd\_set \* | fd\_set \* | struct timespec \* | void \* |
| 336 | ppoll | [man/](http://man7.org/linux/man-pages/man2/ppoll.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ppoll+package:^chromeos_public$) | 0x150 | struct pollfd \* | unsigned int | struct timespec \* | const sigset\_t \* | size\_t | - |
| 337 | unshare | [man/](http://man7.org/linux/man-pages/man2/unshare.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*unshare+package:^chromeos_public$) | 0x151 | unsigned long unshare\_flags | - | - | - | - | - |
| 338 | set_robust_list | [man/](http://man7.org/linux/man-pages/man2/set_robust_list.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*set_robust_list+package:^chromeos_public$) | 0x152 | struct robust\_list\_head \*head | size\_t len | - | - | - | - |
| 339 | get_robust_list | [man/](http://man7.org/linux/man-pages/man2/get_robust_list.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*get_robust_list+package:^chromeos_public$) | 0x153 | int pid | struct robust\_list\_head \* \*head\_ptr | size\_t \*len\_ptr | - | - | - |
| 340 | splice | [man/](http://man7.org/linux/man-pages/man2/splice.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*splice+package:^chromeos_public$) | 0x154 | int fd\_in | loff\_t \*off\_in | int fd\_out | loff\_t \*off\_out | size\_t len | unsigned int flags |
| 341 | arm_sync_file_range | [man/](http://man7.org/linux/man-pages/man2/arm_sync_file_range.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*arm_sync_file_range+package:^chromeos_public$) | 0x155 | ? | ? | ? | ? | ? | ? |
| 341 | sync_file_range2 | [man/](http://man7.org/linux/man-pages/man2/sync_file_range2.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sync_file_range2+package:^chromeos_public$) | 0x155 | int fd | unsigned int flags | loff\_t offset | loff\_t nbytes | - | - |
| 342 | tee | [man/](http://man7.org/linux/man-pages/man2/tee.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*tee+package:^chromeos_public$) | 0x156 | int fdin | int fdout | size\_t len | unsigned int flags | - | - |
| 343 | vmsplice | [man/](http://man7.org/linux/man-pages/man2/vmsplice.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*vmsplice+package:^chromeos_public$) | 0x157 | int fd | const struct iovec \*iov | unsigned long nr\_segs | unsigned int flags | - | - |
| 344 | move_pages | [man/](http://man7.org/linux/man-pages/man2/move_pages.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*move_pages+package:^chromeos_public$) | 0x158 | pid\_t pid | unsigned long nr\_pages | const void \* \*pages | const int \*nodes | int \*status | int flags |
| 345 | getcpu | [man/](http://man7.org/linux/man-pages/man2/getcpu.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getcpu+package:^chromeos_public$) | 0x159 | unsigned \*cpu | unsigned \*node | struct getcpu\_cache \*cache | - | - | - |
| 346 | epoll_pwait | [man/](http://man7.org/linux/man-pages/man2/epoll_pwait.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*epoll_pwait+package:^chromeos_public$) | 0x15a | int epfd | struct epoll\_event \*events | int maxevents | int timeout | const sigset\_t \*sigmask | size\_t sigsetsize |
| 347 | kexec_load | [man/](http://man7.org/linux/man-pages/man2/kexec_load.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*kexec_load+package:^chromeos_public$) | 0x15b | unsigned long entry | unsigned long nr\_segments | struct kexec\_segment \*segments | unsigned long flags | - | - |
| 348 | utimensat | [man/](http://man7.org/linux/man-pages/man2/utimensat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*utimensat+package:^chromeos_public$) | 0x15c | int dfd | const char \*filename | struct timespec \*utimes | int flags | - | - |
| 349 | signalfd | [man/](http://man7.org/linux/man-pages/man2/signalfd.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*signalfd+package:^chromeos_public$) | 0x15d | int ufd | sigset\_t \*user\_mask | size\_t sizemask | - | - | - |
| 350 | timerfd_create | [man/](http://man7.org/linux/man-pages/man2/timerfd_create.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*timerfd_create+package:^chromeos_public$) | 0x15e | int clockid | int flags | - | - | - | - |
| 351 | eventfd | [man/](http://man7.org/linux/man-pages/man2/eventfd.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*eventfd+package:^chromeos_public$) | 0x15f | unsigned int count | - | - | - | - | - |
| 352 | fallocate | [man/](http://man7.org/linux/man-pages/man2/fallocate.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fallocate+package:^chromeos_public$) | 0x160 | int fd | int mode | loff\_t offset | loff\_t len | - | - |
| 353 | timerfd_settime | [man/](http://man7.org/linux/man-pages/man2/timerfd_settime.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*timerfd_settime+package:^chromeos_public$) | 0x161 | int ufd | int flags | const struct \_\_kernel\_itimerspec \*utmr | struct \_\_kernel\_itimerspec \*otmr | - | - |
| 354 | timerfd_gettime | [man/](http://man7.org/linux/man-pages/man2/timerfd_gettime.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*timerfd_gettime+package:^chromeos_public$) | 0x162 | int ufd | struct \_\_kernel\_itimerspec \*otmr | - | - | - | - |
| 355 | signalfd4 | [man/](http://man7.org/linux/man-pages/man2/signalfd4.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*signalfd4+package:^chromeos_public$) | 0x163 | int ufd | sigset\_t \*user\_mask | size\_t sizemask | int flags | - | - |
| 356 | eventfd2 | [man/](http://man7.org/linux/man-pages/man2/eventfd2.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*eventfd2+package:^chromeos_public$) | 0x164 | unsigned int count | int flags | - | - | - | - |
| 357 | epoll_create1 | [man/](http://man7.org/linux/man-pages/man2/epoll_create1.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*epoll_create1+package:^chromeos_public$) | 0x165 | int flags | - | - | - | - | - |
| 358 | dup3 | [man/](http://man7.org/linux/man-pages/man2/dup3.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*dup3+package:^chromeos_public$) | 0x166 | unsigned int oldfd | unsigned int newfd | int flags | - | - | - |
| 359 | pipe2 | [man/](http://man7.org/linux/man-pages/man2/pipe2.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pipe2+package:^chromeos_public$) | 0x167 | int \*fildes | int flags | - | - | - | - |
| 360 | inotify_init1 | [man/](http://man7.org/linux/man-pages/man2/inotify_init1.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*inotify_init1+package:^chromeos_public$) | 0x168 | int flags | - | - | - | - | - |
| 361 | preadv | [man/](http://man7.org/linux/man-pages/man2/preadv.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*preadv+package:^chromeos_public$) | 0x169 | unsigned long fd | const struct iovec \*vec | unsigned long vlen | unsigned long pos\_l | unsigned long pos\_h | - |
| 362 | pwritev | [man/](http://man7.org/linux/man-pages/man2/pwritev.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pwritev+package:^chromeos_public$) | 0x16a | unsigned long fd | const struct iovec \*vec | unsigned long vlen | unsigned long pos\_l | unsigned long pos\_h | - |
| 363 | rt_tgsigqueueinfo | [man/](http://man7.org/linux/man-pages/man2/rt_tgsigqueueinfo.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rt_tgsigqueueinfo+package:^chromeos_public$) | 0x16b | pid\_t tgid | pid\_t pid | int sig | siginfo\_t \*uinfo | - | - |
| 364 | perf_event_open | [man/](http://man7.org/linux/man-pages/man2/perf_event_open.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*perf_event_open+package:^chromeos_public$) | 0x16c | struct perf\_event\_attr \*attr\_uptr | pid\_t pid | int cpu | int group\_fd | unsigned long flags | - |
| 365 | recvmmsg | [man/](http://man7.org/linux/man-pages/man2/recvmmsg.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*recvmmsg+package:^chromeos_public$) | 0x16d | int fd | struct mmsghdr \*msg | unsigned int vlen | unsigned flags | struct timespec \*timeout | - |
| 366 | accept4 | [man/](http://man7.org/linux/man-pages/man2/accept4.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*accept4+package:^chromeos_public$) | 0x16e | int | struct sockaddr \* | int \* | int | - | - |
| 367 | fanotify_init | [man/](http://man7.org/linux/man-pages/man2/fanotify_init.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fanotify_init+package:^chromeos_public$) | 0x16f | unsigned int flags | unsigned int event\_f\_flags | - | - | - | - |
| 368 | fanotify_mark | [man/](http://man7.org/linux/man-pages/man2/fanotify_mark.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fanotify_mark+package:^chromeos_public$) | 0x170 | int fanotify\_fd | unsigned int flags | u64 mask | int fd | const char \*pathname | - |
| 369 | prlimit64 | [man/](http://man7.org/linux/man-pages/man2/prlimit64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*prlimit64+package:^chromeos_public$) | 0x171 | pid\_t pid | unsigned int resource | const struct rlimit64 \*new\_rlim | struct rlimit64 \*old\_rlim | - | - |
| 370 | name_to_handle_at | [man/](http://man7.org/linux/man-pages/man2/name_to_handle_at.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*name_to_handle_at+package:^chromeos_public$) | 0x172 | int dfd | const char \*name | struct file\_handle \*handle | int \*mnt\_id | int flag | - |
| 371 | open_by_handle_at | [man/](http://man7.org/linux/man-pages/man2/open_by_handle_at.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*open_by_handle_at+package:^chromeos_public$) | 0x173 | int mountdirfd | struct file\_handle \*handle | int flags | - | - | - |
| 372 | clock_adjtime | [man/](http://man7.org/linux/man-pages/man2/clock_adjtime.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*clock_adjtime+package:^chromeos_public$) | 0x174 | clockid\_t which\_clock | struct timex \*tx | - | - | - | - |
| 373 | syncfs | [man/](http://man7.org/linux/man-pages/man2/syncfs.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*syncfs+package:^chromeos_public$) | 0x175 | int fd | - | - | - | - | - |
| 374 | sendmmsg | [man/](http://man7.org/linux/man-pages/man2/sendmmsg.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sendmmsg+package:^chromeos_public$) | 0x176 | int fd | struct mmsghdr \*msg | unsigned int vlen | unsigned flags | - | - |
| 375 | setns | [man/](http://man7.org/linux/man-pages/man2/setns.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setns+package:^chromeos_public$) | 0x177 | int fd | int nstype | - | - | - | - |
| 376 | process_vm_readv | [man/](http://man7.org/linux/man-pages/man2/process_vm_readv.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*process_vm_readv+package:^chromeos_public$) | 0x178 | pid\_t pid | const struct iovec \*lvec | unsigned long liovcnt | const struct iovec \*rvec | unsigned long riovcnt | unsigned long flags |
| 377 | process_vm_writev | [man/](http://man7.org/linux/man-pages/man2/process_vm_writev.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*process_vm_writev+package:^chromeos_public$) | 0x179 | pid\_t pid | const struct iovec \*lvec | unsigned long liovcnt | const struct iovec \*rvec | unsigned long riovcnt | unsigned long flags |
| 378 | kcmp | [man/](http://man7.org/linux/man-pages/man2/kcmp.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*kcmp+package:^chromeos_public$) | 0x17a | pid\_t pid1 | pid\_t pid2 | int type | unsigned long idx1 | unsigned long idx2 | - |
| 379 | finit_module | [man/](http://man7.org/linux/man-pages/man2/finit_module.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*finit_module+package:^chromeos_public$) | 0x17b | int fd | const char \*uargs | int flags | - | - | - |
| 380 | sched_setattr | [man/](http://man7.org/linux/man-pages/man2/sched_setattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_setattr+package:^chromeos_public$) | 0x17c | pid\_t pid | struct sched\_attr \*attr | unsigned int flags | - | - | - |
| 381 | sched_getattr | [man/](http://man7.org/linux/man-pages/man2/sched_getattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_getattr+package:^chromeos_public$) | 0x17d | pid\_t pid | struct sched\_attr \*attr | unsigned int size | unsigned int flags | - | - |
| 382 | renameat2 | [man/](http://man7.org/linux/man-pages/man2/renameat2.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*renameat2+package:^chromeos_public$) | 0x17e | int olddfd | const char \*oldname | int newdfd | const char \*newname | unsigned int flags | - |
| 383 | seccomp | [man/](http://man7.org/linux/man-pages/man2/seccomp.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*seccomp+package:^chromeos_public$) | 0x17f | unsigned int op | unsigned int flags | const char \*uargs | - | - | - |
| 384 | getrandom | [man/](http://man7.org/linux/man-pages/man2/getrandom.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getrandom+package:^chromeos_public$) | 0x180 | char \*buf | size\_t count | unsigned int flags | - | - | - |
| 385 | memfd_create | [man/](http://man7.org/linux/man-pages/man2/memfd_create.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*memfd_create+package:^chromeos_public$) | 0x181 | const char \*uname\_ptr | unsigned int flags | - | - | - | - |
| 386 | bpf | [man/](http://man7.org/linux/man-pages/man2/bpf.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*bpf+package:^chromeos_public$) | 0x182 | int cmd | union bpf\_attr \*attr | unsigned int size | - | - | - |
| 387 | execveat | [man/](http://man7.org/linux/man-pages/man2/execveat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*execveat+package:^chromeos_public$) | 0x183 | int dfd | const char \*filename | const char \*const \*argv | const char \*const \*envp | int flags | - |
| 388 | userfaultfd | [man/](http://man7.org/linux/man-pages/man2/userfaultfd.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*userfaultfd+package:^chromeos_public$) | 0x184 | int flags | - | - | - | - | - |
| 389 | membarrier | [man/](http://man7.org/linux/man-pages/man2/membarrier.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*membarrier+package:^chromeos_public$) | 0x185 | int cmd | int flags | - | - | - | - |
| 390 | mlock2 | [man/](http://man7.org/linux/man-pages/man2/mlock2.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mlock2+package:^chromeos_public$) | 0x186 | unsigned long start | size\_t len | int flags | - | - | - |
| 391 | copy_file_range | [man/](http://man7.org/linux/man-pages/man2/copy_file_range.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*copy_file_range+package:^chromeos_public$) | 0x187 | int fd\_in | loff\_t \*off\_in | int fd\_out | loff\_t \*off\_out | size\_t len | unsigned int flags |
| 392 | preadv2 | [man/](http://man7.org/linux/man-pages/man2/preadv2.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*preadv2+package:^chromeos_public$) | 0x188 | unsigned long fd | const struct iovec \*vec | unsigned long vlen | unsigned long pos\_l | unsigned long pos\_h | rwf\_t flags |
| 393 | pwritev2 | [man/](http://man7.org/linux/man-pages/man2/pwritev2.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pwritev2+package:^chromeos_public$) | 0x189 | unsigned long fd | const struct iovec \*vec | unsigned long vlen | unsigned long pos\_l | unsigned long pos\_h | rwf\_t flags |
| 394 | pkey_mprotect | [man/](http://man7.org/linux/man-pages/man2/pkey_mprotect.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pkey_mprotect+package:^chromeos_public$) | 0x18a | unsigned long start | size\_t len | unsigned long prot | int pkey | - | - |
| 395 | pkey_alloc | [man/](http://man7.org/linux/man-pages/man2/pkey_alloc.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pkey_alloc+package:^chromeos_public$) | 0x18b | unsigned long flags | unsigned long init\_val | - | - | - | - |
| 396 | pkey_free | [man/](http://man7.org/linux/man-pages/man2/pkey_free.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pkey_free+package:^chromeos_public$) | 0x18c | int pkey | - | - | - | - | - |
| 397 | statx | [man/](http://man7.org/linux/man-pages/man2/statx.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*statx+package:^chromeos_public$) | 0x18d | int dfd | const char \*path | unsigned flags | unsigned mask | struct statx \*buffer | - |
| 983041 | ARM_breakpoint | [man/](http://man7.org/linux/man-pages/man2/ARM_breakpoint.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ARM_breakpoint+package:^chromeos_public$) | 0xf0001 | ? | ? | ? | ? | ? | ? |
| 983042 | ARM_cacheflush | [man/](http://man7.org/linux/man-pages/man2/ARM_cacheflush.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ARM_cacheflush+package:^chromeos_public$) | 0xf0002 | ? | ? | ? | ? | ? | ? |
| 983043 | ARM_usr26 | [man/](http://man7.org/linux/man-pages/man2/ARM_usr26.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ARM_usr26+package:^chromeos_public$) | 0xf0003 | ? | ? | ? | ? | ? | ? |
| 983044 | ARM_usr32 | [man/](http://man7.org/linux/man-pages/man2/ARM_usr32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ARM_usr32+package:^chromeos_public$) | 0xf0004 | ? | ? | ? | ? | ? | ? |
| 983045 | ARM_set_tls | [man/](http://man7.org/linux/man-pages/man2/ARM_set_tls.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ARM_set_tls+package:^chromeos_public$) | 0xf0005 | ? | ? | ? | ? | ? | ? |

### arm64 (64-bit)

Compiled from [Linux 4.14.0 headers][linux-headers].

| NR | syscall name | references | %x8 | arg0 (%x0) | arg1 (%x1) | arg2 (%x2) | arg3 (%x3) | arg4 (%x4) | arg5 (%x5) |
|:---:|---|:---:|:---:|---|---|---|---|---|---|
| 0 | io_setup | [man/](http://man7.org/linux/man-pages/man2/io_setup.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*io_setup+package:^chromeos_public$) | 0x00 | unsigned nr\_reqs | aio\_context\_t \*ctx | - | - | - | - |
| 1 | io_destroy | [man/](http://man7.org/linux/man-pages/man2/io_destroy.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*io_destroy+package:^chromeos_public$) | 0x01 | aio\_context\_t ctx | - | - | - | - | - |
| 2 | io_submit | [man/](http://man7.org/linux/man-pages/man2/io_submit.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*io_submit+package:^chromeos_public$) | 0x02 | aio\_context\_t | long | struct iocb \* \* | - | - | - |
| 3 | io_cancel | [man/](http://man7.org/linux/man-pages/man2/io_cancel.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*io_cancel+package:^chromeos_public$) | 0x03 | aio\_context\_t ctx\_id | struct iocb \*iocb | struct io\_event \*result | - | - | - |
| 4 | io_getevents | [man/](http://man7.org/linux/man-pages/man2/io_getevents.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*io_getevents+package:^chromeos_public$) | 0x04 | aio\_context\_t ctx\_id | long min\_nr | long nr | struct io\_event \*events | struct timespec \*timeout | - |
| 5 | setxattr | [man/](http://man7.org/linux/man-pages/man2/setxattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setxattr+package:^chromeos_public$) | 0x05 | const char \*path | const char \*name | const void \*value | size\_t size | int flags | - |
| 6 | lsetxattr | [man/](http://man7.org/linux/man-pages/man2/lsetxattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*lsetxattr+package:^chromeos_public$) | 0x06 | const char \*path | const char \*name | const void \*value | size\_t size | int flags | - |
| 7 | fsetxattr | [man/](http://man7.org/linux/man-pages/man2/fsetxattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fsetxattr+package:^chromeos_public$) | 0x07 | int fd | const char \*name | const void \*value | size\_t size | int flags | - |
| 8 | getxattr | [man/](http://man7.org/linux/man-pages/man2/getxattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getxattr+package:^chromeos_public$) | 0x08 | const char \*path | const char \*name | void \*value | size\_t size | - | - |
| 9 | lgetxattr | [man/](http://man7.org/linux/man-pages/man2/lgetxattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*lgetxattr+package:^chromeos_public$) | 0x09 | const char \*path | const char \*name | void \*value | size\_t size | - | - |
| 10 | fgetxattr | [man/](http://man7.org/linux/man-pages/man2/fgetxattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fgetxattr+package:^chromeos_public$) | 0x0a | int fd | const char \*name | void \*value | size\_t size | - | - |
| 11 | listxattr | [man/](http://man7.org/linux/man-pages/man2/listxattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*listxattr+package:^chromeos_public$) | 0x0b | const char \*path | char \*list | size\_t size | - | - | - |
| 12 | llistxattr | [man/](http://man7.org/linux/man-pages/man2/llistxattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*llistxattr+package:^chromeos_public$) | 0x0c | const char \*path | char \*list | size\_t size | - | - | - |
| 13 | flistxattr | [man/](http://man7.org/linux/man-pages/man2/flistxattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*flistxattr+package:^chromeos_public$) | 0x0d | int fd | char \*list | size\_t size | - | - | - |
| 14 | removexattr | [man/](http://man7.org/linux/man-pages/man2/removexattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*removexattr+package:^chromeos_public$) | 0x0e | const char \*path | const char \*name | - | - | - | - |
| 15 | lremovexattr | [man/](http://man7.org/linux/man-pages/man2/lremovexattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*lremovexattr+package:^chromeos_public$) | 0x0f | const char \*path | const char \*name | - | - | - | - |
| 16 | fremovexattr | [man/](http://man7.org/linux/man-pages/man2/fremovexattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fremovexattr+package:^chromeos_public$) | 0x10 | int fd | const char \*name | - | - | - | - |
| 17 | getcwd | [man/](http://man7.org/linux/man-pages/man2/getcwd.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getcwd+package:^chromeos_public$) | 0x11 | char \*buf | unsigned long size | - | - | - | - |
| 18 | lookup_dcookie | [man/](http://man7.org/linux/man-pages/man2/lookup_dcookie.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*lookup_dcookie+package:^chromeos_public$) | 0x12 | u64 cookie64 | char \*buf | size\_t len | - | - | - |
| 19 | eventfd2 | [man/](http://man7.org/linux/man-pages/man2/eventfd2.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*eventfd2+package:^chromeos_public$) | 0x13 | unsigned int count | int flags | - | - | - | - |
| 20 | epoll_create1 | [man/](http://man7.org/linux/man-pages/man2/epoll_create1.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*epoll_create1+package:^chromeos_public$) | 0x14 | int flags | - | - | - | - | - |
| 21 | epoll_ctl | [man/](http://man7.org/linux/man-pages/man2/epoll_ctl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*epoll_ctl+package:^chromeos_public$) | 0x15 | int epfd | int op | int fd | struct epoll\_event \*event | - | - |
| 22 | epoll_pwait | [man/](http://man7.org/linux/man-pages/man2/epoll_pwait.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*epoll_pwait+package:^chromeos_public$) | 0x16 | int epfd | struct epoll\_event \*events | int maxevents | int timeout | const sigset\_t \*sigmask | size\_t sigsetsize |
| 23 | dup | [man/](http://man7.org/linux/man-pages/man2/dup.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*dup+package:^chromeos_public$) | 0x17 | unsigned int fildes | - | - | - | - | - |
| 24 | dup3 | [man/](http://man7.org/linux/man-pages/man2/dup3.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*dup3+package:^chromeos_public$) | 0x18 | unsigned int oldfd | unsigned int newfd | int flags | - | - | - |
| 25 | fcntl | [man/](http://man7.org/linux/man-pages/man2/fcntl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fcntl+package:^chromeos_public$) | 0x19 | unsigned int fd | unsigned int cmd | unsigned long arg | - | - | - |
| 26 | inotify_init1 | [man/](http://man7.org/linux/man-pages/man2/inotify_init1.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*inotify_init1+package:^chromeos_public$) | 0x1a | int flags | - | - | - | - | - |
| 27 | inotify_add_watch | [man/](http://man7.org/linux/man-pages/man2/inotify_add_watch.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*inotify_add_watch+package:^chromeos_public$) | 0x1b | int fd | const char \*path | u32 mask | - | - | - |
| 28 | inotify_rm_watch | [man/](http://man7.org/linux/man-pages/man2/inotify_rm_watch.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*inotify_rm_watch+package:^chromeos_public$) | 0x1c | int fd | \_\_s32 wd | - | - | - | - |
| 29 | ioctl | [man/](http://man7.org/linux/man-pages/man2/ioctl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ioctl+package:^chromeos_public$) | 0x1d | unsigned int fd | unsigned int cmd | unsigned long arg | - | - | - |
| 30 | ioprio_set | [man/](http://man7.org/linux/man-pages/man2/ioprio_set.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ioprio_set+package:^chromeos_public$) | 0x1e | int which | int who | int ioprio | - | - | - |
| 31 | ioprio_get | [man/](http://man7.org/linux/man-pages/man2/ioprio_get.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ioprio_get+package:^chromeos_public$) | 0x1f | int which | int who | - | - | - | - |
| 32 | flock | [man/](http://man7.org/linux/man-pages/man2/flock.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*flock+package:^chromeos_public$) | 0x20 | unsigned int fd | unsigned int cmd | - | - | - | - |
| 33 | mknodat | [man/](http://man7.org/linux/man-pages/man2/mknodat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mknodat+package:^chromeos_public$) | 0x21 | int dfd | const char \* filename | umode\_t mode | unsigned dev | - | - |
| 34 | mkdirat | [man/](http://man7.org/linux/man-pages/man2/mkdirat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mkdirat+package:^chromeos_public$) | 0x22 | int dfd | const char \* pathname | umode\_t mode | - | - | - |
| 35 | unlinkat | [man/](http://man7.org/linux/man-pages/man2/unlinkat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*unlinkat+package:^chromeos_public$) | 0x23 | int dfd | const char \* pathname | int flag | - | - | - |
| 36 | symlinkat | [man/](http://man7.org/linux/man-pages/man2/symlinkat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*symlinkat+package:^chromeos_public$) | 0x24 | const char \* oldname | int newdfd | const char \* newname | - | - | - |
| 37 | linkat | [man/](http://man7.org/linux/man-pages/man2/linkat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*linkat+package:^chromeos_public$) | 0x25 | int olddfd | const char \*oldname | int newdfd | const char \*newname | int flags | - |
| 38 | renameat | [man/](http://man7.org/linux/man-pages/man2/renameat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*renameat+package:^chromeos_public$) | 0x26 | int olddfd | const char \* oldname | int newdfd | const char \* newname | - | - |
| 39 | umount2 | [man/](http://man7.org/linux/man-pages/man2/umount2.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*umount2+package:^chromeos_public$) | 0x27 | ? | ? | ? | ? | ? | ? |
| 40 | mount | [man/](http://man7.org/linux/man-pages/man2/mount.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mount+package:^chromeos_public$) | 0x28 | char \*dev\_name | char \*dir\_name | char \*type | unsigned long flags | void \*data | - |
| 41 | pivot_root | [man/](http://man7.org/linux/man-pages/man2/pivot_root.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pivot_root+package:^chromeos_public$) | 0x29 | const char \*new\_root | const char \*put\_old | - | - | - | - |
| 42 | nfsservctl | [man/](http://man7.org/linux/man-pages/man2/nfsservctl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*nfsservctl+package:^chromeos_public$) | 0x2a | ? | ? | ? | ? | ? | ? |
| 43 | statfs | [man/](http://man7.org/linux/man-pages/man2/statfs.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*statfs+package:^chromeos_public$) | 0x2b | const char \* path | struct statfs \*buf | - | - | - | - |
| 44 | fstatfs | [man/](http://man7.org/linux/man-pages/man2/fstatfs.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fstatfs+package:^chromeos_public$) | 0x2c | unsigned int fd | struct statfs \*buf | - | - | - | - |
| 45 | truncate | [man/](http://man7.org/linux/man-pages/man2/truncate.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*truncate+package:^chromeos_public$) | 0x2d | const char \*path | long length | - | - | - | - |
| 46 | ftruncate | [man/](http://man7.org/linux/man-pages/man2/ftruncate.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ftruncate+package:^chromeos_public$) | 0x2e | unsigned int fd | unsigned long length | - | - | - | - |
| 47 | fallocate | [man/](http://man7.org/linux/man-pages/man2/fallocate.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fallocate+package:^chromeos_public$) | 0x2f | int fd | int mode | loff\_t offset | loff\_t len | - | - |
| 48 | faccessat | [man/](http://man7.org/linux/man-pages/man2/faccessat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*faccessat+package:^chromeos_public$) | 0x30 | int dfd | const char \*filename | int mode | - | - | - |
| 49 | chdir | [man/](http://man7.org/linux/man-pages/man2/chdir.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*chdir+package:^chromeos_public$) | 0x31 | const char \*filename | - | - | - | - | - |
| 50 | fchdir | [man/](http://man7.org/linux/man-pages/man2/fchdir.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fchdir+package:^chromeos_public$) | 0x32 | unsigned int fd | - | - | - | - | - |
| 51 | chroot | [man/](http://man7.org/linux/man-pages/man2/chroot.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*chroot+package:^chromeos_public$) | 0x33 | const char \*filename | - | - | - | - | - |
| 52 | fchmod | [man/](http://man7.org/linux/man-pages/man2/fchmod.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fchmod+package:^chromeos_public$) | 0x34 | unsigned int fd | umode\_t mode | - | - | - | - |
| 53 | fchmodat | [man/](http://man7.org/linux/man-pages/man2/fchmodat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fchmodat+package:^chromeos_public$) | 0x35 | int dfd | const char \* filename | umode\_t mode | - | - | - |
| 54 | fchownat | [man/](http://man7.org/linux/man-pages/man2/fchownat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fchownat+package:^chromeos_public$) | 0x36 | int dfd | const char \*filename | uid\_t user | gid\_t group | int flag | - |
| 55 | fchown | [man/](http://man7.org/linux/man-pages/man2/fchown.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fchown+package:^chromeos_public$) | 0x37 | unsigned int fd | uid\_t user | gid\_t group | - | - | - |
| 56 | openat | [man/](http://man7.org/linux/man-pages/man2/openat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*openat+package:^chromeos_public$) | 0x38 | int dfd | const char \*filename | int flags | umode\_t mode | - | - |
| 57 | close | [man/](http://man7.org/linux/man-pages/man2/close.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*close+package:^chromeos_public$) | 0x39 | unsigned int fd | - | - | - | - | - |
| 58 | vhangup | [man/](http://man7.org/linux/man-pages/man2/vhangup.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*vhangup+package:^chromeos_public$) | 0x3a | - | - | - | - | - | - |
| 59 | pipe2 | [man/](http://man7.org/linux/man-pages/man2/pipe2.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pipe2+package:^chromeos_public$) | 0x3b | int \*fildes | int flags | - | - | - | - |
| 60 | quotactl | [man/](http://man7.org/linux/man-pages/man2/quotactl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*quotactl+package:^chromeos_public$) | 0x3c | unsigned int cmd | const char \*special | qid\_t id | void \*addr | - | - |
| 61 | getdents64 | [man/](http://man7.org/linux/man-pages/man2/getdents64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getdents64+package:^chromeos_public$) | 0x3d | unsigned int fd | struct linux\_dirent64 \*dirent | unsigned int count | - | - | - |
| 62 | lseek | [man/](http://man7.org/linux/man-pages/man2/lseek.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*lseek+package:^chromeos_public$) | 0x3e | unsigned int fd | off\_t offset | unsigned int whence | - | - | - |
| 63 | read | [man/](http://man7.org/linux/man-pages/man2/read.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*read+package:^chromeos_public$) | 0x3f | unsigned int fd | char \*buf | size\_t count | - | - | - |
| 64 | write | [man/](http://man7.org/linux/man-pages/man2/write.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*write+package:^chromeos_public$) | 0x40 | unsigned int fd | const char \*buf | size\_t count | - | - | - |
| 65 | readv | [man/](http://man7.org/linux/man-pages/man2/readv.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*readv+package:^chromeos_public$) | 0x41 | unsigned long fd | const struct iovec \*vec | unsigned long vlen | - | - | - |
| 66 | writev | [man/](http://man7.org/linux/man-pages/man2/writev.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*writev+package:^chromeos_public$) | 0x42 | unsigned long fd | const struct iovec \*vec | unsigned long vlen | - | - | - |
| 67 | pread64 | [man/](http://man7.org/linux/man-pages/man2/pread64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pread64+package:^chromeos_public$) | 0x43 | unsigned int fd | char \*buf | size\_t count | loff\_t pos | - | - |
| 68 | pwrite64 | [man/](http://man7.org/linux/man-pages/man2/pwrite64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pwrite64+package:^chromeos_public$) | 0x44 | unsigned int fd | const char \*buf | size\_t count | loff\_t pos | - | - |
| 69 | preadv | [man/](http://man7.org/linux/man-pages/man2/preadv.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*preadv+package:^chromeos_public$) | 0x45 | unsigned long fd | const struct iovec \*vec | unsigned long vlen | unsigned long pos\_l | unsigned long pos\_h | - |
| 70 | pwritev | [man/](http://man7.org/linux/man-pages/man2/pwritev.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pwritev+package:^chromeos_public$) | 0x46 | unsigned long fd | const struct iovec \*vec | unsigned long vlen | unsigned long pos\_l | unsigned long pos\_h | - |
| 71 | sendfile | [man/](http://man7.org/linux/man-pages/man2/sendfile.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sendfile+package:^chromeos_public$) | 0x47 | int out\_fd | int in\_fd | off\_t \*offset | size\_t count | - | - |
| 72 | pselect6 | [man/](http://man7.org/linux/man-pages/man2/pselect6.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pselect6+package:^chromeos_public$) | 0x48 | int | fd\_set \* | fd\_set \* | fd\_set \* | struct timespec \* | void \* |
| 73 | ppoll | [man/](http://man7.org/linux/man-pages/man2/ppoll.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ppoll+package:^chromeos_public$) | 0x49 | struct pollfd \* | unsigned int | struct timespec \* | const sigset\_t \* | size\_t | - |
| 74 | signalfd4 | [man/](http://man7.org/linux/man-pages/man2/signalfd4.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*signalfd4+package:^chromeos_public$) | 0x4a | int ufd | sigset\_t \*user\_mask | size\_t sizemask | int flags | - | - |
| 75 | vmsplice | [man/](http://man7.org/linux/man-pages/man2/vmsplice.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*vmsplice+package:^chromeos_public$) | 0x4b | int fd | const struct iovec \*iov | unsigned long nr\_segs | unsigned int flags | - | - |
| 76 | splice | [man/](http://man7.org/linux/man-pages/man2/splice.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*splice+package:^chromeos_public$) | 0x4c | int fd\_in | loff\_t \*off\_in | int fd\_out | loff\_t \*off\_out | size\_t len | unsigned int flags |
| 77 | tee | [man/](http://man7.org/linux/man-pages/man2/tee.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*tee+package:^chromeos_public$) | 0x4d | int fdin | int fdout | size\_t len | unsigned int flags | - | - |
| 78 | readlinkat | [man/](http://man7.org/linux/man-pages/man2/readlinkat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*readlinkat+package:^chromeos_public$) | 0x4e | int dfd | const char \*path | char \*buf | int bufsiz | - | - |
| 79 | newfstatat | [man/](http://man7.org/linux/man-pages/man2/newfstatat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*newfstatat+package:^chromeos_public$) | 0x4f | int dfd | const char \*filename | struct stat \*statbuf | int flag | - | - |
| 80 | fstat | [man/](http://man7.org/linux/man-pages/man2/fstat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fstat+package:^chromeos_public$) | 0x50 | unsigned int fd | struct \_\_old\_kernel\_stat \*statbuf | - | - | - | - |
| 81 | sync | [man/](http://man7.org/linux/man-pages/man2/sync.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sync+package:^chromeos_public$) | 0x51 | - | - | - | - | - | - |
| 82 | fsync | [man/](http://man7.org/linux/man-pages/man2/fsync.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fsync+package:^chromeos_public$) | 0x52 | unsigned int fd | - | - | - | - | - |
| 83 | fdatasync | [man/](http://man7.org/linux/man-pages/man2/fdatasync.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fdatasync+package:^chromeos_public$) | 0x53 | unsigned int fd | - | - | - | - | - |
| 84 | sync_file_range | [man/](http://man7.org/linux/man-pages/man2/sync_file_range.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sync_file_range+package:^chromeos_public$) | 0x54 | int fd | loff\_t offset | loff\_t nbytes | unsigned int flags | - | - |
| 85 | timerfd_create | [man/](http://man7.org/linux/man-pages/man2/timerfd_create.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*timerfd_create+package:^chromeos_public$) | 0x55 | int clockid | int flags | - | - | - | - |
| 86 | timerfd_settime | [man/](http://man7.org/linux/man-pages/man2/timerfd_settime.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*timerfd_settime+package:^chromeos_public$) | 0x56 | int ufd | int flags | const struct \_\_kernel\_itimerspec \*utmr | struct \_\_kernel\_itimerspec \*otmr | - | - |
| 87 | timerfd_gettime | [man/](http://man7.org/linux/man-pages/man2/timerfd_gettime.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*timerfd_gettime+package:^chromeos_public$) | 0x57 | int ufd | struct \_\_kernel\_itimerspec \*otmr | - | - | - | - |
| 88 | utimensat | [man/](http://man7.org/linux/man-pages/man2/utimensat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*utimensat+package:^chromeos_public$) | 0x58 | int dfd | const char \*filename | struct timespec \*utimes | int flags | - | - |
| 89 | acct | [man/](http://man7.org/linux/man-pages/man2/acct.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*acct+package:^chromeos_public$) | 0x59 | const char \*name | - | - | - | - | - |
| 90 | capget | [man/](http://man7.org/linux/man-pages/man2/capget.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*capget+package:^chromeos_public$) | 0x5a | cap\_user\_header\_t header | cap\_user\_data\_t dataptr | - | - | - | - |
| 91 | capset | [man/](http://man7.org/linux/man-pages/man2/capset.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*capset+package:^chromeos_public$) | 0x5b | cap\_user\_header\_t header | const cap\_user\_data\_t data | - | - | - | - |
| 92 | personality | [man/](http://man7.org/linux/man-pages/man2/personality.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*personality+package:^chromeos_public$) | 0x5c | unsigned int personality | - | - | - | - | - |
| 93 | exit | [man/](http://man7.org/linux/man-pages/man2/exit.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*exit+package:^chromeos_public$) | 0x5d | int error\_code | - | - | - | - | - |
| 94 | exit_group | [man/](http://man7.org/linux/man-pages/man2/exit_group.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*exit_group+package:^chromeos_public$) | 0x5e | int error\_code | - | - | - | - | - |
| 95 | waitid | [man/](http://man7.org/linux/man-pages/man2/waitid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*waitid+package:^chromeos_public$) | 0x5f | int which | pid\_t pid | struct siginfo \*infop | int options | struct rusage \*ru | - |
| 96 | set_tid_address | [man/](http://man7.org/linux/man-pages/man2/set_tid_address.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*set_tid_address+package:^chromeos_public$) | 0x60 | int \*tidptr | - | - | - | - | - |
| 97 | unshare | [man/](http://man7.org/linux/man-pages/man2/unshare.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*unshare+package:^chromeos_public$) | 0x61 | unsigned long unshare\_flags | - | - | - | - | - |
| 98 | futex | [man/](http://man7.org/linux/man-pages/man2/futex.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*futex+package:^chromeos_public$) | 0x62 | u32 \*uaddr | int op | u32 val | struct timespec \*utime | u32 \*uaddr2 | u32 val3 |
| 99 | set_robust_list | [man/](http://man7.org/linux/man-pages/man2/set_robust_list.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*set_robust_list+package:^chromeos_public$) | 0x63 | struct robust\_list\_head \*head | size\_t len | - | - | - | - |
| 100 | get_robust_list | [man/](http://man7.org/linux/man-pages/man2/get_robust_list.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*get_robust_list+package:^chromeos_public$) | 0x64 | int pid | struct robust\_list\_head \* \*head\_ptr | size\_t \*len\_ptr | - | - | - |
| 101 | nanosleep | [man/](http://man7.org/linux/man-pages/man2/nanosleep.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*nanosleep+package:^chromeos_public$) | 0x65 | struct \_\_kernel\_timespec \*rqtp | struct \_\_kernel\_timespec \*rmtp | - | - | - | - |
| 102 | getitimer | [man/](http://man7.org/linux/man-pages/man2/getitimer.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getitimer+package:^chromeos_public$) | 0x66 | int which | struct itimerval \*value | - | - | - | - |
| 103 | setitimer | [man/](http://man7.org/linux/man-pages/man2/setitimer.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setitimer+package:^chromeos_public$) | 0x67 | int which | struct itimerval \*value | struct itimerval \*ovalue | - | - | - |
| 104 | kexec_load | [man/](http://man7.org/linux/man-pages/man2/kexec_load.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*kexec_load+package:^chromeos_public$) | 0x68 | unsigned long entry | unsigned long nr\_segments | struct kexec\_segment \*segments | unsigned long flags | - | - |
| 105 | init_module | [man/](http://man7.org/linux/man-pages/man2/init_module.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*init_module+package:^chromeos_public$) | 0x69 | void \*umod | unsigned long len | const char \*uargs | - | - | - |
| 106 | delete_module | [man/](http://man7.org/linux/man-pages/man2/delete_module.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*delete_module+package:^chromeos_public$) | 0x6a | const char \*name\_user | unsigned int flags | - | - | - | - |
| 107 | timer_create | [man/](http://man7.org/linux/man-pages/man2/timer_create.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*timer_create+package:^chromeos_public$) | 0x6b | clockid\_t which\_clock | struct sigevent \*timer\_event\_spec | timer\_t \* created\_timer\_id | - | - | - |
| 108 | timer_gettime | [man/](http://man7.org/linux/man-pages/man2/timer_gettime.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*timer_gettime+package:^chromeos_public$) | 0x6c | timer\_t timer\_id | struct \_\_kernel\_itimerspec \*setting | - | - | - | - |
| 109 | timer_getoverrun | [man/](http://man7.org/linux/man-pages/man2/timer_getoverrun.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*timer_getoverrun+package:^chromeos_public$) | 0x6d | timer\_t timer\_id | - | - | - | - | - |
| 110 | timer_settime | [man/](http://man7.org/linux/man-pages/man2/timer_settime.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*timer_settime+package:^chromeos_public$) | 0x6e | timer\_t timer\_id | int flags | const struct \_\_kernel\_itimerspec \*new\_setting | struct itimerspec \*old\_setting | - | - |
| 111 | timer_delete | [man/](http://man7.org/linux/man-pages/man2/timer_delete.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*timer_delete+package:^chromeos_public$) | 0x6f | timer\_t timer\_id | - | - | - | - | - |
| 112 | clock_settime | [man/](http://man7.org/linux/man-pages/man2/clock_settime.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*clock_settime+package:^chromeos_public$) | 0x70 | clockid\_t which\_clock | const struct \_\_kernel\_timespec \*tp | - | - | - | - |
| 113 | clock_gettime | [man/](http://man7.org/linux/man-pages/man2/clock_gettime.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*clock_gettime+package:^chromeos_public$) | 0x71 | clockid\_t which\_clock | struct \_\_kernel\_timespec \*tp | - | - | - | - |
| 114 | clock_getres | [man/](http://man7.org/linux/man-pages/man2/clock_getres.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*clock_getres+package:^chromeos_public$) | 0x72 | clockid\_t which\_clock | struct \_\_kernel\_timespec \*tp | - | - | - | - |
| 115 | clock_nanosleep | [man/](http://man7.org/linux/man-pages/man2/clock_nanosleep.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*clock_nanosleep+package:^chromeos_public$) | 0x73 | clockid\_t which\_clock | int flags | const struct \_\_kernel\_timespec \*rqtp | struct \_\_kernel\_timespec \*rmtp | - | - |
| 116 | syslog | [man/](http://man7.org/linux/man-pages/man2/syslog.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*syslog+package:^chromeos_public$) | 0x74 | int type | char \*buf | int len | - | - | - |
| 117 | ptrace | [man/](http://man7.org/linux/man-pages/man2/ptrace.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ptrace+package:^chromeos_public$) | 0x75 | long request | long pid | unsigned long addr | unsigned long data | - | - |
| 118 | sched_setparam | [man/](http://man7.org/linux/man-pages/man2/sched_setparam.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_setparam+package:^chromeos_public$) | 0x76 | pid\_t pid | struct sched\_param \*param | - | - | - | - |
| 119 | sched_setscheduler | [man/](http://man7.org/linux/man-pages/man2/sched_setscheduler.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_setscheduler+package:^chromeos_public$) | 0x77 | pid\_t pid | int policy | struct sched\_param \*param | - | - | - |
| 120 | sched_getscheduler | [man/](http://man7.org/linux/man-pages/man2/sched_getscheduler.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_getscheduler+package:^chromeos_public$) | 0x78 | pid\_t pid | - | - | - | - | - |
| 121 | sched_getparam | [man/](http://man7.org/linux/man-pages/man2/sched_getparam.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_getparam+package:^chromeos_public$) | 0x79 | pid\_t pid | struct sched\_param \*param | - | - | - | - |
| 122 | sched_setaffinity | [man/](http://man7.org/linux/man-pages/man2/sched_setaffinity.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_setaffinity+package:^chromeos_public$) | 0x7a | pid\_t pid | unsigned int len | unsigned long \*user\_mask\_ptr | - | - | - |
| 123 | sched_getaffinity | [man/](http://man7.org/linux/man-pages/man2/sched_getaffinity.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_getaffinity+package:^chromeos_public$) | 0x7b | pid\_t pid | unsigned int len | unsigned long \*user\_mask\_ptr | - | - | - |
| 124 | sched_yield | [man/](http://man7.org/linux/man-pages/man2/sched_yield.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_yield+package:^chromeos_public$) | 0x7c | - | - | - | - | - | - |
| 125 | sched_get_priority_max | [man/](http://man7.org/linux/man-pages/man2/sched_get_priority_max.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_get_priority_max+package:^chromeos_public$) | 0x7d | int policy | - | - | - | - | - |
| 126 | sched_get_priority_min | [man/](http://man7.org/linux/man-pages/man2/sched_get_priority_min.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_get_priority_min+package:^chromeos_public$) | 0x7e | int policy | - | - | - | - | - |
| 127 | sched_rr_get_interval | [man/](http://man7.org/linux/man-pages/man2/sched_rr_get_interval.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_rr_get_interval+package:^chromeos_public$) | 0x7f | pid\_t pid | struct timespec \*interval | - | - | - | - |
| 128 | restart_syscall | [man/](http://man7.org/linux/man-pages/man2/restart_syscall.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*restart_syscall+package:^chromeos_public$) | 0x80 | - | - | - | - | - | - |
| 129 | kill | [man/](http://man7.org/linux/man-pages/man2/kill.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*kill+package:^chromeos_public$) | 0x81 | pid\_t pid | int sig | - | - | - | - |
| 130 | tkill | [man/](http://man7.org/linux/man-pages/man2/tkill.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*tkill+package:^chromeos_public$) | 0x82 | pid\_t pid | int sig | - | - | - | - |
| 131 | tgkill | [man/](http://man7.org/linux/man-pages/man2/tgkill.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*tgkill+package:^chromeos_public$) | 0x83 | pid\_t tgid | pid\_t pid | int sig | - | - | - |
| 132 | sigaltstack | [man/](http://man7.org/linux/man-pages/man2/sigaltstack.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sigaltstack+package:^chromeos_public$) | 0x84 | const struct sigaltstack \*uss | struct sigaltstack \*uoss | - | - | - | - |
| 133 | rt_sigsuspend | [man/](http://man7.org/linux/man-pages/man2/rt_sigsuspend.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rt_sigsuspend+package:^chromeos_public$) | 0x85 | sigset\_t \*unewset | size\_t sigsetsize | - | - | - | - |
| 134 | rt_sigaction | [man/](http://man7.org/linux/man-pages/man2/rt_sigaction.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rt_sigaction+package:^chromeos_public$) | 0x86 | int | const struct sigaction \* | struct sigaction \* | size\_t | - | - |
| 135 | rt_sigprocmask | [man/](http://man7.org/linux/man-pages/man2/rt_sigprocmask.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rt_sigprocmask+package:^chromeos_public$) | 0x87 | int how | sigset\_t \*set | sigset\_t \*oset | size\_t sigsetsize | - | - |
| 136 | rt_sigpending | [man/](http://man7.org/linux/man-pages/man2/rt_sigpending.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rt_sigpending+package:^chromeos_public$) | 0x88 | sigset\_t \*set | size\_t sigsetsize | - | - | - | - |
| 137 | rt_sigtimedwait | [man/](http://man7.org/linux/man-pages/man2/rt_sigtimedwait.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rt_sigtimedwait+package:^chromeos_public$) | 0x89 | const sigset\_t \*uthese | siginfo\_t \*uinfo | const struct timespec \*uts | size\_t sigsetsize | - | - |
| 138 | rt_sigqueueinfo | [man/](http://man7.org/linux/man-pages/man2/rt_sigqueueinfo.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rt_sigqueueinfo+package:^chromeos_public$) | 0x8a | pid\_t pid | int sig | siginfo\_t \*uinfo | - | - | - |
| 139 | rt_sigreturn | [man/](http://man7.org/linux/man-pages/man2/rt_sigreturn.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rt_sigreturn+package:^chromeos_public$) | 0x8b | ? | ? | ? | ? | ? | ? |
| 140 | setpriority | [man/](http://man7.org/linux/man-pages/man2/setpriority.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setpriority+package:^chromeos_public$) | 0x8c | int which | int who | int niceval | - | - | - |
| 141 | getpriority | [man/](http://man7.org/linux/man-pages/man2/getpriority.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getpriority+package:^chromeos_public$) | 0x8d | int which | int who | - | - | - | - |
| 142 | reboot | [man/](http://man7.org/linux/man-pages/man2/reboot.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*reboot+package:^chromeos_public$) | 0x8e | int magic1 | int magic2 | unsigned int cmd | void \*arg | - | - |
| 143 | setregid | [man/](http://man7.org/linux/man-pages/man2/setregid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setregid+package:^chromeos_public$) | 0x8f | gid\_t rgid | gid\_t egid | - | - | - | - |
| 144 | setgid | [man/](http://man7.org/linux/man-pages/man2/setgid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setgid+package:^chromeos_public$) | 0x90 | gid\_t gid | - | - | - | - | - |
| 145 | setreuid | [man/](http://man7.org/linux/man-pages/man2/setreuid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setreuid+package:^chromeos_public$) | 0x91 | uid\_t ruid | uid\_t euid | - | - | - | - |
| 146 | setuid | [man/](http://man7.org/linux/man-pages/man2/setuid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setuid+package:^chromeos_public$) | 0x92 | uid\_t uid | - | - | - | - | - |
| 147 | setresuid | [man/](http://man7.org/linux/man-pages/man2/setresuid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setresuid+package:^chromeos_public$) | 0x93 | uid\_t ruid | uid\_t euid | uid\_t suid | - | - | - |
| 148 | getresuid | [man/](http://man7.org/linux/man-pages/man2/getresuid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getresuid+package:^chromeos_public$) | 0x94 | uid\_t \*ruid | uid\_t \*euid | uid\_t \*suid | - | - | - |
| 149 | setresgid | [man/](http://man7.org/linux/man-pages/man2/setresgid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setresgid+package:^chromeos_public$) | 0x95 | gid\_t rgid | gid\_t egid | gid\_t sgid | - | - | - |
| 150 | getresgid | [man/](http://man7.org/linux/man-pages/man2/getresgid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getresgid+package:^chromeos_public$) | 0x96 | gid\_t \*rgid | gid\_t \*egid | gid\_t \*sgid | - | - | - |
| 151 | setfsuid | [man/](http://man7.org/linux/man-pages/man2/setfsuid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setfsuid+package:^chromeos_public$) | 0x97 | uid\_t uid | - | - | - | - | - |
| 152 | setfsgid | [man/](http://man7.org/linux/man-pages/man2/setfsgid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setfsgid+package:^chromeos_public$) | 0x98 | gid\_t gid | - | - | - | - | - |
| 153 | times | [man/](http://man7.org/linux/man-pages/man2/times.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*times+package:^chromeos_public$) | 0x99 | struct tms \*tbuf | - | - | - | - | - |
| 154 | setpgid | [man/](http://man7.org/linux/man-pages/man2/setpgid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setpgid+package:^chromeos_public$) | 0x9a | pid\_t pid | pid\_t pgid | - | - | - | - |
| 155 | getpgid | [man/](http://man7.org/linux/man-pages/man2/getpgid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getpgid+package:^chromeos_public$) | 0x9b | pid\_t pid | - | - | - | - | - |
| 156 | getsid | [man/](http://man7.org/linux/man-pages/man2/getsid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getsid+package:^chromeos_public$) | 0x9c | pid\_t pid | - | - | - | - | - |
| 157 | setsid | [man/](http://man7.org/linux/man-pages/man2/setsid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setsid+package:^chromeos_public$) | 0x9d | - | - | - | - | - | - |
| 158 | getgroups | [man/](http://man7.org/linux/man-pages/man2/getgroups.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getgroups+package:^chromeos_public$) | 0x9e | int gidsetsize | gid\_t \*grouplist | - | - | - | - |
| 159 | setgroups | [man/](http://man7.org/linux/man-pages/man2/setgroups.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setgroups+package:^chromeos_public$) | 0x9f | int gidsetsize | gid\_t \*grouplist | - | - | - | - |
| 160 | uname | [man/](http://man7.org/linux/man-pages/man2/uname.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*uname+package:^chromeos_public$) | 0xa0 | struct old\_utsname \* | - | - | - | - | - |
| 161 | sethostname | [man/](http://man7.org/linux/man-pages/man2/sethostname.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sethostname+package:^chromeos_public$) | 0xa1 | char \*name | int len | - | - | - | - |
| 162 | setdomainname | [man/](http://man7.org/linux/man-pages/man2/setdomainname.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setdomainname+package:^chromeos_public$) | 0xa2 | char \*name | int len | - | - | - | - |
| 163 | getrlimit | [man/](http://man7.org/linux/man-pages/man2/getrlimit.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getrlimit+package:^chromeos_public$) | 0xa3 | unsigned int resource | struct rlimit \*rlim | - | - | - | - |
| 164 | setrlimit | [man/](http://man7.org/linux/man-pages/man2/setrlimit.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setrlimit+package:^chromeos_public$) | 0xa4 | unsigned int resource | struct rlimit \*rlim | - | - | - | - |
| 165 | getrusage | [man/](http://man7.org/linux/man-pages/man2/getrusage.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getrusage+package:^chromeos_public$) | 0xa5 | int who | struct rusage \*ru | - | - | - | - |
| 166 | umask | [man/](http://man7.org/linux/man-pages/man2/umask.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*umask+package:^chromeos_public$) | 0xa6 | int mask | - | - | - | - | - |
| 167 | prctl | [man/](http://man7.org/linux/man-pages/man2/prctl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*prctl+package:^chromeos_public$) | 0xa7 | int option | unsigned long arg2 | unsigned long arg3 | unsigned long arg4 | unsigned long arg5 | - |
| 168 | getcpu | [man/](http://man7.org/linux/man-pages/man2/getcpu.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getcpu+package:^chromeos_public$) | 0xa8 | unsigned \*cpu | unsigned \*node | struct getcpu\_cache \*cache | - | - | - |
| 169 | gettimeofday | [man/](http://man7.org/linux/man-pages/man2/gettimeofday.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*gettimeofday+package:^chromeos_public$) | 0xa9 | struct timeval \*tv | struct timezone \*tz | - | - | - | - |
| 170 | settimeofday | [man/](http://man7.org/linux/man-pages/man2/settimeofday.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*settimeofday+package:^chromeos_public$) | 0xaa | struct timeval \*tv | struct timezone \*tz | - | - | - | - |
| 171 | adjtimex | [man/](http://man7.org/linux/man-pages/man2/adjtimex.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*adjtimex+package:^chromeos_public$) | 0xab | struct timex \*txc\_p | - | - | - | - | - |
| 172 | getpid | [man/](http://man7.org/linux/man-pages/man2/getpid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getpid+package:^chromeos_public$) | 0xac | - | - | - | - | - | - |
| 173 | getppid | [man/](http://man7.org/linux/man-pages/man2/getppid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getppid+package:^chromeos_public$) | 0xad | - | - | - | - | - | - |
| 174 | getuid | [man/](http://man7.org/linux/man-pages/man2/getuid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getuid+package:^chromeos_public$) | 0xae | - | - | - | - | - | - |
| 175 | geteuid | [man/](http://man7.org/linux/man-pages/man2/geteuid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*geteuid+package:^chromeos_public$) | 0xaf | - | - | - | - | - | - |
| 176 | getgid | [man/](http://man7.org/linux/man-pages/man2/getgid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getgid+package:^chromeos_public$) | 0xb0 | - | - | - | - | - | - |
| 177 | getegid | [man/](http://man7.org/linux/man-pages/man2/getegid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getegid+package:^chromeos_public$) | 0xb1 | - | - | - | - | - | - |
| 178 | gettid | [man/](http://man7.org/linux/man-pages/man2/gettid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*gettid+package:^chromeos_public$) | 0xb2 | - | - | - | - | - | - |
| 179 | sysinfo | [man/](http://man7.org/linux/man-pages/man2/sysinfo.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sysinfo+package:^chromeos_public$) | 0xb3 | struct sysinfo \*info | - | - | - | - | - |
| 180 | mq_open | [man/](http://man7.org/linux/man-pages/man2/mq_open.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mq_open+package:^chromeos_public$) | 0xb4 | const char \*name | int oflag | umode\_t mode | struct mq\_attr \*attr | - | - |
| 181 | mq_unlink | [man/](http://man7.org/linux/man-pages/man2/mq_unlink.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mq_unlink+package:^chromeos_public$) | 0xb5 | const char \*name | - | - | - | - | - |
| 182 | mq_timedsend | [man/](http://man7.org/linux/man-pages/man2/mq_timedsend.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mq_timedsend+package:^chromeos_public$) | 0xb6 | mqd\_t mqdes | const char \*msg\_ptr | size\_t msg\_len | unsigned int msg\_prio | const struct \_\_kernel\_timespec \*abs\_timeout | - |
| 183 | mq_timedreceive | [man/](http://man7.org/linux/man-pages/man2/mq_timedreceive.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mq_timedreceive+package:^chromeos_public$) | 0xb7 | mqd\_t mqdes | char \*msg\_ptr | size\_t msg\_len | unsigned int \*msg\_prio | const struct \_\_kernel\_timespec \*abs\_timeout | - |
| 184 | mq_notify | [man/](http://man7.org/linux/man-pages/man2/mq_notify.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mq_notify+package:^chromeos_public$) | 0xb8 | mqd\_t mqdes | const struct sigevent \*notification | - | - | - | - |
| 185 | mq_getsetattr | [man/](http://man7.org/linux/man-pages/man2/mq_getsetattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mq_getsetattr+package:^chromeos_public$) | 0xb9 | mqd\_t mqdes | const struct mq\_attr \*mqstat | struct mq\_attr \*omqstat | - | - | - |
| 186 | msgget | [man/](http://man7.org/linux/man-pages/man2/msgget.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*msgget+package:^chromeos_public$) | 0xba | key\_t key | int msgflg | - | - | - | - |
| 187 | msgctl | [man/](http://man7.org/linux/man-pages/man2/msgctl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*msgctl+package:^chromeos_public$) | 0xbb | int msqid | int cmd | struct msqid\_ds \*buf | - | - | - |
| 188 | msgrcv | [man/](http://man7.org/linux/man-pages/man2/msgrcv.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*msgrcv+package:^chromeos_public$) | 0xbc | int msqid | struct msgbuf \*msgp | size\_t msgsz | long msgtyp | int msgflg | - |
| 189 | msgsnd | [man/](http://man7.org/linux/man-pages/man2/msgsnd.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*msgsnd+package:^chromeos_public$) | 0xbd | int msqid | struct msgbuf \*msgp | size\_t msgsz | int msgflg | - | - |
| 190 | semget | [man/](http://man7.org/linux/man-pages/man2/semget.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*semget+package:^chromeos_public$) | 0xbe | key\_t key | int nsems | int semflg | - | - | - |
| 191 | semctl | [man/](http://man7.org/linux/man-pages/man2/semctl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*semctl+package:^chromeos_public$) | 0xbf | int semid | int semnum | int cmd | unsigned long arg | - | - |
| 192 | semtimedop | [man/](http://man7.org/linux/man-pages/man2/semtimedop.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*semtimedop+package:^chromeos_public$) | 0xc0 | int semid | struct sembuf \*sops | unsigned nsops | const struct \_\_kernel\_timespec \*timeout | - | - |
| 193 | semop | [man/](http://man7.org/linux/man-pages/man2/semop.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*semop+package:^chromeos_public$) | 0xc1 | int semid | struct sembuf \*sops | unsigned nsops | - | - | - |
| 194 | shmget | [man/](http://man7.org/linux/man-pages/man2/shmget.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*shmget+package:^chromeos_public$) | 0xc2 | key\_t key | size\_t size | int flag | - | - | - |
| 195 | shmctl | [man/](http://man7.org/linux/man-pages/man2/shmctl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*shmctl+package:^chromeos_public$) | 0xc3 | int shmid | int cmd | struct shmid\_ds \*buf | - | - | - |
| 196 | shmat | [man/](http://man7.org/linux/man-pages/man2/shmat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*shmat+package:^chromeos_public$) | 0xc4 | int shmid | char \*shmaddr | int shmflg | - | - | - |
| 197 | shmdt | [man/](http://man7.org/linux/man-pages/man2/shmdt.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*shmdt+package:^chromeos_public$) | 0xc5 | char \*shmaddr | - | - | - | - | - |
| 198 | socket | [man/](http://man7.org/linux/man-pages/man2/socket.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*socket+package:^chromeos_public$) | 0xc6 | int | int | int | - | - | - |
| 199 | socketpair | [man/](http://man7.org/linux/man-pages/man2/socketpair.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*socketpair+package:^chromeos_public$) | 0xc7 | int | int | int | int \* | - | - |
| 200 | bind | [man/](http://man7.org/linux/man-pages/man2/bind.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*bind+package:^chromeos_public$) | 0xc8 | int | struct sockaddr \* | int | - | - | - |
| 201 | listen | [man/](http://man7.org/linux/man-pages/man2/listen.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*listen+package:^chromeos_public$) | 0xc9 | int | int | - | - | - | - |
| 202 | accept | [man/](http://man7.org/linux/man-pages/man2/accept.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*accept+package:^chromeos_public$) | 0xca | int | struct sockaddr \* | int \* | - | - | - |
| 203 | connect | [man/](http://man7.org/linux/man-pages/man2/connect.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*connect+package:^chromeos_public$) | 0xcb | int | struct sockaddr \* | int | - | - | - |
| 204 | getsockname | [man/](http://man7.org/linux/man-pages/man2/getsockname.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getsockname+package:^chromeos_public$) | 0xcc | int | struct sockaddr \* | int \* | - | - | - |
| 205 | getpeername | [man/](http://man7.org/linux/man-pages/man2/getpeername.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getpeername+package:^chromeos_public$) | 0xcd | int | struct sockaddr \* | int \* | - | - | - |
| 206 | sendto | [man/](http://man7.org/linux/man-pages/man2/sendto.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sendto+package:^chromeos_public$) | 0xce | int | void \* | size\_t | unsigned | struct sockaddr \* | int |
| 207 | recvfrom | [man/](http://man7.org/linux/man-pages/man2/recvfrom.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*recvfrom+package:^chromeos_public$) | 0xcf | int | void \* | size\_t | unsigned | struct sockaddr \* | int \* |
| 208 | setsockopt | [man/](http://man7.org/linux/man-pages/man2/setsockopt.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setsockopt+package:^chromeos_public$) | 0xd0 | int fd | int level | int optname | char \*optval | int optlen | - |
| 209 | getsockopt | [man/](http://man7.org/linux/man-pages/man2/getsockopt.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getsockopt+package:^chromeos_public$) | 0xd1 | int fd | int level | int optname | char \*optval | int \*optlen | - |
| 210 | shutdown | [man/](http://man7.org/linux/man-pages/man2/shutdown.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*shutdown+package:^chromeos_public$) | 0xd2 | int | int | - | - | - | - |
| 211 | sendmsg | [man/](http://man7.org/linux/man-pages/man2/sendmsg.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sendmsg+package:^chromeos_public$) | 0xd3 | int fd | struct user\_msghdr \*msg | unsigned flags | - | - | - |
| 212 | recvmsg | [man/](http://man7.org/linux/man-pages/man2/recvmsg.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*recvmsg+package:^chromeos_public$) | 0xd4 | int fd | struct user\_msghdr \*msg | unsigned flags | - | - | - |
| 213 | readahead | [man/](http://man7.org/linux/man-pages/man2/readahead.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*readahead+package:^chromeos_public$) | 0xd5 | int fd | loff\_t offset | size\_t count | - | - | - |
| 214 | brk | [man/](http://man7.org/linux/man-pages/man2/brk.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*brk+package:^chromeos_public$) | 0xd6 | unsigned long brk | - | - | - | - | - |
| 215 | munmap | [man/](http://man7.org/linux/man-pages/man2/munmap.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*munmap+package:^chromeos_public$) | 0xd7 | unsigned long addr | size\_t len | - | - | - | - |
| 216 | mremap | [man/](http://man7.org/linux/man-pages/man2/mremap.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mremap+package:^chromeos_public$) | 0xd8 | unsigned long addr | unsigned long old\_len | unsigned long new\_len | unsigned long flags | unsigned long new\_addr | - |
| 217 | add_key | [man/](http://man7.org/linux/man-pages/man2/add_key.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*add_key+package:^chromeos_public$) | 0xd9 | const char \*\_type | const char \*\_description | const void \*\_payload | size\_t plen | key\_serial\_t destringid | - |
| 218 | request_key | [man/](http://man7.org/linux/man-pages/man2/request_key.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*request_key+package:^chromeos_public$) | 0xda | const char \*\_type | const char \*\_description | const char \*\_callout\_info | key\_serial\_t destringid | - | - |
| 219 | keyctl | [man/](http://man7.org/linux/man-pages/man2/keyctl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*keyctl+package:^chromeos_public$) | 0xdb | int cmd | unsigned long arg2 | unsigned long arg3 | unsigned long arg4 | unsigned long arg5 | - |
| 220 | clone | [man/](http://man7.org/linux/man-pages/man2/clone.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*clone+package:^chromeos_public$) | 0xdc | unsigned long | unsigned long | int \* | int \* | unsigned long | - |
| 221 | execve | [man/](http://man7.org/linux/man-pages/man2/execve.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*execve+package:^chromeos_public$) | 0xdd | const char \*filename | const char \*const \*argv | const char \*const \*envp | - | - | - |
| 222 | mmap | [man/](http://man7.org/linux/man-pages/man2/mmap.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mmap+package:^chromeos_public$) | 0xde | ? | ? | ? | ? | ? | ? |
| 223 | fadvise64 | [man/](http://man7.org/linux/man-pages/man2/fadvise64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fadvise64+package:^chromeos_public$) | 0xdf | int fd | loff\_t offset | size\_t len | int advice | - | - |
| 224 | swapon | [man/](http://man7.org/linux/man-pages/man2/swapon.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*swapon+package:^chromeos_public$) | 0xe0 | const char \*specialfile | int swap\_flags | - | - | - | - |
| 225 | swapoff | [man/](http://man7.org/linux/man-pages/man2/swapoff.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*swapoff+package:^chromeos_public$) | 0xe1 | const char \*specialfile | - | - | - | - | - |
| 226 | mprotect | [man/](http://man7.org/linux/man-pages/man2/mprotect.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mprotect+package:^chromeos_public$) | 0xe2 | unsigned long start | size\_t len | unsigned long prot | - | - | - |
| 227 | msync | [man/](http://man7.org/linux/man-pages/man2/msync.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*msync+package:^chromeos_public$) | 0xe3 | unsigned long start | size\_t len | int flags | - | - | - |
| 228 | mlock | [man/](http://man7.org/linux/man-pages/man2/mlock.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mlock+package:^chromeos_public$) | 0xe4 | unsigned long start | size\_t len | - | - | - | - |
| 229 | munlock | [man/](http://man7.org/linux/man-pages/man2/munlock.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*munlock+package:^chromeos_public$) | 0xe5 | unsigned long start | size\_t len | - | - | - | - |
| 230 | mlockall | [man/](http://man7.org/linux/man-pages/man2/mlockall.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mlockall+package:^chromeos_public$) | 0xe6 | int flags | - | - | - | - | - |
| 231 | munlockall | [man/](http://man7.org/linux/man-pages/man2/munlockall.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*munlockall+package:^chromeos_public$) | 0xe7 | - | - | - | - | - | - |
| 232 | mincore | [man/](http://man7.org/linux/man-pages/man2/mincore.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mincore+package:^chromeos_public$) | 0xe8 | unsigned long start | size\_t len | unsigned char \* vec | - | - | - |
| 233 | madvise | [man/](http://man7.org/linux/man-pages/man2/madvise.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*madvise+package:^chromeos_public$) | 0xe9 | unsigned long start | size\_t len | int behavior | - | - | - |
| 234 | remap_file_pages | [man/](http://man7.org/linux/man-pages/man2/remap_file_pages.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*remap_file_pages+package:^chromeos_public$) | 0xea | unsigned long start | unsigned long size | unsigned long prot | unsigned long pgoff | unsigned long flags | - |
| 235 | mbind | [man/](http://man7.org/linux/man-pages/man2/mbind.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mbind+package:^chromeos_public$) | 0xeb | unsigned long start | unsigned long len | unsigned long mode | const unsigned long \*nmask | unsigned long maxnode | unsigned flags |
| 236 | get_mempolicy | [man/](http://man7.org/linux/man-pages/man2/get_mempolicy.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*get_mempolicy+package:^chromeos_public$) | 0xec | int \*policy | unsigned long \*nmask | unsigned long maxnode | unsigned long addr | unsigned long flags | - |
| 237 | set_mempolicy | [man/](http://man7.org/linux/man-pages/man2/set_mempolicy.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*set_mempolicy+package:^chromeos_public$) | 0xed | int mode | const unsigned long \*nmask | unsigned long maxnode | - | - | - |
| 238 | migrate_pages | [man/](http://man7.org/linux/man-pages/man2/migrate_pages.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*migrate_pages+package:^chromeos_public$) | 0xee | pid\_t pid | unsigned long maxnode | const unsigned long \*from | const unsigned long \*to | - | - |
| 239 | move_pages | [man/](http://man7.org/linux/man-pages/man2/move_pages.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*move_pages+package:^chromeos_public$) | 0xef | pid\_t pid | unsigned long nr\_pages | const void \* \*pages | const int \*nodes | int \*status | int flags |
| 240 | rt_tgsigqueueinfo | [man/](http://man7.org/linux/man-pages/man2/rt_tgsigqueueinfo.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rt_tgsigqueueinfo+package:^chromeos_public$) | 0xf0 | pid\_t tgid | pid\_t pid | int sig | siginfo\_t \*uinfo | - | - |
| 241 | perf_event_open | [man/](http://man7.org/linux/man-pages/man2/perf_event_open.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*perf_event_open+package:^chromeos_public$) | 0xf1 | struct perf\_event\_attr \*attr\_uptr | pid\_t pid | int cpu | int group\_fd | unsigned long flags | - |
| 242 | accept4 | [man/](http://man7.org/linux/man-pages/man2/accept4.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*accept4+package:^chromeos_public$) | 0xf2 | int | struct sockaddr \* | int \* | int | - | - |
| 243 | recvmmsg | [man/](http://man7.org/linux/man-pages/man2/recvmmsg.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*recvmmsg+package:^chromeos_public$) | 0xf3 | int fd | struct mmsghdr \*msg | unsigned int vlen | unsigned flags | struct timespec \*timeout | - |
| 244 | *not implemented* | | 0xf4 ||
| 245 | *not implemented* | | 0xf5 ||
| 246 | *not implemented* | | 0xf6 ||
| 247 | *not implemented* | | 0xf7 ||
| 248 | *not implemented* | | 0xf8 ||
| 249 | *not implemented* | | 0xf9 ||
| 250 | *not implemented* | | 0xfa ||
| 251 | *not implemented* | | 0xfb ||
| 252 | *not implemented* | | 0xfc ||
| 253 | *not implemented* | | 0xfd ||
| 254 | *not implemented* | | 0xfe ||
| 255 | *not implemented* | | 0xff ||
| 256 | *not implemented* | | 0x100 ||
| 257 | *not implemented* | | 0x101 ||
| 258 | *not implemented* | | 0x102 ||
| 259 | *not implemented* | | 0x103 ||
| 260 | wait4 | [man/](http://man7.org/linux/man-pages/man2/wait4.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*wait4+package:^chromeos_public$) | 0x104 | pid\_t pid | int \*stat\_addr | int options | struct rusage \*ru | - | - |
| 261 | prlimit64 | [man/](http://man7.org/linux/man-pages/man2/prlimit64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*prlimit64+package:^chromeos_public$) | 0x105 | pid\_t pid | unsigned int resource | const struct rlimit64 \*new\_rlim | struct rlimit64 \*old\_rlim | - | - |
| 262 | fanotify_init | [man/](http://man7.org/linux/man-pages/man2/fanotify_init.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fanotify_init+package:^chromeos_public$) | 0x106 | unsigned int flags | unsigned int event\_f\_flags | - | - | - | - |
| 263 | fanotify_mark | [man/](http://man7.org/linux/man-pages/man2/fanotify_mark.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fanotify_mark+package:^chromeos_public$) | 0x107 | int fanotify\_fd | unsigned int flags | u64 mask | int fd | const char \*pathname | - |
| 264 | name_to_handle_at | [man/](http://man7.org/linux/man-pages/man2/name_to_handle_at.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*name_to_handle_at+package:^chromeos_public$) | 0x108 | int dfd | const char \*name | struct file\_handle \*handle | int \*mnt\_id | int flag | - |
| 265 | open_by_handle_at | [man/](http://man7.org/linux/man-pages/man2/open_by_handle_at.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*open_by_handle_at+package:^chromeos_public$) | 0x109 | int mountdirfd | struct file\_handle \*handle | int flags | - | - | - |
| 266 | clock_adjtime | [man/](http://man7.org/linux/man-pages/man2/clock_adjtime.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*clock_adjtime+package:^chromeos_public$) | 0x10a | clockid\_t which\_clock | struct timex \*tx | - | - | - | - |
| 267 | syncfs | [man/](http://man7.org/linux/man-pages/man2/syncfs.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*syncfs+package:^chromeos_public$) | 0x10b | int fd | - | - | - | - | - |
| 268 | setns | [man/](http://man7.org/linux/man-pages/man2/setns.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setns+package:^chromeos_public$) | 0x10c | int fd | int nstype | - | - | - | - |
| 269 | sendmmsg | [man/](http://man7.org/linux/man-pages/man2/sendmmsg.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sendmmsg+package:^chromeos_public$) | 0x10d | int fd | struct mmsghdr \*msg | unsigned int vlen | unsigned flags | - | - |
| 270 | process_vm_readv | [man/](http://man7.org/linux/man-pages/man2/process_vm_readv.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*process_vm_readv+package:^chromeos_public$) | 0x10e | pid\_t pid | const struct iovec \*lvec | unsigned long liovcnt | const struct iovec \*rvec | unsigned long riovcnt | unsigned long flags |
| 271 | process_vm_writev | [man/](http://man7.org/linux/man-pages/man2/process_vm_writev.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*process_vm_writev+package:^chromeos_public$) | 0x10f | pid\_t pid | const struct iovec \*lvec | unsigned long liovcnt | const struct iovec \*rvec | unsigned long riovcnt | unsigned long flags |
| 272 | kcmp | [man/](http://man7.org/linux/man-pages/man2/kcmp.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*kcmp+package:^chromeos_public$) | 0x110 | pid\_t pid1 | pid\_t pid2 | int type | unsigned long idx1 | unsigned long idx2 | - |
| 273 | finit_module | [man/](http://man7.org/linux/man-pages/man2/finit_module.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*finit_module+package:^chromeos_public$) | 0x111 | int fd | const char \*uargs | int flags | - | - | - |
| 274 | sched_setattr | [man/](http://man7.org/linux/man-pages/man2/sched_setattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_setattr+package:^chromeos_public$) | 0x112 | pid\_t pid | struct sched\_attr \*attr | unsigned int flags | - | - | - |
| 275 | sched_getattr | [man/](http://man7.org/linux/man-pages/man2/sched_getattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_getattr+package:^chromeos_public$) | 0x113 | pid\_t pid | struct sched\_attr \*attr | unsigned int size | unsigned int flags | - | - |
| 276 | renameat2 | [man/](http://man7.org/linux/man-pages/man2/renameat2.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*renameat2+package:^chromeos_public$) | 0x114 | int olddfd | const char \*oldname | int newdfd | const char \*newname | unsigned int flags | - |
| 277 | seccomp | [man/](http://man7.org/linux/man-pages/man2/seccomp.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*seccomp+package:^chromeos_public$) | 0x115 | unsigned int op | unsigned int flags | const char \*uargs | - | - | - |
| 278 | getrandom | [man/](http://man7.org/linux/man-pages/man2/getrandom.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getrandom+package:^chromeos_public$) | 0x116 | char \*buf | size\_t count | unsigned int flags | - | - | - |
| 279 | memfd_create | [man/](http://man7.org/linux/man-pages/man2/memfd_create.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*memfd_create+package:^chromeos_public$) | 0x117 | const char \*uname\_ptr | unsigned int flags | - | - | - | - |
| 280 | bpf | [man/](http://man7.org/linux/man-pages/man2/bpf.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*bpf+package:^chromeos_public$) | 0x118 | int cmd | union bpf\_attr \*attr | unsigned int size | - | - | - |
| 281 | execveat | [man/](http://man7.org/linux/man-pages/man2/execveat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*execveat+package:^chromeos_public$) | 0x119 | int dfd | const char \*filename | const char \*const \*argv | const char \*const \*envp | int flags | - |
| 282 | userfaultfd | [man/](http://man7.org/linux/man-pages/man2/userfaultfd.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*userfaultfd+package:^chromeos_public$) | 0x11a | int flags | - | - | - | - | - |
| 283 | membarrier | [man/](http://man7.org/linux/man-pages/man2/membarrier.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*membarrier+package:^chromeos_public$) | 0x11b | int cmd | int flags | - | - | - | - |
| 284 | mlock2 | [man/](http://man7.org/linux/man-pages/man2/mlock2.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mlock2+package:^chromeos_public$) | 0x11c | unsigned long start | size\_t len | int flags | - | - | - |
| 285 | copy_file_range | [man/](http://man7.org/linux/man-pages/man2/copy_file_range.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*copy_file_range+package:^chromeos_public$) | 0x11d | int fd\_in | loff\_t \*off\_in | int fd\_out | loff\_t \*off\_out | size\_t len | unsigned int flags |
| 286 | preadv2 | [man/](http://man7.org/linux/man-pages/man2/preadv2.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*preadv2+package:^chromeos_public$) | 0x11e | unsigned long fd | const struct iovec \*vec | unsigned long vlen | unsigned long pos\_l | unsigned long pos\_h | rwf\_t flags |
| 287 | pwritev2 | [man/](http://man7.org/linux/man-pages/man2/pwritev2.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pwritev2+package:^chromeos_public$) | 0x11f | unsigned long fd | const struct iovec \*vec | unsigned long vlen | unsigned long pos\_l | unsigned long pos\_h | rwf\_t flags |
| 288 | pkey_mprotect | [man/](http://man7.org/linux/man-pages/man2/pkey_mprotect.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pkey_mprotect+package:^chromeos_public$) | 0x120 | unsigned long start | size\_t len | unsigned long prot | int pkey | - | - |
| 289 | pkey_alloc | [man/](http://man7.org/linux/man-pages/man2/pkey_alloc.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pkey_alloc+package:^chromeos_public$) | 0x121 | unsigned long flags | unsigned long init\_val | - | - | - | - |
| 290 | pkey_free | [man/](http://man7.org/linux/man-pages/man2/pkey_free.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pkey_free+package:^chromeos_public$) | 0x122 | int pkey | - | - | - | - | - |
| 291 | statx | [man/](http://man7.org/linux/man-pages/man2/statx.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*statx+package:^chromeos_public$) | 0x123 | int dfd | const char \*path | unsigned flags | unsigned mask | struct statx \*buffer | - |

### x86 (32-bit)

Compiled from [Linux 4.14.0 headers][linux-headers].

| NR | syscall name | references | %eax | arg0 (%ebx) | arg1 (%ecx) | arg2 (%edx) | arg3 (%esi) | arg4 (%edi) | arg5 (%ebp) |
|:---:|---|:---:|:---:|---|---|---|---|---|---|
| 0 | restart_syscall | [man/](http://man7.org/linux/man-pages/man2/restart_syscall.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*restart_syscall+package:^chromeos_public$) | 0x00 | - | - | - | - | - | - |
| 1 | exit | [man/](http://man7.org/linux/man-pages/man2/exit.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*exit+package:^chromeos_public$) | 0x01 | int error\_code | - | - | - | - | - |
| 2 | fork | [man/](http://man7.org/linux/man-pages/man2/fork.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fork+package:^chromeos_public$) | 0x02 | - | - | - | - | - | - |
| 3 | read | [man/](http://man7.org/linux/man-pages/man2/read.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*read+package:^chromeos_public$) | 0x03 | unsigned int fd | char \*buf | size\_t count | - | - | - |
| 4 | write | [man/](http://man7.org/linux/man-pages/man2/write.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*write+package:^chromeos_public$) | 0x04 | unsigned int fd | const char \*buf | size\_t count | - | - | - |
| 5 | open | [man/](http://man7.org/linux/man-pages/man2/open.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*open+package:^chromeos_public$) | 0x05 | const char \*filename | int flags | umode\_t mode | - | - | - |
| 6 | close | [man/](http://man7.org/linux/man-pages/man2/close.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*close+package:^chromeos_public$) | 0x06 | unsigned int fd | - | - | - | - | - |
| 7 | waitpid | [man/](http://man7.org/linux/man-pages/man2/waitpid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*waitpid+package:^chromeos_public$) | 0x07 | pid\_t pid | int \*stat\_addr | int options | - | - | - |
| 8 | creat | [man/](http://man7.org/linux/man-pages/man2/creat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*creat+package:^chromeos_public$) | 0x08 | const char \*pathname | umode\_t mode | - | - | - | - |
| 9 | link | [man/](http://man7.org/linux/man-pages/man2/link.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*link+package:^chromeos_public$) | 0x09 | const char \*oldname | const char \*newname | - | - | - | - |
| 10 | unlink | [man/](http://man7.org/linux/man-pages/man2/unlink.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*unlink+package:^chromeos_public$) | 0x0a | const char \*pathname | - | - | - | - | - |
| 11 | execve | [man/](http://man7.org/linux/man-pages/man2/execve.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*execve+package:^chromeos_public$) | 0x0b | const char \*filename | const char \*const \*argv | const char \*const \*envp | - | - | - |
| 12 | chdir | [man/](http://man7.org/linux/man-pages/man2/chdir.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*chdir+package:^chromeos_public$) | 0x0c | const char \*filename | - | - | - | - | - |
| 13 | time | [man/](http://man7.org/linux/man-pages/man2/time.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*time+package:^chromeos_public$) | 0x0d | time\_t \*tloc | - | - | - | - | - |
| 14 | mknod | [man/](http://man7.org/linux/man-pages/man2/mknod.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mknod+package:^chromeos_public$) | 0x0e | const char \*filename | umode\_t mode | unsigned dev | - | - | - |
| 15 | chmod | [man/](http://man7.org/linux/man-pages/man2/chmod.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*chmod+package:^chromeos_public$) | 0x0f | const char \*filename | umode\_t mode | - | - | - | - |
| 16 | lchown | [man/](http://man7.org/linux/man-pages/man2/lchown.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*lchown+package:^chromeos_public$) | 0x10 | const char \*filename | uid\_t user | gid\_t group | - | - | - |
| 17 | break | [man/](http://man7.org/linux/man-pages/man2/break.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*break+package:^chromeos_public$) | 0x11 | ? | ? | ? | ? | ? | ? |
| 18 | oldstat | [man/](http://man7.org/linux/man-pages/man2/oldstat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*oldstat+package:^chromeos_public$) | 0x12 | ? | ? | ? | ? | ? | ? |
| 19 | lseek | [man/](http://man7.org/linux/man-pages/man2/lseek.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*lseek+package:^chromeos_public$) | 0x13 | unsigned int fd | off\_t offset | unsigned int whence | - | - | - |
| 20 | getpid | [man/](http://man7.org/linux/man-pages/man2/getpid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getpid+package:^chromeos_public$) | 0x14 | - | - | - | - | - | - |
| 21 | mount | [man/](http://man7.org/linux/man-pages/man2/mount.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mount+package:^chromeos_public$) | 0x15 | char \*dev\_name | char \*dir\_name | char \*type | unsigned long flags | void \*data | - |
| 22 | umount | [man/](http://man7.org/linux/man-pages/man2/umount.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*umount+package:^chromeos_public$) | 0x16 | char \*name | int flags | - | - | - | - |
| 23 | setuid | [man/](http://man7.org/linux/man-pages/man2/setuid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setuid+package:^chromeos_public$) | 0x17 | uid\_t uid | - | - | - | - | - |
| 24 | getuid | [man/](http://man7.org/linux/man-pages/man2/getuid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getuid+package:^chromeos_public$) | 0x18 | - | - | - | - | - | - |
| 25 | stime | [man/](http://man7.org/linux/man-pages/man2/stime.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*stime+package:^chromeos_public$) | 0x19 | time\_t \*tptr | - | - | - | - | - |
| 26 | ptrace | [man/](http://man7.org/linux/man-pages/man2/ptrace.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ptrace+package:^chromeos_public$) | 0x1a | long request | long pid | unsigned long addr | unsigned long data | - | - |
| 27 | alarm | [man/](http://man7.org/linux/man-pages/man2/alarm.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*alarm+package:^chromeos_public$) | 0x1b | unsigned int seconds | - | - | - | - | - |
| 28 | oldfstat | [man/](http://man7.org/linux/man-pages/man2/oldfstat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*oldfstat+package:^chromeos_public$) | 0x1c | ? | ? | ? | ? | ? | ? |
| 29 | pause | [man/](http://man7.org/linux/man-pages/man2/pause.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pause+package:^chromeos_public$) | 0x1d | - | - | - | - | - | - |
| 30 | utime | [man/](http://man7.org/linux/man-pages/man2/utime.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*utime+package:^chromeos_public$) | 0x1e | char \*filename | struct utimbuf \*times | - | - | - | - |
| 31 | stty | [man/](http://man7.org/linux/man-pages/man2/stty.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*stty+package:^chromeos_public$) | 0x1f | ? | ? | ? | ? | ? | ? |
| 32 | gtty | [man/](http://man7.org/linux/man-pages/man2/gtty.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*gtty+package:^chromeos_public$) | 0x20 | ? | ? | ? | ? | ? | ? |
| 33 | access | [man/](http://man7.org/linux/man-pages/man2/access.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*access+package:^chromeos_public$) | 0x21 | const char \*filename | int mode | - | - | - | - |
| 34 | nice | [man/](http://man7.org/linux/man-pages/man2/nice.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*nice+package:^chromeos_public$) | 0x22 | int increment | - | - | - | - | - |
| 35 | ftime | [man/](http://man7.org/linux/man-pages/man2/ftime.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ftime+package:^chromeos_public$) | 0x23 | ? | ? | ? | ? | ? | ? |
| 36 | sync | [man/](http://man7.org/linux/man-pages/man2/sync.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sync+package:^chromeos_public$) | 0x24 | - | - | - | - | - | - |
| 37 | kill | [man/](http://man7.org/linux/man-pages/man2/kill.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*kill+package:^chromeos_public$) | 0x25 | pid\_t pid | int sig | - | - | - | - |
| 38 | rename | [man/](http://man7.org/linux/man-pages/man2/rename.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rename+package:^chromeos_public$) | 0x26 | const char \*oldname | const char \*newname | - | - | - | - |
| 39 | mkdir | [man/](http://man7.org/linux/man-pages/man2/mkdir.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mkdir+package:^chromeos_public$) | 0x27 | const char \*pathname | umode\_t mode | - | - | - | - |
| 40 | rmdir | [man/](http://man7.org/linux/man-pages/man2/rmdir.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rmdir+package:^chromeos_public$) | 0x28 | const char \*pathname | - | - | - | - | - |
| 41 | dup | [man/](http://man7.org/linux/man-pages/man2/dup.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*dup+package:^chromeos_public$) | 0x29 | unsigned int fildes | - | - | - | - | - |
| 42 | pipe | [man/](http://man7.org/linux/man-pages/man2/pipe.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pipe+package:^chromeos_public$) | 0x2a | int \*fildes | - | - | - | - | - |
| 43 | times | [man/](http://man7.org/linux/man-pages/man2/times.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*times+package:^chromeos_public$) | 0x2b | struct tms \*tbuf | - | - | - | - | - |
| 44 | prof | [man/](http://man7.org/linux/man-pages/man2/prof.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*prof+package:^chromeos_public$) | 0x2c | ? | ? | ? | ? | ? | ? |
| 45 | brk | [man/](http://man7.org/linux/man-pages/man2/brk.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*brk+package:^chromeos_public$) | 0x2d | unsigned long brk | - | - | - | - | - |
| 46 | setgid | [man/](http://man7.org/linux/man-pages/man2/setgid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setgid+package:^chromeos_public$) | 0x2e | gid\_t gid | - | - | - | - | - |
| 47 | getgid | [man/](http://man7.org/linux/man-pages/man2/getgid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getgid+package:^chromeos_public$) | 0x2f | - | - | - | - | - | - |
| 48 | signal | [man/](http://man7.org/linux/man-pages/man2/signal.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*signal+package:^chromeos_public$) | 0x30 | int sig | \_\_sighandler\_t handler | - | - | - | - |
| 49 | geteuid | [man/](http://man7.org/linux/man-pages/man2/geteuid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*geteuid+package:^chromeos_public$) | 0x31 | - | - | - | - | - | - |
| 50 | getegid | [man/](http://man7.org/linux/man-pages/man2/getegid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getegid+package:^chromeos_public$) | 0x32 | - | - | - | - | - | - |
| 51 | acct | [man/](http://man7.org/linux/man-pages/man2/acct.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*acct+package:^chromeos_public$) | 0x33 | const char \*name | - | - | - | - | - |
| 52 | umount2 | [man/](http://man7.org/linux/man-pages/man2/umount2.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*umount2+package:^chromeos_public$) | 0x34 | ? | ? | ? | ? | ? | ? |
| 53 | lock | [man/](http://man7.org/linux/man-pages/man2/lock.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*lock+package:^chromeos_public$) | 0x35 | ? | ? | ? | ? | ? | ? |
| 54 | ioctl | [man/](http://man7.org/linux/man-pages/man2/ioctl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ioctl+package:^chromeos_public$) | 0x36 | unsigned int fd | unsigned int cmd | unsigned long arg | - | - | - |
| 55 | fcntl | [man/](http://man7.org/linux/man-pages/man2/fcntl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fcntl+package:^chromeos_public$) | 0x37 | unsigned int fd | unsigned int cmd | unsigned long arg | - | - | - |
| 56 | mpx | [man/](http://man7.org/linux/man-pages/man2/mpx.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mpx+package:^chromeos_public$) | 0x38 | ? | ? | ? | ? | ? | ? |
| 57 | setpgid | [man/](http://man7.org/linux/man-pages/man2/setpgid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setpgid+package:^chromeos_public$) | 0x39 | pid\_t pid | pid\_t pgid | - | - | - | - |
| 58 | ulimit | [man/](http://man7.org/linux/man-pages/man2/ulimit.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ulimit+package:^chromeos_public$) | 0x3a | ? | ? | ? | ? | ? | ? |
| 59 | oldolduname | [man/](http://man7.org/linux/man-pages/man2/oldolduname.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*oldolduname+package:^chromeos_public$) | 0x3b | ? | ? | ? | ? | ? | ? |
| 60 | umask | [man/](http://man7.org/linux/man-pages/man2/umask.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*umask+package:^chromeos_public$) | 0x3c | int mask | - | - | - | - | - |
| 61 | chroot | [man/](http://man7.org/linux/man-pages/man2/chroot.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*chroot+package:^chromeos_public$) | 0x3d | const char \*filename | - | - | - | - | - |
| 62 | ustat | [man/](http://man7.org/linux/man-pages/man2/ustat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ustat+package:^chromeos_public$) | 0x3e | unsigned dev | struct ustat \*ubuf | - | - | - | - |
| 63 | dup2 | [man/](http://man7.org/linux/man-pages/man2/dup2.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*dup2+package:^chromeos_public$) | 0x3f | unsigned int oldfd | unsigned int newfd | - | - | - | - |
| 64 | getppid | [man/](http://man7.org/linux/man-pages/man2/getppid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getppid+package:^chromeos_public$) | 0x40 | - | - | - | - | - | - |
| 65 | getpgrp | [man/](http://man7.org/linux/man-pages/man2/getpgrp.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getpgrp+package:^chromeos_public$) | 0x41 | - | - | - | - | - | - |
| 66 | setsid | [man/](http://man7.org/linux/man-pages/man2/setsid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setsid+package:^chromeos_public$) | 0x42 | - | - | - | - | - | - |
| 67 | sigaction | [man/](http://man7.org/linux/man-pages/man2/sigaction.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sigaction+package:^chromeos_public$) | 0x43 | int | const struct old\_sigaction \* | struct old\_sigaction \* | - | - | - |
| 68 | sgetmask | [man/](http://man7.org/linux/man-pages/man2/sgetmask.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sgetmask+package:^chromeos_public$) | 0x44 | - | - | - | - | - | - |
| 69 | ssetmask | [man/](http://man7.org/linux/man-pages/man2/ssetmask.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ssetmask+package:^chromeos_public$) | 0x45 | int newmask | - | - | - | - | - |
| 70 | setreuid | [man/](http://man7.org/linux/man-pages/man2/setreuid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setreuid+package:^chromeos_public$) | 0x46 | uid\_t ruid | uid\_t euid | - | - | - | - |
| 71 | setregid | [man/](http://man7.org/linux/man-pages/man2/setregid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setregid+package:^chromeos_public$) | 0x47 | gid\_t rgid | gid\_t egid | - | - | - | - |
| 72 | sigsuspend | [man/](http://man7.org/linux/man-pages/man2/sigsuspend.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sigsuspend+package:^chromeos_public$) | 0x48 | int unused1 | int unused2 | old\_sigset\_t mask | - | - | - |
| 73 | sigpending | [man/](http://man7.org/linux/man-pages/man2/sigpending.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sigpending+package:^chromeos_public$) | 0x49 | old\_sigset\_t \*uset | - | - | - | - | - |
| 74 | sethostname | [man/](http://man7.org/linux/man-pages/man2/sethostname.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sethostname+package:^chromeos_public$) | 0x4a | char \*name | int len | - | - | - | - |
| 75 | setrlimit | [man/](http://man7.org/linux/man-pages/man2/setrlimit.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setrlimit+package:^chromeos_public$) | 0x4b | unsigned int resource | struct rlimit \*rlim | - | - | - | - |
| 76 | getrlimit | [man/](http://man7.org/linux/man-pages/man2/getrlimit.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getrlimit+package:^chromeos_public$) | 0x4c | unsigned int resource | struct rlimit \*rlim | - | - | - | - |
| 77 | getrusage | [man/](http://man7.org/linux/man-pages/man2/getrusage.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getrusage+package:^chromeos_public$) | 0x4d | int who | struct rusage \*ru | - | - | - | - |
| 78 | gettimeofday | [man/](http://man7.org/linux/man-pages/man2/gettimeofday.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*gettimeofday+package:^chromeos_public$) | 0x4e | struct timeval \*tv | struct timezone \*tz | - | - | - | - |
| 79 | settimeofday | [man/](http://man7.org/linux/man-pages/man2/settimeofday.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*settimeofday+package:^chromeos_public$) | 0x4f | struct timeval \*tv | struct timezone \*tz | - | - | - | - |
| 80 | getgroups | [man/](http://man7.org/linux/man-pages/man2/getgroups.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getgroups+package:^chromeos_public$) | 0x50 | int gidsetsize | gid\_t \*grouplist | - | - | - | - |
| 81 | setgroups | [man/](http://man7.org/linux/man-pages/man2/setgroups.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setgroups+package:^chromeos_public$) | 0x51 | int gidsetsize | gid\_t \*grouplist | - | - | - | - |
| 82 | select | [man/](http://man7.org/linux/man-pages/man2/select.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*select+package:^chromeos_public$) | 0x52 | int n | fd\_set \*inp | fd\_set \*outp | fd\_set \*exp | struct timeval \*tvp | - |
| 83 | symlink | [man/](http://man7.org/linux/man-pages/man2/symlink.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*symlink+package:^chromeos_public$) | 0x53 | const char \*old | const char \*new | - | - | - | - |
| 84 | oldlstat | [man/](http://man7.org/linux/man-pages/man2/oldlstat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*oldlstat+package:^chromeos_public$) | 0x54 | ? | ? | ? | ? | ? | ? |
| 85 | readlink | [man/](http://man7.org/linux/man-pages/man2/readlink.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*readlink+package:^chromeos_public$) | 0x55 | const char \*path | char \*buf | int bufsiz | - | - | - |
| 86 | uselib | [man/](http://man7.org/linux/man-pages/man2/uselib.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*uselib+package:^chromeos_public$) | 0x56 | const char \*library | - | - | - | - | - |
| 87 | swapon | [man/](http://man7.org/linux/man-pages/man2/swapon.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*swapon+package:^chromeos_public$) | 0x57 | const char \*specialfile | int swap\_flags | - | - | - | - |
| 88 | reboot | [man/](http://man7.org/linux/man-pages/man2/reboot.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*reboot+package:^chromeos_public$) | 0x58 | int magic1 | int magic2 | unsigned int cmd | void \*arg | - | - |
| 89 | readdir | [man/](http://man7.org/linux/man-pages/man2/readdir.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*readdir+package:^chromeos_public$) | 0x59 | ? | ? | ? | ? | ? | ? |
| 90 | mmap | [man/](http://man7.org/linux/man-pages/man2/mmap.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mmap+package:^chromeos_public$) | 0x5a | ? | ? | ? | ? | ? | ? |
| 91 | munmap | [man/](http://man7.org/linux/man-pages/man2/munmap.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*munmap+package:^chromeos_public$) | 0x5b | unsigned long addr | size\_t len | - | - | - | - |
| 92 | truncate | [man/](http://man7.org/linux/man-pages/man2/truncate.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*truncate+package:^chromeos_public$) | 0x5c | const char \*path | long length | - | - | - | - |
| 93 | ftruncate | [man/](http://man7.org/linux/man-pages/man2/ftruncate.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ftruncate+package:^chromeos_public$) | 0x5d | unsigned int fd | unsigned long length | - | - | - | - |
| 94 | fchmod | [man/](http://man7.org/linux/man-pages/man2/fchmod.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fchmod+package:^chromeos_public$) | 0x5e | unsigned int fd | umode\_t mode | - | - | - | - |
| 95 | fchown | [man/](http://man7.org/linux/man-pages/man2/fchown.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fchown+package:^chromeos_public$) | 0x5f | unsigned int fd | uid\_t user | gid\_t group | - | - | - |
| 96 | getpriority | [man/](http://man7.org/linux/man-pages/man2/getpriority.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getpriority+package:^chromeos_public$) | 0x60 | int which | int who | - | - | - | - |
| 97 | setpriority | [man/](http://man7.org/linux/man-pages/man2/setpriority.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setpriority+package:^chromeos_public$) | 0x61 | int which | int who | int niceval | - | - | - |
| 98 | profil | [man/](http://man7.org/linux/man-pages/man2/profil.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*profil+package:^chromeos_public$) | 0x62 | ? | ? | ? | ? | ? | ? |
| 99 | statfs | [man/](http://man7.org/linux/man-pages/man2/statfs.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*statfs+package:^chromeos_public$) | 0x63 | const char \* path | struct statfs \*buf | - | - | - | - |
| 100 | fstatfs | [man/](http://man7.org/linux/man-pages/man2/fstatfs.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fstatfs+package:^chromeos_public$) | 0x64 | unsigned int fd | struct statfs \*buf | - | - | - | - |
| 101 | ioperm | [man/](http://man7.org/linux/man-pages/man2/ioperm.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ioperm+package:^chromeos_public$) | 0x65 | unsigned long from | unsigned long num | int on | - | - | - |
| 102 | socketcall | [man/](http://man7.org/linux/man-pages/man2/socketcall.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*socketcall+package:^chromeos_public$) | 0x66 | int call | unsigned long \*args | - | - | - | - |
| 103 | syslog | [man/](http://man7.org/linux/man-pages/man2/syslog.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*syslog+package:^chromeos_public$) | 0x67 | int type | char \*buf | int len | - | - | - |
| 104 | setitimer | [man/](http://man7.org/linux/man-pages/man2/setitimer.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setitimer+package:^chromeos_public$) | 0x68 | int which | struct itimerval \*value | struct itimerval \*ovalue | - | - | - |
| 105 | getitimer | [man/](http://man7.org/linux/man-pages/man2/getitimer.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getitimer+package:^chromeos_public$) | 0x69 | int which | struct itimerval \*value | - | - | - | - |
| 106 | stat | [man/](http://man7.org/linux/man-pages/man2/stat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*stat+package:^chromeos_public$) | 0x6a | const char \*filename | struct \_\_old\_kernel\_stat \*statbuf | - | - | - | - |
| 107 | lstat | [man/](http://man7.org/linux/man-pages/man2/lstat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*lstat+package:^chromeos_public$) | 0x6b | const char \*filename | struct \_\_old\_kernel\_stat \*statbuf | - | - | - | - |
| 108 | fstat | [man/](http://man7.org/linux/man-pages/man2/fstat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fstat+package:^chromeos_public$) | 0x6c | unsigned int fd | struct \_\_old\_kernel\_stat \*statbuf | - | - | - | - |
| 109 | olduname | [man/](http://man7.org/linux/man-pages/man2/olduname.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*olduname+package:^chromeos_public$) | 0x6d | struct oldold\_utsname \* | - | - | - | - | - |
| 110 | iopl | [man/](http://man7.org/linux/man-pages/man2/iopl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*iopl+package:^chromeos_public$) | 0x6e | ? | ? | ? | ? | ? | ? |
| 111 | vhangup | [man/](http://man7.org/linux/man-pages/man2/vhangup.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*vhangup+package:^chromeos_public$) | 0x6f | - | - | - | - | - | - |
| 112 | idle | [man/](http://man7.org/linux/man-pages/man2/idle.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*idle+package:^chromeos_public$) | 0x70 | ? | ? | ? | ? | ? | ? |
| 113 | vm86old | [man/](http://man7.org/linux/man-pages/man2/vm86old.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*vm86old+package:^chromeos_public$) | 0x71 | ? | ? | ? | ? | ? | ? |
| 114 | wait4 | [man/](http://man7.org/linux/man-pages/man2/wait4.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*wait4+package:^chromeos_public$) | 0x72 | pid\_t pid | int \*stat\_addr | int options | struct rusage \*ru | - | - |
| 115 | swapoff | [man/](http://man7.org/linux/man-pages/man2/swapoff.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*swapoff+package:^chromeos_public$) | 0x73 | const char \*specialfile | - | - | - | - | - |
| 116 | sysinfo | [man/](http://man7.org/linux/man-pages/man2/sysinfo.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sysinfo+package:^chromeos_public$) | 0x74 | struct sysinfo \*info | - | - | - | - | - |
| 117 | ipc | [man/](http://man7.org/linux/man-pages/man2/ipc.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ipc+package:^chromeos_public$) | 0x75 | unsigned int call | int first | unsigned long second | unsigned long third | void \*ptr | long fifth |
| 118 | fsync | [man/](http://man7.org/linux/man-pages/man2/fsync.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fsync+package:^chromeos_public$) | 0x76 | unsigned int fd | - | - | - | - | - |
| 119 | sigreturn | [man/](http://man7.org/linux/man-pages/man2/sigreturn.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sigreturn+package:^chromeos_public$) | 0x77 | ? | ? | ? | ? | ? | ? |
| 120 | clone | [man/](http://man7.org/linux/man-pages/man2/clone.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*clone+package:^chromeos_public$) | 0x78 | unsigned long | unsigned long | int \* | int \* | unsigned long | - |
| 121 | setdomainname | [man/](http://man7.org/linux/man-pages/man2/setdomainname.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setdomainname+package:^chromeos_public$) | 0x79 | char \*name | int len | - | - | - | - |
| 122 | uname | [man/](http://man7.org/linux/man-pages/man2/uname.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*uname+package:^chromeos_public$) | 0x7a | struct old\_utsname \* | - | - | - | - | - |
| 123 | modify_ldt | [man/](http://man7.org/linux/man-pages/man2/modify_ldt.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*modify_ldt+package:^chromeos_public$) | 0x7b | ? | ? | ? | ? | ? | ? |
| 124 | adjtimex | [man/](http://man7.org/linux/man-pages/man2/adjtimex.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*adjtimex+package:^chromeos_public$) | 0x7c | struct timex \*txc\_p | - | - | - | - | - |
| 125 | mprotect | [man/](http://man7.org/linux/man-pages/man2/mprotect.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mprotect+package:^chromeos_public$) | 0x7d | unsigned long start | size\_t len | unsigned long prot | - | - | - |
| 126 | sigprocmask | [man/](http://man7.org/linux/man-pages/man2/sigprocmask.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sigprocmask+package:^chromeos_public$) | 0x7e | int how | old\_sigset\_t \*set | old\_sigset\_t \*oset | - | - | - |
| 127 | create_module | [man/](http://man7.org/linux/man-pages/man2/create_module.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*create_module+package:^chromeos_public$) | 0x7f | ? | ? | ? | ? | ? | ? |
| 128 | init_module | [man/](http://man7.org/linux/man-pages/man2/init_module.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*init_module+package:^chromeos_public$) | 0x80 | void \*umod | unsigned long len | const char \*uargs | - | - | - |
| 129 | delete_module | [man/](http://man7.org/linux/man-pages/man2/delete_module.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*delete_module+package:^chromeos_public$) | 0x81 | const char \*name\_user | unsigned int flags | - | - | - | - |
| 130 | get_kernel_syms | [man/](http://man7.org/linux/man-pages/man2/get_kernel_syms.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*get_kernel_syms+package:^chromeos_public$) | 0x82 | ? | ? | ? | ? | ? | ? |
| 131 | quotactl | [man/](http://man7.org/linux/man-pages/man2/quotactl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*quotactl+package:^chromeos_public$) | 0x83 | unsigned int cmd | const char \*special | qid\_t id | void \*addr | - | - |
| 132 | getpgid | [man/](http://man7.org/linux/man-pages/man2/getpgid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getpgid+package:^chromeos_public$) | 0x84 | pid\_t pid | - | - | - | - | - |
| 133 | fchdir | [man/](http://man7.org/linux/man-pages/man2/fchdir.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fchdir+package:^chromeos_public$) | 0x85 | unsigned int fd | - | - | - | - | - |
| 134 | bdflush | [man/](http://man7.org/linux/man-pages/man2/bdflush.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*bdflush+package:^chromeos_public$) | 0x86 | int func | long data | - | - | - | - |
| 135 | sysfs | [man/](http://man7.org/linux/man-pages/man2/sysfs.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sysfs+package:^chromeos_public$) | 0x87 | int option | unsigned long arg1 | unsigned long arg2 | - | - | - |
| 136 | personality | [man/](http://man7.org/linux/man-pages/man2/personality.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*personality+package:^chromeos_public$) | 0x88 | unsigned int personality | - | - | - | - | - |
| 137 | afs_syscall | [man/](http://man7.org/linux/man-pages/man2/afs_syscall.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*afs_syscall+package:^chromeos_public$) | 0x89 | ? | ? | ? | ? | ? | ? |
| 138 | setfsuid | [man/](http://man7.org/linux/man-pages/man2/setfsuid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setfsuid+package:^chromeos_public$) | 0x8a | uid\_t uid | - | - | - | - | - |
| 139 | setfsgid | [man/](http://man7.org/linux/man-pages/man2/setfsgid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setfsgid+package:^chromeos_public$) | 0x8b | gid\_t gid | - | - | - | - | - |
| 140 | _llseek | [man/](http://man7.org/linux/man-pages/man2/_llseek.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*_llseek+package:^chromeos_public$) | 0x8c | ? | ? | ? | ? | ? | ? |
| 141 | getdents | [man/](http://man7.org/linux/man-pages/man2/getdents.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getdents+package:^chromeos_public$) | 0x8d | unsigned int fd | struct linux\_dirent \*dirent | unsigned int count | - | - | - |
| 142 | _newselect | [man/](http://man7.org/linux/man-pages/man2/_newselect.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*_newselect+package:^chromeos_public$) | 0x8e | ? | ? | ? | ? | ? | ? |
| 143 | flock | [man/](http://man7.org/linux/man-pages/man2/flock.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*flock+package:^chromeos_public$) | 0x8f | unsigned int fd | unsigned int cmd | - | - | - | - |
| 144 | msync | [man/](http://man7.org/linux/man-pages/man2/msync.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*msync+package:^chromeos_public$) | 0x90 | unsigned long start | size\_t len | int flags | - | - | - |
| 145 | readv | [man/](http://man7.org/linux/man-pages/man2/readv.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*readv+package:^chromeos_public$) | 0x91 | unsigned long fd | const struct iovec \*vec | unsigned long vlen | - | - | - |
| 146 | writev | [man/](http://man7.org/linux/man-pages/man2/writev.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*writev+package:^chromeos_public$) | 0x92 | unsigned long fd | const struct iovec \*vec | unsigned long vlen | - | - | - |
| 147 | getsid | [man/](http://man7.org/linux/man-pages/man2/getsid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getsid+package:^chromeos_public$) | 0x93 | pid\_t pid | - | - | - | - | - |
| 148 | fdatasync | [man/](http://man7.org/linux/man-pages/man2/fdatasync.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fdatasync+package:^chromeos_public$) | 0x94 | unsigned int fd | - | - | - | - | - |
| 149 | _sysctl | [man/](http://man7.org/linux/man-pages/man2/_sysctl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*_sysctl+package:^chromeos_public$) | 0x95 | ? | ? | ? | ? | ? | ? |
| 150 | mlock | [man/](http://man7.org/linux/man-pages/man2/mlock.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mlock+package:^chromeos_public$) | 0x96 | unsigned long start | size\_t len | - | - | - | - |
| 151 | munlock | [man/](http://man7.org/linux/man-pages/man2/munlock.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*munlock+package:^chromeos_public$) | 0x97 | unsigned long start | size\_t len | - | - | - | - |
| 152 | mlockall | [man/](http://man7.org/linux/man-pages/man2/mlockall.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mlockall+package:^chromeos_public$) | 0x98 | int flags | - | - | - | - | - |
| 153 | munlockall | [man/](http://man7.org/linux/man-pages/man2/munlockall.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*munlockall+package:^chromeos_public$) | 0x99 | - | - | - | - | - | - |
| 154 | sched_setparam | [man/](http://man7.org/linux/man-pages/man2/sched_setparam.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_setparam+package:^chromeos_public$) | 0x9a | pid\_t pid | struct sched\_param \*param | - | - | - | - |
| 155 | sched_getparam | [man/](http://man7.org/linux/man-pages/man2/sched_getparam.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_getparam+package:^chromeos_public$) | 0x9b | pid\_t pid | struct sched\_param \*param | - | - | - | - |
| 156 | sched_setscheduler | [man/](http://man7.org/linux/man-pages/man2/sched_setscheduler.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_setscheduler+package:^chromeos_public$) | 0x9c | pid\_t pid | int policy | struct sched\_param \*param | - | - | - |
| 157 | sched_getscheduler | [man/](http://man7.org/linux/man-pages/man2/sched_getscheduler.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_getscheduler+package:^chromeos_public$) | 0x9d | pid\_t pid | - | - | - | - | - |
| 158 | sched_yield | [man/](http://man7.org/linux/man-pages/man2/sched_yield.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_yield+package:^chromeos_public$) | 0x9e | - | - | - | - | - | - |
| 159 | sched_get_priority_max | [man/](http://man7.org/linux/man-pages/man2/sched_get_priority_max.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_get_priority_max+package:^chromeos_public$) | 0x9f | int policy | - | - | - | - | - |
| 160 | sched_get_priority_min | [man/](http://man7.org/linux/man-pages/man2/sched_get_priority_min.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_get_priority_min+package:^chromeos_public$) | 0xa0 | int policy | - | - | - | - | - |
| 161 | sched_rr_get_interval | [man/](http://man7.org/linux/man-pages/man2/sched_rr_get_interval.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_rr_get_interval+package:^chromeos_public$) | 0xa1 | pid\_t pid | struct timespec \*interval | - | - | - | - |
| 162 | nanosleep | [man/](http://man7.org/linux/man-pages/man2/nanosleep.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*nanosleep+package:^chromeos_public$) | 0xa2 | struct \_\_kernel\_timespec \*rqtp | struct \_\_kernel\_timespec \*rmtp | - | - | - | - |
| 163 | mremap | [man/](http://man7.org/linux/man-pages/man2/mremap.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mremap+package:^chromeos_public$) | 0xa3 | unsigned long addr | unsigned long old\_len | unsigned long new\_len | unsigned long flags | unsigned long new\_addr | - |
| 164 | setresuid | [man/](http://man7.org/linux/man-pages/man2/setresuid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setresuid+package:^chromeos_public$) | 0xa4 | uid\_t ruid | uid\_t euid | uid\_t suid | - | - | - |
| 165 | getresuid | [man/](http://man7.org/linux/man-pages/man2/getresuid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getresuid+package:^chromeos_public$) | 0xa5 | uid\_t \*ruid | uid\_t \*euid | uid\_t \*suid | - | - | - |
| 166 | vm86 | [man/](http://man7.org/linux/man-pages/man2/vm86.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*vm86+package:^chromeos_public$) | 0xa6 | ? | ? | ? | ? | ? | ? |
| 167 | query_module | [man/](http://man7.org/linux/man-pages/man2/query_module.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*query_module+package:^chromeos_public$) | 0xa7 | ? | ? | ? | ? | ? | ? |
| 168 | poll | [man/](http://man7.org/linux/man-pages/man2/poll.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*poll+package:^chromeos_public$) | 0xa8 | struct pollfd \*ufds | unsigned int nfds | int timeout | - | - | - |
| 169 | nfsservctl | [man/](http://man7.org/linux/man-pages/man2/nfsservctl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*nfsservctl+package:^chromeos_public$) | 0xa9 | ? | ? | ? | ? | ? | ? |
| 170 | setresgid | [man/](http://man7.org/linux/man-pages/man2/setresgid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setresgid+package:^chromeos_public$) | 0xaa | gid\_t rgid | gid\_t egid | gid\_t sgid | - | - | - |
| 171 | getresgid | [man/](http://man7.org/linux/man-pages/man2/getresgid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getresgid+package:^chromeos_public$) | 0xab | gid\_t \*rgid | gid\_t \*egid | gid\_t \*sgid | - | - | - |
| 172 | prctl | [man/](http://man7.org/linux/man-pages/man2/prctl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*prctl+package:^chromeos_public$) | 0xac | int option | unsigned long arg2 | unsigned long arg3 | unsigned long arg4 | unsigned long arg5 | - |
| 173 | rt_sigreturn | [man/](http://man7.org/linux/man-pages/man2/rt_sigreturn.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rt_sigreturn+package:^chromeos_public$) | 0xad | ? | ? | ? | ? | ? | ? |
| 174 | rt_sigaction | [man/](http://man7.org/linux/man-pages/man2/rt_sigaction.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rt_sigaction+package:^chromeos_public$) | 0xae | int | const struct sigaction \* | struct sigaction \* | size\_t | - | - |
| 175 | rt_sigprocmask | [man/](http://man7.org/linux/man-pages/man2/rt_sigprocmask.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rt_sigprocmask+package:^chromeos_public$) | 0xaf | int how | sigset\_t \*set | sigset\_t \*oset | size\_t sigsetsize | - | - |
| 176 | rt_sigpending | [man/](http://man7.org/linux/man-pages/man2/rt_sigpending.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rt_sigpending+package:^chromeos_public$) | 0xb0 | sigset\_t \*set | size\_t sigsetsize | - | - | - | - |
| 177 | rt_sigtimedwait | [man/](http://man7.org/linux/man-pages/man2/rt_sigtimedwait.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rt_sigtimedwait+package:^chromeos_public$) | 0xb1 | const sigset\_t \*uthese | siginfo\_t \*uinfo | const struct timespec \*uts | size\_t sigsetsize | - | - |
| 178 | rt_sigqueueinfo | [man/](http://man7.org/linux/man-pages/man2/rt_sigqueueinfo.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rt_sigqueueinfo+package:^chromeos_public$) | 0xb2 | pid\_t pid | int sig | siginfo\_t \*uinfo | - | - | - |
| 179 | rt_sigsuspend | [man/](http://man7.org/linux/man-pages/man2/rt_sigsuspend.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rt_sigsuspend+package:^chromeos_public$) | 0xb3 | sigset\_t \*unewset | size\_t sigsetsize | - | - | - | - |
| 180 | pread64 | [man/](http://man7.org/linux/man-pages/man2/pread64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pread64+package:^chromeos_public$) | 0xb4 | unsigned int fd | char \*buf | size\_t count | loff\_t pos | - | - |
| 181 | pwrite64 | [man/](http://man7.org/linux/man-pages/man2/pwrite64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pwrite64+package:^chromeos_public$) | 0xb5 | unsigned int fd | const char \*buf | size\_t count | loff\_t pos | - | - |
| 182 | chown | [man/](http://man7.org/linux/man-pages/man2/chown.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*chown+package:^chromeos_public$) | 0xb6 | const char \*filename | uid\_t user | gid\_t group | - | - | - |
| 183 | getcwd | [man/](http://man7.org/linux/man-pages/man2/getcwd.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getcwd+package:^chromeos_public$) | 0xb7 | char \*buf | unsigned long size | - | - | - | - |
| 184 | capget | [man/](http://man7.org/linux/man-pages/man2/capget.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*capget+package:^chromeos_public$) | 0xb8 | cap\_user\_header\_t header | cap\_user\_data\_t dataptr | - | - | - | - |
| 185 | capset | [man/](http://man7.org/linux/man-pages/man2/capset.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*capset+package:^chromeos_public$) | 0xb9 | cap\_user\_header\_t header | const cap\_user\_data\_t data | - | - | - | - |
| 186 | sigaltstack | [man/](http://man7.org/linux/man-pages/man2/sigaltstack.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sigaltstack+package:^chromeos_public$) | 0xba | const struct sigaltstack \*uss | struct sigaltstack \*uoss | - | - | - | - |
| 187 | sendfile | [man/](http://man7.org/linux/man-pages/man2/sendfile.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sendfile+package:^chromeos_public$) | 0xbb | int out\_fd | int in\_fd | off\_t \*offset | size\_t count | - | - |
| 188 | getpmsg | [man/](http://man7.org/linux/man-pages/man2/getpmsg.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getpmsg+package:^chromeos_public$) | 0xbc | ? | ? | ? | ? | ? | ? |
| 189 | putpmsg | [man/](http://man7.org/linux/man-pages/man2/putpmsg.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*putpmsg+package:^chromeos_public$) | 0xbd | ? | ? | ? | ? | ? | ? |
| 190 | vfork | [man/](http://man7.org/linux/man-pages/man2/vfork.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*vfork+package:^chromeos_public$) | 0xbe | - | - | - | - | - | - |
| 191 | ugetrlimit | [man/](http://man7.org/linux/man-pages/man2/ugetrlimit.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ugetrlimit+package:^chromeos_public$) | 0xbf | ? | ? | ? | ? | ? | ? |
| 192 | mmap2 | [man/](http://man7.org/linux/man-pages/man2/mmap2.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mmap2+package:^chromeos_public$) | 0xc0 | ? | ? | ? | ? | ? | ? |
| 193 | truncate64 | [man/](http://man7.org/linux/man-pages/man2/truncate64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*truncate64+package:^chromeos_public$) | 0xc1 | const char \*path | loff\_t length | - | - | - | - |
| 194 | ftruncate64 | [man/](http://man7.org/linux/man-pages/man2/ftruncate64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ftruncate64+package:^chromeos_public$) | 0xc2 | unsigned int fd | loff\_t length | - | - | - | - |
| 195 | stat64 | [man/](http://man7.org/linux/man-pages/man2/stat64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*stat64+package:^chromeos_public$) | 0xc3 | const char \*filename | struct stat64 \*statbuf | - | - | - | - |
| 196 | lstat64 | [man/](http://man7.org/linux/man-pages/man2/lstat64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*lstat64+package:^chromeos_public$) | 0xc4 | const char \*filename | struct stat64 \*statbuf | - | - | - | - |
| 197 | fstat64 | [man/](http://man7.org/linux/man-pages/man2/fstat64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fstat64+package:^chromeos_public$) | 0xc5 | unsigned long fd | struct stat64 \*statbuf | - | - | - | - |
| 198 | lchown32 | [man/](http://man7.org/linux/man-pages/man2/lchown32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*lchown32+package:^chromeos_public$) | 0xc6 | ? | ? | ? | ? | ? | ? |
| 199 | getuid32 | [man/](http://man7.org/linux/man-pages/man2/getuid32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getuid32+package:^chromeos_public$) | 0xc7 | ? | ? | ? | ? | ? | ? |
| 200 | getgid32 | [man/](http://man7.org/linux/man-pages/man2/getgid32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getgid32+package:^chromeos_public$) | 0xc8 | ? | ? | ? | ? | ? | ? |
| 201 | geteuid32 | [man/](http://man7.org/linux/man-pages/man2/geteuid32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*geteuid32+package:^chromeos_public$) | 0xc9 | ? | ? | ? | ? | ? | ? |
| 202 | getegid32 | [man/](http://man7.org/linux/man-pages/man2/getegid32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getegid32+package:^chromeos_public$) | 0xca | ? | ? | ? | ? | ? | ? |
| 203 | setreuid32 | [man/](http://man7.org/linux/man-pages/man2/setreuid32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setreuid32+package:^chromeos_public$) | 0xcb | ? | ? | ? | ? | ? | ? |
| 204 | setregid32 | [man/](http://man7.org/linux/man-pages/man2/setregid32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setregid32+package:^chromeos_public$) | 0xcc | ? | ? | ? | ? | ? | ? |
| 205 | getgroups32 | [man/](http://man7.org/linux/man-pages/man2/getgroups32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getgroups32+package:^chromeos_public$) | 0xcd | ? | ? | ? | ? | ? | ? |
| 206 | setgroups32 | [man/](http://man7.org/linux/man-pages/man2/setgroups32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setgroups32+package:^chromeos_public$) | 0xce | ? | ? | ? | ? | ? | ? |
| 207 | fchown32 | [man/](http://man7.org/linux/man-pages/man2/fchown32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fchown32+package:^chromeos_public$) | 0xcf | ? | ? | ? | ? | ? | ? |
| 208 | setresuid32 | [man/](http://man7.org/linux/man-pages/man2/setresuid32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setresuid32+package:^chromeos_public$) | 0xd0 | ? | ? | ? | ? | ? | ? |
| 209 | getresuid32 | [man/](http://man7.org/linux/man-pages/man2/getresuid32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getresuid32+package:^chromeos_public$) | 0xd1 | ? | ? | ? | ? | ? | ? |
| 210 | setresgid32 | [man/](http://man7.org/linux/man-pages/man2/setresgid32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setresgid32+package:^chromeos_public$) | 0xd2 | ? | ? | ? | ? | ? | ? |
| 211 | getresgid32 | [man/](http://man7.org/linux/man-pages/man2/getresgid32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getresgid32+package:^chromeos_public$) | 0xd3 | ? | ? | ? | ? | ? | ? |
| 212 | chown32 | [man/](http://man7.org/linux/man-pages/man2/chown32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*chown32+package:^chromeos_public$) | 0xd4 | ? | ? | ? | ? | ? | ? |
| 213 | setuid32 | [man/](http://man7.org/linux/man-pages/man2/setuid32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setuid32+package:^chromeos_public$) | 0xd5 | ? | ? | ? | ? | ? | ? |
| 214 | setgid32 | [man/](http://man7.org/linux/man-pages/man2/setgid32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setgid32+package:^chromeos_public$) | 0xd6 | ? | ? | ? | ? | ? | ? |
| 215 | setfsuid32 | [man/](http://man7.org/linux/man-pages/man2/setfsuid32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setfsuid32+package:^chromeos_public$) | 0xd7 | ? | ? | ? | ? | ? | ? |
| 216 | setfsgid32 | [man/](http://man7.org/linux/man-pages/man2/setfsgid32.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setfsgid32+package:^chromeos_public$) | 0xd8 | ? | ? | ? | ? | ? | ? |
| 217 | pivot_root | [man/](http://man7.org/linux/man-pages/man2/pivot_root.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pivot_root+package:^chromeos_public$) | 0xd9 | const char \*new\_root | const char \*put\_old | - | - | - | - |
| 218 | mincore | [man/](http://man7.org/linux/man-pages/man2/mincore.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mincore+package:^chromeos_public$) | 0xda | unsigned long start | size\_t len | unsigned char \* vec | - | - | - |
| 219 | madvise | [man/](http://man7.org/linux/man-pages/man2/madvise.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*madvise+package:^chromeos_public$) | 0xdb | unsigned long start | size\_t len | int behavior | - | - | - |
| 220 | getdents64 | [man/](http://man7.org/linux/man-pages/man2/getdents64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getdents64+package:^chromeos_public$) | 0xdc | unsigned int fd | struct linux\_dirent64 \*dirent | unsigned int count | - | - | - |
| 221 | fcntl64 | [man/](http://man7.org/linux/man-pages/man2/fcntl64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fcntl64+package:^chromeos_public$) | 0xdd | unsigned int fd | unsigned int cmd | unsigned long arg | - | - | - |
| 222 | *not implemented* | | 0xde ||
| 223 | *not implemented* | | 0xdf ||
| 224 | gettid | [man/](http://man7.org/linux/man-pages/man2/gettid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*gettid+package:^chromeos_public$) | 0xe0 | - | - | - | - | - | - |
| 225 | readahead | [man/](http://man7.org/linux/man-pages/man2/readahead.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*readahead+package:^chromeos_public$) | 0xe1 | int fd | loff\_t offset | size\_t count | - | - | - |
| 226 | setxattr | [man/](http://man7.org/linux/man-pages/man2/setxattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setxattr+package:^chromeos_public$) | 0xe2 | const char \*path | const char \*name | const void \*value | size\_t size | int flags | - |
| 227 | lsetxattr | [man/](http://man7.org/linux/man-pages/man2/lsetxattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*lsetxattr+package:^chromeos_public$) | 0xe3 | const char \*path | const char \*name | const void \*value | size\_t size | int flags | - |
| 228 | fsetxattr | [man/](http://man7.org/linux/man-pages/man2/fsetxattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fsetxattr+package:^chromeos_public$) | 0xe4 | int fd | const char \*name | const void \*value | size\_t size | int flags | - |
| 229 | getxattr | [man/](http://man7.org/linux/man-pages/man2/getxattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getxattr+package:^chromeos_public$) | 0xe5 | const char \*path | const char \*name | void \*value | size\_t size | - | - |
| 230 | lgetxattr | [man/](http://man7.org/linux/man-pages/man2/lgetxattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*lgetxattr+package:^chromeos_public$) | 0xe6 | const char \*path | const char \*name | void \*value | size\_t size | - | - |
| 231 | fgetxattr | [man/](http://man7.org/linux/man-pages/man2/fgetxattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fgetxattr+package:^chromeos_public$) | 0xe7 | int fd | const char \*name | void \*value | size\_t size | - | - |
| 232 | listxattr | [man/](http://man7.org/linux/man-pages/man2/listxattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*listxattr+package:^chromeos_public$) | 0xe8 | const char \*path | char \*list | size\_t size | - | - | - |
| 233 | llistxattr | [man/](http://man7.org/linux/man-pages/man2/llistxattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*llistxattr+package:^chromeos_public$) | 0xe9 | const char \*path | char \*list | size\_t size | - | - | - |
| 234 | flistxattr | [man/](http://man7.org/linux/man-pages/man2/flistxattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*flistxattr+package:^chromeos_public$) | 0xea | int fd | char \*list | size\_t size | - | - | - |
| 235 | removexattr | [man/](http://man7.org/linux/man-pages/man2/removexattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*removexattr+package:^chromeos_public$) | 0xeb | const char \*path | const char \*name | - | - | - | - |
| 236 | lremovexattr | [man/](http://man7.org/linux/man-pages/man2/lremovexattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*lremovexattr+package:^chromeos_public$) | 0xec | const char \*path | const char \*name | - | - | - | - |
| 237 | fremovexattr | [man/](http://man7.org/linux/man-pages/man2/fremovexattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fremovexattr+package:^chromeos_public$) | 0xed | int fd | const char \*name | - | - | - | - |
| 238 | tkill | [man/](http://man7.org/linux/man-pages/man2/tkill.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*tkill+package:^chromeos_public$) | 0xee | pid\_t pid | int sig | - | - | - | - |
| 239 | sendfile64 | [man/](http://man7.org/linux/man-pages/man2/sendfile64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sendfile64+package:^chromeos_public$) | 0xef | int out\_fd | int in\_fd | loff\_t \*offset | size\_t count | - | - |
| 240 | futex | [man/](http://man7.org/linux/man-pages/man2/futex.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*futex+package:^chromeos_public$) | 0xf0 | u32 \*uaddr | int op | u32 val | struct timespec \*utime | u32 \*uaddr2 | u32 val3 |
| 241 | sched_setaffinity | [man/](http://man7.org/linux/man-pages/man2/sched_setaffinity.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_setaffinity+package:^chromeos_public$) | 0xf1 | pid\_t pid | unsigned int len | unsigned long \*user\_mask\_ptr | - | - | - |
| 242 | sched_getaffinity | [man/](http://man7.org/linux/man-pages/man2/sched_getaffinity.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_getaffinity+package:^chromeos_public$) | 0xf2 | pid\_t pid | unsigned int len | unsigned long \*user\_mask\_ptr | - | - | - |
| 243 | set_thread_area | [man/](http://man7.org/linux/man-pages/man2/set_thread_area.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*set_thread_area+package:^chromeos_public$) | 0xf3 | ? | ? | ? | ? | ? | ? |
| 244 | get_thread_area | [man/](http://man7.org/linux/man-pages/man2/get_thread_area.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*get_thread_area+package:^chromeos_public$) | 0xf4 | ? | ? | ? | ? | ? | ? |
| 245 | io_setup | [man/](http://man7.org/linux/man-pages/man2/io_setup.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*io_setup+package:^chromeos_public$) | 0xf5 | unsigned nr\_reqs | aio\_context\_t \*ctx | - | - | - | - |
| 246 | io_destroy | [man/](http://man7.org/linux/man-pages/man2/io_destroy.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*io_destroy+package:^chromeos_public$) | 0xf6 | aio\_context\_t ctx | - | - | - | - | - |
| 247 | io_getevents | [man/](http://man7.org/linux/man-pages/man2/io_getevents.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*io_getevents+package:^chromeos_public$) | 0xf7 | aio\_context\_t ctx\_id | long min\_nr | long nr | struct io\_event \*events | struct timespec \*timeout | - |
| 248 | io_submit | [man/](http://man7.org/linux/man-pages/man2/io_submit.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*io_submit+package:^chromeos_public$) | 0xf8 | aio\_context\_t | long | struct iocb \* \* | - | - | - |
| 249 | io_cancel | [man/](http://man7.org/linux/man-pages/man2/io_cancel.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*io_cancel+package:^chromeos_public$) | 0xf9 | aio\_context\_t ctx\_id | struct iocb \*iocb | struct io\_event \*result | - | - | - |
| 250 | fadvise64 | [man/](http://man7.org/linux/man-pages/man2/fadvise64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fadvise64+package:^chromeos_public$) | 0xfa | int fd | loff\_t offset | size\_t len | int advice | - | - |
| 251 | *not implemented* | | 0xfb ||
| 252 | exit_group | [man/](http://man7.org/linux/man-pages/man2/exit_group.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*exit_group+package:^chromeos_public$) | 0xfc | int error\_code | - | - | - | - | - |
| 253 | lookup_dcookie | [man/](http://man7.org/linux/man-pages/man2/lookup_dcookie.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*lookup_dcookie+package:^chromeos_public$) | 0xfd | u64 cookie64 | char \*buf | size\_t len | - | - | - |
| 254 | epoll_create | [man/](http://man7.org/linux/man-pages/man2/epoll_create.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*epoll_create+package:^chromeos_public$) | 0xfe | int size | - | - | - | - | - |
| 255 | epoll_ctl | [man/](http://man7.org/linux/man-pages/man2/epoll_ctl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*epoll_ctl+package:^chromeos_public$) | 0xff | int epfd | int op | int fd | struct epoll\_event \*event | - | - |
| 256 | epoll_wait | [man/](http://man7.org/linux/man-pages/man2/epoll_wait.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*epoll_wait+package:^chromeos_public$) | 0x100 | int epfd | struct epoll\_event \*events | int maxevents | int timeout | - | - |
| 257 | remap_file_pages | [man/](http://man7.org/linux/man-pages/man2/remap_file_pages.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*remap_file_pages+package:^chromeos_public$) | 0x101 | unsigned long start | unsigned long size | unsigned long prot | unsigned long pgoff | unsigned long flags | - |
| 258 | set_tid_address | [man/](http://man7.org/linux/man-pages/man2/set_tid_address.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*set_tid_address+package:^chromeos_public$) | 0x102 | int \*tidptr | - | - | - | - | - |
| 259 | timer_create | [man/](http://man7.org/linux/man-pages/man2/timer_create.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*timer_create+package:^chromeos_public$) | 0x103 | clockid\_t which\_clock | struct sigevent \*timer\_event\_spec | timer\_t \* created\_timer\_id | - | - | - |
| 260 | timer_settime | [man/](http://man7.org/linux/man-pages/man2/timer_settime.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*timer_settime+package:^chromeos_public$) | 0x104 | timer\_t timer\_id | int flags | const struct \_\_kernel\_itimerspec \*new\_setting | struct itimerspec \*old\_setting | - | - |
| 261 | timer_gettime | [man/](http://man7.org/linux/man-pages/man2/timer_gettime.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*timer_gettime+package:^chromeos_public$) | 0x105 | timer\_t timer\_id | struct \_\_kernel\_itimerspec \*setting | - | - | - | - |
| 262 | timer_getoverrun | [man/](http://man7.org/linux/man-pages/man2/timer_getoverrun.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*timer_getoverrun+package:^chromeos_public$) | 0x106 | timer\_t timer\_id | - | - | - | - | - |
| 263 | timer_delete | [man/](http://man7.org/linux/man-pages/man2/timer_delete.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*timer_delete+package:^chromeos_public$) | 0x107 | timer\_t timer\_id | - | - | - | - | - |
| 264 | clock_settime | [man/](http://man7.org/linux/man-pages/man2/clock_settime.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*clock_settime+package:^chromeos_public$) | 0x108 | clockid\_t which\_clock | const struct \_\_kernel\_timespec \*tp | - | - | - | - |
| 265 | clock_gettime | [man/](http://man7.org/linux/man-pages/man2/clock_gettime.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*clock_gettime+package:^chromeos_public$) | 0x109 | clockid\_t which\_clock | struct \_\_kernel\_timespec \*tp | - | - | - | - |
| 266 | clock_getres | [man/](http://man7.org/linux/man-pages/man2/clock_getres.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*clock_getres+package:^chromeos_public$) | 0x10a | clockid\_t which\_clock | struct \_\_kernel\_timespec \*tp | - | - | - | - |
| 267 | clock_nanosleep | [man/](http://man7.org/linux/man-pages/man2/clock_nanosleep.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*clock_nanosleep+package:^chromeos_public$) | 0x10b | clockid\_t which\_clock | int flags | const struct \_\_kernel\_timespec \*rqtp | struct \_\_kernel\_timespec \*rmtp | - | - |
| 268 | statfs64 | [man/](http://man7.org/linux/man-pages/man2/statfs64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*statfs64+package:^chromeos_public$) | 0x10c | const char \*path | size\_t sz | struct statfs64 \*buf | - | - | - |
| 269 | fstatfs64 | [man/](http://man7.org/linux/man-pages/man2/fstatfs64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fstatfs64+package:^chromeos_public$) | 0x10d | unsigned int fd | size\_t sz | struct statfs64 \*buf | - | - | - |
| 270 | tgkill | [man/](http://man7.org/linux/man-pages/man2/tgkill.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*tgkill+package:^chromeos_public$) | 0x10e | pid\_t tgid | pid\_t pid | int sig | - | - | - |
| 271 | utimes | [man/](http://man7.org/linux/man-pages/man2/utimes.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*utimes+package:^chromeos_public$) | 0x10f | char \*filename | struct timeval \*utimes | - | - | - | - |
| 272 | fadvise64_64 | [man/](http://man7.org/linux/man-pages/man2/fadvise64_64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fadvise64_64+package:^chromeos_public$) | 0x110 | int fd | loff\_t offset | loff\_t len | int advice | - | - |
| 273 | vserver | [man/](http://man7.org/linux/man-pages/man2/vserver.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*vserver+package:^chromeos_public$) | 0x111 | ? | ? | ? | ? | ? | ? |
| 274 | mbind | [man/](http://man7.org/linux/man-pages/man2/mbind.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mbind+package:^chromeos_public$) | 0x112 | unsigned long start | unsigned long len | unsigned long mode | const unsigned long \*nmask | unsigned long maxnode | unsigned flags |
| 275 | get_mempolicy | [man/](http://man7.org/linux/man-pages/man2/get_mempolicy.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*get_mempolicy+package:^chromeos_public$) | 0x113 | int \*policy | unsigned long \*nmask | unsigned long maxnode | unsigned long addr | unsigned long flags | - |
| 276 | set_mempolicy | [man/](http://man7.org/linux/man-pages/man2/set_mempolicy.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*set_mempolicy+package:^chromeos_public$) | 0x114 | int mode | const unsigned long \*nmask | unsigned long maxnode | - | - | - |
| 277 | mq_open | [man/](http://man7.org/linux/man-pages/man2/mq_open.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mq_open+package:^chromeos_public$) | 0x115 | const char \*name | int oflag | umode\_t mode | struct mq\_attr \*attr | - | - |
| 278 | mq_unlink | [man/](http://man7.org/linux/man-pages/man2/mq_unlink.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mq_unlink+package:^chromeos_public$) | 0x116 | const char \*name | - | - | - | - | - |
| 279 | mq_timedsend | [man/](http://man7.org/linux/man-pages/man2/mq_timedsend.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mq_timedsend+package:^chromeos_public$) | 0x117 | mqd\_t mqdes | const char \*msg\_ptr | size\_t msg\_len | unsigned int msg\_prio | const struct \_\_kernel\_timespec \*abs\_timeout | - |
| 280 | mq_timedreceive | [man/](http://man7.org/linux/man-pages/man2/mq_timedreceive.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mq_timedreceive+package:^chromeos_public$) | 0x118 | mqd\_t mqdes | char \*msg\_ptr | size\_t msg\_len | unsigned int \*msg\_prio | const struct \_\_kernel\_timespec \*abs\_timeout | - |
| 281 | mq_notify | [man/](http://man7.org/linux/man-pages/man2/mq_notify.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mq_notify+package:^chromeos_public$) | 0x119 | mqd\_t mqdes | const struct sigevent \*notification | - | - | - | - |
| 282 | mq_getsetattr | [man/](http://man7.org/linux/man-pages/man2/mq_getsetattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mq_getsetattr+package:^chromeos_public$) | 0x11a | mqd\_t mqdes | const struct mq\_attr \*mqstat | struct mq\_attr \*omqstat | - | - | - |
| 283 | kexec_load | [man/](http://man7.org/linux/man-pages/man2/kexec_load.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*kexec_load+package:^chromeos_public$) | 0x11b | unsigned long entry | unsigned long nr\_segments | struct kexec\_segment \*segments | unsigned long flags | - | - |
| 284 | waitid | [man/](http://man7.org/linux/man-pages/man2/waitid.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*waitid+package:^chromeos_public$) | 0x11c | int which | pid\_t pid | struct siginfo \*infop | int options | struct rusage \*ru | - |
| 285 | *not implemented* | | 0x11d ||
| 286 | add_key | [man/](http://man7.org/linux/man-pages/man2/add_key.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*add_key+package:^chromeos_public$) | 0x11e | const char \*\_type | const char \*\_description | const void \*\_payload | size\_t plen | key\_serial\_t destringid | - |
| 287 | request_key | [man/](http://man7.org/linux/man-pages/man2/request_key.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*request_key+package:^chromeos_public$) | 0x11f | const char \*\_type | const char \*\_description | const char \*\_callout\_info | key\_serial\_t destringid | - | - |
| 288 | keyctl | [man/](http://man7.org/linux/man-pages/man2/keyctl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*keyctl+package:^chromeos_public$) | 0x120 | int cmd | unsigned long arg2 | unsigned long arg3 | unsigned long arg4 | unsigned long arg5 | - |
| 289 | ioprio_set | [man/](http://man7.org/linux/man-pages/man2/ioprio_set.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ioprio_set+package:^chromeos_public$) | 0x121 | int which | int who | int ioprio | - | - | - |
| 290 | ioprio_get | [man/](http://man7.org/linux/man-pages/man2/ioprio_get.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ioprio_get+package:^chromeos_public$) | 0x122 | int which | int who | - | - | - | - |
| 291 | inotify_init | [man/](http://man7.org/linux/man-pages/man2/inotify_init.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*inotify_init+package:^chromeos_public$) | 0x123 | - | - | - | - | - | - |
| 292 | inotify_add_watch | [man/](http://man7.org/linux/man-pages/man2/inotify_add_watch.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*inotify_add_watch+package:^chromeos_public$) | 0x124 | int fd | const char \*path | u32 mask | - | - | - |
| 293 | inotify_rm_watch | [man/](http://man7.org/linux/man-pages/man2/inotify_rm_watch.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*inotify_rm_watch+package:^chromeos_public$) | 0x125 | int fd | \_\_s32 wd | - | - | - | - |
| 294 | migrate_pages | [man/](http://man7.org/linux/man-pages/man2/migrate_pages.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*migrate_pages+package:^chromeos_public$) | 0x126 | pid\_t pid | unsigned long maxnode | const unsigned long \*from | const unsigned long \*to | - | - |
| 295 | openat | [man/](http://man7.org/linux/man-pages/man2/openat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*openat+package:^chromeos_public$) | 0x127 | int dfd | const char \*filename | int flags | umode\_t mode | - | - |
| 296 | mkdirat | [man/](http://man7.org/linux/man-pages/man2/mkdirat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mkdirat+package:^chromeos_public$) | 0x128 | int dfd | const char \* pathname | umode\_t mode | - | - | - |
| 297 | mknodat | [man/](http://man7.org/linux/man-pages/man2/mknodat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mknodat+package:^chromeos_public$) | 0x129 | int dfd | const char \* filename | umode\_t mode | unsigned dev | - | - |
| 298 | fchownat | [man/](http://man7.org/linux/man-pages/man2/fchownat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fchownat+package:^chromeos_public$) | 0x12a | int dfd | const char \*filename | uid\_t user | gid\_t group | int flag | - |
| 299 | futimesat | [man/](http://man7.org/linux/man-pages/man2/futimesat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*futimesat+package:^chromeos_public$) | 0x12b | int dfd | const char \*filename | struct timeval \*utimes | - | - | - |
| 300 | fstatat64 | [man/](http://man7.org/linux/man-pages/man2/fstatat64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fstatat64+package:^chromeos_public$) | 0x12c | int dfd | const char \*filename | struct stat64 \*statbuf | int flag | - | - |
| 301 | unlinkat | [man/](http://man7.org/linux/man-pages/man2/unlinkat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*unlinkat+package:^chromeos_public$) | 0x12d | int dfd | const char \* pathname | int flag | - | - | - |
| 302 | renameat | [man/](http://man7.org/linux/man-pages/man2/renameat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*renameat+package:^chromeos_public$) | 0x12e | int olddfd | const char \* oldname | int newdfd | const char \* newname | - | - |
| 303 | linkat | [man/](http://man7.org/linux/man-pages/man2/linkat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*linkat+package:^chromeos_public$) | 0x12f | int olddfd | const char \*oldname | int newdfd | const char \*newname | int flags | - |
| 304 | symlinkat | [man/](http://man7.org/linux/man-pages/man2/symlinkat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*symlinkat+package:^chromeos_public$) | 0x130 | const char \* oldname | int newdfd | const char \* newname | - | - | - |
| 305 | readlinkat | [man/](http://man7.org/linux/man-pages/man2/readlinkat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*readlinkat+package:^chromeos_public$) | 0x131 | int dfd | const char \*path | char \*buf | int bufsiz | - | - |
| 306 | fchmodat | [man/](http://man7.org/linux/man-pages/man2/fchmodat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fchmodat+package:^chromeos_public$) | 0x132 | int dfd | const char \* filename | umode\_t mode | - | - | - |
| 307 | faccessat | [man/](http://man7.org/linux/man-pages/man2/faccessat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*faccessat+package:^chromeos_public$) | 0x133 | int dfd | const char \*filename | int mode | - | - | - |
| 308 | pselect6 | [man/](http://man7.org/linux/man-pages/man2/pselect6.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pselect6+package:^chromeos_public$) | 0x134 | int | fd\_set \* | fd\_set \* | fd\_set \* | struct timespec \* | void \* |
| 309 | ppoll | [man/](http://man7.org/linux/man-pages/man2/ppoll.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*ppoll+package:^chromeos_public$) | 0x135 | struct pollfd \* | unsigned int | struct timespec \* | const sigset\_t \* | size\_t | - |
| 310 | unshare | [man/](http://man7.org/linux/man-pages/man2/unshare.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*unshare+package:^chromeos_public$) | 0x136 | unsigned long unshare\_flags | - | - | - | - | - |
| 311 | set_robust_list | [man/](http://man7.org/linux/man-pages/man2/set_robust_list.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*set_robust_list+package:^chromeos_public$) | 0x137 | struct robust\_list\_head \*head | size\_t len | - | - | - | - |
| 312 | get_robust_list | [man/](http://man7.org/linux/man-pages/man2/get_robust_list.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*get_robust_list+package:^chromeos_public$) | 0x138 | int pid | struct robust\_list\_head \* \*head\_ptr | size\_t \*len\_ptr | - | - | - |
| 313 | splice | [man/](http://man7.org/linux/man-pages/man2/splice.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*splice+package:^chromeos_public$) | 0x139 | int fd\_in | loff\_t \*off\_in | int fd\_out | loff\_t \*off\_out | size\_t len | unsigned int flags |
| 314 | sync_file_range | [man/](http://man7.org/linux/man-pages/man2/sync_file_range.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sync_file_range+package:^chromeos_public$) | 0x13a | int fd | loff\_t offset | loff\_t nbytes | unsigned int flags | - | - |
| 315 | tee | [man/](http://man7.org/linux/man-pages/man2/tee.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*tee+package:^chromeos_public$) | 0x13b | int fdin | int fdout | size\_t len | unsigned int flags | - | - |
| 316 | vmsplice | [man/](http://man7.org/linux/man-pages/man2/vmsplice.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*vmsplice+package:^chromeos_public$) | 0x13c | int fd | const struct iovec \*iov | unsigned long nr\_segs | unsigned int flags | - | - |
| 317 | move_pages | [man/](http://man7.org/linux/man-pages/man2/move_pages.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*move_pages+package:^chromeos_public$) | 0x13d | pid\_t pid | unsigned long nr\_pages | const void \* \*pages | const int \*nodes | int \*status | int flags |
| 318 | getcpu | [man/](http://man7.org/linux/man-pages/man2/getcpu.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getcpu+package:^chromeos_public$) | 0x13e | unsigned \*cpu | unsigned \*node | struct getcpu\_cache \*cache | - | - | - |
| 319 | epoll_pwait | [man/](http://man7.org/linux/man-pages/man2/epoll_pwait.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*epoll_pwait+package:^chromeos_public$) | 0x13f | int epfd | struct epoll\_event \*events | int maxevents | int timeout | const sigset\_t \*sigmask | size\_t sigsetsize |
| 320 | utimensat | [man/](http://man7.org/linux/man-pages/man2/utimensat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*utimensat+package:^chromeos_public$) | 0x140 | int dfd | const char \*filename | struct timespec \*utimes | int flags | - | - |
| 321 | signalfd | [man/](http://man7.org/linux/man-pages/man2/signalfd.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*signalfd+package:^chromeos_public$) | 0x141 | int ufd | sigset\_t \*user\_mask | size\_t sizemask | - | - | - |
| 322 | timerfd_create | [man/](http://man7.org/linux/man-pages/man2/timerfd_create.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*timerfd_create+package:^chromeos_public$) | 0x142 | int clockid | int flags | - | - | - | - |
| 323 | eventfd | [man/](http://man7.org/linux/man-pages/man2/eventfd.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*eventfd+package:^chromeos_public$) | 0x143 | unsigned int count | - | - | - | - | - |
| 324 | fallocate | [man/](http://man7.org/linux/man-pages/man2/fallocate.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fallocate+package:^chromeos_public$) | 0x144 | int fd | int mode | loff\_t offset | loff\_t len | - | - |
| 325 | timerfd_settime | [man/](http://man7.org/linux/man-pages/man2/timerfd_settime.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*timerfd_settime+package:^chromeos_public$) | 0x145 | int ufd | int flags | const struct \_\_kernel\_itimerspec \*utmr | struct \_\_kernel\_itimerspec \*otmr | - | - |
| 326 | timerfd_gettime | [man/](http://man7.org/linux/man-pages/man2/timerfd_gettime.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*timerfd_gettime+package:^chromeos_public$) | 0x146 | int ufd | struct \_\_kernel\_itimerspec \*otmr | - | - | - | - |
| 327 | signalfd4 | [man/](http://man7.org/linux/man-pages/man2/signalfd4.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*signalfd4+package:^chromeos_public$) | 0x147 | int ufd | sigset\_t \*user\_mask | size\_t sizemask | int flags | - | - |
| 328 | eventfd2 | [man/](http://man7.org/linux/man-pages/man2/eventfd2.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*eventfd2+package:^chromeos_public$) | 0x148 | unsigned int count | int flags | - | - | - | - |
| 329 | epoll_create1 | [man/](http://man7.org/linux/man-pages/man2/epoll_create1.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*epoll_create1+package:^chromeos_public$) | 0x149 | int flags | - | - | - | - | - |
| 330 | dup3 | [man/](http://man7.org/linux/man-pages/man2/dup3.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*dup3+package:^chromeos_public$) | 0x14a | unsigned int oldfd | unsigned int newfd | int flags | - | - | - |
| 331 | pipe2 | [man/](http://man7.org/linux/man-pages/man2/pipe2.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pipe2+package:^chromeos_public$) | 0x14b | int \*fildes | int flags | - | - | - | - |
| 332 | inotify_init1 | [man/](http://man7.org/linux/man-pages/man2/inotify_init1.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*inotify_init1+package:^chromeos_public$) | 0x14c | int flags | - | - | - | - | - |
| 333 | preadv | [man/](http://man7.org/linux/man-pages/man2/preadv.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*preadv+package:^chromeos_public$) | 0x14d | unsigned long fd | const struct iovec \*vec | unsigned long vlen | unsigned long pos\_l | unsigned long pos\_h | - |
| 334 | pwritev | [man/](http://man7.org/linux/man-pages/man2/pwritev.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pwritev+package:^chromeos_public$) | 0x14e | unsigned long fd | const struct iovec \*vec | unsigned long vlen | unsigned long pos\_l | unsigned long pos\_h | - |
| 335 | rt_tgsigqueueinfo | [man/](http://man7.org/linux/man-pages/man2/rt_tgsigqueueinfo.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*rt_tgsigqueueinfo+package:^chromeos_public$) | 0x14f | pid\_t tgid | pid\_t pid | int sig | siginfo\_t \*uinfo | - | - |
| 336 | perf_event_open | [man/](http://man7.org/linux/man-pages/man2/perf_event_open.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*perf_event_open+package:^chromeos_public$) | 0x150 | struct perf\_event\_attr \*attr\_uptr | pid\_t pid | int cpu | int group\_fd | unsigned long flags | - |
| 337 | recvmmsg | [man/](http://man7.org/linux/man-pages/man2/recvmmsg.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*recvmmsg+package:^chromeos_public$) | 0x151 | int fd | struct mmsghdr \*msg | unsigned int vlen | unsigned flags | struct timespec \*timeout | - |
| 338 | fanotify_init | [man/](http://man7.org/linux/man-pages/man2/fanotify_init.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fanotify_init+package:^chromeos_public$) | 0x152 | unsigned int flags | unsigned int event\_f\_flags | - | - | - | - |
| 339 | fanotify_mark | [man/](http://man7.org/linux/man-pages/man2/fanotify_mark.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*fanotify_mark+package:^chromeos_public$) | 0x153 | int fanotify\_fd | unsigned int flags | u64 mask | int fd | const char \*pathname | - |
| 340 | prlimit64 | [man/](http://man7.org/linux/man-pages/man2/prlimit64.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*prlimit64+package:^chromeos_public$) | 0x154 | pid\_t pid | unsigned int resource | const struct rlimit64 \*new\_rlim | struct rlimit64 \*old\_rlim | - | - |
| 341 | name_to_handle_at | [man/](http://man7.org/linux/man-pages/man2/name_to_handle_at.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*name_to_handle_at+package:^chromeos_public$) | 0x155 | int dfd | const char \*name | struct file\_handle \*handle | int \*mnt\_id | int flag | - |
| 342 | open_by_handle_at | [man/](http://man7.org/linux/man-pages/man2/open_by_handle_at.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*open_by_handle_at+package:^chromeos_public$) | 0x156 | int mountdirfd | struct file\_handle \*handle | int flags | - | - | - |
| 343 | clock_adjtime | [man/](http://man7.org/linux/man-pages/man2/clock_adjtime.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*clock_adjtime+package:^chromeos_public$) | 0x157 | clockid\_t which\_clock | struct timex \*tx | - | - | - | - |
| 344 | syncfs | [man/](http://man7.org/linux/man-pages/man2/syncfs.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*syncfs+package:^chromeos_public$) | 0x158 | int fd | - | - | - | - | - |
| 345 | sendmmsg | [man/](http://man7.org/linux/man-pages/man2/sendmmsg.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sendmmsg+package:^chromeos_public$) | 0x159 | int fd | struct mmsghdr \*msg | unsigned int vlen | unsigned flags | - | - |
| 346 | setns | [man/](http://man7.org/linux/man-pages/man2/setns.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setns+package:^chromeos_public$) | 0x15a | int fd | int nstype | - | - | - | - |
| 347 | process_vm_readv | [man/](http://man7.org/linux/man-pages/man2/process_vm_readv.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*process_vm_readv+package:^chromeos_public$) | 0x15b | pid\_t pid | const struct iovec \*lvec | unsigned long liovcnt | const struct iovec \*rvec | unsigned long riovcnt | unsigned long flags |
| 348 | process_vm_writev | [man/](http://man7.org/linux/man-pages/man2/process_vm_writev.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*process_vm_writev+package:^chromeos_public$) | 0x15c | pid\_t pid | const struct iovec \*lvec | unsigned long liovcnt | const struct iovec \*rvec | unsigned long riovcnt | unsigned long flags |
| 349 | kcmp | [man/](http://man7.org/linux/man-pages/man2/kcmp.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*kcmp+package:^chromeos_public$) | 0x15d | pid\_t pid1 | pid\_t pid2 | int type | unsigned long idx1 | unsigned long idx2 | - |
| 350 | finit_module | [man/](http://man7.org/linux/man-pages/man2/finit_module.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*finit_module+package:^chromeos_public$) | 0x15e | int fd | const char \*uargs | int flags | - | - | - |
| 351 | sched_setattr | [man/](http://man7.org/linux/man-pages/man2/sched_setattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_setattr+package:^chromeos_public$) | 0x15f | pid\_t pid | struct sched\_attr \*attr | unsigned int flags | - | - | - |
| 352 | sched_getattr | [man/](http://man7.org/linux/man-pages/man2/sched_getattr.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sched_getattr+package:^chromeos_public$) | 0x160 | pid\_t pid | struct sched\_attr \*attr | unsigned int size | unsigned int flags | - | - |
| 353 | renameat2 | [man/](http://man7.org/linux/man-pages/man2/renameat2.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*renameat2+package:^chromeos_public$) | 0x161 | int olddfd | const char \*oldname | int newdfd | const char \*newname | unsigned int flags | - |
| 354 | seccomp | [man/](http://man7.org/linux/man-pages/man2/seccomp.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*seccomp+package:^chromeos_public$) | 0x162 | unsigned int op | unsigned int flags | const char \*uargs | - | - | - |
| 355 | getrandom | [man/](http://man7.org/linux/man-pages/man2/getrandom.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getrandom+package:^chromeos_public$) | 0x163 | char \*buf | size\_t count | unsigned int flags | - | - | - |
| 356 | memfd_create | [man/](http://man7.org/linux/man-pages/man2/memfd_create.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*memfd_create+package:^chromeos_public$) | 0x164 | const char \*uname\_ptr | unsigned int flags | - | - | - | - |
| 357 | bpf | [man/](http://man7.org/linux/man-pages/man2/bpf.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*bpf+package:^chromeos_public$) | 0x165 | int cmd | union bpf\_attr \*attr | unsigned int size | - | - | - |
| 358 | execveat | [man/](http://man7.org/linux/man-pages/man2/execveat.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*execveat+package:^chromeos_public$) | 0x166 | int dfd | const char \*filename | const char \*const \*argv | const char \*const \*envp | int flags | - |
| 359 | socket | [man/](http://man7.org/linux/man-pages/man2/socket.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*socket+package:^chromeos_public$) | 0x167 | int | int | int | - | - | - |
| 360 | socketpair | [man/](http://man7.org/linux/man-pages/man2/socketpair.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*socketpair+package:^chromeos_public$) | 0x168 | int | int | int | int \* | - | - |
| 361 | bind | [man/](http://man7.org/linux/man-pages/man2/bind.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*bind+package:^chromeos_public$) | 0x169 | int | struct sockaddr \* | int | - | - | - |
| 362 | connect | [man/](http://man7.org/linux/man-pages/man2/connect.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*connect+package:^chromeos_public$) | 0x16a | int | struct sockaddr \* | int | - | - | - |
| 363 | listen | [man/](http://man7.org/linux/man-pages/man2/listen.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*listen+package:^chromeos_public$) | 0x16b | int | int | - | - | - | - |
| 364 | accept4 | [man/](http://man7.org/linux/man-pages/man2/accept4.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*accept4+package:^chromeos_public$) | 0x16c | int | struct sockaddr \* | int \* | int | - | - |
| 365 | getsockopt | [man/](http://man7.org/linux/man-pages/man2/getsockopt.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getsockopt+package:^chromeos_public$) | 0x16d | int fd | int level | int optname | char \*optval | int \*optlen | - |
| 366 | setsockopt | [man/](http://man7.org/linux/man-pages/man2/setsockopt.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*setsockopt+package:^chromeos_public$) | 0x16e | int fd | int level | int optname | char \*optval | int optlen | - |
| 367 | getsockname | [man/](http://man7.org/linux/man-pages/man2/getsockname.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getsockname+package:^chromeos_public$) | 0x16f | int | struct sockaddr \* | int \* | - | - | - |
| 368 | getpeername | [man/](http://man7.org/linux/man-pages/man2/getpeername.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*getpeername+package:^chromeos_public$) | 0x170 | int | struct sockaddr \* | int \* | - | - | - |
| 369 | sendto | [man/](http://man7.org/linux/man-pages/man2/sendto.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sendto+package:^chromeos_public$) | 0x171 | int | void \* | size\_t | unsigned | struct sockaddr \* | int |
| 370 | sendmsg | [man/](http://man7.org/linux/man-pages/man2/sendmsg.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*sendmsg+package:^chromeos_public$) | 0x172 | int fd | struct user\_msghdr \*msg | unsigned flags | - | - | - |
| 371 | recvfrom | [man/](http://man7.org/linux/man-pages/man2/recvfrom.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*recvfrom+package:^chromeos_public$) | 0x173 | int | void \* | size\_t | unsigned | struct sockaddr \* | int \* |
| 372 | recvmsg | [man/](http://man7.org/linux/man-pages/man2/recvmsg.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*recvmsg+package:^chromeos_public$) | 0x174 | int fd | struct user\_msghdr \*msg | unsigned flags | - | - | - |
| 373 | shutdown | [man/](http://man7.org/linux/man-pages/man2/shutdown.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*shutdown+package:^chromeos_public$) | 0x175 | int | int | - | - | - | - |
| 374 | userfaultfd | [man/](http://man7.org/linux/man-pages/man2/userfaultfd.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*userfaultfd+package:^chromeos_public$) | 0x176 | int flags | - | - | - | - | - |
| 375 | membarrier | [man/](http://man7.org/linux/man-pages/man2/membarrier.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*membarrier+package:^chromeos_public$) | 0x177 | int cmd | int flags | - | - | - | - |
| 376 | mlock2 | [man/](http://man7.org/linux/man-pages/man2/mlock2.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*mlock2+package:^chromeos_public$) | 0x178 | unsigned long start | size\_t len | int flags | - | - | - |
| 377 | copy_file_range | [man/](http://man7.org/linux/man-pages/man2/copy_file_range.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*copy_file_range+package:^chromeos_public$) | 0x179 | int fd\_in | loff\_t \*off\_in | int fd\_out | loff\_t \*off\_out | size\_t len | unsigned int flags |
| 378 | preadv2 | [man/](http://man7.org/linux/man-pages/man2/preadv2.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*preadv2+package:^chromeos_public$) | 0x17a | unsigned long fd | const struct iovec \*vec | unsigned long vlen | unsigned long pos\_l | unsigned long pos\_h | rwf\_t flags |
| 379 | pwritev2 | [man/](http://man7.org/linux/man-pages/man2/pwritev2.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pwritev2+package:^chromeos_public$) | 0x17b | unsigned long fd | const struct iovec \*vec | unsigned long vlen | unsigned long pos\_l | unsigned long pos\_h | rwf\_t flags |
| 380 | pkey_mprotect | [man/](http://man7.org/linux/man-pages/man2/pkey_mprotect.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pkey_mprotect+package:^chromeos_public$) | 0x17c | unsigned long start | size\_t len | unsigned long prot | int pkey | - | - |
| 381 | pkey_alloc | [man/](http://man7.org/linux/man-pages/man2/pkey_alloc.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pkey_alloc+package:^chromeos_public$) | 0x17d | unsigned long flags | unsigned long init\_val | - | - | - | - |
| 382 | pkey_free | [man/](http://man7.org/linux/man-pages/man2/pkey_free.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*pkey_free+package:^chromeos_public$) | 0x17e | int pkey | - | - | - | - | - |
| 383 | statx | [man/](http://man7.org/linux/man-pages/man2/statx.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*statx+package:^chromeos_public$) | 0x17f | int dfd | const char \*path | unsigned flags | unsigned mask | struct statx \*buffer | - |
| 384 | arch_prctl | [man/](http://man7.org/linux/man-pages/man2/arch_prctl.2.html) [cs/](https://cs.corp.google.com/search/?q=SYSCALL_DEFINE.*arch_prctl+package:^chromeos_public$) | 0x180 | ? | ? | ? | ? | ? | ? |

### Cross-arch Numbers

This shows the syscall numbers for (hopefully) the same syscall name across architectures.
Consult the [Random Names](#naming) section for common gotchas.

| syscall name | x86_64 | arm | arm64 | x86 |
|---|:---:|:---:|:---:|:---:|
| ARM_breakpoint | - | 983041 | - | - |
| ARM_cacheflush | - | 983042 | - | - |
| ARM_set_tls | - | 983045 | - | - |
| ARM_usr26 | - | 983043 | - | - |
| ARM_usr32 | - | 983044 | - | - |
| _llseek | - | 140 | - | 140 |
| _newselect | - | 142 | - | 142 |
| _sysctl | 156 | 149 | - | 149 |
| accept | 43 | 285 | 202 | - |
| accept4 | 288 | 366 | 242 | 364 |
| access | 21 | 33 | - | 33 |
| acct | 163 | 51 | 89 | 51 |
| add_key | 248 | 309 | 217 | 286 |
| adjtimex | 159 | 124 | 171 | 124 |
| afs_syscall | 183 | - | - | 137 |
| alarm | 37 | - | - | 27 |
| arch_prctl | 158 | - | - | 384 |
| arm_fadvise64_64 | - | 270 | - | - |
| arm_sync_file_range | - | 341 | - | - |
| bdflush | - | 134 | - | 134 |
| bind | 49 | 282 | 200 | 361 |
| bpf | 321 | 386 | 280 | 357 |
| break | - | - | - | 17 |
| brk | 12 | 45 | 214 | 45 |
| capget | 125 | 184 | 90 | 184 |
| capset | 126 | 185 | 91 | 185 |
| chdir | 80 | 12 | 49 | 12 |
| chmod | 90 | 15 | - | 15 |
| chown | 92 | 182 | - | 182 |
| chown32 | - | 212 | - | 212 |
| chroot | 161 | 61 | 51 | 61 |
| clock_adjtime | 305 | 372 | 266 | 343 |
| clock_getres | 229 | 264 | 114 | 266 |
| clock_gettime | 228 | 263 | 113 | 265 |
| clock_nanosleep | 230 | 265 | 115 | 267 |
| clock_settime | 227 | 262 | 112 | 264 |
| clone | 56 | 120 | 220 | 120 |
| close | 3 | 6 | 57 | 6 |
| connect | 42 | 283 | 203 | 362 |
| copy_file_range | 326 | 391 | 285 | 377 |
| creat | 85 | 8 | - | 8 |
| create_module | 174 | - | - | 127 |
| delete_module | 176 | 129 | 106 | 129 |
| dup | 32 | 41 | 23 | 41 |
| dup2 | 33 | 63 | - | 63 |
| dup3 | 292 | 358 | 24 | 330 |
| epoll_create | 213 | 250 | - | 254 |
| epoll_create1 | 291 | 357 | 20 | 329 |
| epoll_ctl | 233 | 251 | 21 | 255 |
| epoll_ctl_old | 214 | - | - | - |
| epoll_pwait | 281 | 346 | 22 | 319 |
| epoll_wait | 232 | 252 | - | 256 |
| epoll_wait_old | 215 | - | - | - |
| eventfd | 284 | 351 | - | 323 |
| eventfd2 | 290 | 356 | 19 | 328 |
| execve | 59 | 11 | 221 | 11 |
| execveat | 322 | 387 | 281 | 358 |
| exit | 60 | 1 | 93 | 1 |
| exit_group | 231 | 248 | 94 | 252 |
| faccessat | 269 | 334 | 48 | 307 |
| fadvise64 | 221 | - | 223 | 250 |
| fadvise64_64 | - | - | - | 272 |
| fallocate | 285 | 352 | 47 | 324 |
| fanotify_init | 300 | 367 | 262 | 338 |
| fanotify_mark | 301 | 368 | 263 | 339 |
| fchdir | 81 | 133 | 50 | 133 |
| fchmod | 91 | 94 | 52 | 94 |
| fchmodat | 268 | 333 | 53 | 306 |
| fchown | 93 | 95 | 55 | 95 |
| fchown32 | - | 207 | - | 207 |
| fchownat | 260 | 325 | 54 | 298 |
| fcntl | 72 | 55 | 25 | 55 |
| fcntl64 | - | 221 | - | 221 |
| fdatasync | 75 | 148 | 83 | 148 |
| fgetxattr | 193 | 231 | 10 | 231 |
| finit_module | 313 | 379 | 273 | 350 |
| flistxattr | 196 | 234 | 13 | 234 |
| flock | 73 | 143 | 32 | 143 |
| fork | 57 | 2 | - | 2 |
| fremovexattr | 199 | 237 | 16 | 237 |
| fsetxattr | 190 | 228 | 7 | 228 |
| fstat | 5 | 108 | 80 | 108 |
| fstat64 | - | 197 | - | 197 |
| fstatat64 | - | 327 | - | 300 |
| fstatfs | 138 | 100 | 44 | 100 |
| fstatfs64 | - | 267 | - | 269 |
| fsync | 74 | 118 | 82 | 118 |
| ftime | - | - | - | 35 |
| ftruncate | 77 | 93 | 46 | 93 |
| ftruncate64 | - | 194 | - | 194 |
| futex | 202 | 240 | 98 | 240 |
| futimesat | 261 | 326 | - | 299 |
| get_kernel_syms | 177 | - | - | 130 |
| get_mempolicy | 239 | 320 | 236 | 275 |
| get_robust_list | 274 | 339 | 100 | 312 |
| get_thread_area | 211 | - | - | 244 |
| getcpu | 309 | 345 | 168 | 318 |
| getcwd | 79 | 183 | 17 | 183 |
| getdents | 78 | 141 | - | 141 |
| getdents64 | 217 | 217 | 61 | 220 |
| getegid | 108 | 50 | 177 | 50 |
| getegid32 | - | 202 | - | 202 |
| geteuid | 107 | 49 | 175 | 49 |
| geteuid32 | - | 201 | - | 201 |
| getgid | 104 | 47 | 176 | 47 |
| getgid32 | - | 200 | - | 200 |
| getgroups | 115 | 80 | 158 | 80 |
| getgroups32 | - | 205 | - | 205 |
| getitimer | 36 | 105 | 102 | 105 |
| getpeername | 52 | 287 | 205 | 368 |
| getpgid | 121 | 132 | 155 | 132 |
| getpgrp | 111 | 65 | - | 65 |
| getpid | 39 | 20 | 172 | 20 |
| getpmsg | 181 | - | - | 188 |
| getppid | 110 | 64 | 173 | 64 |
| getpriority | 140 | 96 | 141 | 96 |
| getrandom | 318 | 384 | 278 | 355 |
| getresgid | 120 | 171 | 150 | 171 |
| getresgid32 | - | 211 | - | 211 |
| getresuid | 118 | 165 | 148 | 165 |
| getresuid32 | - | 209 | - | 209 |
| getrlimit | 97 | - | 163 | 76 |
| getrusage | 98 | 77 | 165 | 77 |
| getsid | 124 | 147 | 156 | 147 |
| getsockname | 51 | 286 | 204 | 367 |
| getsockopt | 55 | 295 | 209 | 365 |
| gettid | 186 | 224 | 178 | 224 |
| gettimeofday | 96 | 78 | 169 | 78 |
| getuid | 102 | 24 | 174 | 24 |
| getuid32 | - | 199 | - | 199 |
| getxattr | 191 | 229 | 8 | 229 |
| gtty | - | - | - | 32 |
| idle | - | - | - | 112 |
| init_module | 175 | 128 | 105 | 128 |
| inotify_add_watch | 254 | 317 | 27 | 292 |
| inotify_init | 253 | 316 | - | 291 |
| inotify_init1 | 294 | 360 | 26 | 332 |
| inotify_rm_watch | 255 | 318 | 28 | 293 |
| io_cancel | 210 | 247 | 3 | 249 |
| io_destroy | 207 | 244 | 1 | 246 |
| io_getevents | 208 | 245 | 4 | 247 |
| io_setup | 206 | 243 | 0 | 245 |
| io_submit | 209 | 246 | 2 | 248 |
| ioctl | 16 | 54 | 29 | 54 |
| ioperm | 173 | - | - | 101 |
| iopl | 172 | - | - | 110 |
| ioprio_get | 252 | 315 | 31 | 290 |
| ioprio_set | 251 | 314 | 30 | 289 |
| ipc | - | - | - | 117 |
| kcmp | 312 | 378 | 272 | 349 |
| kexec_file_load | 320 | - | - | - |
| kexec_load | 246 | 347 | 104 | 283 |
| keyctl | 250 | 311 | 219 | 288 |
| kill | 62 | 37 | 129 | 37 |
| lchown | 94 | 16 | - | 16 |
| lchown32 | - | 198 | - | 198 |
| lgetxattr | 192 | 230 | 9 | 230 |
| link | 86 | 9 | - | 9 |
| linkat | 265 | 330 | 37 | 303 |
| listen | 50 | 284 | 201 | 363 |
| listxattr | 194 | 232 | 11 | 232 |
| llistxattr | 195 | 233 | 12 | 233 |
| lock | - | - | - | 53 |
| lookup_dcookie | 212 | 249 | 18 | 253 |
| lremovexattr | 198 | 236 | 15 | 236 |
| lseek | 8 | 19 | 62 | 19 |
| lsetxattr | 189 | 227 | 6 | 227 |
| lstat | 6 | 107 | - | 107 |
| lstat64 | - | 196 | - | 196 |
| madvise | 28 | 220 | 233 | 219 |
| mbind | 237 | 319 | 235 | 274 |
| membarrier | 324 | 389 | 283 | 375 |
| memfd_create | 319 | 385 | 279 | 356 |
| migrate_pages | 256 | - | 238 | 294 |
| mincore | 27 | 219 | 232 | 218 |
| mkdir | 83 | 39 | - | 39 |
| mkdirat | 258 | 323 | 34 | 296 |
| mknod | 133 | 14 | - | 14 |
| mknodat | 259 | 324 | 33 | 297 |
| mlock | 149 | 150 | 228 | 150 |
| mlock2 | 325 | 390 | 284 | 376 |
| mlockall | 151 | 152 | 230 | 152 |
| mmap | 9 | - | 222 | 90 |
| mmap2 | - | 192 | - | 192 |
| modify_ldt | 154 | - | - | 123 |
| mount | 165 | 21 | 40 | 21 |
| move_pages | 279 | 344 | 239 | 317 |
| mprotect | 10 | 125 | 226 | 125 |
| mpx | - | - | - | 56 |
| mq_getsetattr | 245 | 279 | 185 | 282 |
| mq_notify | 244 | 278 | 184 | 281 |
| mq_open | 240 | 274 | 180 | 277 |
| mq_timedreceive | 243 | 277 | 183 | 280 |
| mq_timedsend | 242 | 276 | 182 | 279 |
| mq_unlink | 241 | 275 | 181 | 278 |
| mremap | 25 | 163 | 216 | 163 |
| msgctl | 71 | 304 | 187 | - |
| msgget | 68 | 303 | 186 | - |
| msgrcv | 70 | 302 | 188 | - |
| msgsnd | 69 | 301 | 189 | - |
| msync | 26 | 144 | 227 | 144 |
| munlock | 150 | 151 | 229 | 151 |
| munlockall | 152 | 153 | 231 | 153 |
| munmap | 11 | 91 | 215 | 91 |
| name_to_handle_at | 303 | 370 | 264 | 341 |
| nanosleep | 35 | 162 | 101 | 162 |
| newfstatat | 262 | - | 79 | - |
| nfsservctl | 180 | 169 | 42 | 169 |
| nice | - | 34 | - | 34 |
| oldfstat | - | - | - | 28 |
| oldlstat | - | - | - | 84 |
| oldolduname | - | - | - | 59 |
| oldstat | - | - | - | 18 |
| olduname | - | - | - | 109 |
| open | 2 | 5 | - | 5 |
| open_by_handle_at | 304 | 371 | 265 | 342 |
| openat | 257 | 322 | 56 | 295 |
| pause | 34 | 29 | - | 29 |
| pciconfig_iobase | - | 271 | - | - |
| pciconfig_read | - | 272 | - | - |
| pciconfig_write | - | 273 | - | - |
| perf_event_open | 298 | 364 | 241 | 336 |
| personality | 135 | 136 | 92 | 136 |
| pipe | 22 | 42 | - | 42 |
| pipe2 | 293 | 359 | 59 | 331 |
| pivot_root | 155 | 218 | 41 | 217 |
| pkey_alloc | 330 | 395 | 289 | 381 |
| pkey_free | 331 | 396 | 290 | 382 |
| pkey_mprotect | 329 | 394 | 288 | 380 |
| poll | 7 | 168 | - | 168 |
| ppoll | 271 | 336 | 73 | 309 |
| prctl | 157 | 172 | 167 | 172 |
| pread64 | 17 | 180 | 67 | 180 |
| preadv | 295 | 361 | 69 | 333 |
| preadv2 | 327 | 392 | 286 | 378 |
| prlimit64 | 302 | 369 | 261 | 340 |
| process_vm_readv | 310 | 376 | 270 | 347 |
| process_vm_writev | 311 | 377 | 271 | 348 |
| prof | - | - | - | 44 |
| profil | - | - | - | 98 |
| pselect6 | 270 | 335 | 72 | 308 |
| ptrace | 101 | 26 | 117 | 26 |
| putpmsg | 182 | - | - | 189 |
| pwrite64 | 18 | 181 | 68 | 181 |
| pwritev | 296 | 362 | 70 | 334 |
| pwritev2 | 328 | 393 | 287 | 379 |
| query_module | 178 | - | - | 167 |
| quotactl | 179 | 131 | 60 | 131 |
| read | 0 | 3 | 63 | 3 |
| readahead | 187 | 225 | 213 | 225 |
| readdir | - | - | - | 89 |
| readlink | 89 | 85 | - | 85 |
| readlinkat | 267 | 332 | 78 | 305 |
| readv | 19 | 145 | 65 | 145 |
| reboot | 169 | 88 | 142 | 88 |
| recv | - | 291 | - | - |
| recvfrom | 45 | 292 | 207 | 371 |
| recvmmsg | 299 | 365 | 243 | 337 |
| recvmsg | 47 | 297 | 212 | 372 |
| remap_file_pages | 216 | 253 | 234 | 257 |
| removexattr | 197 | 235 | 14 | 235 |
| rename | 82 | 38 | - | 38 |
| renameat | 264 | 329 | 38 | 302 |
| renameat2 | 316 | 382 | 276 | 353 |
| request_key | 249 | 310 | 218 | 287 |
| restart_syscall | 219 | 0 | 128 | 0 |
| rmdir | 84 | 40 | - | 40 |
| rt_sigaction | 13 | 174 | 134 | 174 |
| rt_sigpending | 127 | 176 | 136 | 176 |
| rt_sigprocmask | 14 | 175 | 135 | 175 |
| rt_sigqueueinfo | 129 | 178 | 138 | 178 |
| rt_sigreturn | 15 | 173 | 139 | 173 |
| rt_sigsuspend | 130 | 179 | 133 | 179 |
| rt_sigtimedwait | 128 | 177 | 137 | 177 |
| rt_tgsigqueueinfo | 297 | 363 | 240 | 335 |
| sched_get_priority_max | 146 | 159 | 125 | 159 |
| sched_get_priority_min | 147 | 160 | 126 | 160 |
| sched_getaffinity | 204 | 242 | 123 | 242 |
| sched_getattr | 315 | 381 | 275 | 352 |
| sched_getparam | 143 | 155 | 121 | 155 |
| sched_getscheduler | 145 | 157 | 120 | 157 |
| sched_rr_get_interval | 148 | 161 | 127 | 161 |
| sched_setaffinity | 203 | 241 | 122 | 241 |
| sched_setattr | 314 | 380 | 274 | 351 |
| sched_setparam | 142 | 154 | 118 | 154 |
| sched_setscheduler | 144 | 156 | 119 | 156 |
| sched_yield | 24 | 158 | 124 | 158 |
| seccomp | 317 | 383 | 277 | 354 |
| security | 185 | - | - | - |
| select | 23 | - | - | 82 |
| semctl | 66 | 300 | 191 | - |
| semget | 64 | 299 | 190 | - |
| semop | 65 | 298 | 193 | - |
| semtimedop | 220 | 312 | 192 | - |
| send | - | 289 | - | - |
| sendfile | 40 | 187 | 71 | 187 |
| sendfile64 | - | 239 | - | 239 |
| sendmmsg | 307 | 374 | 269 | 345 |
| sendmsg | 46 | 296 | 211 | 370 |
| sendto | 44 | 290 | 206 | 369 |
| set_mempolicy | 238 | 321 | 237 | 276 |
| set_robust_list | 273 | 338 | 99 | 311 |
| set_thread_area | 205 | - | - | 243 |
| set_tid_address | 218 | 256 | 96 | 258 |
| setdomainname | 171 | 121 | 162 | 121 |
| setfsgid | 123 | 139 | 152 | 139 |
| setfsgid32 | - | 216 | - | 216 |
| setfsuid | 122 | 138 | 151 | 138 |
| setfsuid32 | - | 215 | - | 215 |
| setgid | 106 | 46 | 144 | 46 |
| setgid32 | - | 214 | - | 214 |
| setgroups | 116 | 81 | 159 | 81 |
| setgroups32 | - | 206 | - | 206 |
| sethostname | 170 | 74 | 161 | 74 |
| setitimer | 38 | 104 | 103 | 104 |
| setns | 308 | 375 | 268 | 346 |
| setpgid | 109 | 57 | 154 | 57 |
| setpriority | 141 | 97 | 140 | 97 |
| setregid | 114 | 71 | 143 | 71 |
| setregid32 | - | 204 | - | 204 |
| setresgid | 119 | 170 | 149 | 170 |
| setresgid32 | - | 210 | - | 210 |
| setresuid | 117 | 164 | 147 | 164 |
| setresuid32 | - | 208 | - | 208 |
| setreuid | 113 | 70 | 145 | 70 |
| setreuid32 | - | 203 | - | 203 |
| setrlimit | 160 | 75 | 164 | 75 |
| setsid | 112 | 66 | 157 | 66 |
| setsockopt | 54 | 294 | 208 | 366 |
| settimeofday | 164 | 79 | 170 | 79 |
| setuid | 105 | 23 | 146 | 23 |
| setuid32 | - | 213 | - | 213 |
| setxattr | 188 | 226 | 5 | 226 |
| sgetmask | - | - | - | 68 |
| shmat | 30 | 305 | 196 | - |
| shmctl | 31 | 308 | 195 | - |
| shmdt | 67 | 306 | 197 | - |
| shmget | 29 | 307 | 194 | - |
| shutdown | 48 | 293 | 210 | 373 |
| sigaction | - | 67 | - | 67 |
| sigaltstack | 131 | 186 | 132 | 186 |
| signal | - | - | - | 48 |
| signalfd | 282 | 349 | - | 321 |
| signalfd4 | 289 | 355 | 74 | 327 |
| sigpending | - | 73 | - | 73 |
| sigprocmask | - | 126 | - | 126 |
| sigreturn | - | 119 | - | 119 |
| sigsuspend | - | 72 | - | 72 |
| socket | 41 | 281 | 198 | 359 |
| socketcall | - | - | - | 102 |
| socketpair | 53 | 288 | 199 | 360 |
| splice | 275 | 340 | 76 | 313 |
| ssetmask | - | - | - | 69 |
| stat | 4 | 106 | - | 106 |
| stat64 | - | 195 | - | 195 |
| statfs | 137 | 99 | 43 | 99 |
| statfs64 | - | 266 | - | 268 |
| statx | 332 | 397 | 291 | 383 |
| stime | - | - | - | 25 |
| stty | - | - | - | 31 |
| swapoff | 168 | 115 | 225 | 115 |
| swapon | 167 | 87 | 224 | 87 |
| symlink | 88 | 83 | - | 83 |
| symlinkat | 266 | 331 | 36 | 304 |
| sync | 162 | 36 | 81 | 36 |
| sync_file_range | 277 | - | 84 | 314 |
| sync_file_range2 | - | 341 | - | - |
| syncfs | 306 | 373 | 267 | 344 |
| sysfs | 139 | 135 | - | 135 |
| sysinfo | 99 | 116 | 179 | 116 |
| syslog | 103 | 103 | 116 | 103 |
| tee | 276 | 342 | 77 | 315 |
| tgkill | 234 | 268 | 131 | 270 |
| time | 201 | - | - | 13 |
| timer_create | 222 | 257 | 107 | 259 |
| timer_delete | 226 | 261 | 111 | 263 |
| timer_getoverrun | 225 | 260 | 109 | 262 |
| timer_gettime | 224 | 259 | 108 | 261 |
| timer_settime | 223 | 258 | 110 | 260 |
| timerfd_create | 283 | 350 | 85 | 322 |
| timerfd_gettime | 287 | 354 | 87 | 326 |
| timerfd_settime | 286 | 353 | 86 | 325 |
| times | 100 | 43 | 153 | 43 |
| tkill | 200 | 238 | 130 | 238 |
| truncate | 76 | 92 | 45 | 92 |
| truncate64 | - | 193 | - | 193 |
| tuxcall | 184 | - | - | - |
| ugetrlimit | - | 191 | - | 191 |
| ulimit | - | - | - | 58 |
| umask | 95 | 60 | 166 | 60 |
| umount | - | - | - | 22 |
| umount2 | 166 | 52 | 39 | 52 |
| uname | 63 | 122 | 160 | 122 |
| unlink | 87 | 10 | - | 10 |
| unlinkat | 263 | 328 | 35 | 301 |
| unshare | 272 | 337 | 97 | 310 |
| uselib | 134 | 86 | - | 86 |
| userfaultfd | 323 | 388 | 282 | 374 |
| ustat | 136 | 62 | - | 62 |
| utime | 132 | - | - | 30 |
| utimensat | 280 | 348 | 88 | 320 |
| utimes | 235 | 269 | - | 271 |
| vfork | 58 | 190 | - | 190 |
| vhangup | 153 | 111 | 58 | 111 |
| vm86 | - | - | - | 166 |
| vm86old | - | - | - | 113 |
| vmsplice | 278 | 343 | 75 | 316 |
| vserver | 236 | 313 | - | 273 |
| wait4 | 61 | 114 | 260 | 114 |
| waitid | 247 | 280 | 95 | 284 |
| waitpid | - | - | - | 7 |
| write | 1 | 4 | 64 | 4 |
| writev | 20 | 146 | 66 | 146 |
