# Website conventions

User-approved permanent editorial preference for this academic website:

- Use American English Title Case for all English page titles, headings (H1–H6), navigation items, buttons, calls to action, topic labels, and short interface labels, including new pages and future additions.
- Examples: “Finance for a Changing Climate.”, “Writing & Notes”, “Explore Research Interests”, “View Curriculum Vitae”, and “Research Experience”.
- Capitalize the first and last words and principal words. Keep articles, coordinating conjunctions, and short prepositions such as “a”, “the”, “and”, “for”, “of”, and “to” lowercase within a title. Treat a wrapped title as one title, not a separate sentence per line.
- Preserve proper-name and acronym spelling: Tianhua Oliver Wang, GitHub, CV, PDF, ORCID, and so on.
- Keep body paragraphs, complete research questions, descriptions, and empty-state explanations in normal sentence case. Leave the Chinese versions' capitalization unaffected.
- Write correct capitalization in content/site.json, not through CSS text-transform: capitalize. That CSS rule incorrectly capitalizes function words and can distort names.
- Preserve official paper titles and bibliographic metadata as supplied; do not silently rewrite citation text. Apply Title Case to site-authored headings and interface copy around them.
- Maintain the three locales (en-US, zh-CN, zh-HK), rebuild with python3 build.py, and run python3 verify.py after edits.

## Color consistency

- The user-approved green palette is documented in docs/COLORS.md. Read it before any future color changes. The executable definitions are CSS custom properties in assets/style.css.
- Reuse the named color variables across all pages, languages, controls, icons, and new components. Do not introduce isolated hard-coded colors for existing roles.
- Preserve the green theme unless the user asks to change it. Change colors by semantic role rather than by individual page.
- Whenever a palette changes, synchronize docs/COLORS.md with the light, manual-dark, system-dark, and print declarations in assets/style.css. Manual-dark and system-dark values must match.
- Keep text and control contrast readable in both themes, including hover, focus, and selected states. Include the current color table in the downloadable source package.
