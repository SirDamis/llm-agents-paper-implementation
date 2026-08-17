import difflib
import os
import re
import shlex

WINDOW = 30          # half of the file window shown around the cursor
MAX_MATCHES = 30     # cap on search results returned per query
MAX_FIND = 40        # cap on find_file results
IGNORED_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules"}


class Environment:
    """Agent-Computer Interface (ACI): a filesystem sandbox whose actions
    return deliberately summarized, limited output instead of raw dumps."""

    def __init__(self, root="."):
        self.root = os.path.abspath(root)
        self.open_path = None
        self.cursor = 1
        self.modified = {}

    # ---------- helpers ----------
    def _resolve(self, path):
        p = path if os.path.isabs(path) else os.path.join(self.root, path)
        return os.path.normpath(p)

    def _iter_files(self, dirpath):
        for dirpath, dirs, files in os.walk(dirpath):
            dirs[:] = [
                d for d in dirs
                if d not in IGNORED_DIRS and not d.startswith(".")
            ]
            for name in files:
                yield os.path.join(dirpath, name)

    def _readlines(self, path):
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.readlines()

    def _view(self, lines, cursor, header=None):
        total = len(lines)
        start = max(1, cursor - WINDOW)
        end = min(total, cursor + WINDOW)
        out = []
        if header:
            out.append(header)
        out.append(f"Showing lines {start}-{end} of {total}:")
        for i in range(start, end + 1):
            marker = ">" if i == cursor else " "
            out.append(f"{marker}{i:4d}| {lines[i - 1].rstrip()}")
        return "\n".join(out)

    # ---------- actions ----------
    def _search_dir(self, args, content):
        parts = shlex.split(args)
        if not parts:
            return "Error: search_dir needs a search term."
        term = parts[0]
        target = self._resolve(parts[1]) if len(parts) > 1 else self.root
        if not os.path.isdir(target):
            return f"Error: not a directory: {parts[1] if len(parts) > 1 else '.'}"

        results = []
        files_hit = 0
        for path in self._iter_files(target):
            try:
                lines = self._readlines(path)
            except (OSError, UnicodeDecodeError):
                continue
            hits = [i for i, l in enumerate(lines, 1) if term.lower() in l.lower()]
            if not hits:
                continue
            files_hit += 1
            rel = os.path.relpath(path, self.root)
            results.append(f"{rel}:")
            for ln in hits[:3]:
                results.append(f"  {ln:4d}: {lines[ln - 1].strip()}")
            if len(hits) > 3:
                results.append(f"  ... ({len(hits) - 3} more match(es))")

        if not results:
            return f"No matches for '{term}'."
        truncated = len(results) > MAX_MATCHES
        return (
            f"Found '{term}' in {files_hit} file(s):\n"
            + "\n".join(results[:MAX_MATCHES])
            + ("\n(output truncated)" if truncated else "")
        )

    def _search_file(self, args, content):
        parts = shlex.split(args)
        if not parts:
            return "Error: search_file needs a search term."
        term = parts[0]
        if len(parts) > 1:
            path = self._resolve(parts[1])
        elif self.open_path:
            path = self.open_path
        else:
            return "Error: no file is open and no file was given."
        if not os.path.isfile(path):
            return "Error: file not found."

        lines = self._readlines(path)
        rel = os.path.relpath(path, self.root)
        hits = [i for i, l in enumerate(lines, 1) if term.lower() in l.lower()]
        if not hits:
            return f"No matches for '{term}' in {rel}."
        out = [f"{rel}: {len(hits)} match(es) for '{term}':"]
        for ln in hits[:MAX_MATCHES]:
            out.append(f"  {ln:4d}: {lines[ln - 1].strip()}")
        return "\n".join(out)

    def _find_file(self, args, content):
        parts = shlex.split(args)
        if not parts:
            return "Error: find_file needs a name."
        name = parts[0].lower()
        target = self._resolve(parts[1]) if len(parts) > 1 else self.root
        if not os.path.isdir(target):
            return f"Error: not a directory: {parts[1] if len(parts) > 1 else '.'}"

        found = [
            os.path.relpath(p, self.root)
            for p in self._iter_files(target)
            if name in os.path.relpath(p, self.root).lower()
        ]
        if not found:
            return f"No file matching '{parts[0]}'."
        truncated = len(found) > MAX_FIND
        return (
            f"{len(found)} file(s) found:\n"
            + "\n".join(found[:MAX_FIND])
            + ("\n(output truncated)" if truncated else "")
        )

    def _open(self, args, content):
        parts = shlex.split(args)
        if not parts:
            return "Error: open needs a path."
        path = self._resolve(parts[0])
        if not os.path.isfile(path):
            return f"Error: file not found: {parts[0]}"
        lines = self._readlines(path)
        cursor = int(parts[1]) if len(parts) > 1 else 1
        self.open_path = path
        self.cursor = max(1, min(cursor, len(lines)))
        rel = os.path.relpath(path, self.root)
        return self._view(lines, self.cursor, header=f"Opened {rel} ({len(lines)} lines)")

    def _goto(self, args, content):
        if self.open_path is None:
            return "Error: no file is open. Use `open` first."
        line = int(args.strip())
        lines = self._readlines(self.open_path)
        self.cursor = max(1, min(line, len(lines)))
        return self._view(lines, self.cursor)

    def _scroll_up(self, args, content):
        n = int(args.strip()) if args.strip() else WINDOW
        if self.open_path is None:
            return "Error: no file is open. Use `open` first."
        lines = self._readlines(self.open_path)
        self.cursor = max(1, self.cursor - n)
        return self._view(lines, self.cursor)

    def _scroll_down(self, args, content):
        n = int(args.strip()) if args.strip() else WINDOW
        if self.open_path is None:
            return "Error: no file is open. Use `open` first."
        lines = self._readlines(self.open_path)
        self.cursor = min(len(lines), self.cursor + n)
        return self._view(lines, self.cursor)

    def _edit(self, args, content):
        if self.open_path is None:
            return "Error: no file is open. Use `open` first."
        r = re.match(r"\s*(\d+)\s*:\s*(\d+)", args)
        if not r:
            return "Error: edit needs a range like 10:12."
        start, end = int(r.group(1)), int(r.group(2))
        lines = self._readlines(self.open_path)
        if start < 1 or end > len(lines) or start > end:
            return f"Error: range {start}:{end} out of bounds (file has {len(lines)} lines)."
        if content is None:
            return "Error: edit needs content ending with end_of_edit."

        content = content.replace("\r\n", "\n")
        block = [l + "\n" for l in content.split("\n")] if content else []
        new_lines = lines[: start - 1] + block + lines[end:]
        self.modified[self.open_path] = new_lines
        self.cursor = start
        rel = os.path.relpath(self.open_path, self.root)
        return self._view(
            new_lines, start, header=f"Edited {rel} (replaced lines {start}-{end})"
        )

    def _submit(self, args, content):
        if not self.modified:
            return "No changes were made."
        diffs = []
        for path, new_lines in self.modified.items():
            orig = self._readlines(path)
            rel = os.path.relpath(path, self.root)
            diffs.append(
                "".join(
                    difflib.unified_diff(
                        orig, new_lines, fromfile=f"a/{rel}", tofile=f"b/{rel}"
                    )
                )
            )
            with open(path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
        self.modified.clear()
        return "Submitted patch:\n" + "\n".join(diffs)

    # ---------- dispatch ----------
    def step(self, action, args, content):
        handler = {
            "search_dir": self._search_dir,
            "search_file": self._search_file,
            "find_file": self._find_file,
            "open": self._open,
            "goto": self._goto,
            "scroll_up": self._scroll_up,
            "scroll_down": self._scroll_down,
            "edit": self._edit,
            "submit": self._submit,
        }.get(action)
        if handler is None:
            return f"Error: unknown action '{action}'."
        try:
            return handler(args, content)
        except Exception as e:
            return f"Error executing {action}: {e}"
