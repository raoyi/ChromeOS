# Local & Remote Source Tree Layouts

Here we discuss the layout of files in the local source checkout as well as the
remote Git server.
The goal is both to document the current state of things and to provide guidance
when adding new repos.

Some repos might exist in places that don't follow these guidelines, but the
goal is to align rather than keep adding exceptions.

[TOC]

## Local Checkout

This is the layout as seen when you get a full CrOS checkout.
We cover the source repos separately from the generated paths to make the
provenance of the paths clearer.

### Source directories

Some of these are marked as *(non-standard)* to indicate that, someday maybe,
the repo would be moved to a more appropriate path.

*   `chromeos-admin/`: *(non-standard)* Internal repo used by the build/infra
    team to hold scripts and tools for managing various infrastructure systems.
*   [`chromite/`][chromite]: All of CrOS's build tools live here.
*   `chromium/`: *(non-standard)* Mirrors of repos from the Chromium project.
*   [`cros-signing/`][cros-signing]: *(non-standard)* Signing server code.
*   [`crostools/`][crostools]: *(non-standard)* Signing instructions for
    builders.
*   [`docs/`][docs]: Public documentation.
*   [`docs-internal/`][docs-internal]: Internal documentation.
*   `infra/`: Projects for various CrOS infra systems.
*   `infra_internal/`: Internal projects for various CrOS infra systems.
*   `infra_virtualenv/`: Python virtualenv tooling for CrOS infra projects.
*   [`manifest/`][manifest]: Public Chromium OS manifest.
*   [`manifest-internal/`][manifest-internal]: Internal Chrome OS manifest.
*   `src/`: Most source code people care about.
    *   `aosp/`: Mirrors of repos from the [Android project][AOSP GoB].
    *   [`overlays`/][board-overlays]: Single git repo holding all public
        board/etc... overlays.
        *   `baseboard-*/`: Overlays for "base boards".  Content that is for the
            specified board only and is "software stack" independent.
        *   `chipset-*/`: Overlays for specific chipsets/SoCs.  Board or OS
            specific details don't generally belong in here.
        *   `overlay-*/`: Overlays for the actual board.  These often extend a
            baseboard or chipset and blend in a project or OS stack.
        *   `project-*/`: Software stacks for standalone projects.  These are
            used to share code easily among different boards.
    *   `partner_private/`: Separate git repos for internal partner repos.
        These hold source repos that isn't open source or authored by Google.
    *   `platform/`: Separate git repos for Google/Chromium OS authored
        projects.  Here are a few notable repos.
        *   [`dev/`][dev-util]: Various developer and testing scripts.
            *   [`contrib/`][contrib]: Where developers can share their personal
                scripts/tools/etc...  Note: completely unsupported.
        *   [`vboot_reference/`][vboot_reference]: Code and tools for working
            with verified boot, as well as image signing and key generation
            scripts.
        *   `$PROJECT/`: Each project gets its own directory.
    *   [`platform2/`][platform2]: Combined git repo for Chromium OS system
        projects.  Used to help share code, libraries, build, and test logic.
    *   `private-overlays/`: Separate git repos for internal partner repos to
        simplify sharing with specific partners.  This mirrors the structure
        of `src/overlays/`.
        *   `baseboard-*-private/`: Internal base boards shared with specific
            partners.
        *   `chipset-*-private/`: Internal chipsets shared with specific
            partners.
        *   [`chromeos-overlay/`][chromeos-overlay]: Chrome OS settings &
            packages (not Chromium OS) not shared with partners.
        *   [`chromeos-partner-overlay/`][chromeos-partner-overlay]: Chrome OS
            settings & packages shared with all partners.
        *   `overlay-*-private/`: Internal boards shared with specific partners.
        *   `project-*-private/`: Internal projects shared with specific
            partners.
    *   [`repohooks/`][repohooks]: Hooks used by the `repo` tool.  Most notably,
        these are the test run at `repo upload` time to verify CLs.
    *   [`scripts/`][crosutils]: Legacy Chromium OS build scripts.  Being moved
        to chromite and eventually dropped.  No new code should be added here.
    *   `third_party/`: Separate git repos for third party (i.e. not Google or
        Chromium OS authored) projects, or projects that are intended to be used
        beyond CrOS.  These are often forks of upstream projects.
        *   [`chromiumos-overlay/`][chromiumos-overlay]: Custom ebuilds for just
            Chromium OS.  Also where forked Gentoo ebuilds are kept (instead of
            `portage-stable/`).
        *   [`eclass-overlay/`][eclass-overlay]: Overlay for custom eclasses
            that are used by all other overlays (board, project, etc...).
        *   [`kernel/`][kernel]: The Linux kernel.  Separate checkouts are used
            for each version we track.
        *   [`portage-stable/`][portage-stable]: Unmodified ebuilds copied from
            Gentoo.  If you want to make custom changes, packages are moved to
            [chromiumos-overlay]/ instead.  See the [Package Upgrade Process]
            for details on updating these.
        *   [`portage_tool/`][portage_tool]: Fork of Gentoo's portage project
            (i.e. `emerge` and `ebuild`).
        *   `$PROJECT/`: Each project gets its own directory.
    *   `weave/`: Mirrors of repos from the Weave project.

