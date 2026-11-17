# Task: Add multilingual course navigation

## Objective

Add first-class multilingual navigation to the VitePress course so visitors can
switch between Portuguese and English while browsing the same course.

The implementation must preserve the existing course structure, links, visual
identity, and local development workflow. English is the first additional
locale; the design should allow another locale to be added without replacing
the routing model.

## Context

The site is a VitePress documentation site under `docs/`. It currently uses
Portuguese content and route paths such as `/lectures/`, `/projects/`, and
`/reference/`. The repository will be used by a global team, so language
selection must be visible and usable from every course page.

## Scope

1. Define a locale-aware route structure. Prefer `/pt-BR/` and `/en/` prefixes
   unless the existing VitePress configuration provides a stronger convention.
2. Add a language switcher to the site navigation or theme layout. It must show
   the current language, provide the other available language, and preserve the
   equivalent page when a translation exists.
3. Add language metadata, titles, navigation labels, and canonical or alternate
   links appropriate for both locales.
4. Translate the course content into English while keeping Portuguese available.
   Preserve code identifiers, command names, file paths, URLs, API names, and
   technical terms that should remain unchanged.
5. Handle missing translations explicitly. A missing page must lead to a useful
   locale landing page or a clear fallback, never a broken navigation link.
6. Keep links between lessons, projects, references, and resources within the
   selected locale whenever the target exists.
7. Document the translation workflow so future contributors know how to add or
   update a locale.

## Acceptance criteria

- A visitor can switch between Portuguese and English from any course page.
- The switcher keeps the visitor on the equivalent page when that translation
  exists.
- Direct links to both locale home pages and representative lesson, project,
  reference, and resource pages work in a production build.
- Browser titles, navigation labels, and visible interface text match the
  selected locale.
- No existing Portuguese page becomes unreachable.
- The implementation does not duplicate the full VitePress configuration for
  every locale without a documented reason.
- The build passes and includes checks for locale routing, switcher behavior,
  and representative cross-page links.
- The README explains how to run the site and how to contribute translations.

## Suggested implementation sequence

1. Inspect the current VitePress config, theme, sidebar, and internal links.
2. Choose and document the route and content layout for locales.
3. Implement the shared language switcher and locale-aware navigation.
4. Migrate a representative slice first: home page, one lesson, one project,
   one reference page, and one resource page.
5. Translate the remaining content while preserving code and technical names.
6. Add automated route and link checks, then run the production build.

## Risks and decisions to record

- Whether locale prefixes are added to every route or generated through a
  localized VitePress configuration.
- How untranslated pages are represented during the migration.
- Whether Portuguese should be labeled `pt-BR` or `pt` in URLs and metadata.
- How search indexing and canonical URLs behave for translated pages.

## Out of scope

- Rewriting the course curriculum.
- Changing the visual design system beyond what the language switcher requires.
- Adding Node.js course examples; that is a separate task.
