# Building Chrome for Chrome OS (Simple Chrome)

This workflow allows you to quickly build/deploy Chrome to a Chrome OS
[VM] or device without needing a Chrome OS source checkout or chroot. It's useful
for trying out your changes on Chrome OS while you're doing Chrome
development. If you have an OS checkout and want your local Chrome changes to
be included when building a full OS image, see the [OS development guide].

At its core is the `chrome-sdk` shell which sets up the shell environment and
fetches the necessary SDK components (Chrome OS toolchain, sysroot, VM, etc.).

[TOC]

## Typography conventions

| Label         | Paths, files, and commands                            |
|---------------|-------------------------------------------------------|
|  (shell)      | outside the chroot and SDK shell on your workstation  |
|  (sdk)        | inside the `chrome-sdk` SDK shell on your workstation |
|  (chroot)     | inside the `cros_sdk` chroot on your workstation      |
|  (device)     | in your [VM] or Chrome OS device                        |


## Getting started

Check out a copy of the [Chrome source code and depot_tools].
Be certain to [update .gclient] to include `target_os = ["chromeos"]`.

### Get the Google API keys

In order to sign in to Chrome OS you must have Google API keys:

*   External contributors: See [api-keys]. You'll need to put them in your
    `out_$BOARD/Release/args.gn file`, see below.
*   *Googlers*: See [go/chrome-build-instructions] to get the internal source.
    If you have `src-internal` in your `.gclient` file the official API keys
    will be set up automatically.

### Set up gsutil

Use depot_tools/gsutil.py and run `gsutil.py config` to set the authentication
token. (*Googlers*: Use your @google.com account.) Otherwise steps below may run
slowly and fail with "Login Required" from gsutil.

When prompted for a project ID, enter `134157665460` (this is the Chrome OS
project ID).

### Install build deps

You'll also need to pull in Android native toolchain dependencies to build
ARC++ support libraries. This is done by running the
[install-build-deps-android.sh] script in Chrome's source code, located at
`$CHROME_DIR/src/build/install-build-deps-android.sh`.

### VM versus Device

The easiest way to develop on Chrome OS is to use a [VM].

If you need to test hardware-specific features such as graphics acceleration,
bluetooth, mouse or input events, etc, you may also use a physical device
(Googlers: Chromestop has the hardware). See [Set up the Chrome OS device] for
details.

---

## Enter the Simple Chrome environment

Building Chrome for Chrome OS requires a toolchain customized for each
Chromebook model (or "board"). For the Chrome OS [VM], and non-Googlers, use
`amd64-generic`. For a physical device, look up the [Chrome OS board name] by
navigating to the URL `about:version` on the device. For example:
`Platform 10176.47.0 (Official Build) beta-channel samus` has board `samus`.

To enter the Simple Chrome environment, run these from within your Chrome
checkout:

```
(shell) cd /path/to/chrome/src
(shell) export BOARD=amd64-generic
(shell) cros chrome-sdk --board=$BOARD --log-level=info [--download-vm] [--gomadir=~/goma]
```

The command prompt will change to look like `(sdk $BOARD $VERSION)`.

Entering the Simple Chrome environment does the following:

1.  Fetches the Chrome OS toolchain and sysroot (SDK) for building Chrome.
1.  Creates out_$BOARD/Release and generates or updates args.gn.
1.  Installs and starts [Goma].  (*Non-Googlers* may need to disable this with
    `--nogoma`, Googlers would want to reuse existing installation with
    `--gomadir`.)
1.  `--download-vm` will download a Chrome OS VM and a QEMU binary.

### cros chrome-sdk options

*   `--internal` Sets up Simple Chrome to build and deploy the official *Chrome*
    instead of *Chromium*.
*   `--gn-extra-args='extra_arg=foo other_extra_arg=bar'` For setting
    extra gn args, e.g. 'dcheck_always_on=true'.
*   `--log-level=info` Sets the log level to 'info' or 'debug' (default is
    'warn').
*   `--nogn-gen` Do not run 'gn gen' automatically.

**Chrome OS developers**: Please set `dcheck_always_on=true` and file bugs if
you encounter any DCHECK crashes.
```
(shell) cros chrome-sdk --internal --board=$BOARD --log-level=info --gn-extra-args='dcheck_always_on=true'
```

### cros chrome-sdk tips

