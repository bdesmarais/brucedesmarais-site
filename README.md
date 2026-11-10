# brucedesmarais.com (new site, preview)

Jekyll site built natively by GitHub Pages. Preview: https://bdesmarais.github.io/brucedesmarais-site/

## Updating
- **News:** add a Markdown file to `_posts/` named `YYYY-MM-DD-short-title.md` with `title:` and optional `tags:` (use `govfeeds` to show it on the Public Square Analytics page) and `linkedin:` (a LinkedIn activity number to embed the post).
- **LinkedIn posts on the home page:** add the activity number to the top of `_data/linkedin.yml`.
- **Publications, talks, press, awards, grants, advisees:** these come from the CV. After editing `desmarais-lab.github.io/cv/desmarais_cv.tex` or `vitabib.bib`, run `python3 scripts/build_data.py` and commit.
- **Lab members:** `_data/lab.yml`, photos in `assets/img/people/`.
- **Google Analytics:** set `google_analytics:` in `_config.yml` to the GA4 measurement ID (G-...).

## Moving to brucedesmarais.com
Set `url: https://brucedesmarais.com` and `baseurl: ""` in `_config.yml`, then merge into the desmarais-lab.github.io repo (keeping its existing files, such as the CV PDF, course pages, quizzes and sign-up pages, at their current paths) or point the domain's CNAME at this repo.
