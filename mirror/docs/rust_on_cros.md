# Rust on Chrome OS

This provides information on creating [Rust] projects for installation within
Chrome OS and Chrome OS SDK. All commands and paths given are from within the
SDK's chroot.

[TOC]

## Usage

[cros-rust.eclass] is an eclass that supports first-party and third-party crate
dependencies. Rust project's ebuild should inherit the eclass to support Rust
building in Chrome OS build system.

> **WARNING**: Some legacy projects are still using [cargo.eclass]. These two
> eclasses can't be used together in a single project. Rust projects with
> dependencies should all use `cros-rust.eclass`.

### cros-rust.eclass

All the Rust projects using `cros-rust.eclass` will get dependent crates from
`/build/${BOARD}/usr/lib/cros_rust_registry` instead of [crates.io].
You'll learn how to publish first-party and third-party crates to
`cros_rust_registry` in the following sections.

### Third-party ebuild crates

To import a third-party crate, we need to create an ebuild for it in
`~/chromiumos/src/third_party/chromiumos-overlay/dev-rust/<crate_name>/<crate_name>-<crate_version>.ebuild`.
For an `example` crate with [SemVer] dependencies:

```toml
[dependencies]
crate1 = "^0.4"
crate2 = "^1.2"
crate3 = "~1.3"
```

Here is its ebuild:

```bash
# Copyright <copyright_year> The Chromium OS Authors. All rights reserved.
# Distributed under the terms of the GNU General Public License v2

EAPI="6"

CROS_RUST_REMOVE_DEV_DEPS=1

inherit cros-rust

DESCRIPTION="An example library"
HOMEPAGE="url/to/the/homepage"
SRC_URI="https://crates.io/api/v1/crates/${PN}/${PV}/download -> ${P}.crate"

LICENSE="|| ( <fill in license> )"
SLOT="${PV}/${PR}"
KEYWORDS="*"

DEPEND="
	>=dev-rust/crate1-0.4:=
	>=dev-rust/crate2-1.2:=
	<dev-rust/crate2-2.0
	=dev-rust/crate3-1.3*:=
"
```

-   `DESCRIPTION`, `HOMEPAGE`, `SRC_URI` and `LICENSE` should be found from
    `Cargo.toml` or [crates.io].
-   All the dependencies should have a `cros-rust` ebuild and be listed in
    DEPEND section.
-   Download the crate from [crates.io] and upload it to [localmirror].
    (Check details in "Depending on Crates" section).
-   Run command `ebuild example.ebuild digest` to generate Manifest.

After creating the ebuild file, running `emerge-${BOARD} <crate_name>` will
install the crate's package to `cros-rust-registry`.

Many third party crates have dev dependencies that are not actually needed
for Chrome OS. To keep dev dependencies from being enforced
`cros-rust.eclass` provides, `CROS_RUST_REMOVE_DEV_DEPS` which can be set to
remove the dev dependencies during `src_prepare`. This is especially useful when
there would otherwise be circular dependencies.

### Empty crates