> **Important:** When you sync/update your Chrome source, the Chrome OS SDK
> version (src/chromeos/CHROMEOS_LKGM) may change. When the SDK version changes
> you may need to exit and re-enter the Simple Chrome environment to
> successfully build and deploy Chrome.

> **Non-Googlers**: Only generic boards have publicly available SDK downloads,
> so you will need to use a generic board (e.g. amd64-generic) or your own
> Chrome OS build (see [Using a custom Chrome OS build]). For more info and
> updates star [crbug.com/360342].

> **Note**: See also [Using a custom Chrome OS build].

---

## Build Chrome

To build Chrome, run:

```
(sdk) autoninja -C out_${SDK_BOARD}/Release chrome nacl_helper
```

> **Note**: Targets other than **chrome**, **nacl_helper** or
> (optionally) **chromiumos_preflight** are not supported in Simple Chrome and
> will likely fail. browser_tests should be run outside the Simple Chrome
> environment. Some unit_tests may be built in the Simple Chrome environment and
> run in the Chrome OS VM. For details, see
> [Running a Chrome Google Test binary in the VM].

> **Note**: Simple Chrome uses [Goma]. To watch the build progress, find the
> Goma port (`$ echo $SDK_GOMA_PORT`) and open http://localhost:<port_number>
> in a browser.

> **Note:** The default extensions will be installed by the test image you use
> below.

---

## Set up the Chrome OS device

### Getting started

You need the following:
1.  USB flash drive 4 GB or larger (for example, a Sandisk Extreme USB 3.0)
1.  USB to Gigabit Ethernet adapter

Before you can deploy your build of Chrome to the device, it needs to have a
"test" OS image loaded on it. A test image has tools like rsync that are not
part of the end-user image.

Chrome should be deployed to a recent Chrome OS test image, ideally the
version shown in your SDK prompt (or `(sdk) echo $SDK_VERSION`).

### Create a bootable USB stick

**Googlers**: Images for all boards are available on [go/goldeneye]:

1.  Find the matching Chrome OS version and click on the column for 'Canary'
    or 'Dev'.
1.  Click on the dropdown icon in the 'Images' column and click on 'Unsigned
    test image'.

**Non-Googlers**: The build infrastructure is currently in flux. See
[crbug.com/360342] for more details. You may need to build your own Chrome OS
image.

After you download the compressed tarball containing the test image (it should
have "test" somewhere in the file name), extract the image by running:

```
(sdk) tar xvf ~/Downloads/<image-you-downloaded>
```

Copy the image to your USB stick using `cros flash`:

```
(sdk) cros flash usb:// chromiumos_test_image.bin
```

> **Tip:** If you have a Chrome OS checkout, the following can be used to
update a device that already has a test image installed. Star
[crbug.com/403086] for updates on a proposal to support this without a
Chrome OS checkout.

```
.../chromeos/src $ cros flash $IP_ADDR chromiumos_test_image.bin
```

### Put your Chrome OS device in dev mode

You can skip this section if you're using a [VM].

> **Note:** Switching to dev mode wipes all data from the device (for security
> reasons).

Most recent devices can use the [generic instructions]. To summarize:

