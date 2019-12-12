## Acronyms

*   __3PL__: Third Party Labs.
*   __ACLs__: Access Control Lists.
*   __AFE__: Auto Test Front End.
*   __AP__: Application Processor.
*   __AU__: Auto Updates.
*   __AVL__: Approved Vendor List.
*   __BCS__: Binary Component Server.
*   __BFT__: Board Function Testing.
*   __BOM__: Bill of Materials.
*   __BSP__: Board support package.
*   __BVT__: Build & Verification Test.
*   __CL__: "Change List", a set of changes to files (akin to a
    single git commit).
*   __CPFE__: Chrome OS Partner Front End.
*   __CQ__: "Commit Queue", infrastructure to automatically
    check/build/test/verify/etc... CLs before merging into the tree.
    See also the [Chromium CQ] and [Chromium OS CQ] pages.
*   __CRX file__: [CRX files](https://developer.chrome.com/extensions/hosting)
    are ZIP files with a special header and the .crx file extension used to
    package Extensions and Apps.
*   __CTS__: Android Compatibility Test Suite.
*   __CWS__: ["Chrome Web Store"](https://chrome.google.com/webstore/), used to
    host & distribute Chrome extensions.
*   __DPTF__: (Intel's) Dynamic Platform & Thermal Framework.
*   __DUT__: "Device under test", used to refer to the system running
    Chromium [OS] and where tests are being executed.
*   __DVT__: Design Validation and Testing.
*   __EC__: Embedded Controller.
*   __EVT__: Engineering Validation and Testing.
*   __FAFT__: Fully Automated Firmware Test.
*   __FCS__: Final Customer Ship.
*   __FFT__: Final Function Testing.
*   __FSI__: Final Shipping Image.
*   __FSP__: Firmware Support Package.
*   __GBB__: Google Binary Block, a chunk of data stored in the NVRAM.
    Contains variables related to boot and identity.
*   __GERBER__: When ODM gives full set of files for board vendor
     to make appropriate holes etc.
*   __GRT__: Google Required Tests.
*   __GS__: "Google Storage", used to refer to Google Storage Buckets
    (e.g. gs:// URIs).
*   __GTM__: Go To Market.
*   __GTTF__: "Green Tree Task Force".
*   __GoB__: "Git-on-Borg" or "Gerrit-on-Borg" or "Gitiles-on-Borg"
    depending on the context. Used as an umbrella term to refer to
    the git related services on [chromium-review.googlesource.com]
    and [chromium.googlesource.com].
*   __HDCP__: High Bandwidth Digital Content Protection.
*   __HEDT__: High End Desktop.
*   __HW WP__: Hardware Write Protect. Physical mechanism to prevent
    disabling software write protect. Typically a signal grounded by
    a screw.
*   __IQC__: Incoming Quality Control.
*   __LGTM__: "Looks good to me", commonly used to approve a code
    review.
*   __LKCR__: "Last known compilable revision" - similar to LKGR
    (below), the last build that compiled.
*   __LKGM__: "Last known good manifest", the last manifest version
    that passed a minimal set of tests.
*   __LKGR__: "Last known good revision", the last build that passed
    all tests.
*   __LOEM__: Local OEM, process model that different OEMs share
    exactly same device (with no difference) that uses same firmware
    code and disk image. Only OEM is different.
*   __MLB__: Main Logic Board (aka motherboard).
*   __MVP__: "Minimum viable product", used to refer to the subset of
    a feature we want to ship initially.
*   __NRE__: Non-Recoverable Engineering cost.
*   __OGR__: OEM Gate Review Meetings.
*   __OOBE__: Out-of-box experience.
*   __OQC__: Ongoing Quality Control, check for sampling.
*   __PCB__: Printed Circuit Board.
*   __PCIe__: Peripheral Component Interconnect Express expansion bus
    standard for connecting devices.
*   __PCRs__: Platform Configuration Registers.
*   __PDG__: Platform Design Guide.
*   __PFQ__: "Preflight queue", used to describe bot configurations
    in the waterfall that run to test/gate changes before they're
    allowed into the tree for everyone to see.
*   __PS__: Patchset.  Never used to mean "patch series".
*   __PSR__: Panel Self Refresh (eDP).
*   __PTAL__: "Please take a[nother] look", often used when someone
    is happy with the state of a CL and want reviewers to look
    [again].
*   __PVT__: Production Validation and Testing.
*   __PoR__: Process of Record / Plan of Record.
*   __QAV__: Quality Assurance Verification.
*   __RSLGTM__: "Rubber stamp looks good to me", used when the
    reviewer is merely granting OWNERS approval without doing a
    proper code review.
*   __SGTM__: Secret Google Time Machine "Sounds good to me".
*   __SI__: Signal Integrity.
*   __SMT__: Surface-mount Technology.
*   __SW WP__: Software Write Protect.
*   __Servo__: a debugging board that connects via USB to a host
    machine and a device under test.
*   __TBR__: "To be reviewed". In
    [specific circumstances](https://chromium.googlesource.com/chromium/src/+/master/docs/code_reviews.md#TBR-To-Be-Reviewed)
    used to land code and have it reviewed later.
*   __TCPC__: Type C Port Controller.
*   __TPM__: ["Trusted Platform Module"](https://en.wikipedia.org/wiki/Trusted_Platform_Module),
    Tamper-resistant chip that the CPU can talk to. Securely stores
    keys and does cryptographic ops. We use this to encrypt the keys
    used to encrypt user files (to make passphrase recovery more
    difficult). See also TpmQuickRef.
*   __ToT__: "Tip of Tree" or "Top of Tree", as in the latest
    revision of the source tree.
*   __UFS__: Universal Flash Storage.
*   __UMA__: User Metrics Analysis.
*   __VPD__: Vital Product Data.
*   __WAI__: "Working As Intended", e.g. the behavior described is
    not a bug, but working as it is supposed to. This is not to say
    the intention cannot change (as a feature request), simply that
    it is not a bug.
*   __WIP__: "Work In Progress" - e.g. a patch that's not finished,
    but may be worth an early look.
*   __Zerg__: Process model for partner to build multiple new devices that only
    had slight variance from the reference board (touch/no touch, etc…). These
    devices share single firmware code and disk image.

## English Acronyms and Abbreviations

*   __AFAICT__: as far as I can tell
*   __AFAIK__: as far as I know
*   __e.g.__: (latin) for example
*   __FWIW__: for what it's worth
*   __IANAL__: I am not a lawyer
*   __IIRC__: if I recall/remember correctly
*   __IIUC__: if I understand correctly
*   __IMO__: in my opinion
*   __IMHO__: in my honest opinion
*   __IOW__: in other words
*   __i.e.__: (latin) in other words
*   __nit__: short for "nitpick"; refers to a trivial suggestion such as style
    issues
*   __PSA__: public service announcement
*   __WRT__: with respect to

## Chrome Concepts

*   __Chrome Component__: Components of chrome that can be updated
    independently from Chrome its self. Examples are PDF Viewer, Flash Plugin.
*   __Component App / Component Extension__: App or Extension built and
    shipped with Chrome. Examples are
    [Bookmark Manager](https://cs.chromium.org/search/?sq=package:chromium&type=cs&q=bookmark_manager),
    [File manager](https://cs.chromium.org/search/?sq=package:chromium&type=cs&q=file_manager).
*   __Default Apps__: Apps or Extensions that are shipped with Chrome as .CRX
    files and installed on first run.
*   [__Extension__](https://developer.chrome.com/extensions):  Third party
    developed code that modifies the browser.
*   [__Packaged App__](https://developer.chrome.com/apps/about_apps):  Packaged
    apps run outside of the browser, are built
    using web technologies and privileged APIs.
*   __Packaged App (old)__: Older packaged apps (pre 2013) still ran in tabs,
    but with offline packaged resources.
*   __Shared Modules__: Extensions or Apps that export resources accessible
    from other Ext/Apps. Dependencies are installed automatically.
*   __Aura__: The unified graphics compositor (docs).
*   __Ash__: The Aura shell (e.g. the Chromium OS look); see Aura for more
    info.

## Building

*   __buildbot__: A column in the build waterfall, or the slave (machine)
    connected to that column, or the
    [build waterfall infrastructure](https://dev.chromium.org/developers/testing/chromium-build-infrastructure/tour-of-the-chromium-buildbot)
    as a whole.
*   __clobber__: To delete your build output directory.
*   __component build__: A shared library / DLL build, not a static library
    build.
*   __land__: Landing a patch means to commit it.
*   __slave__: A machine connected to the buildbot master, running a sequence
    of build and test steps.
*   [__tryserver__](https://ci.chromium.org/p/chromium/builders/luci.chromium.try/linux_arm):
    A machine that runs a subset of all tests on all platforms.
*   __sheriff__: The person currently charged with watching over the build
    waterfall to make sure it stays green (not failing). There are usually two
    sheriffs at one time. The current sheriffs can be seen in the upper left
    corner of the waterfall page.
*   __symbolication__: The process of resolving stack addresses and backtraces
    to human readable source code methods/lines/etc...
*   __tree__: This means the source tree in subversion. Often used in the
    context of "the tree is closed" meaning commits are currently disallowed.
*   __try__: To try a patch means to submit it to the tryserver before
    committing.
*   [__waterfall__](https://ci.chromium.org/p/chromium/g/chromium/console):
    The page showing the status of all the buildbots.

## General

*   __Flakiness__: Intermittent test failures (including crashes and hangs),
    often caused by a poorly written test.
*   __Jank/Jankiness__: User-perceptible UI lag.
*   __Chumping__: Bypassing the CQ and committing your change directly to the
    tree. Generally frowned upon as it means automatic testing was bypassed
    before the CL hits developer systems.

## User Interface

*   __Bookmark bubble__: A "modal" bubble that appears when the user adds a
    bookmark allowing them to edit properties or cancel the addition.
*   __Download bar__: The bar that appears at the bottom of the browser during
    or after a file has been downloaded.
*   __Extensions bar__: Similar to the download bar, appears at the bottom of
    the screen when the user has installed an extension.
*   __Infobar__: The thing that drops down below asking if you want to save a
    password, did you mean to go to another URL, etc.
*   __NTB__: New Tab button (the button in the tab strip for creating a new
    tab)
*   __NTP or NNTP__: The New Tab Page, or the freshly rebuilt new tab
    functionality dubbed New New Tab Page.
*   __Status bubble__: The transient bubble at the bottom left that appears
    when you hover over a url or a site is loading.

## Video

*   __channels__: The number of audio channels present. We use "mono" to refer
    to 1 channel, "stereo" to refer to 2 channels, and "multichannel" to refer
    to 3+ channels.
*   __clicking__: Audio artifacts caused by bad/corrupted samples.
*   __corruption__: Visible video decoding artifacts. Usually a result of
    decoder error or seeking without fully flushing decoder state. Looks similar
    to this.
*   __FFmpeg__: The open source library Chromium uses for decoding audio and
    video files.
*   __sample__: A single uncompressed audio unit. Changes depending on the
    format but is typically a signed 16-bit integer.
*   __sample bits__: The number of bits per audio sample. Typical values are
    8, 16, 24 or 32.
*   __sample rate__: The number of audio samples per second. Typical values
    for compressed audio formats (AAC/MP3/Vorbis) are 44.1 kHz or 48 kHz.
*   __stuttering__: Short video or audio pauses. Makes the playback look/sound
    jerky, and is often caused by insufficient data or processor.
*   __sync__: Audio/video synchronization.

## Toolchain (compiler/debugger/linker/etc...)

*   __ASan, LSan, MSan, TSan__: [AddressSanitizer], [LeakSanitizer],
    [MemorySanitizer], and [ThreadSanitizer] bug detection tools used in
    Chromium testing. ASan detects addressability issues (buffer overflow, use
    after free etc), LSan detects memory leaks, MSan detects use of
    uninitialized memory and TSan detects data races.
*   __AFDO__: Automatic FDO; see FDO & PGO.
*   __FDO__: Feedback-Directed Optimization; see AFDO & PGO.
*   __fission__: A new system for speeding up processing of debug information
    when using GCC; see [this page](https://gcc.gnu.org/wiki/DebugFission) for
    more details.
*   __gold__: The GNU linker; a newer/faster open source linker written in C++
    and supporting threading.
*   __ICE__: Internal Compiler Error; something really bad happened and you
    should file a bug.
*   __PGO__: Profile Guided Optimization; see AFDO & FDO.

# Chromium OS

*   __board__: The name of the system you're building Chromium OS for; see the
    [official Chrome OS device list](https://www.chromium.org/chromium-os/developer-information-for-chrome-os-devices)
    for examples.
*   __devserver__: System for updating packages on a Chromium OS device
    without having to use a USB stick or doing a full reimage. See the
    [Dev Server page](https://chromium.googlesource.com/chromiumos/chromite/+/refs/heads/master/docs/devserver.md).
*   __powerwash__: Wiping of the stateful partition (system & all users) to
    get a device back into a pristine state. The TPM is not cleared, and Lockbox
    is kept intact (thus it is not the same as a factory reset). See the
    [Powerwash design doc](https://www.chromium.org/chromium-os/chromiumos-design-docs/powerwash).

[Chromium CQ]: https://chromium.googlesource.com/chromium/src/+/master/docs/infra/cq.md
[Chromium OS CQ]: https://www.chromium.org/developers/tree-sheriffs/sheriff-details-chromium-os/commit-queue-overview
[chromium-review.googlesource.com]: https://chromium-review.googlesource.com
[chromium.googlesource.com]: https://chromium.googlesource.com
[AddressSanitizer]: https://www.chromium.org/developers/testing/addresssanitizer
[LeakSanitizer]: https://www.chromium.org/developers/testing/leaksanitizer
[MemorySanitizer]: https://www.chromium.org/developers/testing/memorysanitizer
[ThreadSanitizer]: https://www.chromium.org/developers/testing/threadsanitizer-tsan-v2
