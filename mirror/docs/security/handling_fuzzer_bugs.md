# Handling bugs found by fuzzers

Thanks to the work of the Chrome Security Bugs-- team, the Chrome OS Toolchain
team, and the Chrome OS security team, there is an increasing number of fuzzers
written for Chrome OS targets. This document describes the expectations for
handling bugs found by these fuzzers.

## Ownership

The expectation is that bugs, including security bugs, found by a fuzzer will be
owned and fixed by the team that owns the code being fuzzed. While the Chrome OS
security team handles triaging duties for security bugs, *the responsibility
for fixing those bugs rests on the team that owns the code in question*. Bugs
found by fuzzers in third-party packages should similarly be owned by the team
pulling in that third-party package. The Chrome OS security team maintains a
[list of security-sensitive Chrome OS packages]. Bugs in these packages should
be prioritized by the teams owning or pulling in the package.

This is consistent with the Chrome OS position that teams are ultimately
responsible for all aspects of their features, includign security; while the
Chrome OS security team maintains security-critical features and services,
develops tools, and provides advice and support.

## Timeline

Security bugs found by fuzzers are handled just like any other
internally-reported security bug, and should be fixed according to the
[security severity guidelines].

[security severity guidelines]: https://chromium.googlesource.com/chromiumos/docs/+/master/security_severity_guidelines.md

[list of security-sensitive Chrome OS packages]: https://chromium.googlesource.com/chromiumos/docs/+/master/security/sensitive_chromeos_packages.md