1.  With the device on, hit Esc + Refresh (F2 or F3) + power button
1.  Wait for the white "recovery screen"
1.  Hit Ctrl-D to switch to developer mode (there's no prompt)
1.  Press enter to confirm
1.  Once it is done, hit Ctrl-D again to boot, then wait

From this point on you'll always see the white screen when you turn on
the device. Press Ctrl-D to boot.

Older devices may have [device-specific instructions].

*Googlers*: If the device asks you to "enterprise enroll", click the X in the
top-right of the dialog to skip it. Trying to use your google.com credentials
will result in an error.

### Enable booting from USB

By default Chromebooks will not boot off a USB stick for security reasons.
You need to enable it.

1.  Start the device
1.  Press Ctrl-Alt-F2 to get a terminal. (You can use Ctrl-Alt-F1 to switch
    back if you need to.)
1.  Login as `root` (no password yet, there will be one later)
1.  Run `enable_dev_usb_boot`

### Install the test image onto your device

> **Note:** Do not log into this test image with a username and password you
> care about. The root password is public ("test0000"), so anyone with SSH
> access could compromise the device. Create a test Gmail account and use that.

1.  Plug the USB stick into the machine and reboot.
1.  At the dev-mode warning screen, press Ctrl-U to boot from the USB stick.
1.  Switch to terminal by pressing Ctrl-Alt-F2
1.  Login as user `chronos`, password `test0000`.
1.  Run `/usr/sbin/chromeos-install`
1.  Wait for it to copy the image
1.  Run `poweroff`

You can now unplug the USB stick.

### Connect device to Ethernet

Use your USB-to-Ethernet adapter to connect the device to a network.

*Googlers*: If your building has Ethernet jacks connected to the test VLAN
(e.g. white ports), use one of those jacks. Otherwise get a second Ethernet
adapter and see [go/shortleash] to reverse tether your Chromebook to your
workstation.

### Checking the IP address

1.  Click the status area in the lower-right corner
1.  Click the network icon
1.  Click the circled `i` symbol in the lower-right corner
1.  A small window pops up that shows the IP address

You can also run `ifconfig` from the terminal (Ctrl-Alt-F2).

---

## Deploying Chrome to the device

To deploy the build to a device/VM, you will need direct SSH access to it from
your computer. The scripts below handle everything else.

### Using deploy_chrome

The `deploy_chrome` script uses rsync to incrementally deploy Chrome to the
device/VM.

Specify the build output directory to deploy from using `--build-dir`. For the
[VM]:

```
(sdk) deploy_chrome --build-dir=out_${SDK_BOARD}/Release --to=localhost --port=9222
```

For a physical device, which must be ssh-able as user 'root', you must specify
the IP address using `--to`:

```
(sdk) deploy_chrome --build-dir=out_${SDK_BOARD}/Release --to=$IP_ADDR
```

> **Note:** The first time you run this you will be prompted to remove rootfs
> verification from the device. This is required to overwrite /opt/google/chrome
> and will reboot the device. You can skip the prompt with `--force`.

### Deploying Chrome to the user partition

It is also possible to deploy Chrome to the user partition of the device and
set up a temporary mount from `/opt/google/chrome` using the option `--mount`.
This is useful when deploying a binary that will not otherwise fit on the
device, e.g.:

*   When using `--nostrip` to provide symbols for backtraces.
*   When using other compile options that produce a significantly larger image.

```
(sdk) deploy_chrome --build-dir=out_$SDK_BOARD/Release --to=$IP_ADDR --mount [--nostrip]
```

> **Note:** This also prompts to remove rootfs verification so that
> /etc/chrome_dev.conf can be modified (see [Command-line flags and
> environment variables]). You can skip that by adding
> `--noremove-rootfs-verification`.

#### Additional Notes:

*   The mount is transient and does not survive a reboot. The easiest way to
    reinstate the mount is to run the same deploy_chrome command after reboot.
    It will only redeploy binaries if there is a change. To verify that the
    mount is active, run `findmnt /opt/google/chrome`. The output should be:
```
TARGET             SOURCE                                      FSTYPE OPTIONS
/opt/google/chrome /dev/sda1[/deploy_rootfs/opt/google/chrome] ext4   rw,nodev,noatime,resgid=20119,commit=600,data=ordered
```
*   If startup needs to be tested (i.e. before deploy_chrome can be run), a
    symbolic link will need to be created instead:
    *   ssh to device
        *   `mkdir /usr/local/chrome`
        *   `rm -R /opt/google/chrome`
        *   `ln -s /usr/local/chrome /opt/google/chrome`
     *   `deploy_chrome --build-dir=out_${SDK_BOARD}/Release --to=$IP_ADDR
         --nostrip`
     *   The device can then be rebooted and the unstripped version of Chrome
         will be run.
*   `deploy_chrome` lives under `$CHROME_DIR/src/third_party/chromite/bin`.
    You can run `deploy_chrome` outside of a `chrome-sdk` shell.

## Updating the Chrome OS image

In order to keep Chrome and Chrome OS in sync, the Chrome OS test image
should be updated weekly. See [Create a bootable USB stick] for a tip on
updating an existing test device if you have a Chrome OS checkout.

---

## Debugging

### Log files

[Chrome-related logs] are written to several locations on the device running a
test image:

*   `/var/log/ui/ui.LATEST` contains messages written to stderr by Chrome
    before its log file has been initialized.
*   `/var/log/chrome/chrome` contains messages logged by Chrome both before and
    after login since Chrome runs with `--disable-logging-redirect` on test
    images.
*   `/var/log/messages` contains messages logged by `session_manager`
    (which is responsible for starting Chrome), in addition to kernel
    messages when a Chrome process crashes.

### Command-line flags and environment variables

If you want to tweak the command line of Chrome or its environment, you have to
do this on the device itself.

Edit the `/etc/chrome_dev.conf` (device) file. Instructions on using it are in
the file itself.

### Custom build directories

This step is only necessary if you run `cros chrome-sdk` with `--nogn-gen`.

To create a GN build directory, run the following inside the chrome-sdk shell:

```
(sdk) gn gen out_$SDK_BOARD/Release --args="$GN_ARGS"
```

This will generate `out_$SDK_BOARD/Release/args.gn`.

*   You must specify `--args`, otherwise your build will not work on the device.
*   You only need to run `gn gen` once within the same `cros chrome-sdk`
    session.
*   However, if you exit the session or sync/update Chrome the `$GN_ARGS` might
    change and you need to `gn gen` again.

You can edit the args with:

```
(sdk) gn args out_$SDK_BOARD/Release
```

You can replace `Release` with `Debug` (or something else) for different
configurations. See [Debug builds].

[GN build configuration] discusses various GN build configurations. For more
info on GN, run `gn help` on the command line or read the [quick start guide].

### Debug builds

For cros chrome-sdk GN configurations, Release is the default. A debug build of
Chrome will include useful tools like DCHECK and debug logs like DVLOG. For a
Debug configuration, specify
`--args="$GN_ARGS is_debug=true is_component_build=false"`.

Alternately, you can just turn on DCHECKs for a release build. You can do this
with `--args="$GN_ARGS dcheck_always_on=true"`.

To deploy a debug build you need to add `--nostrip` to `deploy_chrome` because
otherwise it will strip symbols even from a debug build. This requires
[Deploying Chrome to the user partition].

> **Note:** If you just want crash backtraces in the logs you can deploy a
> release build with `--nostrip`. You don't need a debug build (but you still
> need to deploy to a user partition).
>
> **Note:** You may hit `DCHECKs` during startup time, or when you login, which
> eventually may reboot the device. You can check log files in `/var/log/chrome`
> or `/home/chronos/user/log`.
>
> You can create `/run/disable_chrome_restart` to prevent a restart loop and
> investigate.
>
> You can temporarily disable these `DCHECKs` to proceed, but please file a
> bug for such `DCHECK` because it's most likely a bug.

