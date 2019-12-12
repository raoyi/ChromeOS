# libchrome

[TOC]

## Background

The Chromium project has an general utility library referred to as
[libbase]. Because it is standalone and does not depend on any other parts
of Chromium, it has been been picked up by other Google related projects so
people don't have to reinvent these things.

Along those lines, a package in Chromium OS is provided so that projects
specific to us can share the code without having to bundle it multiple
times over. Currently, there are over 20 such projects in Chromium OS.
To keep people on their toes, the package is named `libchrome` as
`libbase` by itself is too confusing. Granted, `libchrome` isn't exactly
clear itself, but it's a lose-lose situation, and we tried our best.
Please still love us.

## Using libchrome in Chromium OS

### In an ebuild (non-platform2)

**Note:** If your package is integrated into the [platform2] ebuild,
then this is already handled for you in the common platform2 ebuild
and you can skip this section.

There are 4 things to make sure the ebuild does when building a Chromium
OS package that uses libchrome:

1.  inherit the `cros-debug` eclass
1.  depend on a specific version (SLOT) of libchrome with the right
    USE=cros-debug setting
1.  call `cros-debug-add-NDEBUG` in one of `src_prepare`, `src_configure`,
    or `src_compile`.
1.  export `BASE_VER` to the version you are depending on

Below you can find copy & paste snippets that should work for any ebuild
in the Chromium OS tree. All you should need to change is the `125070` as
the number is updated.

```
...
inherit cros-debug
...
LIBCHROME_VERS="125070"
...
RDEPEND="chromeos-base/libchrome:${LIBCHROME_VERS}[cros-debug=]"
...
src_compile() {
  ...
  tc-export PKG_CONFIG
  cros-debug-add-NDEBUG
  export BASE_VER=${LIBCHROME_VERS}
  ...
}
```

### In the platform2 build system

If your package has been upgraded to [platform2] (if not, why not?),
then it's simple.

In your package's `BUILD.gn`, list libchrome as a dependency as needed
(e.g. either in the project-common `target_defaults` or the target-specific
section). For example, `portier` takes the former approach:

```
pkg_config("target_defaults") {
  pkg_deps = [
    "libbrillo-${libbase_ver}",
    "libchrome-${libbase_ver}",
    "protobuf",
  ]
}
```

At time of writing, the platform2 build system automatically takes care
of the rest for you.

### In common.mk (deprecated)

In a standard `common.mk` Chromium OS platform project, you can use these
snippets in your Makefile:

```
# If the build env has exported $PKG_CONFIG to a wrapper, use that, else use
# the default pkg-config wrapper (so we can "make" in place for testing).
PKG_CONFIG ?= pkg-config

# If the build env has exported $BASE_VER, use that. Else, use the last
# version that we tested against. This allows the ebuild to update to a
# newer version without having to explicitly update the source build
# system for trivial changes.
BASE_VER ?= 125070

# You can add as many or as view pkg-config libraries to this PC_DEPS
# value. Here we just use a specific version of libbase.
PC_DEPS = libchrome-$(BASE_VER)

# Look up the compiler flags and linker settings via the pkg-config
# wrapper once. That is why we use a dedicated variable and the :=
# operator -- if we use =, then make will end up executing the
# pkg-config wrapper many times.
PC_CFLAGS := $(shell $(PKG_CONFIG) --cflags $(PC_DEPS))
PC_LIBS := $(shell $(PKG_CONFIG) --libs $(PC_DEPS))
```

### In a package's source code

In your source, include files from `base/` like normal. So if you want to
use the string printf API, do:

```c
#include <base/stringprintf.h>
```

## Internal Details

Over time, we've evolved how we package up the base source tree. Here
we'll cover the lessons we've learned, and why we do the things that we
do. This way, future decisions can take into consideration all the
factors without missing something.

