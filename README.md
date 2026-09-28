# Fergus Imrie's Website

Personal website built with Jekyll, based on a template by Martin Saveski.

## Local setup

This repo uses Jekyll 3.10 with Ruby 3.3 (see `.ruby-version`) and Bundler.
Use a current Ruby 3.3 patch release. The committed `Gemfile.lock` is used both
locally and in GitHub Actions.

If you manage Ruby with conda, create an environment (or use `conda install`
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
bundle install
```

## Run locally

Build the site once:

```bash
bundle exec jekyll build
```

Serve the site with:

```bash
bundle exec jekyll serve --livereload
```

Jekyll will print the local URL in the terminal.

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

## Deployment

GitHub Pages continues to host the site at <https://fimrie.github.io/>.
`.github/workflows/site.yml` builds with Bundler and publishes the generated
`_site` artifact. The build uses the gems in this repository's lockfile, rather
than the default Pages builder's `github-pages` bundle.

| Trigger | Checks | Publishes |
| --- | --- | --- |
| Pull request targeting `master` | Site build, Ruby audit, dependency review | No |
| Push to `master` | Site build and Ruby audit | After both pass |
| Manual run on `master` | Site build and Ruby audit | After both pass |
| Manual run on another branch | Site build and Ruby audit | No |
| Monday at 08:23 UTC | Ruby audit with current advisories | No |

Build runs upload a Pages artifact that can be downloaded from the Actions run
for inspection, including on pull requests. Only the deployment job has Pages
write and identity-token permissions; pull requests use read-only repository
permissions. Actions are pinned to commit SHAs and maintained by Dependabot.

### Activating the new workflow

1. Open a pull request with the workflow and dependency changes. Confirm that
   **Build site**, **Audit Ruby dependencies**, and **Review dependency changes**
   pass. Inspect the generated site artifact before changing the publishing source.
2. In repository **Settings → Pages → Build and deployment**, set **Source** to
   **GitHub Actions**. Configure the `github-pages` environment to allow
   deployments only from `master`.
3. Merge the pull request. The push to `master` builds, audits, and deploys the
   site. Check the deployment result and the live homepage, publication tabs,
   links, `/404.html`, and `/feed.xml`.
4. Once the checks have run, add a branch ruleset for `master` requiring pull
   requests and the three checks named above. An additional approving reviewer
   is optional for this personal repository. Configure any owner bypass
   deliberately; otherwise direct pushes will be blocked.

Changing the publishing source, enabling a ruleset, and configuring repository
security settings are separate GitHub settings; these files do not change them.

The site retains Jekyll 3.10 and Minima 2.5. Removing the unused Pages plugins
also removes their `rubyzip` and `json` dependency chains. Check that the related
Dependabot alerts close after the new lockfile reaches `master`.

## Dependency updates

Dependabot security updates are enabled in the repository settings and can open
fix pull requests when a compatible patched version exists.
`.github/dependabot.yml` also checks Ruby gems (including indirect dependencies)
and GitHub Actions every Monday at 09:00 Europe/London. Routine minor and patch
updates are grouped per ecosystem; major updates remain separate. Security
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

Secret scanning and push protection should be enabled separately in repository
security settings. CodeQL can also be enabled there for JavaScript and workflow
analysis. These checks do not replace maintenance of manually vendored assets
such as the JavaScript libraries under `libs/external/`.
