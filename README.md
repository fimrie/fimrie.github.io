# Fergus Imrie's Website

Personal website built with Jekyll, based on a template by Martin Saveski.

## Local setup

This repo uses Jekyll via Bundler.

If Ruby is not available system-wide, create a local conda environment:

```bash
conda create -n fimrie-site -c conda-forge ruby=3.2 compilers pkg-config -y
conda activate fimrie-site
gem install bundler
```

Install project dependencies:

```bash
bundle install
```

## Run locally

Serve the site with:

```bash
bundle exec jekyll serve
```

Jekyll will print the local URL in the terminal.

## Updating the site

Most content and layout changes live in:

- `_data/`
- `index.html`
- `_layouts/`
- `libs/custom/`

Generated files in `_site/` should not be committed.

## Deployment

Push source changes to GitHub and GitHub Pages will rebuild and publish the site automatically.

## Dependency updates

To refresh dependencies:

```bash
bundle update
```
