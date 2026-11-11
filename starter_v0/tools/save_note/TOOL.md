---
name: save_note
track: bonus
kind: local_formatter
provider: Local filesystem
requires_env: []
inputs: [title, content, filename]
outputs: [status, path, bytes_written]
side_effect: local_file_write
---
# save_note

Saves a research note or summary as a sanitized Markdown file inside `starter_v0/notes/`.