### Generated directories

These paths are all created on the fly and do not have any relationship to git
repos on the servers.
You should not normally need to manage these directly or clean them up.
In fact, you should avoid trying to do so to avoid breaking the build system.
If you're running out of space, use the `cros clean` command to help trim the
various caches and build directories safely.

*   `.cache/`: Various files cached by the build tools.  Designed to be shared
    between different CrOS checkouts and branch versions.
    *   `common/`: Various artifacts cached by [chromite] tools.
    *   `distfiles/`: Artifacts used while running emerge.
        *   `ccache/`: Compiler cache used by the toolchain to save objects.
        *   `host/`: Tarballs used by emerge in the SDK itself.
        *   `target/`: Tarballs used when emerging board packages.
    *   `sdks/`: Copies of the initial SDK tarball (for `chroot/`).
*   `.repo/`: Internal state used by [repo] to manage the checkout.  You usually
    don't have to mess around with paths under here, so this is more of an
    informational section.
    *   [`local_manifests/`][Local manifests]: Local manifests to add custom
        repos to the local checkout.
    *   `manifests/`: Local checkout of the manifest repo using the
        `--manifest-branch` setting from `repo init`.  This is used during
        all repo operations like `repo sync` and `repo upload`.
    *   `manifests.git/`: Local bare clone of the remote manifest repo.
        This is the `--manifest-url` setting used during `repo init`.
    *   `manifest.xml`: Symlink to the manifest in the `manifests/` directory.
        This is the `--manifest-name` setting used during `repo init`.
    *   `project-objects/`: Used by `repo` to hold git objects for all the
        checked out repos.  The `.git/` subdir will often symlink to paths
        under here.
    *   `projects/`: Same as `project-objects/`, but for non-objects git files.
    *   `repo/`: Local checkout of the [repo] tool itself.  This is the code
        behind every `repo` command.  This is the `--repo-url` setting used
        during `repo init`.
*   [`chroot/`][chroot]: The full chroot used by `cros_sdk` where boards are
    built.  See the [filesystem layout] document for more details.
    Use `cros_sdk --delete` to safely remove this directory.
*   `chroot.img`: A disk image for the `chroot/` directory.  Provides hermetic
    guarantees about the filesystem, and helps speed up things like snapshots.
    Use `cros_sdk --delete` to safely remove these paths.
*   `src/`:
    *   `build/`: All final artifacts & images are written here (e.g.
        `build_image` outputs).
        *   `images/$BOARD/`: Every board goes into a unique output directory.
            *   `latest/`: A symlink that is automatically updated to point to
                the latest build for this board.
            *   `$VERSION/`: Each version gets a unique directory.

## Git Server Layout

This is the layout as organized on the Git server.
This isn't comprehensive, but should provide enough guidance here.

Note that the layout (and even specific names) of repos on the server do not
need to exactly match the layout of the local source checkout.
The manifest used by [repo] allows for the paths and names to be completely
independent.
Often times they are pretty similar since we try to keep the naming policies
coherent as it's less confusing that way.

