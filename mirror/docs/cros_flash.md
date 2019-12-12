# Cros Flash

## Overview

`cros flash` is a script to update a Chromium OS device with an image, or to
copy image onto a removable device (e.g. a USB drive). `cros flash` utilizes
the [devserver] to download images and/or generate payloads.

When updating a Chromium OS device, `cros flash` relies on an SSH connection
to talk to the device (which is enabled in test images). `cros flash` assumes
that the device is NOT capable of initiating an SSH connection to your
workstation, allowing it to be used in a more restricted/secured network
environment.

[TOC]

## Requirements

### Updating a Chromium device

1.  A Chromium OS device with a test image.
2.  SSH test keys so that the script can SSH into the test device without a
    password. See [Setting up SSH Access] to your test device.
3.  Chroot: `cros flash` downloads artifacts and generates payloads.
4.  Full Chromium OS checkout.

If your device is currently running a non-test image, you will need to use a
USB stick to image the device first (see [developer guide]).

There are plans to eliminate requirements 3 and 4, and the test image
requirement so that `cros flash` may be integrated into the [Simple Chrome]
workflow (bug [980627](http://crbug.com/980627)).

### Download images/payloads from Google Storage

1.  Chroot: `cros flash` xBuddy/[devserver] to download the files.
    Devserver currently only runs in the chroot.
2.  Credentials to download from Google Storage. External developers can only
    download images for publicly available boards such as amd64-generic and
    kevin.

## Example Usage

```bash
cros flash <device> <image>
```

*   `<device>`: Required. `ssh://IP[:port]` of your ChromiumOS device,
    `usb://path/to/removable/device`, or `file://path/to/a/file`
*   `<image>`: Optional.  Can be a path to an image, an xBuddy path, a payload
    directory, or simply `latest` for latest locally-built image. Defaults to
    `latest`.

For example, to update the device with the latest locally-built image, you can
use the shortcut `latest`:
```bash
cros flash ssh://${DUT_IP} latest
```

or simply:
```bash
cros flash ssh://${DUT_IP}
```

To use a locally-built test image:
```bash
cros flash ssh://${DUT_IP} xBuddy://local/amd64-generic/R78-12450.0.0
```

To specify a local image by path:
```bash
cros flash ssh://${DUT_IP} path/to/image
```

To download the latest canary image:
```bash
cros flash ssh://${DUT_IP} xBuddy://remote/amd64-generic/latest-canary
```
> Note: external developers will not be able to download non-public remote
> images.
> If you are prompted to confirm due to board mismatch, simply type 'yes' to
> proceed.

You can replace `ssh://${DUT_IP}` in the above examples with
`usb://device/path` or `usb://` to copy the image onto a removable device.
However, you have to specify the board to use.
```bash
cros flash usb:// ${BOARD}/latest

cros flash usb:///dev/sdc path/to/image
```

Finally, if you just want to look at the image you are installing (using
`mount_gpt_image.sh`) or save the file for later, you can use `file://` to save
it to a file of your choice e.g.
```bash
cros flash file://path/to/save/image.bin path/to/image
```

## Device

### Chromium OS Device

Device can be `ssh://hostname[:port]` or `hostname[:port]`. Port number is the
SSH port to use to connect to your device (defaults to `22`).

> Note: If you use `cros flash` to install a non-test image, `cros flash` will
> not be able to confirm that the device has rebooted successfully after the
> update. Also, you will not be able to use `cros flash` to reimage again
> because `cros flash` relies on being able to ssh into the device. You will
> need to use a USB stick to image your device.

### Removable Device

Device can be `usb://path/to/removable/device` or `usb://`. If a device path is
specified, `cros flash` will check if the device is indeed removable. If no path
is given, the user will be prompted to choose from a list of removable devices.
Note that auto-mounting of USB devices should be turned off as it may corrupt
the disk image while it's being written.

## xBuddy paths

Please see the [xBuddy documentation] for more information on the format of
xBuddy paths.

## Pre-generated payloads

`cros flash` your pre-generated update payloads directly if you pass a
payload directory as `<image>`:
```bash
cros flash ${DUT_IP} path_to_payload_directory
```

`cros flash` looks for `update.gz` and/or `stateful.tgz` in the payload
directory and uses them to update the device.

## Testing OS updates without reboot

`cros flash` can be used to test Chromium OS update process without rebooting
using option `--no-reboot`. This is useful when testing the update UI
repeatedly.

```bash
cros flash --no-reboot ssh://${DUT_IP} path/to/image
```

## Known problems and fixes

### Where is Cros Flash?

`cros flash` is in the chromite repo. The script is
`chromite/cli/cros/cros_flash.py`. The source is [available here].

### Failures related to update engine

Make sure that update-engine service on device is running. If not:

```bash
# On the device
start update-engine
```

[available here]: https://chromium.googlesource.com/chromiumos/chromite/+/refs/heads/master/cli/cros/cros_flash.py
[devserver]: https://chromium.googlesource.com/chromiumos/chromite/+/refs/heads/master/docs/devserver.md
[Setting up SSH Access]: https://www.chromium.org/chromium-os/testing/autotest-developer-faq/ssh-test-keys-setup
[Simple Chrome]: /simple_chrome_workflow.md
[developer guide]: /developer_guide.md
[xBuddy documentation]: /xbuddy.md
[cros deploy]: https://sites.google.com/a/chromium.org/dev/chromium-os/build/cros-deploy