### Remote GDB

Core dumps are disabled by default. See [additional debugging tips] for how to
enable core files.

On the target machine, open up a port for the gdb server to listen on, and
attach the gdb server to the top-level Chrome process.

```
(device) sudo /sbin/iptables -A INPUT -p tcp --dport 1234 -j ACCEPT
(device) sudo gdbserver --attach :1234 $(pgrep chrome -P $(pgrep session_manager))
```

On your host machine (inside the chrome-sdk shell), run gdb and start the Python
interpreter:

```
(sdk) cd %CHROME_DIR%/src
(sdk) gdb out_${SDK_BOARD}/Release/chrome
Reading symbols from /usr/local/google2/chromium2/src/out_amd64-generic/Release/chrome...
(gdb) pi
>>>
```

> **Note:** These instructions are for targeting an x86_64 device. For now, to
> target an ARM device, you need to run the cross-compiled gdb from within a
> chroot.

Then from within the Python interpreter, run these commands:

```python
import os
sysroot = os.environ['SYSROOT']
board = os.environ['SDK_BOARD']
gdb.execute('set sysroot %s' % sysroot)
gdb.execute('set solib-absolute-prefix %s' % sysroot)
gdb.execute('set debug-file-directory %s/usr/lib/debug' % sysroot)
# "Debug" for a debug build
gdb.execute('set solib-search-path out_%s/Release/lib' % board)
gdb.execute('target remote $IP_ADDR:1234')
```

If you wish, after you connect, you can Ctrl-D out of the Python shell.

Extra debugging instructions are located at [debugging tips].

---

## Additional instructions

### Updating the version of the Chrome OS SDK

When you invoke `cros chrome-sdk`, the script fetches the version of the SDK
that corresponds to your Chrome checkout. To update the SDK, sync your Chrome
checkout and re-run `cros chrome-sdk`.

