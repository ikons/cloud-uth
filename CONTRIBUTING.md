# Contributing

## Language and file naming convention

This repository is maintained in both Greek and English.

### General rule
- Keep the original Greek files unchanged when possible.
- Add English versions as parallel files using the `.en` suffix before the extension.

Examples:
- `README.md` -> Greek
- `README.en.md` -> English
- `guide.docx` -> Greek
- `guide.en.docx` -> English

## Documentation rules

### Markdown guides
- Greek guide: `README.md`
- English guide: `README.en.md`
- Keep the same structure, section order, code blocks, and examples across both versions.
- When updating one language, update the corresponding file in the other language as soon as possible.

### Word guides
- Greek guide: original `.docx`
- English guide: matching `.en.docx`
- English Word documents should stay aligned with the English Markdown versions.

## Code comments and teaching material
- Prefer English for inline comments inside code snippets that are intended for international students or collaborators.
- Do not change commands, file names, or Kubernetes/Docker object names unless there is a technical reason.
- Keep placeholders such as `<username>` exactly as they are.

## Style guidelines for English content
- Use clear technical English.
- Prefer instructional phrasing such as "Run the following command" or "Create the file below".
- Keep terminology consistent across all guides:
  - container
  - image
  - deployment
  - service
  - secret
  - configmap
  - persistent volume claim

## Recommended workflow for future updates
1. Edit the Greek source file if it is the canonical teaching version.
2. Update the corresponding English file.
3. Verify that code blocks and command examples still match.
4. If a Word guide exists, sync the `.en.docx` version with the latest English Markdown content.

## Pull request checklist
- [ ] Greek and English versions are both updated where needed
- [ ] File naming follows the `.en` convention
- [ ] Code blocks were preserved accurately
- [ ] Links between README files and guides still work
- [ ] Screenshots or exported Word files were checked, if applicable
