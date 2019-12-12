# Reporting Chrome OS bugs

[TOC]

## Chromebook Central Help Forum

The [Chromebook Central Help Forum] is an active, searchable community for user
discussion of bugs and feature requests. It's a great place to ask for help, and
there's a good chance that your question has already been asked (and answered,
hopefully).

## Feedback reports {#feedback}

Feedback reports are the primary mechanism by which Chrome OS users can send
feedback about the project. Reports are clustered into categories that are used
to identify larger issues, but they are typically not individually reviewed.
Submitted reports are not publicly accessible.

To submit a feedback report, type Alt+Shift+i or click `Report an issue...`
within the `Help` submenu while logged in. Feedback reports include selected
system logs if the `Send system and app information, and metrics` checkbox is
checked. You can click the links within the checkbox text to see the information
that will be attached to the report. See the [official feedback documentation]
for more information.

## Public issue tracker {#public}

The Chromium project's [public issue tracker] is used by developers to track
Chrome OS bugs and feature requests. New issues submitted here are periodically
triaged to receive component labels, at which point they should be examined by
component owners. If you're a Chromium project member, you can assign components
and other labels yourself to expedite this process.

[new.crbug.com] or [crbug.com/new] are interchangeable handy shortcuts that can
be used to start a new issue in the public tracker.

Issues are publicly-viewable by default, but the `Restrict-View-Google` label
restricts the issue to Google employees. [go/newcrosbug] (internal link) may be
used to start a new issue with this label.

## Security bugs {#security}

If you want to report a security bug, please follow [Reporting Security Bugs].

That covers how to securely and privately report issues to the right group.
Please do *not* use the default [crbug.com/new] system as that creates public
bugs which anyone can view.

Note that while the Chrome browser does not consider physically-local attacks to
be inside its threat model, Chrome OS does include certain physically-local
attacks in its threat model. The reason for this difference is that while the
Chrome browser does not control the operating system it runs on, on Chrome OS we
are responsible for the entire system. This means that Chrome OS does need to
protect against certain physically-local attackers, such as at the lock screen.
See the [Chrome OS Security Severity Guidelines] for details.

Also note that we do not handle account compromises with your Google account
(e.g. someone stole your Gmail password).  Please see the
[Google Account Help document](https://support.google.com/accounts/answer/7539929)
and related articles instead.

## Collecting full debug logs {#logs}

It's also possible to collect extensive system logs rather than the subset
that's included in feedback reports. To do this, enter
`chrome://net-internals/#chromeos` in the location bar and click the `Store
Debug Logs` button. The resulting `debug-logs` archive file will be placed in
your Downloads folder. It may contain personally identifiable information, so
you may want to either:

*   extract only the relevant log files, or
*   upload the archive to your Drive account and share it only with the
    developer investigating the issue.

## Taking screenshots {#screenshots}

Screenshots are extremely helpful when debugging UI-related issues. To capture a
screenshot on a Chrome OS device, hold Ctrl and hit the Switch Window (a.k.a. `[
]]]`) key (or F5 if you're using a non-Chrome-OS keyboard). The screenshot will
be written to your Downloads folder if you're logged in or to `/tmp` (which can
be accessed by browsing to `file:///tmp` after logging in) if captured at the
login screen. To take a screenshot of a limited region of the screen, use
Ctrl+Shift+Switch Window and drag a rectangle using the touchpad.

## Crash reports {#crash}

When the Chrome process, some other system process, or the Linux kernel crashes,
a crash report will be generated and sent if the `Automatically send diagnostic
and usage data to Google` setting is enabled. When this happens, you should
later be able to see information about the report at `chrome://crashes`,
including:

*   the report's ID (a 16-character hexadecimal string like `68fcfd6707e38d28`)
*   the crash type (e.g. `Chrome`, `ChromeOS`, or `ChromeOS_ARC`)
*   the time at which the crash was uploaded

If you give the ID to a Chrome OS developer, they can look up more details about
the report that will hopefully help them determine the crash's cause.

## Reporting system hangs {#hang}

If the entire UI (including the cursor) freezes or hangs, it can indicate
various problems, including:

*   a bug in Chrome's browser process
*   a bug in the Linux kernel
*   a hardware defect

If you see a freeze, try pressing Alt+Volume Up+X once, with the keys depressed
in that order. (If you're using a non-Chrome-OS keyboard, use Alt+F10+X
instead.) This will instruct the Linux kernel to attempt to make the Chrome
process crash and restart.

If that doesn't help, try pressing the three-key-combination two more times.
This should trigger a kernel panic, resulting in the system rebooting.

If the system is still frozen, you've probably encountered a lower-level issue.
Holding the power button for eight seconds should force a reboot.

If you were able to trigger a Chrome crash or kernel panic, you may be able to
find the crash ID at `chrome://crashes` after logging in again. Full debug logs
may also contain more information about what went wrong.

## Recommendations for reporting bugs {#recommendations}

If you think you've identified a bug in Chrome OS, please do the following:

1.  Search the [public issue tracker] to see if the bug has already been
    reported. If it has, you can click the star icon at the top-left corner of
    the page to indicate that you're also affected by the issue and receive
    email notifications whenever it's updated. If you have additional
    information you think might help resolve the issue, feel free to add it, but
    **please do not add "+1" or "Me too" comments -- just click the star icon.**
2.  If you're able to consistently reproduce the bug or if you regularly see it,
    hit Alt+Shift+i to send a feedback report immediately after seeing it. Write
    a short description of the problem in the text field and make sure that the
    `Send system and app information, and metrics` checkbox is checked before
    sending the report. Sending system information allows developers to view
    logs; this is almost always necessary in order to investigate bug reports.
    (If an issue is already tracking the bug, please include its ID in the
    feedback report's description and add a comment to the issue mentioning that
    you've submitted feedback).
3.  Go to [new.crbug.com] and create a new issue. Include as much information as
    you can about the bug and what was happening when you experienced it. If you
    were able to submit a feedback report, please mention that in the issue,
    along with the approximate time at which the bug occurred and the account
    that you used to submit the feedback report (if it differs from the account
    you're using to report the issue). Please attach any relevant screenshots or
    crash IDs, too.
4.  You'll receive email notifications when your issue is updated. If a
    developer asks for additional information about the bug, please supply it.
    The developer may ask you to provide debug logs that you collected
    previously.


[Chromebook Central Help Forum]: https://productforums.google.com/forum/#!forum/chromebook-central
[official feedback documentation]: https://support.google.com/chromebook/answer/2982029
[public issue tracker]: https://bugs.chromium.org/p/chromium/issues/list
[new.crbug.com]: https://new.crbug.com/
[crbug.com/new]: https://crbug.com/new
[go/newcrosbug]: https://goto.google.com/newcrosbug
[Reporting Security Bugs]: https://dev.chromium.org/Home/chromium-security/reporting-security-bugs
[Chrome OS Security Severity Guidelines]: https://chromium.googlesource.com/chromiumos/docs/+/master/security_severity_guidelines.md