**IMPORTANT NOTES:**

*   Every time that you update Chrome or the Chrome OS SDK, it is possible
    that Chrome may start depending on new features from a new Chrome OS
    image. This can cause unexpected problems, so it is important to update
    your image regularly. Instructions for updating your Chrome OS image are
    above in [Set up the Chrome OS device]. This is not a concern for a
    downloaded VM.
*   Don't forget to re-configure your custom build directories if you have them
    (see [Custom build directories]).

### Specifying the version of the Chrome OS SDK to use

You can specify a version of Chrome OS to build against. This is handy for
tracking down when a particular bug was introduced.

```
(shell) cros chrome-sdk --board=$BOARD --version=11005.0.0
```

Once you are finished testing the old version of the chrome-sdk, you can
always start a new shell with the latest version again. Here's an example:

```
(shell) cros chrome-sdk --board=$BOARD --clear-sdk-cache
```

### Updating Chrome

```
(sdk) exit
(shell) git checkout master && git pull   # (or if you prefer, git rebase-update)
(shell) gclient sync
(shell) cros chrome-sdk --board=$BOARD --log-level=info
```

> **Tip:** If you update Chrome inside the chrome-sdk, you may then be using an
> SDK that is out of date with the current Chrome.
> See [Updating the version of the Chrome OS SDK] section above.


### Updating Deployed Files

`deploy_chrome` determines which files to copy in `chrome_util.py` in the
[chromite repo] which is pulled into `chrome/src/third_party/chromite` via DEPS.

When updating the list:

1.  Make changes to the appropriate list (e.g. `_COPY_PATHS_CHROME`).
1.  Be aware that deploy_chrome is used by the chromeos-chrome ebuild, so when
    adding new files make sure to set optional=True initially.
1.  Changes to chromite will not affect Simple Chrome until a chromite roll
    occurs.

### Using a custom Chrome OS build

If you are making changes to Chrome OS and have a Chrome OS build inside a
chroot that you want to build against, run `cros chrome-sdk` with the `--chroot`
option:

```
(shell) cros chrome-sdk --board=$BOARD --chroot=/path/to/chromiumos/chroot
```

### Using cros flash with xbuddy to download images

`cros flash` with `xbuddy` will automatically download an image and write it to
USB for you. It's very convenient, but for now it requires a full Chrome OS
checkout and must be run inside the Chrome OS chroot. ([issue 437877])

```
(chroot) cros flash usb:// xbuddy://remote/$BOARD/<version>
(chroot) cros flash $IP_ADDR xbuddy://remote/$BOARD/<version>
```

Replace `$BOARD`, `$IP_ADDR`, `<version>` with the right values. The board and
version can be seen in your SDK prompt (e.g. `(sdk kevin R80-12734.0.0)` is the
kevin board using version R80-12734.0.0).

See the [Cros Flash page] for more details.

### Running tests

Chrome's unit and browser tests are compiled into test binaries. At the moment,
not all of them run on a Chrome OS device. Most of the unit tests and part of
interactive_ui_tests that measure Chrome OS performance should work.

To build and run a chrome test on device (or VM),
```bash
(sdk) .../chrome/src $ cros_run_test --build --device=$IP --chrome-test -- \
out_$SDK_BOARD/Release/interactive_ui_tests \
    --dbus-stub \
    --enable-pixel-output-in-tests \
    --gtest_filter=SplitViewTest.SplitViewResize
```

Alternatively, manually build and use the generated `run_$TEST` scripts to run
like build bots:
```bash
(sdk) .../chrome/src $ autoninja -C out_$SDK_BOARD/Release interactive_ui_tests
(sdk) .../chrome/src $ out_$SDK_BOARD/Release/bin/run_interactive_ui_tests \
    --device=$IP \
    --dbus-stub \
    --enable-pixel-output-in-tests \
    --gtest_filter=SplitViewTest.SplitViewResize
```

To run tests locally on dev box, follow the [instructions for running tests on
Linux] using a separate GN build directory with `target_os = "chromeos"` in its
arguments. (You can create one using the `gn args` command.)

If you're running tests which create windows on-screen, you might find the
instructions for using an embedded X server in [web_tests_linux.md] useful.

### Setting a custom prompt

By default, cros chrome-sdk prepends something like '`(sdk link R52-8315.0.0)`'
to the prompt (with the version of the prebuilt system being used).