### Public Chromium GoB

This is the public https://chromium.googlesource.com/ site.

The majority of repos should live under either `platform/` or `third_party/`.
It's very uncommon to create projects outside of those paths.
If you want to create a new project somewhere else, please check with the
build/infra team first using [chromium-os-dev@chromium.org][Contact].

*   `aosp/`: Mirrors of Android projects.  Should use the same layout as on the
    [AOSP GoB] host.
*   `apps/`: Various Chromium OS applications.  Usually these are "Chrome Apps"
    written in HTML/JavaScript/CSS.
*   `chromium/`: Chromium (the browser) related projects.  These are managed
    entirely by the browser team.
*   `chromiumos/`: Chromium OS related projects.  Most Chrome OS people will
    only ever work on projects under these paths.
    *   [`chromite/`][chromite]: All of CrOS's build tools live here.
    *   `containers/`: Projects for the [VM/containers] project.  Mainly for
        projects that don't integrate directly into CrOS builds, otherwise the
        projects are stored under `platform2/vm_tools/`.
        *   `$PROJECT/`: Each project gets its own repo.
    *   [`docs/`][docs]: General project documentation repo.
    *   `infra/`: Projects for various CrOS infra systems.
    *   [`manifest/`][manifest]: The manifest use by `repo init` and `repo sync`
        to get a public Chromium OS checkout.
    *   `overlays/`: Various ebuild overlays used to build Chromium OS.  These
        are where all the packages and their compile/install logic live.
        *   [`board-overlays/`][board-overlays]: All public board overlays.
        *   [`chromiumos-overlay/`][chromiumos-overlay]: Custom ebuilds for just
            Chromium OS.  Also where forked Gentoo ebuilds are kept (instead of
            [portage-stable]/).
        *   [`eclass-overlay/`][eclass-overlay]: Overlay for custom eclasses
            that are used by all other overlays (board, project, etc...).
        *   [`portage-stable/`][portage-stable]: Unmodified ebuilds from Gentoo.
            When making custom changes, packages are moved to
            [chromiumos-overlay]/ instead.  See the [Package Upgrade Process]
            for details on updating these.
    *   `platform/`: Projects written by the Chromium OS project, or some Google
        authored projects.  Many of these have since been merged into
        [platform2]/.
        *   `$PROJECT/`: Each project gets its own repo.
    *   [`platform2/`][platform2]: Combined git repo for Chromium OS system
        projects.  Used to help share code, libraries, build, and test logic.
    *   [`repohooks/`][repohooks]: Hooks used by the `repo` tool.  Most notably,
        these are the test run at `repo upload` time to verify CLs.
    *   `third_party/`: Projects that were not written by Chromium OS project,
        or projects that are intended to be used beyond CrOS.
        *   `$PROJECT/`: Each project gets its own repo.
*   `external/`: Mirrors of various external projects.
    *   `$HOST/`: Domain name for the hosting site.  e.g. `github.com`.
        Subpaths here tend to reflect the structure of the hosting site.

### Internal Chrome GoB

This is the internal https://chrome-internal.googlesource.com/ site.

The majority of repos should live under `overlays/`, `platform/`, or
`third_party/`.
It's very uncommon to create projects outside of those paths.
If you want to create a new project somewhere else, please check with the
build/infra team first using [chromeos-chatty-eng@google.com][Contact].

*   `android/`: Mirrors of internal Android projects.  Should use the same
    layout as on the [AOSP GoB] host.
*   `chrome/`: Chrome (the browser) related projects.  These are managed
    entirely by the browser team.
