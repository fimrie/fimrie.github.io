# Fergus Imrie's Website

Personal website built with Jekyll, based on a template by Martin Saveski.

## Local setup

This repo uses Jekyll 4.4 with Ruby 3.3 (see `.ruby-version`) and Bundler.
Use a current Ruby 3.3 patch release. The committed `Gemfile.lock` is used both
locally and in GitHub Actions.

On macOS, use Homebrew's versioned Ruby:

```bash
brew install ruby@3.3
export PATH="$(brew --prefix ruby@3.3)/bin:$PATH"
gem install bundler -v 4.0.10 --no-document
```

The preview command below selects this Ruby automatically, even when an older
Ruby is on your shell's `PATH`. It also works with an already active Ruby 3.3
from another version manager when Homebrew's Ruby is not installed.

If you prefer conda, create an environment (or use `conda install`
with the same packages to update an existing `fimrie-site` environment):

```bash
conda create -n fimrie-site -c conda-forge ruby=3.3 compilers pkg-config make openssl zlib libffi -y
conda activate fimrie-site
gem install bundler -v 4.0.10
```

Conda's Ruby package can lag official security releases. Check `ruby --version`
against the [current Ruby releases](https://www.ruby-lang.org/en/downloads/),
and use a Ruby version manager if a current patch is unavailable from conda.
CI selects the latest Ruby 3.3 patch available to its pinned `ruby/setup-ruby`
action; Dependabot maintains that action reference.

Install project dependencies:

```bash
bundle config set --local path vendor/bundle
bundle install
```

## Run locally

Build the site once:

```bash
bundle exec jekyll build
```

Start the local preview from the project directory:

```bash
./bin/preview
```

Open <http://127.0.0.1:4000/>. Jekyll rebuilds when you save changes and
LiveReload refreshes the browser. Stop it with Ctrl-C. Extra Jekyll options can
be passed to the command, for example `./bin/preview --port 4001`.

## Updating the site

Most content and layout changes live in:

- `_data/`
- `index.html`
- `_layouts/`
- `libs/custom/`

Generated files in `_site/` should not be committed.

Publication entries in `_data/publications.yaml` use `publication_type` to control
category tabs. Allowed values are:

- `preprint`
- `journal`
- `ml_conference`
- `book_chapter`

Publication tabs open Highlights by default. Category links use their panel IDs,
for example `/#papers-journals` or `/#papers-preprints`. Clicking a tab adds a
browser history entry; arrow-key navigation updates the current entry. Without
the tab script, the full publication list remains available and the tab controls
are hidden.

Project and experience data are retained as template examples. The project
markup in `index.html` is inside a Liquid comment so Jekyll does not render it.
The timeline stylesheet is also retained; add its stylesheet link to a layout
when a timeline is actually used. The example project paths need updating before
publishing, and its old tabs need adapting to the current accessible tab markup.

After building, validate the content and generated local references:

```bash
python3 bin/check-site.py _site
```

The checker uses Ruby for YAML and Python 3.9+ standard-library HTML parsing.
It checks publication/news fields, category and flag values, URL syntax, local
targets and fragments, duplicate IDs, and tab/panel relationships. It makes no
network requests and does not validate unpublished template project links.

## Analytics

Both layouts use `_includes/google_tag_manager.html`; the container ID is in
`_config.yml` as `google_tag_manager_id`. Analytics is included only in production
builds, and the script loads the container only on the hostname configured in
`site.url`. Ordinary local previews do not include the analytics snippets.

GA4 measurement destinations belong to the Tag Manager configuration, rather
than a second analytics snippet in the website code. The confirmed container is
`GTM-T4H46C4`, sending to the GA4 stream `G-G0KYDY7NX0`. Before changing the
container or destination, confirm that the container belongs to your account
and matches the intended GA4 web stream. In Google Analytics, select the
property, then Admin → Data streams → the website stream to find its `G-`
measurement ID. In Tag Manager, select the website container and check its
Google tag and trigger. Use one Google tag for the intended stream and one
page-load trigger; do not also install a separate direct `gtag.js` snippet.

For this single-page profile, publication filters should not count as new page
visits. In the GA4 web stream, open Enhanced measurement → Page views → advanced
settings and disable “Page changes based on browser history events”. Retain page
views on page load. Check any custom Tag Manager History Change triggers too.
This setting was saved and verified for the confirmed stream on 7 October 2026.
Use Tag Assistant and GA4 Realtime/DebugView to confirm one `page_view` per page
load, with no extra page views when selecting publication categories.

If you only use GA4 and do not own a Tag Manager container, a direct Google tag
is also supported; replace the container integration with one shared Google tag
for the confirmed stream instead of adding it alongside Tag Manager.

## Deployment

GitHub Pages continues to host the site at <https://fimrie.github.io/>.
`.github/workflows/site.yml` builds with Bundler and publishes the generated
`_site` artifact. The build uses the gems in this repository's lockfile, rather
than the default Pages builder's `github-pages` bundle.

| Trigger | Checks | Publishes |
| --- | --- | --- |
| Pull request targeting `master` | Site build, content checks, Ruby audit, dependency review | No |
| Push to `master` | Site build, content checks, Ruby audit | After checks pass |
| Manual run on `master` | Site build, content checks, Ruby audit | After checks pass |
| Manual run on another branch | Site build, content checks, Ruby audit | No |
| Monday at 08:23 UTC | Ruby audit with current advisories | No |

Build runs upload a Pages artifact that can be downloaded from the Actions run
for inspection, including on pull requests. Only the deployment job has Pages
write and identity-token permissions; pull requests use read-only repository
permissions. Actions are pinned to commit SHAs and maintained by Dependabot.

### Repository protection

Pages uses GitHub Actions, and the `github-pages` environment permits deployments
only from `master`. The active branch ruleset requires pull requests and passing
**Build site**, **Audit Ruby dependencies**, and **Review dependency changes**
checks. Branches must be up to date before merging; direct pushes, force pushes,
and deleting `master` are blocked.

After merging an update, confirm the deployment succeeds and check the live
homepage, publication tabs, links, `/404.html`, and `/feed.xml`. Review major
renderer updates separately and inspect their generated site before merging.
These protections are configured in GitHub settings, not by these files.

The build uses Jekyll 4.4 and Minima 2.5. The unused Pages plugins and their
`rubyzip` dependency are removed. Jekyll 4 requires `json`; its locked version
includes the security fix and is checked by the Ruby audit.

## Dependency updates

Dependabot security updates are enabled in the repository settings and can open
fix pull requests when a compatible patched version exists.
`.github/dependabot.yml` also checks Ruby gems (including indirect dependencies)
and GitHub Actions every Monday at 09:00 Europe/London. Routine minor and patch
updates are grouped per ecosystem; direct major updates remain separate.
Review the whole lockfile diff: resolving an update can also change the major
version of an indirect dependency. Security
updates are not delayed until the weekly version-update check. Updates are
reviewed and merged manually.

To update a specific gem without unnecessarily changing other dependencies:

```bash
bundle update GEM_NAME --conservative
bundle exec bundle-audit check --update
JEKYLL_ENV=production bundle exec jekyll build --trace
```

Commit both `Gemfile` (if changed) and `Gemfile.lock`. Keep the Linux platform in
the lockfile so that CI can install it without re-resolving dependencies.
Changes to the Ruby release series in `.ruby-version` and `Gemfile` need manual
review; Dependabot does not upgrade the Ruby interpreter. Ruby 3.3 is in security
maintenance with an expected end of support on 31 March 2027; plan a runtime
upgrade before then.

The audit checks the full locked Ruby dependency set and fails on any known
vulnerability. Dependency review additionally checks dependencies introduced by
a pull request. A failed audit prevents a new deployment; the already published
site continues to be served. Weekly audit failures appear in GitHub Actions;
enable workflow-failure and Dependabot security notifications in your account.

Secret scanning and push protection are enabled in repository security settings.
CodeQL has not been configured. These checks do not replace maintenance of
manually vendored assets under `libs/external/`.

The site does not use jQuery. Publication tabs use native browser APIs in
`libs/custom/my_js.js`; the old jQuery bundle and unused Skeleton Tabs JavaScript
have been removed. Keep the Skeleton Tabs CSS, which still styles the tabs.
