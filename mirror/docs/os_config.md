# Chromium OS Configuration

Often times browser and OS programs need to change their behavior at runtime
based on how the OS has been configured.
Further, many of pieces of code often ask the same question (e.g. "Is dev mode
enabled?"), and the way to answer the question might not be clear, or it might
be possible to find the answer through different means.
Here we'll document those various configuration sources and which ones you
should (or should not) be using.

Remember that many of these settings are not finalized at build time, and the
same binary might be used in many different configurations.
For example, we do not compile programs for a specific channel (i.e. the same
binary image is used on stable, beta, dev, and canary), nor do we compile for
a specific runtime mode (i.e. programs need to detect dev-mode vs normal-mode).

[TOC]

## /etc/lsb-release {#LSB}

This file provides a number of fields for the browser, daemons, and users.
However, many of these fields are meant purely for users/debugging, and they
should not be parsed out directly.

Here are all the known fields and whether people may rely on their value.
If it is not marked as *Usable*, then you *must not* parse it out for anything
other than informational display to users.
If a field is not documented here, you must assume it's the same as Usable=No,
in which case you *must not* parse it.

If you want to add more fields, they should go in [os-release] instead.

| Usable | Field                               | Meaning | Example Values |
|:------:|-------------------------------------|---------|----------------|
|   No   | `CHROMEOS_RELEASE_APPID`            | The release Omaha appid | `{DC2BBB48-BC2C-493E-82DA-89BEE8321A5A}` |
|   No   | `CHROMEOS_BOARD_APPID`              | This boards Omaha appid | `{DC2BBB48-BC2C-493E-82DA-89BEE8321A5A}` |
|   No   | `CHROMEOS_CANARY_APPID`             | The canary channel Omaha appid | `{90F229CE-83E2-4FAF-8479-E368A34938B1}` |
|  Yes   | `CHROMEOS_ARC_VERSION`              | The ARC++ version in the system | `4979549` |
|  Yes   | `CHROMEOS_ARC_ANDROID_SDK_VERSION`  | The Android SDK version supported by ARC++ | `25` |
|   No   | `CHROMEOS_RELEASE_BOARD`            | Human readable board name (and keyset used for signing) | `betty` `eve-signed-mpkeys` |
|  Yes   | `CHROMEOS_RELEASE_BUILD_NUMBER`     | Major OS version number | `11012` |
|  Yes   | `CHROMEOS_RELEASE_BRANCH_NUMBER`    | Minor OS version number used by branches | `0` |
|  Yes   | `CHROMEOS_RELEASE_CHROME_MILESTONE` | Chrome major version/release number | `70` |
|  Yes   | `CHROMEOS_RELEASE_PATCH_NUMBER`     | Patch OS version number (datestamps for developer builds) | `0` `2018_08_28_1422` |
|  Yes   | `CHROMEOS_RELEASE_TRACK`            | OS release channel | `stable-channel` `testimage-channel` |
|   No   | `CHROMEOS_RELEASE_DESCRIPTION`      | Human readable description for this build | `11012.0.2018_08_28_1422 (Test Build - vapier) developer-build betty` |
|   No   | `CHROMEOS_RELEASE_BUILD_TYPE`       | Human readable build type | `Official Build` `Test Build - vapier` |
|   No   | `CHROMEOS_RELEASE_NAME`             | Human readable OS Product name | `Chrome OS` `Chromium OS` |
|  Yes   | `CHROMEOS_RELEASE_UNIBUILD`         | Set to 1 for unified builds. | `1` |
|  Yes   | `CHROMEOS_RELEASE_VERSION`          | The full OS version number | `11012.0.2018_08_28_1422` |
|  Yes   | `GOOGLE_RELEASE`                    | The full OS version number | `11012.0.2018_08_28_1422` |
|  Yes   | `CHROMEOS_AUSERVER`                 | URI used to get OS updates | `https://tools.google.com/service/update2` `http://vapier.cam.corp.google.com:8080/update` |
|  Yes   | `CHROMEOS_DEVSERVER`                | URI to access the dev_server | `http://vapier.cam.corp.google.com:8080` |
|  Yes   | `DEVICETYPE`                        | General device type | `CHROMEBIT` `CHROMEBASE` `CHROMEBOOK` `CHROMEBOX` `REFERENCE` `OTHER` |

### Examples

See the [lsb-release](./lsb-release.md) document for more details.

## /etc/os-release {#os-release}

This file provides a number of fields for the browser, daemons, and users.
However, many of these fields are meant purely for users/debugging, and they
should not be parsed out directly.

More details on this file can be found in the [os-release man page].
It's a standard file among Linux distros and we aim to follow the spec.

Here are all the known fields and whether people may rely on their value.
If it is not marked as *Usable*, then you *must not* parse it out for anything
other than informational display to users.
If a field is not documented here, you must assume it's the same as Usable=No,
in which case you *must not* parse it.

| Usable | Field             | Meaning | Example Value |
|:------:|-------------------|---------|---------------|
|  Yes   | `BUG_REPORT_URL`  | Site where to report bugs | `https://crbug.com/new` |
|  Yes   | `BUILD_ID`        | Full OS version | `11012.0.2018_08_28_1422` |
|  Yes   | `GOOGLE_CRASH_ID` | ID used when reporting crashes ([crash-reporter]) | `ChromeOS` |
|  Yes   | `HOME_URL`        | Site where people can find info about this project | `https://www.chromium.org/chromium-os` |
|  Yes   | `ID`              | Unique ID for the OS | `chromeos` |
|  Yes   | `ID_LIKE`         | Unique IDs that the OS is related to | `chromiumos` |
|  Yes   | `NAME`            | For name for the OS | `Chrome OS` |
|  Yes   | `VERSION`         | Major release version | `70` |
|  Yes   | `VERSION_ID`      | Full release version | `70` |

[crash-reporter]: https://chromium.googlesource.com/chromiumos/platform2/+/master/crash-reporter/
[os-release man page]: https://www.freedesktop.org/software/systemd/man/os-release.html

### /etc/os-release.d/

Overrides and fragments can be dropped in here.
These have higher precedence than the `/etc/os-release` file.
The format is simple: the filename is the key and the content is the value.

For example, if there is an `/etc/os-release.d/NAME` file, then it will be used
instead of the `NAME=...` line in the `/etc/os-release` file.

### Examples

If you want to access fields in this file, please do not parse it yourself.

#### Compiled Code

In platform code, Chromium OS provides a generic `brillo::OsReleaseReader` in
[brillo/osrelease_reader.h] that can process this file.
This handles both `/etc/os-release` and `/etc/os-release.d/` automatically.

```cpp
...
#include <brillo/osrelease_reader.h>
...
  brillo::OsReleaseReader reader;
  reader.Load();

  std::string value;
  if (!reader.GetString(kSomeKey, &value)) {
    // kSomeKey isn't defined.
    return false;
  }

  // Do something with |value| now.
...
```

[brillo/osrelease_reader.h]: https://chromium.googlesource.com/chromiumos/platform2/+/master/libbrillo/brillo/osrelease_reader.h

#### Shell Code

If you're writing shell code, you shouldn't be accessing this file.
[Please rewrite your code in a better language][rewrite-shell].

## crossystem

This [vboot_reference] `crossystem` program is used to query NVRAM and other
low level system/firmware functionality.

While there are many fields, here are the only ones developers should rely upon
in normal use.
There are a few more, but only for specific usage, which we'll cover next.

All other fields not covered here should be avoided.
Low level firmware projects (like [firmware updater] or [vboot_reference]) are
a bit of an exception as they're tightly integrated.

[firmware updater]: https://chromium.googlesource.com/chromiumos/platform/firmware
[vboot_reference]: https://chromium.googlesource.com/chromiumos/platform/vboot_reference

### Common Fields

| Field                   | R/W | Description |
|-------------------------|:---:|--------------|
| block_devmode           | R/W | Block all use of developer mode |
| clear_tpm_owner_request | R/W | Clear TPM owner on next boot |
| cros_debug              | RO  | OS should allow debug features |
| debug_build             | RO  | OS image built for debug features |
| dev_boot_legacy         | R/W | Enable developer mode boot Legacy OSes |
| dev_boot_signed_only    | R/W | Enable developer mode boot only from official kernels |
| dev_boot_usb            | R/W | Enable developer mode boot from USB/SD |
| devsw_boot              | RO  | Developer switch position at boot |
| devsw_cur               | RO  | Developer switch current position |
| disable_dev_request     | R/W | Disable virtual dev-mode on next boot |
| fwid                    | RO  | Active firmware ID |
| inside_vm               | RO  | Running in a VM? |
| mainfw_act              | RO  | Active main firmware |
| mainfw_type             | RO  | Active main firmware type |
| nvram_cleared           | RO  | Have NV settings been lost? |
| recovery_reason         | RO  | Recovery mode reason for current boot |
| recovery_request        | R/W | Recovery mode request |
| recoverysw_boot         | RO  | Recovery switch position at boot |
| recoverysw_cur          | RO  | Recovery switch current position |
| ro_fwid                 | RO  | Read-only firmware ID |
| wpsw_boot               | RO  | Firmware write protect hardware switch position at boot |
| wpsw_cur                | RO  | Firmware write protect hardware switch current position |

### Specific-Use Fields

These fields may be used, but generally they're used only in highly specific
code and projects.

| Field                   | R/W | Description |
|-------------------------|:---:|-------------|
| dev_enable_udc          | RO  | Enable USB Device Controller |
| fw_vboot2               | RO  | If firmware was selected by vboot2 |
| kernel_max_rollforward  | R/W | Max kernel version to store into TPM |
| recoverysw_is_virtual   | RO  | Recovery switch is virtual |
| tpm_attack              | R/W | TPM was interrupted since this flag was cleared |
| tpm_fwver               | RO  | Firmware version stored in TPM |
| tpm_kernver             | RO  | Kernel version stored in TPM |
| vdat_flags              | RO  | Raw bit flags from VbSharedData |
| wipeout_request         | R/W | Firmware requested factory reset (wipeout) |

### Banned Fields

There are some fields that specifically should not be used.
We'll document their alternatives.

* `arch` (RO): Shell code could use `uname -a` to get the kernel architecture.
  Userland code generally shouldn't be changing behavior based on the arch.
* `hwid` (RO): See the [board/device detection FAQ](#detect-device).

### Examples

Keep in mind that all fields are not guaranteed to always have a valid value.
That means your queries should be constructed to "fail closed".
In the case of `cros_debug`, you want to always check if dev-mode is enabled
by using `if crossystem 'cros_debug?1'; then` and never check if dev-mode is
disabled by using `if ! crossystem 'cros_debug?0'; then`.
If the system were broken or failing and `cros_debug` was not set up properly,
then `cros_debug` might not be `1` or `0`, so the latter code will wrongly
"succeed"!

#### Compiled Code

The [crossystem.h] header provides a few `VbGet` helpers in the `vboot_host`
library.
Be sure to use pkg-config to locate the `vboot_host` library instead of using
`-lvboot_host` directly.

```c
#include <crossystem.h>
...
  int value = VbGetSystemPropertyInt("cros_debug");
  if (value < 0) {
    // Unable to read the value.
    return false;
  }

  if (value == 1) {
    // Dev mode is enabled.
    return true;
  } else {
    // Not dev mode.
    return false;
  }
```

[crossystem.h]: https://chromium.googlesource.com/chromiumos/platform/vboot_reference/+/master/host/include/crossystem.h

#### Shell Code

The `crossystem` command provides a simple interface for testing values.

```
  crossystem [param1 [param2 [...]]]
    Prints the current value(s) of the parameter(s).
  crossystem [param1=value1] [param2=value2 [...]]]
    Sets the parameter(s) to the specified value(s).
  crossystem [param1?value1] [param2?value2 [...]]]
    Checks if the parameter(s) all contain the specified value(s).
```

So you can write shell code like:

```sh
if crossystem 'cros_debug?1'; then
  # The cros_debug field is equal to 1.
  ...
else
  # The cros_debug field is not equal to 1 (including not set).
  ...
fi
```

## vpd

The [vpd] tool provides access to Vital Product Data.
Its homepage provides all the details on tools and fields.

Briefly, you'll want to use `vpd_get_value <field>` in tools.

## chromeos-config

The [chromeos-config project] (for unibuild configurations) takes care of
storing and accessing device-specific details.
Its homepage provides all the details on tools and fields.

Briefly, you'll want to use the `cros_config` program and `libcros_config`
library in tools.
Be sure to use pkg-config to locate the `cros_config` library instead of using
`-lcros_config` directly.

## USE Flags

Gentoo USE flags may be used at build time to control high level features.
This is useful for a build that wants to enable/disable large functionality
like touchscreen support, stylus support, or ARC++ availability.

This will usually take the shape of the ebuild listing the flag in IUSE and
then passing that down to the build environment.

These flags can be passed to the runtime as well via [libchromeos-use-flags].
This is explained in more detail in the [login_manager documentation].

USE flags must not be used to set board names (e.g. `kevin` or `link`).
See the [board/device behavior FAQ](#device-behavior) for alternatives.

[libchromeos-use-flags]: https://chromium.googlesource.com/chromiumos/overlays/chromiumos-overlay/+/master/chromeos-base/libchromeos-use-flags/

### cros-board.eclass

No package should be using the [cros-board.eclass] anymore.
This was used in the past to allow packages to vary behavior at build time based
on the board, but we no longer want to let packages do that.

You might still find some packages in the tree using them, but it's because we
haven't yet migrated them off.
https://crbug.com/407731 is tracking that work.

[cros-board.eclass]: https://chromium.googlesource.com/chromiumos/overlays/chromiumos-overlay/+/master/eclass/cros-board.eclass

## FAQ

### How do I query dev mode status?

Use `cros_debug?1` from [crossystem].
Never use `cros_debug?0`.

This tells you whether to enable dev-mode-specific features (like shell access).
In general, programs should not change their behavior depending on whether the
system is in dev-mode or normal-mode.
This makes testing much harder as we do not run any tests in normal-mode.

Do not confuse dev-mode with "rootfs verification enabled" or "verified mode".
It is possible to have rootfs verification enabled while in dev-mode.

Do not confuse dev-mode with the keyset used to sign or verify the system.
This has no relationship to devkeys, premp keys, or mp keys.

Do not confuse dev-mode with the dev channel release track.
They have no relationship at all.

### How do I find the current channel?

Use `CHROMEOS_RELEASE_TRACK` from [lsb-release].

This will have values like `stable-channel`, `beta-channel`, `dev-channel`,
`canary-channel`, and `testimage-channel`.
Take note that test images use a `testimage` prefix and not `test`.

It is not possible (by design) to build code for a specific channel.
Our release process takes an OS image and publishes it in the canary channel.
Promoting it to dev/beta/stable only involves modifying the [lsb-release] file.
The code is never recompiled.

However, most code should never change its behavior based on the active channel.
If you have a feature you want to keep testing in e.g. canary channel before
releasing it in a newer version, then you should look into [Finch] instead.
Among other things, it provides a kill switch in case something goes wrong.

### How do I change behavior based on board/device? {#device-behavior}

If the board is already unibuild-enabled, then you should always use that to
change runtime behavior.
See the [chromeos-config section] for more details.
If the project you're working on does not yet support unibuild, then you will
need to update it to support unibuild.
If the setting you want to vary isn't in the unibuild schema yet, then you will
need to update it to include/document this new setting.
The difficulty of extending existing projects is not an excuse to use deprecated
methods for changing settings (i.e. the next paragraphs).

If you're working on an older board that isn't unibuild-enabled, then you have a
few options:

* If a USE flag is already available, [key off of that](#use-flags).
* Update the board's bsp ebuild to install custom init scripts or config files.
* [Query the board name](#detect-device).

### How do I find the current board/device? {#detect-device}

Please see the previous question about changing behavior based on board/device.
If you follow those guidelines, you usually shouldn't need the exact board/device
name in the first place.

Use `cros_config / name` to get the device name.

Put simply, a single board (e.g. coral) can be used across multiple devices
(e.g. astronaut, nasher, robo, etc...).
The device name is used to disambiguate at runtime in a single board image.

Do not use `crossystem hwid` or `CHROMEOS_RELEASE_BOARD` in `/etc/lsb-release`.
These do not handle unibuild where a single board supports multiple devices.

### How do I pass different flags to Chrome (the browser)?

See the [login_manager documentation] for more details.

### How do I find out the keyset used to sign the image (PreMP/MP/etc...)?

In short, you don't.
Code must not change its behavior based on whether the running image has been
signed with "premp" or "mp" keys.
Trying to do this significantly & negatively impacts both automated testing and
early dogfood testing with users.

Use some other knob to control behavior (such as [Finch]).

[chromeos-config section]: #chromeos_config
[chromeos-config project]: https://chromium.googlesource.com/chromiumos/platform2/+/master/chromeos-config
[crossystem]: https://chromium.googlesource.com/chromiumos/platform/vboot_reference/+/master/utility/crossystem.c
[Finch]: http://go/finch-guide
[login_manager documentation]: https://chromium.googlesource.com/chromiumos/platform2/+/master/login_manager/docs/flags.md
[lsb-release]: #LSB
[os-release]: #os-release
[rewrite-shell]: ./development_basics.md#shell
[vpd]: https://chromium.googlesource.com/chromiumos/platform/vpd