*   `chromeos/`: Chrome OS related projects.  Most Chrome OS people will only
    ever work on projects under these paths.
    *   `overlays/`: Separate git repos for internal partner repos to simplify
        sharing with specific partners.
        *   `baseboard-*-private/`: Internal base boards shared with specific
            partners.
        *   `chipset-*-private/`: Internal chipsets shared with specific
            partners.
        *   [`chromeos-overlay/`][chromeos-overlay]: Chrome OS settings &
            packages (not Chromium OS) not shared with partners.
        *   [`chromeos-partner-overlay/`][chromeos-partner-overlay]: Chrome OS
            settings & packages shared with all partners.
        *   `overlay-*-private/`: Internal boards shared with specific partners.
        *   `project-*-private/`: Internal projects shared with specific
            partners.
    *   `platform/`: Internal projects written by the Chrome OS project, or some
        Google-authored projects.  Most projects should be open source though and
        live in the [Chromium GoB] instead.
    *   `third_party/`: Internal projects that were not written by Chromium OS.
        Often used for early work before being made public, or to hold some code
        from partners.
    *   `vendor/`: Various partner-specific projects like bootloaders or firmware.
*   `external/`: Mirrors of other projects.
    *   `gob/`: Mirrors of other GoB instances.  Uses a $GOB_NAME subdir followed
        by the path as it exists on the remote GoB server.

## Branch naming

We have a few conventions when it comes to branch names in our repos.
Not all repos follow all these rules, but moving forward new repos should.

When cloning/syncing git repos, only `heads/` and `tags/` normally get synced.
Any other refs stay on the server and are accessed directly.

Note: All the paths here assume a `refs/` prefix on them.
So when using `git push`, make sure to use `refs/heads/xxx` and not just `xxx`
to refer to the remote ref.

*   `tags/`: CrOS doesn't use git tags normally.  Repos that do tend to do so
    for their own arbitrary usage.  If they are used, they should follow the
    [SemVerTag] format (e.g. `v1.2.3`).
*   `heads/`: The majority of CrOS development happens under these branches.
    *   `factory-xxx`: Every device gets a unique branch for factory purposes.
        Factory developers tend to be the only ones who work on these.
        Typically it uses `<device>-<OS major version>.B` names.
    *   `firmware-xxx`: Every device gets a unique branch for maintaining a
        stable firmware release.  Firmware developers tend to be the only ones
        who work on these.  Typically it uses `<device>-<OS major version>.B`
        names.
    *   `master`: The normal ToT branch where current development happens.
    *   `release-xxx`: Every release gets a unique branch.  When developers
        need to cherry pick back changes to releases to fix bugs, these are
        the branches they work on.  Typically it uses
        `R<milestone>-<OS major version>.B` names.
    *   `stabilize-xxx`: Temporary branches used for testing new releases.
        Developers pretty much never work with these and they're managed by
        TPMs.  Typically it uses `<OS major version>.B` names.
*   `sandbox/`: Arbitrary developer scratch space.  See the [sandbox]
    documentation for more details.

### Automatic m/ repo refs

Locally, repo provides some pseudo refs to help developers.
It uses the `m/xxx` style where `xxx` is the branch name used when running
`repo init`.
It often matches the actual git branch name used in the git repo, but there is
no such requirement.

For example, when getting a repo checkout of the master branch (i.e. after
running `repo init -b master`), every git repo will have a pseudo `m/master`
that points to the branch associated with that project in the [manifest].
In chromite, `m/master` will point to `heads/master`, but in bluez, `m/master`
will point to `heads/chromeos`.

In another example, when getting a repo checkout of the R70 release branch (i.e.
after running `repo init -b release-R70-11021.B`), every git repo will have a
pseudo `m/release-R70-11021.B` that points to the branch associated with that
project in the [manifest].
In chromite, `m/release-R70-11021.B` will point to `heads/release-R70-11021.B`,
but in kernel/v4.14, `m/release-R70-11021.B-chromeos-4.14`.

### Other refs

There are a few additional paths that you might come across, although they
aren't commonly used, or at least directly.

*   `changes/`: Read-only paths used by Gerrit to expose uploaded CLs and their
    various patchsets.  See the [Gerrit refs/for] docs for more details.
*   `for/xxx`: All paths under `for/` are a Gerrit feature for uploading commits
    for Gerrit review in the `xxx` branch.  See the [Gerrit refs/for] docs for
    more details.
*   `infra/config`: Branch used by [LUCI] for configuring that service.
*   `meta/config`: Branch for storing per-repo Gerrit settings & ACLs.  Usually
    people use the [Admin UI] in each GoB to manage these settings indirectly,
    but users can manually check this out and upload CLs by hand for review.
    See the [Gerrit project config] docs for more details.

