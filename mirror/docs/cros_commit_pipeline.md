# Life of a Chrome OS commit

This document provides a brief overview of how Chrome OS changes get committed
and tested.

For details on **Chrome** changes, see
[Life of a Chrome commit on Chrome OS](chrome_commit_pipeline.md).

## Create a Chrome OS change

### Make and upload changes

See the [developer guide] for how to create a branch and make changes.

Once a change is completed and tested locally, upload it to [chromium-review]:

```repo upload --current-branch .```

### Have your change reviewed

Use [chromium-review] to review your change and prepare it for the commit queue.

See the [developer guide] for details.

## The Chrome OS commit pipeline

### The Pre-Commit Queue

When a change is marked 'Trybot-Ready' or when it has been approved, it will be
submitted to the **[precommit queue]** which runs on a handful of buildbots
depending on the patch.

### The Commit Queue

When a change is marked verified, approved and marked Commit-Queue ready, it
will be sent to the commit queue.

This takes the current set of approved changes, applies them to the tip-of-tree,
and runs the entire suite of **[paladin]** builders (currently 57).

If the [paladin] builder succeeds then the changes will be committed and the
LKGM version of Chrome OS will be updated for devs and builders (e.g. the
[PFQ]).

Otherwise it will need to be re-submitted once the developer fixes the failure
or ensures that the failure was unrelated to their change.


### The Release (Canary) Builders

The ToT (canary) **[release]** builders are triggered automatically according
to a schedule, currently 3 times per day.

### The Chrome PFQ Builders

Once a commit lands, it will be picked up by the next **[PFQ]** build.

### Simple Chrome

[Simple Chrome] is intended to provide developers with a reasonably stable
Chrome OS environment for Chrome development.

It uses the results of the [Chrome LKGM] builder to identify a recent stable
canary build (generally the most recent).



[chromium-review]: https://chromium-review.googlesource.com
[developer guide]: developer_guide.md
[precommit queue]: https://luci-milo.appspot.com/buildbot/chromiumos.tryserver/pre_cq/
[paladin]: https://luci-milo.appspot.com/buildbot/chromeos/master-paladin/
[release]: https://uberchromegw.corp.google.com/i/chromeos/builders/master-release
[PFQ]: https://uberchromegw.corp.google.com/i/chromeos/builders/master-chromium-pfq
[Simple Chrome]: simple_chrome_workflow.md
[Chrome LKGM]: https://yaqs.googleplex.com/eng/q/5254238507106304
