# Task: Make the repository globally usable in English

## Objective

Convert the repository's user-facing documentation, contributor instructions,
examples, and operational text to English so a global team can use and maintain
it consistently.

This task concerns repository language and contributor experience. It must
preserve the course's technical meaning, executable behavior, examples, and
historical references that are intentionally part of the teaching material.

## Scope

1. Inventory all tracked human-readable content, including Markdown, YAML,
   JSON labels, shell help text, Python messages, HTML reports, templates, and
   contributor documentation.
2. Translate Portuguese prose and user-facing messages into clear, natural
   technical English.
3. Translate headings, navigation labels, table contents, error messages,
   comments, examples, and generated-report text where the source is maintained
   in this repository.
4. Keep stable technical identifiers unchanged: file paths, package names,
   environment variables, commands, Python and JavaScript identifiers, URLs,
   schema keys, test names, and public API names.
5. Preserve the meaning of domain terms and explain local product-team context in
   English where it is needed by a global reader.
6. Update links, titles, metadata, and navigation labels that still refer to
   Portuguese names after translation.
7. Establish an English-only contributor rule for new repository content and
   document it in the README or contributor guide.

## Important boundary

The course may still teach concepts that were previously demonstrated with
AgEnFK or other tools. Translate those lessons into English and preserve their
technical value; do not reintroduce project-level workflow dependencies or
installation hooks for tools that are no longer used by this repository.

## Acceptance criteria

- A repository-wide scan finds no unintended Portuguese in maintained
  user-facing content.
- Code identifiers, commands, paths, URLs, schema keys, and test names remain
  valid and unchanged unless a deliberate migration is documented.
- All navigation labels, page titles, README sections, templates, and generated
  report text intended for users are in English.
- The course builds successfully after translation.
- Existing tests still execute with the same test discovery and assertion
  behavior; no test is deleted, renamed away, skipped, or weakened merely to
  avoid translation work.
- A reviewer can identify any intentionally preserved Portuguese text, such as
  source quotations, fixture data, or historical examples.
- The README describes the English-only repository convention and points to the
  multilingual course navigation task for localized learner content.

## Suggested implementation sequence

1. Generate an inventory grouped by file type and audience: learner,
   contributor, runtime output, fixture, or historical report.
2. Translate contributor and operational documentation first.
3. Translate course pages and navigation while preserving route intent and
   cross-links.
4. Translate runtime messages and maintained report templates without changing
   machine-readable output fields.
5. Run a Portuguese-language scan, build, and the existing test suites.
6. Review a representative sample for tone, technical accuracy, and broken
   links.

## Out of scope

- Adding a second runtime implementation in Node.js.
- Redesigning the course information architecture.
- Translating fixture data when the original language is required to test
  parsing or localization behavior.
