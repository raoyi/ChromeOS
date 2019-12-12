# Kernel FAQ

This document describes the basic workflow to follow, after you've made a
change to the Linux Kernel in the Chromium OS sources, to submit a your changes
to the Chromium OS repository, and to submit your changes upstream to the
official Linux Kernel repository.

[TOC]

## What commit message should I use?

See the [Kernel Design
page](https://sites.google.com/a/chromium.org/dev/chromium-os/chromiumos-design-docs/chromium-os-kernel)
for some more details.

### Code Changes

For changes which cannot be submitted upstream to the official Linux Kernel
repository, the commit message is important. We use the following conventions:

*   Begin the commit message with **CHROMIUM:**
*   If it is architecture specific, add the architecture. The following are
    samples of supported architectures: **ARM:** or **X86:**
*   If it is machine specific, add machine-identifying information. For
    example, **tegra2:** or **x86-mario:**.
*   Follow the needed tags with the subject for the commit message.
*   Follow the subject line with the body of the commit message. The message
    should not only describe **what**, but also **why**, you have created the
    change. Please include information about the testing that you performed to
    ensure the code is valid.
*   **Signed-off-by** is required, and our gerrit server is a bit picky about
    the order. It appears to require this line immediately before the
    **Change-Id** line if present.

An example subject line is: **CHROMIUM: ARM: tegra: Add initial support for
aebl**

**If not sure, use git log to check commit messages of earlier commits for the
same file or other files in the same directory.**

Do not include configuration changes (i.e. changes to files within
chromeos/config) with other code changes. See the next section for these.

Files may not be suitable for submission upstream because they have Chromium
OS-specific information, or may be based on other changes which are local to
the Chromium OS project. Such changes may not be upstreamed, but the Chromium
OS project team will continue to maintain the changes.

### Configuration Changes

When a commit involves configuration changes, make sure that any code changes
are separated out into a different commit. The configuration commit should
contain only changes to files within the chromeos/config directory tree.

The commit message should start with **CHROMIUM: config:**

An example message is: **CHROMIUM: config: enable aebl config**

## How do I send a patch upstream?

Changes to parts of the kernel which are not purely Chrome OS- specific should
be upstreamed where possible. This includes just about any part of the kernel:
ARM- and x86-specific changes, driver patches and changes within the main
kernel and mm source. You can start with a code review if you like. Take a look
on the kernel mailing list to get a feel for how people submit and review
patches.

To upstream, create a remote to track upstream.

For example the main kernel:

```bash
git remote add upstream git://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
git fetch upstream
git checkout -b send-upstream upstream/master
```

You can then create a commit within this branch. This can be done either by
cherry-picking the commit from another branch and perhaps changing the commit
message:

```bash
git cherry-pick my-change
git commit --amend
# edit the message and save
```

or using git am to turn a patch into a commit:

```bash
git am my-change.patch
```

or manually applying a patch, and then committing:

```bash
patch -p1 < my-change.patch
git add ...
git commit
# create a suitable message
```

### Sending patches the easy way (patman)

Patman automates patch creation, checking, change list creation, cover letter,
sending to the mailing list, etc. You can find patman in the U-Boot tree
(src/third\_party/u-boot/files/tools/patman). There is also a kernel patch set
[here](https://lkml.org/lkml/2015/5/3/105) with a newer version. Upstream
U-Boot has it also.

Amend your top commit to have the line:

```
Series-to: LKML <linux-kernel@vger.kernel.org>
Series-cc: (anyone you want to Cc all patches in the series to)
```

Then type:

```bash
patman -n
```

to generate patches, check that they will go to the right place, and send them. Or:

```bash
patman
```

to generate patches and send them.

Various options are available. Particularly useful ones are:

*   \-m - by default patman sends your patches to relevant maintainers. Use this option to turn that off
*   \-t - ignore tags in the subject line which cannot be found
*   \-n - do a dry run

Full documentation is available in the README (patman -h) or [here](http://git.denx.de/?p=u-boot.git;a=blob;f=tools/patman/README). Take a look at the automated change list creation and the alias support also.

### Sending patches manually

Like any kernel patch you should use checkpatch.pl to make sure it is clean
(see below). Also see Documentation/SubmittingPatches in the kernel source tree
for instructions. You can use `git show HEAD` to see your patch.

To send upstream, you can create patch files with `git format-patch`, and
then email then. This creates a set of patch files named '000n-<something>'
where 'n' is incremented starting from 1, and "something" comes from the first
line of each change description.

You can use `get_maintainer.pl` to figure out who to send it to.

```bash
# turn top commit into a patch
git format-patch HEAD~

# or perhaps you want to do the top 5 commits
git format-patch HEAD~5
# edit patches if you like

./scripts/get_maintainer.pl 0001-mypatch.patch | \
  sed 's/ *([^)]*) *//g' | \
  sed 's/"//g' | \
  sed 's/^\(.*\)$/--cc="\1" /' | \
  tr -d '\n'
# spits out a list of --cc addresses

# send out email, with subject prefix PATCH v5 (you can leave this out for default)
git send-email --to=linux-arm-kernel@lists.infradead.org --cc=... --cc=... --signoff --subject-prefix="PATCH v5" --annotate 0001-my-change.patch
# Edit the patch as required
```

> (**Note:** `git send-email` requires `git-email` to be installed on your host (`sudo apt-get install git-email`),
> or you will get the message "`git: 'send-email' is not a git command. See git --help.`".
> You also need to configure `.gitconfig` to use your SMTP server)

If you are sending a series of patches it is nice to include a cover letter.
This turns up as patch zero in the series. Pass the `--cover-letter` flag to
`git format-patch` and it will create a 0000-subject file which you can
edit to contain your cover letter. When you use `git send-email` you can
send files 000\* to send the cover letter and all your patches as one email
set.

Another flow that might work is to send email directly, without going through
`git format-patch`. For example you can email the top five commits to the
mailing list with something like:

```bash
git send-email --to=... -cc=... --signoff --subject-prefix=... --annotate HEAD~5
```

The `--annotate` lets you edit them before they go out, which is probably a good idea in this case!

When replying to an email thread with an updated patch, use the something like
the following to attach your email to the thread:

```bash
git send-email --thread --no-chain-reply-to --in-reply-to=<message id> --to=... --cc=... --signoff --subject-prefix=... --annotate 0002-...
```

You can find the message id under the label <Message-Id> in gmail in the 'Show
Original' link in the drop down options for the email you want to reply to.

There is a video here:
[http://www.youtube.com/watch?v=LLBrBBImJt4](http://www.youtube.com/watch?v=LLBrBBImJt4)

The patch flow throughout the video is:
[](http://www.youtube.com/watch?v=LLBrBBImJt4)

1.  `git diff`
2.  `git commit`
3.  `git show`
4.  `git format-patch`
5.  `git send-email`

Patch checklist: (at 34:30 of the video)

1.  Kernel builds with patch applied
2.  Correct "**From:**" address
3.  Concise "**Subject:**"
4.  Explain the patch
5.  **Signed-off-by**
6.  Check you have removed **Change ID**, **TEST=** and **BUG=** from the commit message

## Which copyright header should I use?

When adding new files to the kernel, please add a regular Google copyright
header to them. In particular this is true for any code that will eventually
find its way upstream (which should include practically everything we do).  The
main reason for this is that there's no concept of "The Chromium OS Authors"
outside of our project, since it refers to the AUTHORS file that isn't bundled
with the kernel.

Each file type has its own SPDX comment format, [discussed
here](https://www.kernel.org/doc/html/latest/process/license-rules.html#license-identifier-syntax):

C header files:
```c
/* SPDX-License-Identifier: GPL-2.0 */
/*
 * <short description>
 *
 * Copyright 2019 Google LLC.
 */
```

C source files:
```c
// SPDX-License-Identifier: GPL-2.0
/*
 * <short description>
 *
 * Copyright 2019 Google LLC.
 */
```

For reference, old drivers already existing in upstream might still have the
full text format, which would look like below.

```c
/*
 * Copyright 2018 Google LLC.
 *
 * This software is licensed under the terms of the GNU General Public
 * License version 2, as published by the Free Software Foundation, and
 * may be copied, distributed, and modified under those terms.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 */
```

## How do I check my patches are correct?

There are two aspects of having correct patches to send upstream: not having
Chromium OS-specific details, and meeting all the Linux kernel requirements.

For the following sections, you will need to have created a _patch_ file using
git format-patch. Also note that you will have to recreate the patch file, and
re-check your patch file each time you check in code to your source tree.

### Remove Chromium OS-specific Details

Verifying these details is as simple as loading the patch file in your favorite
editor. Edit the file manually to become compliant; this will, of course, have
no affect on the source or commit message stored by git.

*   No CHROMIUM:in the subject line of the patch file.
*   No **BUG=** in the patch file.
*   No **TEST=** in the patch file.
*   No **Change-Id:** in the patch file.
*   **Signed-off-by:** is in the patch file.

Once all of the above is true, you can move on to checking for compliance with
the Linux Kernel guidelines.

### Check for Compliance with Linux Kernel Requirements

You should use this perl script to check that your patch conforms to the kernel
coding standard. It is kept in the linux kernel tree.

```bash
git format-patch HEAD~
scripts/checkpatch.pl 0001-my-change.patch
# make improvements
git add ...
git commit --amend
# rinse and repeat
```

### Automating the Compliance Checks

This script might be useful also, as it checks a series of patches, checks for
Chrome OS-specific commit tags and prints a summary at the end. Put it in your
path and run it from anywhere.

```bash
#! /bin/sh

KERNEL=./scripts/
OUT=$(tempfile)
while (( "$#" )); do
ERRCP=
ERR=
"${KERNEL}/checkpatch.pl" $1 || ERRCP=1
grep BUG= $1 && ERR="$ERR BUG"
grep TEST= $1 && ERR="$ERR TEST"
grep "Change-Id" $1 && ERR="$ERR Change-Id"
grep "Review URL" $1 && ERR="$ERR Review URL"
if [ -n "${ERR}" ]; then
echo "Bad $1 ($ERR)" >>$OUT
else
echo "OK $1" >>$OUT
fi
shift
done
cat $OUT
```

## How do I backport an upstream patch?

Let's suppose you've spotted a juicy new commit in Linus's [upstream linux
kernel](http://git.kernel.org/?p=linux/kernel/git/torvalds/linux-2.6.git;a=summary)
tree that you just must have. Instead of creating a new branch and manually
applying the changes, use `git cherry-pick` to do it for you. In addition, the
repository maintainers appreciate it if the cherry-picked commit still contains
the original author and git hash of the original upstream commit.

For "simple" UPSTREAM cherry-picks, one should first try using
[fromupstream.py] script to prepare CLs "automagically". Doug Anderson (author)
provided [examples for
use](https://groups.google.com/a/chromium.org/forum/#!msg/chromium-os-reviews/S6eICwvbvbg/zEcikcTVAAAJ).

Otherwise, the follow steps use `git cherry-pick -x` to do most of the work:

```bash
NAME
        git-cherry-pick - Apply the changes introduced by some existing commits

SYNOPSIS
        git cherry-pick [--edit] [-n] [-m parent-number] [-s] [-x] [--ff] <commit>...

DESCRIPTION
	Given one or more existing commits, apply the change each one
	introduces, recording a new commit for each. This requires your working
	tree to be clean (no modifications from the HEAD commit).

OPTIONS
...
    -x
	When recording the commit, append to the original commit message a note
	that indicates which commit this change was cherry-picked from. Append
	the note only for cherry picks without conflicts. Do not use this
	option if you are cherry-picking from your private branch because the
	information is useless to the recipient. If on the other hand you are
	cherry-picking between two publicly visible branches (e.g. backporting
	a fix to a maintenance branch for an older release from a development
        branch), adding this information can be useful.
```

First, add Linus's tree as a remote to the chromium-os kernel tree (assuming the chromium-os root is `~/chromiumos`):

```bash
cd ~/chromiumos/src/third_party/kernel
git remote add linus git://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
git remote update
```

This will take a little while as git fetches all upstream commits. Luckily, git
is smart and won't refetch commits already in the chromium-os tree.

Once the tree is updated, take a brief look at whats been happening upstream
recently to a particular path (`--oneline` shows short-form upstream hashes and
the brief commit message):

```bash
git log --oneline linus/master /path/of/interest
```

We can view that juicy commit using its upstream hash:

```bash
git show <upstream_commit_hash>
```

To backport the commit to the chromium-os tree, first start a new branch from
the current Tip of Tree (ToT). Then cherry-pick with `-x` to preserve the
original author and hash, and `-s` to sign-off-by the commit:

```bash
repo sync .
repo start my_upstream_commit .
git cherry-pick -x -s <upstream_commit_hash>
```

Add TEST= and BUG= lines at the bottom of the patch description. Also, remember
to keep the patch subject intact with only an addition of UPSTREAM: or
BACKPORT: as a new prefix. Use UPSTREAM: if you are applying an upstream patch
as-is, or BACKPORT: if you had to change the code to make it run with an older
kernel version.

**NOTE:** Do not make functional changes to backported patches! Downstream
changes in backports should be strictly limited to resolving conflicts. If you
need to make a functional change to a backport (ie: changing a delay, tweaking a
default value, etc), backport the change from upstream as-is and follow up with
a separate patch with CHROMIUM prefix.

Now, the upstream commit is on its own branch, let's upload it to gerrit, like
usual:

```bash
repo upload .
```

This will generate a gerrit change for review.

After review, submit the patch in gerrit like usual.

### UPSTREAM, BACKPORT, FROMLIST, and you

When backporting patches from Linus's kernel tree, you should tag your patch
with UPSTREAM (or BACKPORT, if modifications were needed). But what about
patches that are "on their way" upstream, but haven't been merged for an
official release yet?

*   **FROMLIST:** use this tag when a patch has been sent to a public mailing
    list for review, but hasn't yet been merged anywhere. Before submitting a
    patch like this, try to address any review comments made in the public
    forum. Please also include a link to the list the patch was obtained from.
    For example:

    ```
    FROMLIST: bibble: a patch to fix everything
    ...
    ... original description verbatim, including any tags,
    ... e.g. Signed-off-by, Reviewed-by, etc.
    ...
    (am from https://lore.kernel.org/patchwork/patch/1060242/)
    ...
    ... any additional downstream information goes here, e.g.
    ... - (also found at A-LINK-BASED-ON-MESSAGE-ID),
    ... - BUG=,
    ... - TEST=,
    ... - Change-Id,
    ... - list of conflicts (e.g. generated by git),
    ... - cherry-picker's Signed-off-by, if not present in original description,
    ... - etc.
    ...
    ```
    *   **NOTE:** If a patch is rejected on the list, and it is still suitable
        for inclusion in the chromium kernel, it must be labeled as
        "CHROMIUM: FROMLIST:". These patches must have a link to the upstream
        discussion and must include the reason why we are diverging from
        upstream.

*   **UPSTREAM:** this tag should be used exclusively for patches that have
    actually landed in Linus' tree, not for cherry-picks from maintainer trees.

*   **BACKPORT:** follow the same rules as UPSTREAM, except that if you have to
    make changes to the patch, you should label it with BACKPORT and document
    what you had to change.

    *   **NOTE:** Do not make functional changes to backported patches!
        See the note in the previous section for guidance on how to handle
        functional changes to upstream patches.

*   **FROMGIT**: use this tag for cherry-picks of patches from maintainer
    trees, which have been applied in preparation for an upcoming release.

    *   Although it is a good reference for "what's going into the next
	release" **never** backport a patch straight from
	[linux-next](https://www.kernel.org/doc/man-pages/linux-next.html).
	Always source either a maintainer tree or a mailing list post.
    *   When including patches from maintainer trees, be specific about your
        source tree and branch. For example, for a patch from the for-next
        branch in the chrome-platform tree:

        ```
        FROMGIT: spi: mediatek: Only do dma for 4-byte aligned buffers
        ...
        (cherry picked from commit 1ce24864bff40e11500a699789412115fdf244bf
         git://git.kernel.org/pub/scm/linux/kernel/git/chrome-platform/linux.git for-next)
        ```

*   **BACKPORT: FROMLIST:** or **BACKPORT: FROMGIT:** follow  the same rules as
    FROMLIST or FROMGIT, except that if you have to make changes to the patch,
    you should also label it with BACKPORT (in addition to FROMLIST/FROMGIT)
    and document what you had to change.

Previous discussions:

*   [https://groups.google.com/a/chromium.org/forum/#!msg/chromium-os-dev/D56e2JxDhmc/IjgixwEReasJ](https://groups.google.com/a/chromium.org/forum/#!msg/chromium-os-dev/D56e2JxDhmc/IjgixwEReasJ)
*   [https://groups.google.com/a/chromium.org/forum/#!msg/chromium-os-dev/\_nY16h27k1s/FuHbWFCABwAJ](https://groups.google.com/a/chromium.org/forum/#!msg/chromium-os-dev/_nY16h27k1s/FuHbWFCABwAJ)

## [Kernel Configuration](https://sites.google.com/a/chromium.org/dev/chromium-os/how-tos-and-troubleshooting/kernel-configuration)

Kernel configuration in Chromium OS has an extra level of indirection from the
normal .config file. So do the instructions - [see this page for more
information](https://sites.google.com/a/chromium.org/dev/chromium-os/how-tos-and-troubleshooting/kernel-configuration).

### How to get the kernel config from a running system

The kernel config is not loaded by default (to save memory), so you'll need to
use `modprobe` to load it first:

```bash
(DUT)# modprobe configs; zcat /proc/config.gz
```

## How to quickly test kernel modifications (the fast way)

Do an incremental build of the kernel:

```bash
(chroot) $ FEATURES="noclean" cros_workon_make --board=${BOARD} --install chromeos-kernel-[3_8|3_10|3_14|3_18|4_4]
```

To enable debug options like lockdep and KASAN, add `USE="debug"` to the
command line above. This is highly recommended because the default build
is optimized for performance rather than debugging purpose. Note that the
debug build bloats the size of kernel image, and the image may not be able
to fit into its partition on some older devices. The debug build also takes
much longer to boot.

You can also enable serial port at the same time by `USE="debug pcserial"`.

Update the kernel on the target:

```bash
(chroot) $ ~/trunk/src/scripts/update_kernel.sh --remote <ip of target>
```

*** note
Note that using `cros_workon_make` leaves build artifacts in your source
directory under the `build` directory. When you do a regular emerge of the
kernel (and are `cros_workon`-ed) this will slow things down because the
entire source directory gets copied. So delete the `build` directory when
you're done.
***

*** note
Note: Please ensure that verity is disabled on the target before running the
`update_kernel.sh` script, otherwise the script won't be able to copy over
kernel modules and the target will be rebooted with just the kernel image
updated. Since the network drivers are built as modules, this leaves machine in
a state where there is no way to connect to the network after the reboot.
Verity can be disabled using the command
`/usr/share/vboot/bin/make_dev_ssd.sh --remove_rootfs_verification --partition <partition number>`
on the target followed by a reboot.
***

### Dealing with a bad kernel installation

One problem with this fast approach is that it requires an already installed
and booted target system. If you update with a bad kernel so that it no longer
boots, this approach is no longer available. The system is generally
recoverable by booting physical media (USB stick or SD card) and copying its
kernel blob over your kernel partition:

```bash
# Assuming you boot physical media as sdb, and your local disk is sda,
$ dd if=/dev/sdb2 of=/dev/sda2
```

#### Dealing with partition corruption due to bad kernel recovery

One time I really screwed up my system by recovering (after bad kernel
installation) with 'dd if=/dev/sdb of=/dev/sda'. I forgot the '2' after each
drive specification. This overwrote my internal partition table with an exact
copy of the USB stick's partition table, including the GUIDs. When I
subsequently tried to boot USB, the system always seemed to boot off the
internal disk. 'rootdev -s' reported (internal partition) /dev/sda3. After an
hour or so, consultation with Bill showed that I really was booting the kernel
from /dev/sda2, but the kernel found the matching GUID on sda before even
looking at sdb. This was recovered with:

```bash
$ a=$(uuidgen)
$ cgpt add -i 3 -u $a /dev/sda
```

which generates and installs a new GUID for sda3.

### Dealing with issues - preparing the environment

Below are described some problems you might encounter. If instructions above
work, you might skip them. We assume that you want to boot using the most
recently built image.

First, to prepare for other steps:

```bash
# cd to the image directory
(chroot) $ cd ~/trunk/src/build/images/${BOARD}/latest

# produce separate images for every partition
(chroot) $ ./unpack_partitions.sh chromiumos_image.bin
```

### SSHD keys

If sshd on the target machine complains about missing keys:

```bash
# Mount stateful partition
(chroot) $ sudo mount -o loop part_1 stateful_partition/

(chroot) $ sudo mkdir -p stateful_partition/etc/ssh/

# Generate and save keys.
# The paths below correspond to /mnt/stateful_partition/etc/ssh/ssh_host_{rsa,dsa}_key on target.
# Make sure these are correct for your configuration.
(chroot) $ sudo ssh-keygen -t rsa -f stateful_partition/etc/ssh/ssh_host_rsa_key
(chroot) $ sudo ssh-keygen -t dsa -f stateful_partition/etc/ssh/ssh_host_dsa_key

# Unmount the stateful partition
(chroot) $ sudo umount stateful_partition
```

### Public key authorization

update\_kernel.sh uses for authorization keys that, depending on your
configuration, might not be present in your image. If that's the case, you will
be prompted for password during script execution. To fix it, run the following
commands in your image directory:

```bash
# Mount root filesystem
(chroot) $ mkdir rootfs_dir/
(chroot) $ sudo mount -o loop part_3 rootfs_dir/

(chroot) $ sudo mkdir -p rootfs_dir/root/.ssh/
(chroot) $ sudo cp ~/trunk/src/scripts/mod_for_test_scripts/ssh_keys/testing_rsa.pub rootfs_dir/root/.ssh/authorized_keys

# Unmount root filesystem
(chroot) $ sudo umount rootfs_dir/
```

### iptables configuration

Iptables - again, depending on your configuration - might be configured to
refuse all the incoming connections, in which case update\_kernel.sh will be
unable to ssh to your target machine. If you encounter this problem, to fix it:

1.  Again mount the root filesystem:

    `(chroot) $ sudo mount -o loop part_3 rootfs_dir/`

2.  Edit file rootfs\_dir/etc/init/iptables.conf. Find the following line:

    `iptables -P INPUT DROP`

3.  Change it to:

    `iptables -P INPUT ACCEPT`

4.  Save and unmount the filesystem:

    `(chroot) $ sudo umount rootfs_dir/`
### Dealing with issues - cleaning up

To build new image after modifications to one or more of the partitions, simply
run:

```bash
(chroot) $ ./pack_partitions.sh chromiumos_image.bin
```

## How to test kernel modifications (the slow and not recommended way)

**Note:** there is more information (possibly more useful too) in the [disk
format](https://sites.google.com/a/chromium.org/dev/chromium-os/chromiumos-design-docs/disk-format)
document, and more specifically
[here](http://www.chromium.org/chromium-os/chromiumos-design-docs/disk-format#TOC-Kernel-partition-format).

Check out the tree somewhere as usual, make the chroot, build packages, build
image, blah blah blah. Create a bootable USB key from that image. We'll modify
that key with our testing kernel.

At this point you need to `cros_workon` the kernel (and clone the kernel tree
in case you used mini-layout). See the big picture and instructions in
[Chromium OS Developer
Guide](developer_guide.md), but as a quick
reference you are expected to run the following inside `chroot`:

```bash
~/trunk/src/scripts $ cros_workon start --board=<your platform> chromeos-kernel
~/trunk/src/scripts $ repo sync chromiumos/third_party/kernel
```

Then, still inside `chroot`, run this:

```bash
~/trunk/src/scripts $ export BUILD_DIR=/tmp/kernel # pick any new directory you like
~/trunk/src/scripts $ mkdir ${BUILD_DIR}
~/trunk/src/scripts $ cp /build/<your platform>/boot/config ${BUILD_DIR}/.config
~/trunk/src/scripts $ cd ../third_party/kernel/files
~/trunk/src/third_party/kernel/files $ ARCH=<your target arch> make oldconfig O=${BUILD_DIR}
~/trunk/src/third_party/kernel/files $ mv .git .git.bak
~/trunk/src/third_party/kernel/files $ CROSS_COMPILE=/usr/bin/<base_toolchain_name>- \
    ARCH=<your target arch> \
    make -j <num> <image_type> modules O=${BUILD_DIR}
~/trunk/src/third_party/kernel/files $ mv .git.bak .git
```

Where

*   `<your_target_arch>` is `arm` or `x86`, depending on your platform
*   `<base_toolchain_name>` is `armv7a-cros-linux-gnueabi-` or `i686-pc-linux-gnu-`, respectively,
*   `<image_type>` is `bzImage` for `x86` or `uImage` for `arm`,
*   `<num>` should be set to an integer which is twice the number of cores on your development machine.

Renaming of the `.git` directory for the duration for the build is required to
prevent mangling the module path by the kernel make. The `make` will produce
`${BUILD_DIR}/arch/<your_target_arch>/boot/{bzImage|uImage}`, which is the
kernel image you want to try. The next step varies depending on whether your
hardware has an EFI BIOS, legacy BIOS or u-boot. You can ether copy the kernel
to your USB stick and tell the bootloader to use your new kernel, possibly with
extra debugging arguments, or use netboot/NFS for u-boot equipped targets (see
[network based development]
for details).

If you need your module to be present on the target, you can scp it from the
build location to your target (provided your target is set for `ssh` access and
allows `chronos` account login).

### Testing with an EFI BIOS

**FIXME: Does this still apply to current boards? If yes, to which ones?**

Copy the new `bzImage` file into the `/efi/boot/` directory on your USB key's
partition 12. The `/efi/boot/grub.cfg` file will look for the kernel called
`vmlinuz`, but you can edit that config file to add a line to look for your
test kernel too. For example, here's my USB key's partition 12:

```bash
blackadder$ mount | grep vfat
/dev/sdc12 on /media/disk type vfat (rw,nosuid,nodev,uhelper=hal,shortname=mixed,uid=100135,utf8,umask=077,flush)

blackadder$ ls -l /media/disk/efi/boot/
total 6600
-rwx------ 1 wfrichar root 262656 Apr 21 10:21 bootx64.efi*
-rwx------ 1 wfrichar root 2851056 Apr 21 10:12 bzImage*
-rwx------ 1 wfrichar root 1040 Apr 21 08:51 grub.cfg*
-rwx------ 1 wfrichar root 2821296 Apr 19 11:19 vmlinuz*
blackadder$ cat /media/disk/efi/boot/grub.cfg
set timeout=10
set default=0

menuentry "bzImage normal" {
linux /efi/boot/bzImage quiet console=tty2 init=/sbin/init boot=local rootwait
root=/dev/sda3 ro noresume noswap i915.modeset=1 loglevel=1
}

menuentry "bzImage serial normal" {
linux /efi/boot/bzImage earlyprintk=serial,ttyS0,115200 console=ttyS0,115200 i
nit=/sbin/init boot=local rootwait root=/dev/sda3 ro noresume noswap i915.modese
t=1 loglevel=7
}

menuentry "bzImage serial add_efi_memmap" {
linux /efi/boot/bzImage add_efi_memmap earlyprintk=serial,ttyS0,115200 console
=ttyS0,115200 init=/sbin/init boot=local rootwait root=/dev/sda3 ro noresume nos
wap i915.modeset=1 loglevel=7
}

menuentry "vmlinuz normal" {
linux /efi/boot/vmlinuz quiet console=tty2 init=/sbin/init boot=local rootwait
root=/dev/sda3 ro noresume noswap i915.modeset=1 loglevel=1
}

menuentry "vmlinuz serial debug" {
linux /efi/boot/vmlinuz earlyprintk=serial,ttyS0,115200 console=ttyS0,115200 i
nit=/sbin/init boot=local rootwait root=/dev/sda3 ro noresume noswap i915.modese
t=1 loglevel=7
}
```

When the USB key boots, I'll see a menu that lets me select which boot path to use.

### Testing with a legacy BIOS

**FIXME: Does this still apply to current boards?** **If yes, to which ones?**

Copy the new `bzImage` file into the `/boot` directory on your USB key's
partition 3. The /boot/extlinux.conf file will look for the kernel called
`vmlinuz`, but you can edit that config file to add a line to look for your
test kernel too. For example, here's my USB key's partition 3:

```bash
blackadder$ mount | grep sdc3
/dev/sdc3 on /media/C-KEYFOB type ext3 (rw,nosuid,nodev,uhelper=hal)

blackadder$ ls -l /media/C-KEYFOB/boot
total 6940
lrwxrwxrwx 1 root root 19 Apr 23 01:55 System.map -> System.map-2.6.32.9
-rw-r--r-- 1 root root 1313402 Apr 23 00:12 System.map-2.6.32.9
-rw-r----- 1 root root 2851056 Apr 26 10:30 bzImage
lrwxrwxrwx 1 root root 15 Apr 23 01:55 config -> config-2.6.32.9
-rw-r--r-- 1 root root 74534 Apr 23 00:12 config-2.6.32.9
-rw-r--r-- 1 root root 409 Apr 23 01:53 extlinux.conf
-r--r--r-- 1 root root 14336 Apr 23 01:53 extlinux.sys
lrwxrwxrwx 1 root root 16 Apr 23 01:55 vmlinuz -> vmlinuz-2.6.32.9
-rw-r--r-- 1 root root 2821296 Apr 23 00:12 vmlinuz-2.6.32.9

blackadder$ cat /media/C-KEYFOB/boot/extlinux.conf
DEFAULT chromeos-usb
PROMPT 1
TIMEOUT 20

label chromeos-usb
  menu label chromeos-usb
  kernel vmlinuz
  append quiet console=tty2 init=/sbin/init boot=local rootwait root=/dev/sdb3 ro noresume noswap i915.modeset=1 loglevel=1

label chromeos-test
  menu label chromeos-test
  kernel bzImage
  append console=tty1 init=/sbin/init boot=local rootwait root=/dev/sdb3 ro noresume noswap i915.modeset=1 loglevel=7
```

When the USB key boots, I can hit TAB to see the list of boot choices, and can
pick the one I want by entering the label.

## Debugging messages

*** note
**FIXME: We don't have `CONFIG_DRM_FBDEV_EMULATION` set in our kernel configs,
so this might not work anymore.**
***

With either bootloader, you can debug early kernel failures by increasing the
verbosity and location of kernel debug messages. You can modify the config
files without rebuilding anything. The default boot args have this:

```
quiet console=tty2 loglevel=1
```

Using args like these instead may be helpful:

```
console=tty1 loglevel=7
```

## Dynamic Debugging (dev_dbg / pr_debug)

Dynamic debugging allows one to enable/disable debugging messages in kernel
code at runtime (e.g., calls to `dev_dbg` or `pr_debug`).

### Enabling

Using dynamic debugging requires the `CONFIG_DYNAMIC_DEBUG` config option to be
enabled. By default [dynamic debug is disabled on Chrome OS].

If using `menuconfig`, the following enables it:

```
Kernel hacking
     ---> printk and dmesg options
          ---> [*] Enable dynamic printk() support
```

Once the kernel is compiled with `CONFIG_DYNAMIC_DEBUG`, you can use the
following commands to control the output.

### Enable all dynamic debugging

```bash
echo "+p" > /sys/kernel/debug/dynamic_debug/control
```

### Disable all dynamic debugging

```bash
echo "-p" > /sys/kernel/debug/dynamic_debug/control
```

### Enable dynamic debugging for specific modules

```bash
echo "module cros_ec_spi +p" > /sys/kernel/debug/dynamic_debug/control
echo "module cros_ec_proto +p" > /sys/kernel/debug/dynamic_debug/control
```

### View all of the individual statements that can be enabled

```bash
cat /sys/kernel/debug/dynamic_debug/control
```

See [Dynamic Debug] for complete details and syntax.

## Working on several kernel issues

`git` supports multiple branches coexisting in the same directory tree, and
kernel make system supports placing the kernel build output in a separate
directory (using the `O=<path>` make command line parameter).

To create separate builds get per kernel git branch, while in the cloned kernel
source tree root create a build directory for your current branch, for
instance:

```bash
mkdir ../build/<branch_name>
```

and then just add `O=../../build/<branch_name>` to make invocations described
above. Or use the following bash script to take care of all make command line
parameters other than make targets:

```bash
kmake () {
  b=$(git branch 2>/dev/null | grep '^\*' | awk '{print $2}')
  if [ "${b}" == "" ]; then
    echo "not in a git tree"
    return
  fi
  build_dir="../build/${b}"
  if [ ! -d "${build_dir}" ]; then
    echo "build directory ${build_dir} does not exist"
    return
  fi
  make_jobs=$(expr 2 \* $(cat /proc/cpuinfo | grep -c '^processor'))
  make ARCH=i386 O=${build_dir} -j "${make_jobs}" $*
}
```

### Modifying H2C Bios kernel command line

**FIXME: Does this still apply to current boards?** **If yes, to which ones?**

Place kernel blob into a file (`<original_kernel>`), either using `dd` on the
target or by dismantling `chromiumos_image.bin` generated by build\_image.
Store the desired kernel command line in a file <new\_cmd\_line> and then use
the following to change the kernel command line:

```bash
vbutil_kernel --repack <modified_kernel> --config <new_cmd_line> \
  --signprivate <path_to>/vboot_reference/``tests/devkeys/<key> \
  --oldblob <original_kernel>
```

where `<key>` is `kernel_data_key.vbprivk` for the main kernel or
`recovery_kernel_data_key.vbprivk` for the flash drive based recovery kernel
The keys can be found in the [vboot\_reference repository](/). Then `dd` the
`<modified_kernel>` file back to where `<original_kernel>` came from.

The command line to boot a kernel with verified rootfs disabled can be obtain
by editing the regular command line as follows:

```bash
vbutil_kernel --verify <original_kernel> --verbose | tail -1 | sed '
s/dm_verity[^ ]\+//g
s|verity /dev/sd%D%P /dev/sd%D%P ||
s| root=/dev/dm-0 | root=/dev/sd%D%P |
s/dm="[^"]\+" //' > new_cmd_line
```

## Installing onto SSD

**FIXME: Does this still apply to current boards?** **If yes, to which ones?**

Instead of booting the kernel from USB as described above, it can be installed
directly on the SSD of the target device. With modern H2C Bios, this requires
signing the blob with the development key and booting with the target machine's
development mode switch set appropriately. Also, since there are two
kernel/root partition pairs in our partition scheme, we need to select which
one we want to use. Usually we stay with the current pair.

To sign with the devkey as per the Disk Format doc
[http://www.chromium.org/chromium-os/chromiumos-design-docs/disk-format#TOC-Quick-development](http://www.chromium.org/chromium-os/chromiumos-design-docs/disk-format#TOC-Quick-development):

```bash
vbutil_kernel --pack new_kern.bin --keyblock /usr/share/vboot/devkeys/kernel.keyblock --signprivate <keys_path>/kernel_data_key.vbprivk --version 1 --config config.txt --bootloader /lib64/bootstub/bootstub.efi --vmlinuz vmlinuz
```

Transfer `new_kern.bin` to the target system. I prefer `scp`, but it can be
placed on USB stick as well.

Identify the preferred kernel partition. This will be either `sda2` or `sda4`.
`rootdev -s` will identify the root partition, and that can be used to identify
the currently booted kernel partition.

|         | Kernel      | Root        |
|---------|-------------|-------------|
| pair A  | `/dev/sda2` | `/dev/sda3` |
| pair B  | `/dev/sda4` | `/dev/sda5` |

Copy the image to the partition.

```bash
dd if=new_kern.bin of=/dev/sda2
```

`dev_debug_vboot` can be used to verify the kernel partition has a properly signed image. Indeed, it will actually tell you in what modes (ie, development, recovery, neither) your kernel will boot.

```bash
localhost ~ # dev_debug_vboot
 :
TEST: verify HD kernel B with firmware A key
Key block:
  Size:                0x4b8
  Flags:               7  !DEV DEV !REC
 :
```

`cgpt` can be used as an alternative to `rootdev` above to find the currently
preferred kernel partition.

```bash
localhost ~ # cgpt show /dev/sda
     start      size    part  contents
 :
      4096     32768       2  Label: "KERN-A"
                              Type: ChromeOS kernel
                              UUID: B87DAA9E-E82E-B449-B93A-5EB0BD81BCEC
                              Attr: priority=3 tries=0 successful=1
 :
     36864     32768       4  Label: "KERN-B"
                              Type: ChromeOS kernel
                              UUID: 4581FC5C-58D1-8148-9FC4-E4B983C90782
                              Attr: priority=0 tries=0 successful=0
 :
```

## Getting a Kernel Trace

Run the following commands on the target. This needs to be done just once after
an install.

```bash
touch /var/lib/crash_sender_paused
touch /home/chronos/"Consent To Send Stats"
chown chronos:chronos /var/lib/crash_sender_paused
chown chronos:chronos /home/chronos/"Consent To Send Stats"
sync; sync; sync
```

The crashes will then appear in /var/spool/crash.

## Loading Kernel modules from outside the root filesystem

If you need to load kernel modules from a location other than the root
filesystem, module locking must be disabled. Either a kernel command line
option can be used:

```
lsm.module_locking=0
```

Or, on images with dm-verity disabled (--noenable\_rootfs\_verification), the
restriction can be disabled via the exposed sysctl:

```bash
echo 0 >/proc/sys/kernel/chromiumos/module_locking
```

## Blacklisting Kernel modules for individual overlays

If you need to blacklist kernel modules for specific overlays. Modify the
overlay-<name>/chromeos-base/chromeos-bsp-<name>/chromeos-bsp-<name>-<version>.ebuild
file.

Add the following two lines to the end of the src\_install() function:

```bash
insinto "/etc/modprobe.d"
doins "${FILESDIR}/<blacklist file>"
```

The ${FILESDIR} variable points to the files/ directory within the
chromeos-bsp-<name>/ directory. Within this directory, add your <blacklist
file> (ex cros-blacklist.conf).

For each kernel module you wish to blacklist, add the following line to
<blacklist file>:

```
blacklist <module name>
```

You can also use # comments within these files to explain why the kernel module
needs to be blacklisted.

## Building and installing kernel-next on a specific overlay

If given target device is not building kernel-next, you can switch by unmerging
the standard kernel and then building kernel-next normally:

```bash
cros_workon --board=${BOARD} stop sys-kernel/chromeos-kernel
emerge-${BOARD} --unmerge sys-kernel/chromeos-kernel
cros_workon --board=${BOARD} start sys-kernel/chromeos-kernel-next
cros_workon_make --board=${BOARD} sys-kernel/chromeos-kernel-next --install
~/trunk/src/scripts/update_kernel.sh --board=${BOARD} --remote=hostname...
```

## Debugging kernel crashes

TODO: This is anecdotal, and may not be an optimal or fully correct solution.
Please verify and remove the TODO.

You have a few options:

1\. Googler-only: Check out go/xstability. Clicking on sample crashes here
go/crash with the filter set for that particular crash. Click on a sample
report. Below the "Report Time" and "Client ID" you should "Files" with a link
to "upload\_file\_kcrash". This has the stack trace towards the end.

TODO: Add more details on this

2\. If you are debugging a local crash on your device, look for the crash in
/var/log/messages (unlikely that it would be saved there) or
/sys/fs/pstore/console-ramoops. You may see some symbols preceded by question
marks in the stack trace, something like the below.

```
<5>[ 25.801932] Call Trace:
<5>[ 25.801947] [<ffffffffc008c064>] ieee80211_amsdu_to_8023s+0xec/0x2df [cfg80211]
<5>[ 25.801968] [<ffffffffc02af0f2>] __iwl7000_ieee80211_sta_ps_transition+0x154a/0x21dc [iwl7000_mac80211]
<5>[ 25.801987] [<ffffffffc03154e4>] ? iwl_mvm_send_lq_cmd+0x8e/0x9c [iwlmvm]
<5>[ 25.802003] [<ffffffffc0324409>] ? iwl_mvm_rs_tx_status+0xf9c/0x1f5cd /4 [iwlmvm]
<5>[ 25.802023] [<ffffffffc02b06f2>] __iwl7000_ieee80211_mark_rx_ba_filtered_frames+0x96e/0xcb0 [iwl7000_mac80211]
<5>[ 25.802041] [<ffffffff9e4ee0f0>] ? kmem_cache_free+0x8a/0xc5
<5>[ 25.802059] [<ffffffffc02b08a1>] __iwl7000_ieee80211_mark_rx_ba_filtered_frames+0xb1d/0xcb0 [iwl7000_mac80211]
<5>[ 25.802080] [<ffffffffc02b0dc6>] __iwl7000_ieee80211_rx_napi+0x392/0x46a [iwl7000_mac80211]
<5>[ 25.802098] [<ffffffffc0316578>] iwl_mvm_rx_rx_mpdu+0x749/0x78b [iwlmvm]
<5>[ 25.802113] [<ffffffffc0310f16>] iwl_mvm_enter_d0i3+0x359/0xe7f [iwlmvm]
<5>[ 25.802128] [<ffffffffc023d504>] iwl_pci_unregister_driver+0xfdb/0x1439 [iwlwifi]
<5>[ 25.802143] [<ffffffffc023e883>] iwl_pcie_irq_handler+0x57d/0x7d1 [iwlwifi]
<5>[ 25.802157] [<ffffffff9e48c255>] ? free_irq+0x8a/0x8a
<5>[ 25.802168] [<ffffffff9e48c272>] irq_thread_fn+0x1d/0x3c
<5>[ 25.802179] [<ffffffff9e48be1a>] irq_thread+0x117/0x21a
<5>[ 25.802191] [<ffffffff9e921dda>] ? __schedule+0x589/0x5d3
<5>[ 25.802202] [<ffffffff9e48b863>] ? kzalloc.constprop.37+0x1c/0x1c
<5>[ 25.802214] [<ffffffff9e48bd03>] ? irq_thread_check_affinity+0x8f/0x8f
<5>[ 25.802227] [<ffffffff9e45183b>] kthread+0xc0/0xc8
<5>[ 25.802238] [<ffffffff9e45177b>] ? __kthread_parkme+0x6b/0x6b
<5>[ 25.802249] [<ffffffff9e92389c>] ret_from_fork+0x7c/0xb0
<5>[ 25.802259] [<ffffffff9e45177b>] ? __kthread_parkme+0x6b/0x6b
```

There are a few ways you can resolve the "? some\_symbol + 0xoffset" format
into a line of source code. For example, you can enter the cros\_sdk
chroot and load up the vmlinux file in gdb.

Be careful to use the gdb binary from the cross-toolchain of the $BOARD you are
debugging on. TODO(crbug.com/995661): Chromium OS runs 32-bit ARM userspace on
ARM64 boards and there is no good programmatic way of getting the right gdb
tuple in such case, so just use aarch64-cros-linux-gnu-gdb with them for the
time being.

```bash
(cr) user@machine /build/samus $ gdb="$(portageq-$BOARD envvar CHOST)-gdb"
(cr) user@machine /build/samus $ file /build/$BOARD/usr/lib/debug/boot/vmlinux | grep -q aarch64 && gdb="aarch64-cros-linux-gnu-gdb"
(cr) user@machine /build/samus $ ${gdb} /build/$BOARD/usr/lib/debug/boot/vmlinux
```

Next, use the list command to print the code at given address

```bash
Reading symbols from /build/samus/usr/lib/debug/boot/vmlinux...done.
(gdb) list *( iwl_mvm_send_lq_cmd+0x8e)
0x12b5 is in iwl_mvm_send_lq_cmd (/mnt/host/source/src/third_party/kernel/v3.14/drivers/net/wireless-3.8/iwl7000/iwlwifi/mvm/utils.c:752).
747  };
748
749  if (WARN_ON(lq->sta_id == IWL_MVM_STATION_COUNT))
750  return -EINVAL;
751
752  return iwl_mvm_send_cmd(mvm, &cmd);
753  }
754
755  /**
756  * iwl_mvm_update_smps - Get a request to change the SMPS mode
(gdb)
```

3\. A slightly more tedious way of getting symbols is to symbolize the whole kernel using objdump -

```bash
cd /build/samus/var/cache/portage/sys-kernel/chromeos-kernel-3_14
# Pick a proper output location - the resulting file is > 2GB in size!
objdump -e vmlinux > /tmp/objdump-output.txt
grep your_kernel_symbol /tmp/objdump-output.txt
```

More information [here](https://wiki.ubuntu.com/Kernel/KernelDebuggingTricks) and [here](http://www.linuxjournal.com/article/9252).

## Profiling functions and/or following code flow in the kernel

TODO: This is anecdotal, and may not be an optimal or fully correct solution.
Please verify and remove the TODO.

One way to do this is by function tracing for the functions/modules you are
interested in the kernel.

```bash
cd /sys/kernel/debug/tracing
# Sample output: blk function_graph function nop. These are valid values you can echo into current_tracer
cat available_tracers

# By default this should output 'nop'
cat current_tracer

# function_graph is useful too
echo "function" > current_tracer

# This should output "all functions enabled" by default
cat set_ftrace_filter

# You can also append with "echo *nl80211* >> set_ftrace_filter"
echo *nl80211* > set_ftrace_filter

# Should be the number of functions enabled.
wc -l set_ftrace_filter

# Clear out the tracing pipe of the previous junk. You will need to Ctrl-C kill this after a while
cat trace_pipe > /dev/null

# You should see nothing, now start performing actions that will lead to your module/code being called.
cat trace_pipe
```

More information here: [https://lwn.net/Articles/370423/](https://lwn.net/Articles/370423/)

## Debugging with KGDB/KDB

KGDB is an in-kernel debugger implementation, which allows developers to attach
a local GDB instance on their development machine to debug the kernel on a
remote test machine, using a serial connection. You can find some information
here:

*   [https://www.kernel.org/pub/linux/kernel/people/jwessel/kdb/](https://www.kernel.org/pub/linux/kernel/people/jwessel/kdb/)
*   [http://elinux.org/Kgdb](http://elinux.org/Kgdb)
*   https://events.static.linuxfound.org/sites/events/files/slides/ELC-E%20Linux%20Awareness.pdf

To use KGDB with Chromium OS requires two steps for the test machine:

1.  Enable KGDB in the kernel configuration
2.  Set kernel parameters to enable the appropriate debug console

Step 1 can be done by building with `USE="kgdb"`:

```bash
USE="kgdb vtconsole" emerge-${BOARD} chromeos-kernel-${VER}
```

Step 2 can be done by adding `kgdboc=$TTY` to the kernel config.txt, where
`$TTY` depends on the board -- for many systems, this should be `ttyS0`, but
some ARM SoCs use `ttyS2`.

Once you configure the target device, you can break into debug mode with the
`Alt-SysRq-G` shortcut (see [Linux SysRq
docs](https://www.kernel.org/doc/html/latest/admin-guide/sysrq.html)); e.g.:

*   `Alt-VolUp-G` on the DUT keyboard
*   ``<enter> ` Z G`` (brk-g) if using servo
*   `echo g > /proc/sysrq-trigger`

then attach to the target console with your cross-targeted GDB:

```bash
${CROSS_ARCH}-gdb \
         /build/${BOARD}/usr/lib/debug/boot/vmlinux \
         -ex "set remotebaud 115200" \
         -ex "target remote $(dut-control cpu_uart_pty | cut -d: -f2)"
```

Once attached, you can use standard GDB commands, though report has it that not
everything works well (e.g., stepping and breakpoints) -- YMMV.

Besides basic GDB commands, you can make use of Linux-specific KDB commands via
the `monitor` command. For more info, run this while attached:

```bash
(gdb) monitor help
Command Usage Description
----------------------------------------------------------
[...]
```

### Debugging modules

You can get a list of modules and addresses in kgdb with `monitor` `lsmod`.
Then you can add symbol files using the base addresses found there:

```bash
add-symbol-file /build/${BOARD}/usr/lib/debug/lib/modules/3.8.11/kernel/drivers/net/wireless/mwifiex/mwifiex.ko.debug 0xbf077000
add-symbol-file /build/${BOARD}/usr/lib/debug/lib/modules/3.8.11/kernel/drivers/net/wireless/mwifiex/mwifiex_sdio.ko.debug 0xbf0a0000
```

If you're in kgdb and want to get back to kdb:

```
maintenance packet 3
Ctrl-Z
kill -9 %
```

### Multiplexing the console

If you want to use both KGDB and a standard serial console over the same serial
port, you need to run a program like `kdmx` or `agent-proxy` to multiplex your
connection. Both can be found at:

[https://kernel.googlesource.com/pub/scm/utils/kernel/kgdb/agent-proxy/](https://kernel.googlesource.com/pub/scm/utils/kernel/kgdb/agent-proxy/)

kdmx is probably easier to deal with. If your serial port is at `/dev/pts/80`,
you can start it with:

```bash
agent-proxy/kdmx/kdmx -n -b 115200 -p /dev/pts/80 -s /tmp/kdmx_tty_
```

You can find the ttys to use for console in `/tmp/kdmx_tty_trm` and for gdb in
`/tmp/kdmx_tty_gdb`. Thus connect to the terminal with:

```bash
cu --nostop -l $(cat /tmp/kdmx_tty_trm)
```

and attach gdb with:

```bash
${CROSS_ARCH}-gdb \
	/build/${BOARD}/usr/lib/debug/boot/vmlinux \
	-ex "target remote $(cat /tmp/kdmx_tty_gdb)"
```

If telnet is more your style, use agent-proxy with:

```bash
agent-proxy 127.0.0.1:5510^127.0.0.1:5511 0 /dev/pts/80,115200
```

Then connect to the terminal with:

```bash
telnet localhost 5510
```

and attach gdb with:

```bash
${CROSS_ARCH}-gdb \
         /build/${BOARD}/usr/lib/debug/boot/vmlinux \
         -ex "target remote localhost:5511"
```

### Errata

*   KDB's `monitor ftdump` calls sleeping allocation functions (as of
    2016-11-17)
*   [https://lkml.kernel.org/r/20161117191605.GA21459@google.com](https://lkml.kernel.org/r/20161117191605.GA21459@google.com)

## Old stuff (may still work with some old boards)

### How to quickly test kernel modifications (the fastest way, outdated)

**FIXME: The instructions the link leads to seem to apply only to ancient
boards running U-Boot.**

Please take a look at doc on [network based development].
While setting up your environment might appear to be harder and more time
consuming, in many cases it will allow to test kernel modifications much faster
and easier than the ways described below.

[fromupstream.py]: https://chromium.googlesource.com/chromiumos/platform/dev-util/+/master/contrib/fromupstream.py
[Dynamic Debug]: https://www.kernel.org/doc/html/v4.19/admin-guide/dynamic-debug-howto.html
[dynamic debug is disabled on Chrome OS]: https://crbug.com/188825
[network based development]: http://www.chromium.org/chromium-os/how-tos-and-troubleshooting/network-based-development
