source "https://rubygems.org"
ruby "~> 3.3.0"

# Manage the build independently of pages-gem and review locked updates.
gem "jekyll", "~> 4.4.1"
gem "kramdown-parser-gfm", "~> 1.1"
gem "minima", "~> 2.5"
gem "webrick", "~> 1.9"

group :jekyll_plugins do
  gem "jekyll-feed", "~> 0.17"
end

# Run the same dependency audit locally and in GitHub Actions.
group :development do
  gem "bundler-audit", "~> 0.9", require: false
end
