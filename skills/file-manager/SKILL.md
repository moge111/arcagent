---
name: file-manager
description: "Browse, search, create, edit, and manage files on the server"
allowed-tools: ["shell_exec", "read_file", "write_file"]
---

# File Manager Skill

When the user wants to work with files on the server:

## Browse files
- Use `ls -la <path>` to list files
- Use `find <path> -name "<pattern>"` to search
- Use `tree <path> -L 2` to show directory structure

## Read files
- Use the `read_file` tool for text files
- Use `file <path>` to check file type first

## Create/Edit files
- Use the `write_file` tool to create or overwrite files
- Use `sed` or `awk` via `shell_exec` for in-place edits

## File operations
- Copy: `cp -r <src> <dst>`
- Move: `mv <src> <dst>`
- Delete: `rm <path>` (ask for confirmation first for important files)
- Permissions: `chmod <mode> <path>`
