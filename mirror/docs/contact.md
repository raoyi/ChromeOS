# Chromium OS Contact

The Chromium OS project has many communication channels.
Finding out which one makes sense for your question/issue can be overwhelming.

We strongly discourage e-mailing or messaging specific developers:

*   Direct contact does not scale (especially when a developer is contacted by
    many different groups).
*   Most questions tend to be generic and either covered in existing
    documentation or answerable by the wider team.
*   Answers to questions not covered by existing documentation can then be used
    for reference with others via mailing list archive links (private threads
    are never archived).
*   Questions without an existing answer often solicit input from the team.

[TOC]

## Project announcements

If you're a developer who just joined the project, you should make sure to
subscribe to at least the [chromium-os-dev] group.
Important project discussions & PSA's are sent here.

## Public discussion groups

While anyone may join these groups and browse their archives, due to spam
problems, people who join are initially & automatically moderated.
Once their accounts & posts are verified to not be spam related, they are
approved to post freely.
However this initial moderation step might take some time (especially on
nights & weekends), so please be patient when first joining.

### User support

*   [Google Chrome Help Center]: Official documentation for Chrome and Chrome
    OS.  Lots of articles for common user questions.
*   [chromebook-central]: All users should start with the official
    [chromebook-central] product forums.  The number of other users that post
    is quite staggering, and there are many knowledgeable and helpful people.
    Any question related to Chrome OS, Chromebooks, etc... is OK here.
*   [chromium-os-discuss]: Group for non-development related questions.  There
    aren't as many people in this group, and responses can take longer.  This
    group was created long before [chromebook-central] which is why it still
    exists.

### Developer support

*   [chromium-dev]: For all Chromium browser development related questions.
    Any UI you see (including the login screen) is browser code.
*   [chromium-os-dev]: For all OS development related questions.  Browser
    questions should use [chromium-dev] instead.
*   [chromium-extensions]: For all Chrome Extension & Chrome App related
    questions.  The API layers are all in the browser, so this is a better
    group to find help than asking the OS developers (who don't write HTML
    or JS at all).
*   [chromium-os-bugs]: A read-only high-volume list of all Chromium bugs.
*   [chromium-os-checkins]: A read-only high-volume list for all commits that
    are made to all Chromium OS repositories.
*   [chromium-os-reviews]: A read-only high-volume list of all Chromium OS
    code reviews.

For more specific developer groups, see this page:
https://dev.chromium.org/developers/technical-discussion-groups

## Issue tracker (bugs & features)

Please see the [Reporting Chrome OS bugs] document for more details.
That covers all types of reports: public, private, security, etc...

## Private discussion groups

Keep in mind that the vast majority of questions about the project can be posted
to our public discussion groups.
The private groups are meant to be used for unreleased projects, sensitive
topics, and partner-specific only.
We strongly encourage people to try and stick to the public groups whenever
possible.

*   [chrome-discuss]: Internal mailing list for general Chrome (browser)
    discussion.  More user rather than engineering focused.  Sees many questions
    and bug reports that haven't been formally filed.  Chrome OS related topics
    should be in the next group.
*   [chromeos-discuss]: Internal mailing list for general Chrome OS discussion.
    More user rather than engineering focused.  Sees many questions/bug reports
    that haven't been formally filed.  Chrome (browser) specified topics should
    be in the previous group.
*   [chromeos-chatty-eng]: Internal mailing list for general engineering
    questions. While it is a high-volume "chatty" group, the focus is on Chrome
    OS. Browser topics would be better served on browser-specific groups.
*   [chromeos-chatty-kernel]: Internal mailing list for kernel questions.
*   [chromeos-chatty-firmware]: Internal mailing list for firmware questions.


## FAQ

### I need help with Crouton.

Please send all questions related to [Crouton] to the [Crouton] project.

### I need help with my Chrome Extension or Chrome App or Kiosk App.

Please post all questions to [chromium-extensions].
Very few people who work on Chrome OS have any familiarity with writing Chrome
Extensions code, or even JavaScript.

### I need help installing/running Ubuntu/Debian/\<some distro\>.

We don't generally support users trying to run other distros instead of CrOS.
Please contact those projects directly for support instead.

### I need help with Crostini.

Check out the [VM/containers] document for more details.

### I want to report a security bug.

Check out the [Reporting Chrome OS bugs] document.
It has a section specifically about filing security sensitive bugs.


[chromebook-central]: https://productforums.google.com/d/forum/chromebook-central
[chrome-discuss]: http://g/chrome-discuss
[chromeos-chatty-eng]: http://g/chromeos-chatty-eng
[chromeos-chatty-kernel]: http://g/chromeos-chatty-kernel
[chromeos-chatty-firmware]: http://g/chromeos-chatty-firmware
[chromeos-discuss]: http://g/chromeos-discuss
[chromium-dev]: https://groups.google.com/a/chromium.org/group/chromium-dev
[chromium-extensions]: https://groups.google.com/a/chromium.org/group/chromium-extensions
[chromium-os-bugs]: https://groups.google.com/a/chromium.org/group/chromium-os-bugs
[chromium-os-checkins]: https://groups.google.com/a/chromium.org/group/chromium-os-checkins
[chromium-os-dev]: https://groups.google.com/a/chromium.org/group/chromium-os-dev
[chromium-os-discuss]: https://groups.google.com/a/chromium.org/group/chromium-os-discuss
[chromium-os-reviews]: https://groups.google.com/a/chromium.org/group/chromium-os-reviews
[Crouton]: https://github.com/dnschneid/crouton
[Google Chrome Help Center]: https://www.google.com/support/chrome/
[Report a problem or send feedback]: https://support.google.com/chromebook/answer/2982029
[Reporting a Crash Bug]: https://dev.chromium.org/for-testers/bug-reporting-guidelines/reporting-crash-bug
[Reporting Chrome OS bugs]: reporting_bugs.md
[VM/containers]: containers_and_vms.md
