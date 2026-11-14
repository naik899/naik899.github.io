# naik899.github.io

Personal site and blog of Ravindra Naik — Cloud Architect & Gen AI Developer. Live at **https://naik899.github.io**.

Built with Jekyll and deployed to GitHub Pages by [`.github/workflows/pages.yml`](.github/workflows/pages.yml).

## Layout

| Path | What it is |
| --- | --- |
| `index.html` | Homepage |
| `_data/experience.yml`, `_data/projects.yml` | Career timeline and selected work |
| `_data/videos.json` | YouTube videos, refreshed daily by the workflow |
| `_posts/` | Blog posts (`YYYY-MM-DD-slug.md`, served at `/blog/<slug>/`) |
| `videos.html`, `blog.html`, `categories.html` | Videos, blog and topic pages |
| `assets/css/site.css` | All styles (light and dark) |

## Write a post

Add `_posts/YYYY-MM-DD-slug.md`:

```markdown
---
title: "Post title"
categories: [Gen AI, Azure]
---

First paragraph becomes the excerpt.
```

## Run locally

```bash
docker run --rm -it -p 4000:4000 -v "$PWD":/site -w /site ruby:3.3 \
  sh -c "bundle config set --local path vendor/bundle && bundle install && bundle exec jekyll serve --host 0.0.0.0"
```

Then open http://localhost:4000. To refresh the video list by hand, run `python3 scripts/sync_youtube.py`.