### Local heads/ namespaces

You might see that, depending on the repo, the remote branches look like
`remotes/cros/xxx` or `remotes/cros-internal/xxx` or `remotes/aosp/xxx`.
The `cros` and such names come from the `remote` name used in the [manifest]
for each `project` element.

For example, the [manifest] has:
```xml
<manifest>
  <remote  name="cros"
           fetch="https://chromium.googlesource.com"
           review="https://chromium-review.googlesource.com" />

  <default revision="refs/heads/master"
           remote="cros" sync-j="8" />

  <project path="chromite" name="chromiumos/chromite" ?>
  <project path="src/aosp/external/minijail"
           name="platform/external/minijail"
           remote="aosp" />
</manifest>
```

The `default` element sets `remote` to `cros`, so that's why it shows up in
the chromite (whose `project` omits `remote`) repo as `remotes/cros/xxx`.

The minijail project has an explicit `remote=aosp`, so that's why it shows up
as `remotes/aosp/xxx` in the local checkout.

## FAQ

### How do I create a new repo on the server?

Follow the steps in this guide:
http://dev.chromium.org/chromium-os/how-tos-and-troubleshooting/git-server-side-information

### How do I add a repo to the manifest?

If the repo is public (i.e. exists on the [Chromium GoB]), then update the
[full.xml] file in the public [manifest] repo and the [external_full.xml]
file in the internal [manifest-internal] repo.
Both files in both repos must be updated together, so make sure to use a
[Cq-Depend] to land them atomically.

If the repo is private (i.e. exists on the [Chrome GoB]), then update the
[internal_full.xml] file in the internal [manifest-internal] repo.

You can follow the examples in the files already.

### How do I change branches for an existing repo?

Set the `revision` attribute in the relevant `<project .../>` element in the
manifest files.

See the previous question about adding a repo for details on which repos you
will need to update.

### How do I test a manifest change?

The [manifest] and [manifest-internal] repos in the checkout are purely for
developer convenience in making & uploading changes.
They are not used for anything else.

When you run `repo sync` in your checkout, that only looks at the manifest under
the `.repo/manifests/` directory.
That is an independent checkout of the manifest that was specified originally
when running `repo init`.

So the flow is usually:

*   Write the CLs in [manifest] and [manifest-internal].
*   Extract the change from the relevant repo.
    *   Use `git format-patch -1` to create a patch you can apply.
    *   If you're using a private checkout, then extract it from
        [manifest-internal].
    *   If you're using a public checkout, then extract it from [manifest].
*   Apply the change to the local directory.
    *   Run `cd .repo/manifests/`.
    *   Use `git am` to apply the patch from above.
*   Run `repo sync` to use the modified manifest.
*   Do whatever testing/validation as makes sense.

At this point, your checkout is in a modified state.
That means any CLs other people are landing to the manifest will be pulled in
when you run `repo sync`.
If those changes cause conflicts, your checkout won't sync properly.
Thus your final step should be to remove your changes.

*   Reset the branch back to the remote state.
    This will throw away all local changes!
    *   You can usually run the following commands:
        ```
        # This might say "No rebase in progress" which is OK.
        git rebase --abort
        git reset --hard HEAD^
        git checkout -f
        ```
    *   If those "simple" commands didn't work, try this more complicated one:
        ```
        git reset --hard "remotes/$(git config --get branch.default.remote)/$(basename "$(git config --get branch.default.merge)")"
        ```
*   If those commands don't work, you basically want to figure out what the
    remote branch is currently at and reset to it.

If your manifest CL hasn't landed yet, then when you run `repo sync`, the
changes you made will be lost.
So if you were adding a repo, it will be deleted again from the checkout.
If you were removing a repo, it will be added again to the checkout.

### Where do I put ebuilds only for Googlers and internal Chrome OS builds?

The [chromeos-overlay] holds all packages & settings for this.
It is not made public or shared with any partners, so this is for restricted
packages and features only.

