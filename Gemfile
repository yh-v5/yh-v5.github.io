source 'https://rubygems.org'

gem 'jekyll'

# Pin activesupport to a Ruby-3-compatible version. Without this, bundler can
# resolve to ancient activesupport (e.g. 3.1.12 from 2011) via transitive
# constraints, which raises `circular argument reference - now (SyntaxError)`
# on Ruby 3.x. Required by _plugins/google-scholar-citations.rb.
gem 'activesupport', '~> 7.1'

# Force jekyll-sass-converter v3, which uses sass-embedded (Dart Sass).
# v2 uses sassc/libsass which is deprecated and does NOT support the `@use`
# rule that al-folio's _sass/*.scss files depend on. With v2 the SCSS is
# emitted as-is into _site/assets/css/main.css and no theme styles apply.
gem 'jekyll-sass-converter', '~> 3.0'
# al-folio's _sass/_themes.scss uses `color.channel(...)` which was added in
# Dart Sass 1.79 (2024-10). The sass-embedded transitive constraint from
# jekyll-sass-converter 3.0.0 (`~> 1.54`) lets bundler pick anything from
# 1.54 to <2.0, but it can resolve to an older version. Pin >= 1.79.
# sass-embedded 1.79+ requires Ruby >= 3.1; this WSL has 3.0.2. Cap below.
# The al-folio code uses `color.channel(...)` which was added in 1.79; we
# patch _sass/_themes.scss to use plain rgba() instead so the < 1.79 cap
# doesn't break the build.
gem 'sass-embedded', '< 1.79'

# Core plugins that directly affect site building
group :jekyll_plugins do
    gem 'jekyll-3rd-party-libraries'
    gem 'jekyll-archives-v2'
    gem 'jekyll-cache-bust'
    gem 'jekyll-email-protect'
    gem 'jekyll-feed'
    gem 'jekyll-get-json'
    gem 'jekyll-imagemagick'
    gem 'jekyll-jupyter-notebook'
    gem 'jekyll-link-attributes'
    gem 'jekyll-minifier'
    gem 'jekyll-paginate-v2'
    gem 'jekyll-regex-replace'
    gem 'jekyll-scholar'
    gem 'jekyll-sitemap'
    gem 'jekyll-socials'
    gem 'jekyll-tabs'
    gem 'jekyll-terser', :git => "https://github.com/RobertoJBeltran/jekyll-terser.git"
    gem 'jekyll-toc'
    gem 'jekyll-twitter-plugin'
    gem 'jemoji'

    gem 'classifier-reborn'  # used for content categorization during the build
end

# Gems for development or external data fetching (outside :jekyll_plugins)
group :other_plugins do
    gem 'css_parser'
    gem 'feedjira'
    gem 'httparty'
    gem 'observer'       # used by jekyll-scholar
    gem 'ostruct'        # used by jekyll-twitter-plugin
    # gem 'terser'         # used by jekyll-terser
    # gem 'unicode_utils' -- should be already installed by jekyll
    # gem 'webrick' -- should be already installed by jekyll
end
