# GN in Chrome OS (go/chromeos-gn)

New packages should use
[GN](https://gn.googlesource.com/gn/+/master/docs/reference.md) instead of GYP.

See the official [step-by-step introduction](
https://gn.googlesource.com/gn/+/master/docs/quick_start.md#Step_by_step) for
the GN basics. This article discusses Chrome OS specific stuff.

## How to build your package with GN

Example: [arc/adbd/BUILD.gn](https://chromium.googlesource.com/chromiumos/platform2/+/master/arc/adbd/BUILD.gn)

- Put `BUILD.gn` in your package directory, which is determined by
  `PLATFORM_SUBDIR` in your ebuild. Existence of `BUILD.gn` indicates to the
  platform2 build system that GN should be used to build this package.
- Have a target named `"all"` in the `BUILD.gn`. It's the root target built
  by the platform2 build system. Typically it's a `group` target depends on all
  the targets to be built.
- `common-mk/` contains common templates or common settings, which your build
  files can utilize.
    - `pkg_config.gni` defines the `pkg_config` rule to generate configs for
      package dependencies.
    - `BUILDCONFIG.gn` defines the default configs for each target type (e.g.
      executable). You can remove default configs in individual target with
      `configs -=` if needed.
      ([example](https://crrev.com/d2f92d07e9b0950157b7ce3a0f70cfee72fe76e7/hammerd/BUILD.gn#39))

## How to write ebuilds

Example: [arc-adbd-9999.ebuild](
https://chromium.googlesource.com/chromiumos/overlays/chromiumos-overlay/+/master/chromeos-base/arc-adbd/arc-adbd-9999.ebuild)

Note we should add `.gn` in `CROS_WORKON_SUBTREE` so that the platform2 build
system can access the file.

### Packages outside platform2

For packages outside platform2, use `CROS_WORKON_DESTDIR` to copy the
package under `<workspace>/platform2/` while building it.
([example](https://crrev.com/2bee6447043f11d39c61d2c3ea0b02287793dcf9/chromeos-base/update_engine/update_engine-9999.ebuild#8))

## How to check USE flags in GN

In GN files, USE flags can be referred as `use.foo`.
([example](https://crrev.com/d2f92d07e9b0950157b7ce3a0f70cfee72fe76e7/hammerd/BUILD.gn#12))

Only whitelisted USE flags can be used. If you need to use new USE flags, update:
- `_IUSE` constant in `platform2/common-mk/platform2.py` ([example](https://crrev.com/c/1605185/5/common-mk/platform2.py))
- `IUSE` variable in your ebuild file ([example](https://crrev.com/c/1617184))

## How to write unit tests

`use.test` flag is set to true on unit testing. Enclose test only targets with
`if (use.test) {}` to reduce compile time on production.
The test targets are typically executables which depend on `//common-mk:test` to
use gtest and gmock.

How to run unit tests doesn't change: In chroot, run
`cros_workon --board=$BOARD start $package_name` if you haven't. Then run

```
FEATURES=test emerge-$BOARD $package_name
```

Prepend `VERBOSE=1` to see GN and ninja commands (plus other logs).

## FAQ

### How to create standalone static library?

Static libraries are compiled with thin archive enabled by default i.e. not standalone.
Remove `use_thin_archive` from configs and add `nouse_thin_archive` to generate a standalone static library ([example](https://chromium.googlesource.com/chromiumos/platform2/+/HEAD/glib-bridge/BUILD.gn#25)).

TODO(crbug.com/991440): consider making standalone library the default and replace static_library with source_set whenever possible.