### Where do I put ebuilds to share with partners?

The [chromeos-partner-overlay] holds all packages & settings for this.
It is not made public, but it is shared among *all* partners.

If you want to share a package with specific partners for a specific board,
then put it in the respective `src/private-overlays/xxx-private/` overlay.

### Can I put ebuilds for private changes into public overlays?

No.
All ebuilds in public overlays must be usable by the public.
Even if the ebuild itself contains no secret details (e.g. it just installs a
binary from a tarball), if the tarball is not publicly available, then we do
not put the ebuild in the public overlays.

Use one of the respective private overlays instead.
See the previous questions in this FAQ for more details.


[Admin UI]: https://chromium-review.googlesource.com/admin/repos
[AOSP GoB]: https://android.googlesource.com/
[Chrome GoB]: https://chrome-internal.googlesource.com/
[chromeos-overlay]: https://chrome-internal.googlesource.com/chromeos/overlays/chromeos-overlay/
[chromeos-partner-overlay]: https://chrome-internal.googlesource.com/chromeos/overlays/chromeos-partner-overlay/
[chromite]: https://chromium.googlesource.com/chromiumos/chromite/
[Chromium GoB]: https://chromium.googlesource.com/
[chromiumos-overlay]: https://chromium.googlesource.com/chromiumos/overlays/chromiumos-overlay/
[chroot]: filesystem_layout.md#SDK
[Cq-Depend]: contributing.md#CQ-DEPEND
[Contact]: contact.md
[contrib]: https://chromium.googlesource.com/chromiumos/platform/dev-util/+/HEAD/contrib/
[cros-signing]: https://chrome-internal.googlesource.com/chromeos/cros-signing/
[crostools]: https://chrome-internal.googlesource.com/chromeos/crostools/
[crosutils]: https://chromium.googlesource.com/chromiumos/platform/crosutils/
[dev-util]: https://chromium.googlesource.com/chromiumos/platform/dev-util/
[docs-internal]: https://chrome-internal.googlesource.com/chromeos/docs/
[docs]: https://chromium.googlesource.com/chromiumos/docs/
[eclass-overlay]: https://chromium.googlesource.com/chromiumos/overlays/eclass-overlay/
[external_full.xml]: https://chrome-internal.googlesource.com/chromeos/manifest-internal/+/HEAD/external_full.xml
[filesystem layout]: filesystem_layout.md
[full.xml]: https://chromium.googlesource.com/chromiumos/manifest/+/HEAD/full.xml
[Gerrit project config]: https://www.gerritcodereview.com/config-project-config.html
[Gerrit refs/for]: https://www.gerritcodereview.com/concept-refs-for-namespace.html
[internal_full.xml]: https://chrome-internal.googlesource.com/chromeos/manifest-internal/+/HEAD/internal_full.xml
[kernel]: https://chromium.googlesource.com/chromiumos/third_party/kernel/
[Local manifests]: https://gerrit.googlesource.com/git-repo/+/master/docs/manifest-format.md#Local-Manifests
[LUCI]: https://chromium.googlesource.com/infra/luci/luci-py/
[manifest]: https://chromium.googlesource.com/chromiumos/manifest/
[manifest-internal]: https://chrome-internal.googlesource.com/chromeos/manifest-internal/
[board-overlays]: https://chromium.googlesource.com/chromiumos/overlays/board-overlays/
[Package Upgrade Process]: portage/package_upgrade_process.md
[platform2]: https://chromium.googlesource.com/chromiumos/platform2/
[portage-stable]: https://chromium.googlesource.com/chromiumos/overlays/portage-stable/
[portage_tool]: https://chromium.googlesource.com/chromiumos/third_party/portage_tool/
[repo]: https://gerrit.googlesource.com/git-repo
[repohooks]: https://chromium.googlesource.com/chromiumos/repohooks/
[sandbox]: contributing.md#sandbox
[SemVerTag]: https://semver.org/spec/v1.0.0.html#tagging-specification-semvertag
[vboot_reference]: https://chromium.googlesource.com/chromiumos/platform/vboot_reference/
[VM/containers]: containers_and_vms.md
