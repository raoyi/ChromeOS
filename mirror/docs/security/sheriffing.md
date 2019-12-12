# Chrome OS security sheriffing

## What is sheriffing?

The Chrome OS security team maintains a [security sheriff rotation] to ensure
that [incoming security bugs] are triaged promptly and fixed according to our
[security severity guidelines]. Each sheriffing shift lasts a week, from
Tuesday to Monday of the following week. You are **not** expected to sheriff
during the weekend.

## Sheriff responsibilities

*   The role of a sheriff is to route issues and make sure existing issues get
    fixed according to the [security severity guidelines].
*   It is not the sheriff's responsibility to fix all the bugs coming in.
*   Initially, expect to spend 20% of your time sheriffing during your shift.
*   Triage bugs in the spreadsheet. I.e., make things less red.
*   Make sure questions to [chromeos-security@] don't go unanswered.

## How do I sheriff?

Open the spreadsheet at
[go/chromeos-security-bugs](https://goto.google.com/chromeos-security-bugs).
Identify the cells that are red. This happens for bugs that don't have owners,
that are not assigned to a component, or don't have an Impact, Milestone, or
Severity flag; or bugs that haven't seen an update in a while.

Attempt to reduce the amount of red on the spreadsheet. Find owners for
un-owned bugs, assign proper components to bugs without components. Triage
Impact, Milestone, and Severity for bugs. Make sure progress is happening on
High+ severity bugs.

If you see a bug reported in a third-party package, check the
[security-sensitive package list]. If the package is in the list, make it a
priority to update the package before your shift ends. You can often find newer
versions of portage packages in
[upstream Gentoo](https://packages.gentoo.org/categories). Do not worry if
the version you need to resolve a security issue isn't marked stable. There are
instructions for upgrading packages in the
[portage-stable mirror](../portage/package_upgrade_process.md).

Sometimes a security bug might be in an unused feature of a third party package.
If this is the case, you can often disable features during the configuration
step
([example](https://crrev.com/c/1641862/1/chromeos/config/env/net-misc/curl)).

## Sheriffing and full-chain exploits

### Ownership

When a full-chain exploit comes in, the current sheriff owns the issue for the
lifetime of the chain. If more than one chain comes in a given sheriff week,
the next sheriff owns the next chain, and so on and so forth. Refer to the
[security sheriff rotation] to find the next sheriff.

### Handling a full-chain exploit

When a full-chain exploit comes in, the objective is to break the chain: to fix
enough bugs that the exploit as submitted no longer works.

The sheriff should handle a full-chain exploit by breaking the exploit down into
its component bugs: each link in the chain should get a separate bug in
[crbug.com](https://crbug.com). This allows making faster progress on individual
bugs and therefore breaking the chain faster and allowing easier merge of the
fixes into release branches.

The exit criteria for a full-chain exploit are:

*   The chain is broken on the stable branch.
*   A short post-mortem is written covering which mitigations were useful and
    which parts of the system need more hardening. This document doesn't need to
    be long, it just needs to be comprehensive. Each full-chain exploit is a
    great prioritization mechanism. The objective of the post-mortem is to write
    down the information required for prioritization while it's still fresh in
    our minds.
    *   The [crash reporter security document] has some examples of short
        analyses of security bugs.
    *   A longer analysis for a Chrome browser full chain exploit can be found
        at [A tale of two Pwnies (part 1)]. Keep in mind that the post-mortem
        doesn't need to be this long. A one-pager doc should be enough.

Once these two requirements are met, the main issue for the full-chain exploit
can be marked as *Fixed*. Individual sub-bugs don't necessarily need to be
closed before marking the main bug as fixed, as long as the exploit chain is
successfully broken.

[security sheriff rotation]: https://goto.google.com/chromeos-security-sheriffs
[incoming security bugs]: https://goto.google.com/chromeos-security-bugs
[security severity guidelines]: https://chromium.googlesource.com/chromiumos/docs/+/master/security_severity_guidelines.md
[security-sensitive package list]: https://chromium.googlesource.com/chromiumos/docs/+/master/security/sensitive_chromeos_packages.md
[chromeos-security@]: https://groups.google.com/a/google.com/forum/#!forum/chromeos-security
[crash reporter security document]: https://chromium.googlesource.com/chromiumos/platform2/+/HEAD/crash-reporter/docs/security.md
[A tale of two Pwnies (part 1)]: https://blog.chromium.org/2012/05/tale-of-two-pwnies-part-1.html
