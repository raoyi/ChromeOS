# Developer Mode

Production Chrome OS devices that are shipped from the factory are locked down
and will not let you make changes to the software. This page describes how to
enable developer mode and get root access to your system.

[TOC]

## Enable Developer Mode {#dev-mode}

Modern Chrome OS devices can be put into developer mode by pressing
[specific keys][debug buttons] while Chrome OS is booting:

*   [Developer mode for devices with a keyboard][keyboard developer mode]
*   [Developer mode for devices without a keyboard (tablets)][keyboardless developer mode]

**Caution: Modifications you make to the system are not supported by Google, may
cause hardware, software or security issues and may void warranty.**

NOTE: Putting your device into developer mode inherently makes it a little less
secure. Specifically, it makes the "verified boot" that's built-in to your
hardware a little bit more lax, allowing your hardware to run custom
(non-Google-signed) images. It also gives you access to a "root" shell.

You can tell that you're in Developer Mode if you see one of these screens when
you turn the device on:

![developer mode 1] ![developer mode 2] ![developer mode 3]

## Switch to Normal Mode {#normal-mode}

To restore your device to Normal Mode (i.e., disable Developer Mode), reboot
your device and perform the following action:

*   Device with keyboard: Press the `Spacebar` at the firmware screen.
*   Devices without keyboard (tablet): Use the `Volume-Up` and `Volume-Down`
    keys to select the `Enable OS Verification` option. Press the `Power` button
    to confirm.

NOTE: If you've made changes to the rootfs filesystem while in developer mode,
you may have to use the [recovery process] to restore your device to its factory
condition. However, as long as you don't crack open the case, you shouldn't be
able to do anything that can't be undone by recovery (software).

## Getting to a Command Prompt {#shell}

If you're a Linux hacker, you probably know that Google Chrome OS is built on
top of Linux and you're wondering how you can jailbreak your device so you can
get to a command prompt. It turns out: there's no need. The command prompt is
built in to your device!

NOTE: Before following these instructions, remember to put your device into
[Developer Mode](#dev-mode).

### Get the Command Prompt Through VT-2 {#vt2}

One way to get the login prompt is through something called `VT-2`, or "virtual
terminal 2". If you're a Linux user, this is probably familiar. You can get to
`VT-2` by pressing:

```
[ Ctrl ] [ Alt ] [ → ]
```

where the `[ → ]` key is the right-arrow key just above the number `3` on your
keyboard.

Once you have the login prompt, you should see a set of instructions telling you
about command-line access. By default, you can login as the `chronos` user with
no password. This includes the ability to do password-less `sudo`. The
instructions on the screen will tell you how you can set a password. They also
tell you how to disable screen dimming.

In order to get back to the browser press:

```
[ Ctrl ] [ Alt ] [ ← ]
```

where the `[ ← ]` key is the left-arrow key just above the number `1` on your
keyboard.

NOTE: The top-rows of the keyboard on a Chrome OS device are actually treated by
Linux as the keys `F1` through `F10`. Thus, the `[ → ]` key is actually `F2`
and the `[ ← ]` key is actually `F1`.

NOTE: Kernel messages show up on `VT-8`.

### Getting the Command Prompt Through "crosh" {#crosh}

An alternate way to get to a terminal prompt is to use [`crosh`]:

1.  Go through the standard Chrome OS login screen (you'll need to setup a
    network, etc) and get to the web browser. It's OK if you login as guest.
1.  Press `[ Ctrl ] [ Alt ] [ T ]` to get the [`crosh`] shell.
1.  Use the shell command to get the shell prompt. NOTE: even if you set a
    password for the chronos user, you won't need it here (though you still need
    it for sudo access)

NOTE: Entering the shell this way doesn't give you all the instructions that
[`VT-2`] does (like how to set your password). You might want to follow the
[`VT-2`] steps once just to get the instructions.

If you want to get back to the browser without killing the shell, you can use `[
Alt ] [ Tab ]`.

NOTE: You can create as many shells as you want with `[ Ctrl ] [ Alt ] [ T ]`
again and another shell will be opened. You can `[ Alt ] [ Tab ]` between them.

## Making Changes to the Filesystem {#disable-verity}

The Chromium OS rootfs is mounted read-only. In developer mode you can disable
the rootfs verification, enabling it to be modified.

**NOTE: If you mount the root filesystem in writeable mode, even if you make no
changes, it will no longer be verifiable and you'll have to use a recovery image
to restore your system when you switch back to normal mode. Auto updates may
also fail until a full payload is downloaded.**

To make your rootfs writable, run the following command from a shell on the
device:

```bash
(dut) $ sudo /usr/share/vboot/bin/make_dev_ssd.sh --remove_rootfs_verification
```

Then reboot. Your rootfs will be mounted read/write.

## Specifying Command Line Flags for Chrome {#chrome-cmdline-flags}

*   [Enable developer mode.](#dev-mode)
*   [Disable rootfs verification.](#disable-verity)
*   [Access a shell.](#shell)
*   Modify `/etc/chrome_dev.conf` (read the comments in the file for more
    details).
*   Restart the UI with:

    ```bash
    (dut) $ sudo restart ui
    ```

## Booting into alternative firmware {#alt-firmware}

Starting in 2019 some Chromebooks support selecting different firmware at the
developer screen. Press a number to choose the firmware.

Available options are:

1.  U-Boot
1.  TianoCore (x86 only)
1.  SeaBIOS (x86 only)
1.  Memtest86plus (x86 only)

This firmware is stored in the RW_LEGACY section of the SPI flash, which is a
read-write section; you can update it if you like. See the `chromeos-bootimage`
ebuild for the `altfw` feature and how this CBFS region is populated.

<!-- Links -->

[`VT-2`]: #vt2
[crosh]: https://chromium.googlesource.com/chromiumos/platform2/+/master/crosh
[debug buttons]: https://chromium.googlesource.com/chromiumos/docs/+/master/debug_buttons.md
[keyboard developer mode]: https://chromium.googlesource.com/chromiumos/docs/+/master/debug_buttons.md#firmware-keyboard-interface
[keyboardless developer mode]: https://chromium.googlesource.com/chromiumos/docs/+/master/debug_buttons.md#firmware-menu-interface
[recovery process]: https://www.google.com/chromeos/recovery

<!-- Images -->

[developer mode 1]: ./images/developer_mode1.jpg
[developer mode 2]: ./images/developer_mode2.jpg
[developer mode 3]: ./images/developer_mode3.jpg