If some third-party crates are dependent on some **unused** crates (e.g.,
dependencies uses by unused features or they're in dev-dependencies) and we want
to mock those **unused** crates out, we could create empty-crate ebuilds for
them. Here is an empty ebuild for example crate:

```bash
# Copyright <copyright_year> The Chromium OS Authors. All rights reserved.
# Distributed under the terms of the GNU General Public License v2

EAPI="6"

CROS_RUST_EMPTY_CRATE=1

inherit cros-rust

DESCRIPTION="Empty example crate"
HOMEPAGE=""

LICENSE="BSD-Google"
SLOT="${PV}/${PR}"
KEYWORDS="*"
```

### First-party crates

You can create your Rust project in anywhere in the Chrome OS system and it's
ebuild in a suitable place in `chromiumos-overlay` with name
`<category>/<crate_name>-9999.ebuild`. Here is an ebuild for
an example **first-party** crate:

```bash
# Copyright <copyright_year> The Chromium OS Authors. All rights reserved.
# Distributed under the terms of the GNU General Public License v2

EAPI="6"

CROS_WORKON_LOCALNAME="example"
CROS_WORKON_PROJECT="path/to/project/repository"
# We don't use CROS_WORKON_OUTOFTREE_BUILD here since project's Cargo.toml is
# using "provided by ebuild" macro which supported by cros-rust.
CROS_WORKON_SUBTREE="path/to/project/subtree"

inherit cros-workon cros-rust

DESCRIPTION="An example first party project"
HOMEPAGE="home_page_url"

LICENSE="BSD-Google"
SLOT="0/${PVR}"
KEYWORDS="~*"
IUSE="test"

DEPEND="
	dev-rust/third_party_crate:=
	example2/first_party_crate:=
"

src_unpack() {
	cros-workon_src_unpack
	S+="/path/to/project/subtree"

	cros-rust_src_unpack
}

src_compile() {
	ecargo_build
	use test && ecargo_test --no-run
}

src_test() {
	if use x86 || use amd64; then
		ecargo_test
	else
		elog "Skipping rust unit tests on non-x86 platform"
	fi
}

src_install() {
	# You can
	# 1. Publish this library for other first-party crates by
	cros-rust_publish "${PN}" "$(cros-rust_get_crate_version)"
	# 2. Install the binary to image by
	dobin "$(cros-rust_get_build_dir)/example_bin"
}
```

If the Rust project will be used by other first-party crates, remember to
publish it by using the `cros-rust_publish` command.

> **WARNING**: Please make sure your project could be built by both steps for
> engineering productivity:
>
> 1.  From chroot with `emerge-${BOARD} CRATE-EBUILD-NAME`
>
>     **Tips**: You can set `USE=-lto` to speed up build times when using
>     emerge. This turns off link time optimization, which is useful for
>     release builds but significantly increases build times and isn't really
>     needed during development.
>
> 2.  From project root directory with `cargo build`
>
> We add two macros to resolve conflicts between these two build system. Check
> details from the following section.

### Cargo.toml macros

Using `cros-rust` ebuild could support building crates in Chrome OS build
system, but it will break local `cargo build` in some situations. We add two
macros which are recognized by ebuild for `Cargo.toml` to keep both build system
work.

-   Provided by ebuild

    This macro introduces a replacement of:

    ```toml
    [dependencies]
    data_model = { path = "../data_model" }  # provided by ebuild
    ```

    with:

    ```toml
    [dependencies]
    data_model = { version = "*" }
    ```

    **Example usage**: Add dependency to first-party crate

    1.  Add the dependent crate to DEPEND section in ebuild.
    2.  Use relative path for imported crates in `Cargo.toml` but with
        `# provided by ebuild` macro:

    ```toml
    [dependencies]
    data_model = { path = "../data_model" }  # provided by ebuild
    ```

-   Ignored by ebuild

    We will use this to discard parts of `[patch.crates-io]` which should be
    applied to local developer builds but not to ebuilds.

    This macro introduces a replacement of:

    ```toml
    audio_streams = { path = "../../third_party/adhd/audio_streams" } # ignored by ebuild
    ```

    with empty line while building with emerge.

    **Example usage**: Add dependency to first-party crate for sub-crates from
    root crate.

    1.  Add the dependent crate to DEPEND section in root crate's ebuild.
    2.  Use relative path for imported crates in `[patch.crates-io]` section in
        root crate's `Cargo.toml` but with `# ignored by ebuild` macro:

    ```toml
    [patch.crates-io]
    audio_streams = { path = "../../third_party/adhd/audio_streams" } # ignored by ebuild
    ```

## Depending on Crates

Because the sources for all ebuilds in Chrome OS must be available at
[localmirror], you will have to upload all third-party crate dependencies for
the project to localmirror.

The following will download a crate, upload it to localmirror, and make it
accessible for download:

> **WARNING**: localmirror is shared by all Chrome OS developers. If you break
> it, everybody will have a bad day.

```bash
curl -L 'https://crates.io/api/v1/crates/<crate_name>/<crate_version>/download' >/tmp/crates/<crate_name>-<crate_version>.crate
gsutil cp -a public-read /tmp/crates/<crate_name>-<crate_version>.crate gs://chromeos-localmirror/distfiles/
```

## Cross-compiling

The toolchain that is installed by default is targetable to the following triples:

| Target Triple                 | Description                                                                         |
|-------------------------------|-------------------------------------------------------------------------------------|
| `x86_64-pc-linux-gnu`         | **(default)** Used exclusively for packages installed in the chroot                 |
| `armv7a-cros-linux-gnueabihf` | Used by 32-bit usermode ARM devices                                                 |
| `aarch64-cros-linux-gnu`      | Used by 64-bit usermode ARM devices (none of these exist as of November 30th, 2018) |
| `x86_64-cros-linux-gnu`       | Used by x86_64 devices                                                              |

When building Rust projects for development, a non-default target can be
selected as follows:

```bash
cargo build --target=<target_triple>
```

If a specific board is being targeted, that board's sysroot can be used for
compiling and linking purposes by setting the `SYSROOT` environment variable as
follows:

```bash
export SYSROOT="/build/<board>"
```

If C files are getting compiled with a build script that uses the `cc` or `gcc`
crates, you may also need to set the `TARGET_CC` environment variable to point
at the appropriate C compiler.

```bash
export TARGET_CC="<target_triple>-clang"
```

If a C/C++ package is being pulled in via `pkg-config`, the
`PKG_CONFIG_ALLOW_CROSS` environment
variable should be exposed. Without this, you might see `CrossCompilation`
as part of an error message during build script execution.

```bash
export PKG_CONFIG_ALLOW_CROSS=1
```

[rust]: https://www.rust-lang.org
[cargo]: https://crates.io/
[cargo.eclass]: https://chromium.googlesource.com/chromiumos/overlays/chromiumos-overlay/+/master/eclass/cargo.eclass
[crates.io]: https://crates.io
[cros-rust.eclass]: https://chromium.googlesource.com/chromiumos/overlays/chromiumos-overlay/+/master/eclass/cros-rust.eclass
[localmirror]: archive_mirrors.md
[link time optimizations]: https://en.wikipedia.org/wiki/Interprocedural_optimization
[semver]: https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html
