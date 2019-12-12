# Chrome OS kernel tips and tricks

This is a collection of tips and tricks, useful information, for anyone who
wants to pick up kernel and/or bringup work, especially in Chrome OS. This is
not intended as a detailed guide for any of the items, but as general hints that
these tools are available.

*** promo
Note for Googlers: There are additional Google-specific notes and
work-in-progress notes at [go/chromeos-kernel-tips-and-tricks], as well as a
Google Docs mirror of this markdown. If you find a mistakes in the notes below,
or want to add some content, but don't have time to make a CL to fix it, feel
free to just make a suggestion in the doc and somebody will move it here. Same
thing if you have a comment.
***

[TOC]

## Finding problems

So the first step is to figure out _what_ are the problems:

*   Look at kernel messages (`dmesg`), on boot, or at any time, and find errors
    or warnings that should not be there.  e.g. what does `dmesg -w` give.
*   Look at `/var/log/messages` (contains kernel logs from `dmesg`, as well as
    logs from most system services).
*   Look at `top` output, to check if certain processes are hogging CPU or
    memory.
*   Build the kernel with `USE=kasan`. [KASan] is a great tool to find memory
    issues in the kernel (use it with the other tests below).
*   Other debugging kernel options:

    *   `USE=ubsan`
    *   `USE=lockdep`
    *   `USE=kmemleak`
    *   `USE=failslab`. Then configure in `/sys/kernel/debug/failslab` (setting
        `probability` to `10` and `times` to `1000` is a good start).
    *   `FAIL_MMC_REQUEST`
        *   Enable `CONFIG_FAIL_MMC_REQUEST`, `CONFIG_FAULT_INJECTION` and
            `CONFIG_FAULT_INJECTION_DEBUG_FS`, and then configure in
            `/sys/kernel/debug/mmc{n}/fail_mmc_request/`.
    *   Others? (memory debugging? Please add here!)