If you prefer to colorize the prompt, you can set `PS1` in
`~/.chromite/chrome_sdk.bashrc`, e.g. to prepend a yellow
'`(sdk link 8315.0.0)`' to the prompt:

```
PS1='\[\033[01;33m\](sdk ${SDK_BOARD} ${SDK_VERSION})\[\033[00m\] \w \[\033[01;36m\]$(__git_ps1 "(%s)")\[\033[00m\] \$ '
```
NOTE: Currently the release version (e.g. 52) is not available as an
environment variable.

### GYP

The legacy `GYP` build system is no longer supported.

[Custom build directories]: #custom-build-directories
[Updating the version of the Chrome OS SDK]: #updating-the-version-of-the-chrome-os-sdk
[Using a custom Chrome OS build]: #using-a-custom-chrome-os-build
[Command-line flags and environment variables]: #command-line-flags-and-environment-variables
[Deploying Chrome to the user partition]: #deploying-chrome-to-the-user-partition
[Debug builds]: #debug-builds
[Create a bootable USB stick]: #create-a-bootable-usb-stick
[Set up the Chrome OS device]: #set-up-the-chrome-os-device
[OS development guide]: https://chromium.googlesource.com/chromiumos/docs/+/master/developer_guide.md
[Chrome source code and depot_tools]: https://chromium.googlesource.com/chromium/src/+/master/docs/linux_build_instructions.md
[instructions for running tests on Linux]: https://chromium.googlesource.com/chromium/src/+/master/docs/linux_build_instructions.md#Running-test-targets
[update .gclient]: https://chromium.googlesource.com/chromium/src/+/HEAD/docs/chromeos_build_instructions.md#updating-your-gclient-config
[Chrome OS board name]: https://www.chromium.org/chromium-os/developer-information-for-chrome-os-devices
[GN build configuration]: https://www.chromium.org/developers/gn-build-configuration
[quick start guide]: https://gn.googlesource.com/gn/+/master/docs/quick_start.md
[device-specific instructions]: https://www.chromium.org/chromium-os/developer-information-for-chrome-os-devices
[generic instructions]: https://www.chromium.org/a/chromium.org/dev/chromium-os/developer-information-for-chrome-os-devices/generic
[rootfs has been removed]: developer_mode.md#TOC-Making-changes-to-the-filesystem
[remounted as read-write]: https://www.chromium.org/chromium-os/how-tos-and-troubleshooting/debugging-tips#TOC-Setting-up-the-device
[additional debugging tips]: https://www.chromium.org/chromium-os/how-tos-and-troubleshooting/debugging-tips#TOC-Enabling-core-dumps
[chromite repo]: https://chromium.googlesource.com/chromiumos/chromite/
[issue 437877]: https://bugs.chromium.org/p/chromium/issues/detail?id=403086
[Cros Flash page]: https://chromium.googlesource.com/chromiumos/docs/+/master/cros_flash.md
[VM]: https://chromium.googlesource.com/chromiumos/docs/+/master/cros_vm.md
[Running a Chrome Google Test binary in the VM]: https://chromium.googlesource.com/chromiumos/docs/+/master/cros_vm.md#Run-a-Chrome-GTest-binary-in-the-VM
[go/goldeneye]: https://cros-goldeneye.corp.google.com/chromeos/console/listBuild
[go/shortleash]: https://goto.google.com/shortleash
[debugging tips]: https://www.chromium.org/chromium-os/how-tos-and-troubleshooting/debugging-tips
[go/chrome-build-instructions]: https://companydoc.corp.google.com/company/teams/chrome/chrome_build_instructions.md
[api-keys]: https://www.chromium.org/developers/how-tos/api-keys
[install-build-deps-android.sh]: https://chromium.googlesource.com/chromium/src/+/master/build/install-build-deps-android.sh
[Goma]: https://chromium.googlesource.com/infra/goma/client/
[Chrome-related logs]: https://chromium.googlesource.com/chromium/src/+/lkgr/docs/chrome_os_logging.md
[crbug.com/360342]: https://bugs.chromium.org/p/chromium/issues/detail?id=360342
[crbug.com/403086]: https://bugs.chromium.org/p/chromium/issues/detail?id=403086
[web_tests_linux.md]: https://chromium.googlesource.com/chromium/src/+show/master/docs/web_tests_linux.md
