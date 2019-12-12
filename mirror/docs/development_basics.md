# Chromium OS Development Basics

This document covers guidelines to keep in mind when working on the Chromium OS
project.

[TOC]

## Documentation

### General guidelines

Chromium OS follows the Chromium project's [documentation guidelines] and
[documentation best practices].

### Design documents

Design documents typically describe the problem that you're trying to solve,
different approaches that you considered, and the path that you're planning to
take. They're useful for soliciting opinions from others before you start on the
implementation, but they also help your code reviewers get their bearings and
can answer other developers' "why was this done like that?" questions after the
work is complete (even after you've forgotten the reasons why!). On top of all
that, a design doc often helps you solidify a design in your own mind and
convince yourself that you're not missing anything.

Most non-trivial additions of new functionality, and particularly ones that
require adding new daemons or new interactions between different processes,
should have their own design docs. For smaller changes, documenting what you're
doing and why in the issue tracker is often enough.

Share your design docs with your team mailing list, if not with the full
[chromium-os-dev] mailing list. See the existing [Chromium OS design docs] and
[Chromium design docs] for inspiration.

## Programming languages and style

### C++

Nearly all userspace code in the Chromium OS project, whether it's part of the
Chrome browser itself or a system daemon exposing new functionality, is written
in C++. Do not use another language unless there's a compelling reason why C++
can't work for what you're doing. (Being more familiar with another language
than with C++ is not a compelling reason.)

The Chromium project, and by extension the Chromium OS project, follow the
[Google C++ style guide], with the [Chromium C++ style guide] layered on top to
provide additional guidelines and clarify ambiguities. The [C++11 use in
Chromium] document lists which of the many new features introduced in the C++11
standard are allowed.

New C++ programs should go into new directories in the [platform2 repository],
which is checked out to `src/platform2`.

### C

C should only be used for code that is part of the Linux kernel or Chrome OS
firmware.

Both kernel and firmware code should follow the [Linux kernel coding style]. The
[Kernel FAQ] has more details about Chrome OS kernel development, and the
[EC Development page] discusses firmware.

### Shell

Sometimes shell scripting can be the best way to perform lightweight,
non-persistent tasks that need to run periodically on Chrome OS systems, but
there are also big downsides: it's much more difficult to write tests for shell
scripts than for C++ code, and scripts have a tendency to grow to the point
where they become difficult to maintain. If you're planning to add a shell
script that is likely to grow in complexity, consider instead using C++ from the
start to save yourself the trouble of rewriting it down the road.

Shell scripts are mainly used for a few categories of tasks in Chrome OS:

*   Upstart initialization scripts, as in [src/platform2/init]. See the
    [init STYLE file] and [init README file] for guidelines.
*   Portage `.ebuild` files, as in the [chromiumos-overlay repository]. We
    follow the upstream guidelines; see the [Ebuild Writing] page and
    specifically the [Ebuild File Format].
*   Miscellaneous development-related tasks

Read the [Google shell style guide] and [Chromium OS shell style guidelines]
before writing scripts, with the caveat that the Upstart or Portage guidelines
take precedence when writing those types of scripts.

For shell scripts that ship with the OS image, be extra careful. The shell
provides powerful features, but the flip side is that security pitfalls are
tricky to avoid. Think twice whether your shell statements can have unintended
side effects, in particular if your script runs with full privileges (as is the
case with init scripts). As a guideline, keep things simple and move more
complex processing to a properly sandboxed environment in an C++ daemon.

### Python

The Python interpreter is not included in production Chrome OS system images,
but Python is used heavily for development and testing.

We largely follow the [Google Python style guide], but see the
[Chromium OS Python style guidelines] for important differences, particularly
around indenting and naming. For tests, see the [autotest coding style].

## Testing

The [Chromium OS testing site] is the main repository of information about
testing.

### Unit tests

Unit tests should be added alongside new code. It's important to design your
code with testability in mind, as adding tests after-the-fact often requires
heavy refactoring.

Good unit tests are fast, lightweight, reliable, and easy to run within the
chroot as part of your development workflow. We use [Google Test] (which is
comprised of the GoogleTest unit testing framework and the GoogleMock mocking
framework) to test C++ code. [Why Google C++ Testing Framework?] and the
[Google Test FAQ] are good introductions, and the [unit testing document] has
more details about how unit tests get run.

See the [Best practices for writing Chrome OS unit tests] document for more
guidance on writing good unit tests.

### Autotest

[Autotest] is used to run tests on live Chrome OS systems. Autotests are useful
for performing integration testing (e.g. verifying that two processes are able
to communicate with each other over IPC), but they have heavy costs:

*   Autotests are harder to run than unit tests: you need either a dedicated
    test device or a virtual machine.
*   Autotests are much slower than unit tests: even a no-op test can take 30
    seconds or longer per run.
*   Since autotests involve at least a controlling system and a test device,
    they're susceptible to networking issues and hardware flakiness.
*   Since autotests run on full, live systems, failures can be caused by issues
    in components unrelated to the one that you're trying to test.

Whenever you can get equivalent coverage from either unit tests or autotests,
use unit tests. Design your system with unit testing in mind.

## Code reviews

The Chromium OS project follows the [Chromium code review policy]: all code and
data changes must be reviewed by another project member before being committed.
Note that Chromium OS's review process has some differences; see the
[Developer Guide's code review instructions].

OWNERS files are not (yet) enforced for non-browser parts of the Chromium OS
codebase, but please act as if they were. If there's an OWNERS file in the
directory that you're modifying or a parent directory, add at least one
developer that's listed in it to your code review and wait for their approval
before committing your change.

Owners may want to consider setting up notifications for changes to their code.
To receive notifications of changes to `src/platform2/debugd`, open your
[Gerrit notification settings] and add a new entry for project
`chromiumos/platform2` and expression `file:"^debugd/.*"`.

## Issue trackers

Public Chromium OS bugs and feature requests are tracked using the
[chromium issue tracker]. Note that this tracker is shared with the Chromium
project; most OS-specific issues are classified under an `OS>`-prefixed
component and have an `OS=Chrome` label. The `crbug.com` redirector makes it
easy to jump directly to an issue with a given ID; `https://crbug.com/123` will
redirect to issue #123, for instance.

Keep discussion in the issue tracker instead of in email or over IM. Issues
remain permanently available and are viewable by people not present for the
original discussion; email and IM exchanges are harder to find after the fact
and may even be deleted automatically. `BUG=chromium:123` lines in commit
descriptions and `https://crbug.com/123` mentions in code comments also make it
easy to link back to the issue that describes the original motivation for a
change.

Avoid discussing multiple problems in a single issue. It's not possible to split
an existing issue into multiple new issues, and it can take a long time to read
through an issue's full history to figure out what is currently being discussed.

Similarly, do not reopen an old, closed issue in response to the reoccurrence of
a bug: the old issue probably contains now-irrelevant milestone and merge labels
and outdated information. Instead, create a new issue and refer to the prior
issue in its initial description. Text of the form `issue 123` will
automatically be turned into a link.

There is much more information about filing bugs and using labels in the
[Chromium bug reporting guidelines].

## Mailing lists

See the [contact] document for more details.

## Developing in the open

Chromium OS is an open-source project. Whenever possible (i.e. when not
discussing private, partner-related information), use the public issue tracker
and mailing lists rather than the internal versions.

[contact]: contact.md
[documentation guidelines]: https://chromium.googlesource.com/chromium/src/+/master/docs/documentation_guidelines.md
[documentation best practices]: https://chromium.googlesource.com/chromium/src/+/master/docs/documentation_best_practices.md
[Chromium OS design docs]: https://www.chromium.org/chromium-os/chromiumos-design-docs
[Chromium design docs]: https://www.chromium.org/developers/design-documents
[Google C++ style guide]: https://google.github.io/styleguide/cppguide.html
[Chromium C++ style guide]: https://chromium.googlesource.com/chromium/src/+/master/styleguide/c++/c++.md
[C++11 use in Chromium]: https://chromium-cpp.appspot.com/
[platform2 repository]: platform2_primer.md
[Linux kernel coding style]: https://github.com/torvalds/linux/blob/master/Documentation/process/coding-style.rst
[Kernel FAQ]: kernel_faq.md
[EC Development page]: https://chromium.googlesource.com/chromiumos/platform/ec/+/master/README.md
[src/platform2/init]: https://chromium.googlesource.com/chromiumos/platform2/+/master/init/
[init STYLE file]: https://chromium.googlesource.com/chromiumos/platform2/+/master/init/STYLE
[init README file]: https://chromium.googlesource.com/chromiumos/platform2/+/master/init/README
[chromiumos-overlay repository]: https://chromium.googlesource.com/chromiumos/overlays/chromiumos-overlay/+/master
[Ebuild Writing]: https://devmanual.gentoo.org/ebuild-writing/index.html
[Ebuild File Format]: https://devmanual.gentoo.org/ebuild-writing/file-format/index.html
[Google shell style guide]: https://google.github.io/styleguide/shell.xml
[Chromium OS shell style guidelines]: styleguide/shell.md
[Google Python style guide]: https://google.github.io/styleguide/pyguide.html
[Chromium OS Python style guidelines]: styleguide/python.md
[autotest coding style]: https://chromium.googlesource.com/chromiumos/third_party/autotest/+/master/docs/coding-style.md
[Chromium OS testing site]: https://www.chromium.org/chromium-os/testing
[Google Test]: https://github.com/google/googletest
[Why Google C++ Testing Framework?]: https://github.com/google/googletest/blob/master/googletest/docs/primer.md
[Google Test FAQ]: https://github.com/google/googletest/blob/master/googletest/docs/faq.md
[unit testing document]: https://www.chromium.org/chromium-os/testing/adding-unit-tests-to-the-build
[Best practices for writing Chrome OS unit tests]: testing/unit_tests.md
[Autotest]: https://chromium.googlesource.com/chromiumos/third_party/autotest/+/master/docs/user-doc.md
[Chromium code review policy]: https://chromium.googlesource.com/chromium/src/+/master/docs/code_reviews.md
[Developer Guide's code review instructions]: developer_guide.md#Upload-your-changes-and-get-a-code-review
[Gerrit notification settings]: https://chromium-review.googlesource.com/settings/#Notifications
[chromium issue tracker]: https://bugs.chromium.org/p/chromium/issues/list
[Chromium bug reporting guidelines]: https://www.chromium.org/for-testers/bug-reporting-guidelines
[chromium-os-dev]: https://groups.google.com/a/chromium.org/forum/#!forum/chromium-os-dev