*   Stress tests:
    *   Single iteration suspend test: `powerd_dbus_suspend`
    *   Multi-iteration suspend test: `suspend_stress_test`
    *   Reboot loops, keeping ramoops at each reboot to analyse failures (setup
	    [SSH keys] first):

        ```bash
		#!/bin/bash

		IP=$1
		i=0
		while true; do
			while ! scp root@$IP:/sys/fs/pstore/console-ramoops-0 ramoops-$i; do
			sleep 1
			done
			ssh root@$IP reboot
			sleep 20
			i=$((i+1))
		done
        ```

		Then run this to extract out the bad ramoops
		```bash
		mkdir bad; ls ramoops-* | xargs -I{} sh -c \
		    'tail -n 1 {} | grep -v "reboot: Restarting system" && cp {} bad/{}'
        ```

    *   `restart ui` in a loop.
    *   Run tests (autotests, CTS, etc.)
    *   Stress test `cpufreq` by changing frequency constantly
        *   Other drivers may have similar knobs that one can play with.
    *   Balloons (from [crbug.com/468342], or
        `src/platform/microbenchmarks/mmm_donut.py`
    *   Unbind/rebind drivers (may be nice with `kasan`/`kmemleak`, too):

        ```bash
        cd /usr/local
        find /sys/bus/\*/drivers/\*/\* -type l -maxdepth 0 | grep -v "module$" > list
        sync
        cat list | xargs -I{} sh -c 'echo {}; cd \`dirname {}\`; echo \`basename {}\` > unbind; echo \`basename {}\` > bind; sleep 5'
        # see what crashes, edit list to remove bad drivers, continue
        ```

## Debugging

### kgdb

*   See [Debugging with KGDB/KDB].

### printk debugging

*   Add printks in strategic places (`dev_[info/warn/err]` or
    `pr_[info/warn/err]`), reboot, see what happens.
*   `dev_dbg/pr_dbg` in the kernel code can be enabled by setting
    `#define DEBUG` at the top of the source file (before all includes).
*   These are generally not written out to serial so have less effect on
    performance, but are not preserved in ramoops/serial on an OOPs.
*   Adding `dump_stack calls` in places may also be very useful.

Sometimes adding too many printk changes behaviour ([Heisenbug]), or makes the
system unusable.

*   Consider switching to `ftrace`, see below.
*   Use `ratelimit` to minimize the number of prints. See [example CL].

### Getting backtraces with BUG/WARN

BUG/WARN and friends provide nice backtraces. These can be very useful for
figuring out what code path is triggering a hard to reproduce issue.

#### Decoding backtraces

For 4.19 kernel, update as needed:

  ```bash
  ../third_party/kernel/v4.19/scripts/decode_stacktrace.sh \
  /build/kukui/usr/lib/debug/boot/vmlinux \
  /mnt/host/source/src/third_party/kernel/v4.19 \
  /build/kukui/usr/lib/debug/lib/modules/4.19.*/
  ```

Sometimes gdb is more useful (aarch64, update as needed):

  ```
  aarch64-cros-linux-gnu-gdb /build/kukui/usr/lib/debug/boot/vmlinux
  disas /m function
  ```

### ftrace debugging

*   [ftrace] allows you to trace events in the kernel (e.g. function calls,
    graphs), without introducing too much overhead. This is especially useful
    to debug timing/performance issues, or for cases when adding printk changes
    the behaviour.

*   It is possible to add custom messages by using `trace_printk`.
*   Example, to trace functions starting with `rt5667` and `mtk_spi`:

    ```bash
    cd /sys/kernel/debug/tracing
    echo "rt5677*" > set_ftrace_filter
    echo "mtk_spi_*" >> set_ftrace_filter
    echo function > current_tracer
    echo 1 > tracing_on
    # Look at the trace
    cat trace
    ```

Other tricks:

*   It is also possible to start tracing on boot by adding kernel parameters
    (useful to debug early hangs).
*   It is possible to ask the kernel to dump the ftrace buffer to uart on oops,
    this is useful to debug hangs/crashes:

    ```bash
    echo 1 > /proc/sys/kernel/ftrace_dump_on_oops.
    ```

*   Dumping the whole buffer may take an enormous amount of time at serial rate,
    but sometimes it's worth it.

## Workflow

### Build and deploy

  ```bash
  (chroot) emerge-kukui chromeos-kernel-4_19 && ./update_kernel.sh --remote=$IP --remote_bootargs
  ```

*   `cros_workon_make` is faster than emerge if you just want to do a build
    test.
*   You need `--install` though if you want to deploy the resulting kernel (and
    in that case emerge is equally fast).

### Recover from USB

One issue is often to figure out how to recover if you flash a bad kernel.
Booting from USB and running `chromeos-install` is one solution, but that's
slow.

*   Always have a good USB stick connected to the device.
*   Make sure you use a serial-enabled coreboot firmware.
*   If the kernel on internal storage does not boot anymore:

    1.  Boot from USB (slam Ctrl-U during FW bootup)
    1.  Copy kernel and modules back to internal storage (instructions below
        assume eMMC)

        ```bash
        dd if=/dev/sda2 of=/dev/mmcblk0p2
        mkdir /tmp/mnt
        mount /dev/mmcblk0p3 /tmp/mnt
        rm -rf /tmp/mnt/lib/modules/4.1*
        cp -a /lib/modules/4.1*/tmp/mnt/lib/modules/
        dd if=/dev/sda2 of=/dev/mmcblk0p4
        umount /tmp/mnt
        mount /dev/mmcblk0p5 /tmp/mnt
        rm -rf /tmp/mnt/lib/modules/4.1*
        cp -a /lib/modules/4.1*/tmp/mnt/lib/modules/
        umount /tmp/mnt
        # Optional, only if USB stick has rootfs verification on
        # /usr/share/vboot/bin/make_dev_ssd.sh --remove_rootfs_verification -i /dev/mmcblk0
        sync
        reboot
        ```

    1.  System should boot from internal storage again

### Inspect kernel config

*   Kernel config is at `/boot/` on the device
*   `/build/$BOARD/boot/config` in the chroot

### Modify kernel command line on device

*   For example, to enable the console on a recovery image on USB stick
    `/dev/sdb`:

    ```bash
    sudo make_dev_ssd.sh -i /dev/sdb --partitions 2 --save_config ./foo
    vi ./foo
    add the updated command line, for example: earlycon=uart,mmio32,0xfedc6000,115200,48000000
    save & exit vi
    sudo make_dev_ssd.sh -i /dev/sdb --partitions 2 --set_config ./foo
    sudo make_dev_ssd.sh -i /dev/sdb --recovery_key
    ```

### Modify kernel command line in depthcharge

```bash
(chroot) cros_workon-${board} depthcharge
vi /src/platform/depthcharge/src/board/${board}/board.c
```

Add the following function containing your command line addition:

```C
const char *mainboard_commandline(void)
{
     /* Make sure there are spaces at the start and end of the string. */
     return " earlycon=uart,mmio32,0xfedc6000,115200,48000000  ";
}
```

Rebuild depthcharge, and build it into the image.

## CLs

### Patch tags

See the [kernel_faq] guidelines for [UPSTREAM, BACKPORT and FROMLIST] tags.

### KConfig changes

Kconfig changes (changes that affect `chromeos/config`) should be normalized by
running `chromeos/scripts/kernelconfig olddefconfig`

### Sending patches

#### (Compile) test

Make sure that your patch builds fine with allmodconfig:

```bash
mkdir -p ../build/x86-64../build/arm64
# Native build (x86-64)
make O=../build/x86-64 allmodconfig
make O=../build/x86-64all -j50 2>&1|tee ../v3.18-build/x86-64.log
# arm64 build
CROSS_COMPILE=aarch64-cros-linux-gnu- ARCH=arm64 O=../build/arm64 make allmodconfig
CROSS_COMPILE=aarch64-cros-linux-gnu- ARCH=arm64 O=../build/arm64 make -j64 >/dev/null
```

Test build with Chrome OS config:

```bash
cd src/third_party/kernel/v4.19
git checkout linux-next/master
# Checkout config options only
git checkout m/master -- chromeos
# Normal emerge
(chroot) emerge-kukui -av chromeos-kernel-4_19
```

### Picking patches from mailing lists / upstream

See also [https://chromium.googlesource.com/chromiumos/docs/+/master/kernel\_faq.md#How-do-I-backport-an-upstream-patch](https://www.google.com/url?q=https://chromium.googlesource.com/chromiumos/docs/%2B/master/kernel_faq.md%23How-do-I-backport-an-upstream-patch&sa=D&ust=1557465766398000).

#### FROMGIT

```bash
../../../platform/dev/contrib/fromupstream.py -b b:123489157 \
  -t "Deploy kukui kernel with USE=kmemleak, no kmemleak warning in __arm_v7s_alloc_table" \
  'git://git.kernel.org/pub/scm/linux/kernel/git/joro/iommu.git#next/032ebd8548c9d05e8d2bdc7a7ec2fe29454b0ad0'
```

#### FROMLIST

Add project url in `~/.pwclientrc`

```rc
[options]
default=kernel

[kernel]
url=https://patchwork.kernel.org/
```

Then run:

```bash
../../../platform/dev/contrib/fromupstream.py -b b:132314838 -t "no crash with CONFIG_FAILSLAB" 'pw://10957015/'
# or
../../../platform/dev/contrib/fromupstream.py -b b:132314838 -t "no crash with CONFIG_FAILSLAB" 'pw://kernel/10957015/'
```

### Submitting patch series by gerrit cmd tool

In CrOS chroot:

```bash
gerrit deps ${CL_NUMBER} --raw
gerrit verify `gerrit deps ${CL\_NUMBER} --raw` 1
gerrit ready `gerrit deps ${CL\_NUMBER} --raw` 2
```

### Downloading a patch from patchwork into IMAP

So you have an email/patch on patchwork, but you didn't subscribe to the mailing
list, so you can't reply to/review the change.

To fetch the email into your IMAP/gmail account:

1.  Download the patchwork mbox file.
1.  Clone the [imap-upload] repo.
1.  `python2.7 ./imap_upload.py patch.mbox --gmail`
1.  Use @chromium.org account.
1.  Find the email in your mailbox, and reply!

mbox downloaded from patchwork doesn't include replies to the patch (e.g.
reviewer comments). To obtain mbox containing replies, download mbox.gz files
from https://lore.kernel.org/lkml/ instead.

[crbug.com/468342]: https://bugs.chromium.org/p/chromium/issues/detail?id=468342
[Debugging with KGDB/KDB]: ./kernel_faq.md#debugging-with-kgdb_kdb
[example CL]: https://chromium-review.googlesource.com/c/chromiumos/third_party/kernel/+/1325821
[ftrace]: https://www.kernel.org/doc/Documentation/trace/ftrace.txt
[go/chromeos-kernel-tips-and-tricks]: https://goto.google.com/chromeos-kernel-tips-and-tricks
[Heisenbug]: https://en.wikipedia.org/wiki/Heisenbug
[imap-upload]: https://github.com/rgladwell/imap-upload
[KASan]: https://www.kernel.org/doc/html/v4.14/dev-tools/kasan.html
[kernel_faq]: ./kernel_faq.md
[UPSTREAM, BACKPORT and FROMLIST]: ./kernel_faq.md#UPSTREAM_BACKPORT_FROMLIST_and-you
[SSH keys]: http://www.chromium.org/chromium-os/testing/autotest-developer-faq/ssh-test-keys-setup