For some more background (and specifics), see
[this thread](https://groups.google.com/a/chromium.org/d/topic/chromium-os-dev/daH97iacQeQ/discussion).

### Single Static Library

The first iteration involved creating a single `libbase.a` from a single
version of Chromium (and install headers into `/usr/include/base/`).
Then anyone who wanted to use this code base would
link with `-lbase` and `#include <base/foo.h>`.

The advantages here:

1.  It was very simple to put together/manage/get running.
1.  Only the specific objects a project wanted were included (as the
    `libbase.a` archive was actually a bunch of .o files, and only the
    needed ones were pulled in).
1.  Runtime foot print was relatively small, even though some symbols
    were duplicated between projects.

Unfortunately, as it was widely deployed, we hit scaling issues:

1.  If the objects pulled in from `libbase.a` needed third-party
    libraries, projects had to manually link those in themselves (like
    `-lrt` or `-lm` or `-lpthread` or `-lglib-2.0` or ...).
1.  The exact list of additional libraries that projects needed to specify
    in order to successfully link against `libbase.a` changed over time, so
    many projects ended up just copying and pasting a long list of libraries
    leading to overlinking (pulling in libraries that at runtime never get
    used), which in turn leads to runtime overhead.
1.  Similarly, the exact third-party headers that libbase itself
    uses changes over time. So projects ended up passing `-I` paths to many
    third-party projects just in case libbase needed them.
1.  People would use libbase in shared libraries and not notice that the
    symbols pulled in from libbase were now exported as part of the shared
    library interface. With applications, there is only one copy of the
    libbase code active, but with shared libraries, applications might
    have the missing symbols satisfied via those! This meant sometimes
    the application would get the symbols from `libbase.a` and sometimes
    it wouldn't (depending on the order of libraries during link time!).
    This is a bad state to be in terms of reproducibility and reliability.
1.  Upgrading libbase often broke various projects as the API evolved over
    time. This happens because libbase is maintained as part of Chromium,
    so when the API evolves there, all consumers get updated. But Chromium
    OS projects aren't part of Chromium, so we didn't see those updates
    propagating across.
1.  Due to the large number of Chromium OS projects being locked to a
    specific version, updates in our system required simultaneous
    coordination of many groups in order to update all the source trees
    and ebuild packages more or less atomically. Any regressions in this
    led to hard-to-revert tree states and build failures that could last
    a few days as everyone scrambled.
1.  Even after everyone was on board, some projects would inevitably
    get missed because it's not easy to determine applications that
    linked against a static library (there's nothing to search for in
    the ELF), and sometimes ebuilds would be added with missing version
    information.
1.  Since upgrading is so painful, in practice the upgrade would happen
    only once or twice a year, and generally only because a project
    needed some API features only extant in newer versions of Chromium.
    Even then, sometimes groups avoided upgrading as long as possible
    so they wouldn't get blamed by other groups when things fell apart.

The first few points were annoying, but bearable. The latter points
(related to upgrading), however, were not. So we embarked on a search
for a solution!

### Slotted Static Libraries

Since static libraries were so trivial to throw together, we tried to
expand on this concept. Now, rather than installing `libbase.a`, we
would install `libbase-<version>.a` and `/usr/include/base-<version>/base/`.
Then projects would be built and linked against a specific version of
libbase by using e.g. `-lbase-85268` and compiled against a matching set
of headers by using e.g. `-I/usr/include/base-85268`.

This has advantages over a single static library:

1.  Updating one project to a newer version of libbase does not affect
    any other project making testing much easier (`build_packages` still
    works!) for people.
1.  Subgroups can update their specific projects to newer versions on
    their own schedule.
1.  Newer versions of libbase can be added without affecting any projects,
    so people doing experiments with newer APIs can easily do so.

However, after building and testing this prototype, we hit problems that
were non-starters for deploying related to libraries. When a Chromium OS
shared library (e.g. libmetrics) links against a specific libbase version,
it turns around and exports the symbols from that version. So when linking
an application against a different version of libbase, and that shared
library, we cannot guarantee that the ABI between the two versions are the
same. While the compile might have been clean, we don't know if the
runtime will be clean, and the behavior could change depending on the link
order (`-lbase-### -lmetrics vs -lmetrics -lbase-###`). This could easily
lead to hard-to-debug and hard-to-understand crashes or misbehavior at
runtime.

We could say that the shared library would clean up its exported ABI by
never exporting any libbase symbols (which would be a good thing
regardless), but the resulting system is still unmanageable. Since
linking against the static library pulls in both functions and state,
and some of the APIs from libbase have initialization functions (such as
the logging framework which sets up message headers, files, and
maintains a buffer), libmetrics now has its own copy of the logging
code, and the end application has its own copy of logging code. When the
application initializes the logging framework, it initializes its own
logging state, not libmetrics' logging state. So when libmetrics
attempts to do logging of its own, it often times will crash as its
logging state is uninitialized. We could add initialization functions to
libmetrics so that it too would initialize its own libbase state, but
now we have two parallel logging functions at runtime which could be
clobbering the external state (e.g. files).

Similar complications come up when using static libraries that
themselves use libbase. If libmetrics was built against `libbase-1234`,
and another project was built against `libbase-5678`, they'll want
different functions at link time which can lead to symbol clashing
leading either to link time failures or runtime failures (as detailed
above).

This is all fairly fragile, and is arguably trading one set of problems
(hard to build and upgrade) for a different, and perhaps even worse, set
of problems (things are easy to build and upgrade, but hard to run and
debug). We can do better, so let's think harder.

### Slotted Dynamic Libraries

Since the slotted aspect of the previous
proposal got us the upgrade path that we desired, we now just have to
solve the duplicate state problem. That could be done by only using
shared libraries with libbase -- there's no chance to have multiple
states be linked in as there are no static archives anymore. Now instead
of providing `libbase-<version>.a`, we provide `libbase-<version>.so`.
The other aspects of the previous proposal are the same (include paths,
as well as compiling and linking flags).

The advantages here:

1.  There is only one copy of all libbase functions and state at runtime
    -- when we call a logging function, we know that function has one copy
    of its state, and know that everyone will be using that same function.
1.  We know exactly what version of libbase an application was linked with
    after it's been built (by looking at `DT_NEEDED` ELF tags).
1.  We can track down exactly what packages are implicitly using libbase
    without declaring it in its ebuild.

It's not all peaches and apple pie though -- there are some trade-offs here:

1.  All programs using libbase load all of libbase at runtime, even parts
    they don't use (functions and state).
    *   Arguably, this overhead is small, but it is not zero.
1.  All third-party libraries that libbase needs get pulled in at runtime,
    even if they're only needed by parts of libbase the application doesn't
    use (and those libraries could pull in other libraries!).
    *   This overhead is much more noticeable than the previously-mentioned
        issue.
1.  The libchrome ebuild has to be complete in terms of what files it
    builds and links together as any undefined references will cause a
    shared library link error.
    *   This is actually a good thing as it means we can be confident
        that when updating, our package has included all the objects we
        care about. Otherwise, we have to try compiling all the other
        projects and see if they all pass (without undefined references)
        before we know the new package built all the necessary files.
1.  Static libraries (other than project-specific ones -- e.g. convenience
    libraries) are no longer allowed to use libbase (e.g. a project provides
    `libfoo.a` which uses libbase and multiple other projects use
    `libfoo.a`) as this is hard to track, and leads to similar problems as
    slotted static libraries in terms of mismatch of ABI.
    *   Not a big deal as we have few libraries in Chromium OS that use
        libbase, and making them all shared has been okay.
1.  Projects that link against a shared library that links against
    libbase must use the same version of libbase. Otherwise, at runtime,
    an application will load `libbase-1234.so` and `libfoo.so`, and
    `libfoo.so` will load `libbase-5678.so`, and both libbases
    will attempt to satisfy symbol references leading to runtime ABI
    conflicts and possibly random crashes.
    *   To be safe, this improves the set of packages that need to be
        upgraded simultaneously from all consumers of libbase to consumers
        of a specific library. So anyone who links against libmetrics
        (which uses libbase) has to use the same version of libbase as
        libmetrics. When an upgrade occurs, they should all upgrade
        together. For standalone projects which don't link against any
        libraries that use libbase, they can safely upgrade/downgrade
        independently.

The last point here is the only real show stopper.
Fortunately, two things work in our favor. Generally, the ABI is stable
with libbase (across the version ranges we upgrade between), so the
runtime "mostly works". This means we can tolerate a period of time
where we are upgrading to a newer version of libbase but some
applications are actually (runtime) linked against multiple versions. By
the time we actually release, the upgrade will have completed, so there
will once again only be one version live at a time. Further, since we
can detect exactly what versions of a library an ELF has been linked
against, we can confidently detect the cases where a program uses one
version of libbase, but links against a shared library which pulls in a
different one and act appropriately (i.e. update all the packages).

At this point, we have a workable solution. But we can still do better.
Onwards!

### Using pkg-config

Since we need to change all projects that use libbase
(from `-lbase` to `-lbase-<version>`, and adding
`-I/usr/include/base-<version>`), we might as well come up with a better
answer overall that scales and addresses other annoyances. This brings
us to [pkg-config].

The advantages of providing a `.pc` file for projects to query are
significant!

1.  We can hide all of libbases' dependencies from projects that just
    want to use libbase. Rather than having the projects manually specify
    `-lrt` or `-lpthread` or `-I/usr/include/...` or anything else, the
    `.pc` file declares everything it depends on. Projects then just ask
    for the CFLAGS and libraries that libbase needs, and it gets expanded
    as needed.
1.  If we want to make any library changes in the future (moving or
    renaming the files or the install paths), we only have to update the
    `.pc` file. No end projects need change.

For the nit-pickers out there, there are disadvantages:

*   You have to depend on the pkg-config package, and execute `pkg-config`
    at build time.
    *   This is required by many other projects already (like glib), so
        not really unique to libbase problem.

So this cleans up the compiling/linking process nicely, and integrates
with existing pkg-config framework that other libraries depend on.

### Optimized Slotted Dynamic Libraries

The biggest disadvantage to shared libraries is that libbase isn't
really one API, but rather a large collection of different APIs.
Some require third party libraries to work (like pcre or glib or
pthreads), while others require very little. So forcing one project
that wants just the simple APIs (like string functions) to pull in more
complicated APIs which pull in other third party libraries (like pcre)
even though it won't use them is a waste of runtime resources.

We can combat this though by leveraging some linker tricks. When you
specify a library like `-lfoo`, it doesn't have to be just a static
archive (`libfoo.a`) or a shared ELF (`libfoo.so`), it could even be a
[linker script]! Combined with the useful `AS_NEEDED` directive, we can
create an arbitrary number of smaller shared libraries (like
`libbase-core-1234` and `libbase-pcre-1234` and `libbase-foo-1234`) where
each one has its own additional library requirements and provides different
sets of APIs. Then when people link against `-lbase-1234`, the linker will
look at all of the smaller libbase shared libraries and only pull in the
ones we actually use. This is all transparent to the user of the libbase
API.

So we have all of the advantages of slotted dynamic libraries, and only
one of the downsides: we still have possible runtime conflicts where a
program uses one version, but a library it links against uses a
different version. As noted previously, this is an acceptable trade off
for now, and makes the upgrade situation significantly more manageable.

### cros-debug and NDEBUG

Some of libbase's headers define structs or classes that include or
exclude members based on whether the `NDEBUG` macro is defined or not.
If libbase is built with `NDEBUG` defined, but then a program that
dynamically links against libbase includes those headers with `NDEBUG`
undefined (or vice versa), resulting in disagreements about the sizes
of objects, hard-to-debug segfaults can occur. We define a `cros-debug`
`USE` flag to try to ensure that `NDEBUG` is set or unset consistently
across different packages.

### Future Work

Here are some random thoughts that might be worth investigating to try and
improve the current situation:

*   Put all of libbase into a version-specific C++ namespace.

## Building libbase

See the
[gn build recipe](https://chromium.googlesource.com/aosp/platform/external/libchrome/+/refs/heads/master/BUILD.gn)
.

It maintains a list of all the files which go into a shared library
fragment (such as 'core' and 'glib' and 'event'). It's largely split
along the lines of what third party libraries will get pulled in (so the
'core' only requires C libraries, 'glib' additionally requires glib,
'event' additionally requires libevent, etc...). The fragments could
conceivably be split further, but the trade-offs in terms of runtime
overhead were found to not warrant it (generally in the range of "system
noise").

This build file is also responsible for generating the pkg-config `.pc`
file and linker script.

## Upgrade/Release Plans

Once a Chromium OS project has identified newer
APIs that they want to utilize, or the upstream Chromium project has
introduced features that make it more attractive to us (such as no
longer hard requiring GTK+), it's time for us to schedule an upgrade!
Here is a general approach which should work for people:

1.  Announce your intention to upgrade libbase to the
    chromium-os-dev@chromium.org mailing list!
    *   The various Chromium OS groups now can't say they didn't see this
        coming :).
1.  Wait for the next branch to be made so that ToT starts development anew.
    *   Gives plenty of time to all the various Chromium OS groups to plan
        an upgrade before the *next* branch.
1.  Figure out what revision number you want to use for libchrome.
    *   Look at the LKGRs for the latest Chrome branch.
    *   See what revision number it lists.
1.  Figure out what git SHA-1 that revision number maps to in each of
    the sub-repositories.
    1.  Check out a bunch of Chromium sub-repos that contain portions of
        the main Chromium repository:
        *   [chromium/src/base]
        *   [chromium/src/build]
        *   [chromium/src/components/timers]
        *   [chromium/src/crypto]
        *   [chromium/src/dbus]
        *   [chromium/src/sandbox]
    1.  Look at the git log -- every commit has metadata in it that
        tells you the revision number it maps to, e.g.
        `Cr-Original-Commit-Position: refs/heads/master@{#334285}`.
    1.  Note that since upstream Chrome maps a single repository into many
        projects, the revision number that you choose from the main
        Chromium repository is unlikely to be present in the base, dbus,
        etc. repos. Instead, find the commits that are closest to (but do
        not exceed) the revision number from the main repository.
1.  Update the libchrome source on the Android `aosp/master` branch
    (this is the code that's built by the libchrome ebuild). This is a new,
    exciting process -- hope you're ready for an adventure!
    1.  Check out aosp/master if you don't have it already.
    1.  The libchrome source lives in external/libchrome. Several pieces are
        brought together in this directory:
        1.  base/, build/build_config.h, components/timers/, crypto/, dbus/,
            and sandbox/ are copied wholesale from Chromium sub-repos.
        1.  Several small patches have been applied on top of the above
            code to get it to build. (In general, we try to upstream
            whatever changes we can.)
        1.  Additional files that are needed to build and test are under
            testing/ and third_party/.
        1.  Finally, there's an `Android.mk` file for building libchrome
            on Android, an SConstruct file for building it on Chrome OS,
            and `MODULE_LICENSE_BSD` and `NOTICE` files.
    1.  The easiest approach here is probably something like:
        1.  Identify all of the local changes that have been applied to the
            stock upstream code.
        1.  Copy in the new upstream code from the sub-repos.
        1.  Reapply the local changes.
        1.  Wrestle with libchrome until it builds for Android (Android
            always builds the most-recently-checked in code, so you need to
            get it compiling before you commit it).
    1.  Add a new `libchrome-####` ebuild and update the revision it uses
        from the AOSP repository.
    1.  Update the libchromeos code as needed by handling the new `BASE_VER`
        value.
        *   Could be developed and even committed before the branch since
            it won't (yet) affect anything.
    1.  Update the `platform2-9999.ebuild` code to depend on the new
        libchrome version.
        *   Must be done after the branch as now the new libchrome ebuild
            will be pulled in, compiled, and shipped in images.
    1.  Look for the `LIBCHROME_VERS` array and just add the new `####` to
        it.
    1.  Update the `platform.gyp` file in `src/platform/common-mk/`.
        *   Add the new libchromeos version to the `targets.dependencies`
            section.
    1.  Start upgrading the various projects to the new libbase.
        *   Upgrade packages that are looped by way of other libraries
            (e.g. libchaps needs libbase, so all projects that use libchaps)
            together.
    1.  Once everyone has upgraded:
        1.  Update the `platform2-9999.ebuild` to only depend on the latest
            libchrome version.
        1.  Update the `platform.gyp` to only include latest libchromeos
            version.
        1.  Drop the older libchromeos `.gyp` files.
        1.  Remove all references to older `BASE_VER` in libchromeos code
            base.

This really should be done within a single development cycle so that we
aren't wasting system resources by shipping (and having active) multiple
libbase shared libraries. One of the advantages of using shared libraries
is that all of the non-writable sections (like .text) get shared between
processes, and that's defeated in part by multiple active libbase versions.

## See also

[libbase] on Google Git

[libbase]: https://chromium.googlesource.com/chromium/src/base/
[platform2]: ../platform2_primer.md
[pkg-config]: https://www.freedesktop.org/wiki/Software/pkg-config/
[linker script]: https://sourceware.org/binutils/docs/ld/Implicit-Linker-Scripts.html
[chromium/src/base]: https://chromium.googlesource.com/chromium/src/base/
[chromium/src/build]: https://chromium.googlesource.com/chromium/src/build/
[chromium/src/components/timers]: https://chromium.googlesource.com/chromium/src/components/timers/
[chromium/src/crypto]: https://chromium.googlesource.com/chromium/src/crypto/
[chromium/src/dbus]: https://chromium.googlesource.com/chromium/src/dbus/
[chromium/src/sandbox]: https://chromium.googlesource.com/chromium/src/sandbox/
