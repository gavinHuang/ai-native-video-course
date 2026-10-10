"""Small helper for module edits: add quiz items, insert text before a heading, replace text.
Usage from Python: from patch_module import Mod; m = Mod(path); m.quiz([...]); m.before("## Worked example", text); m.save()"""
import json


class Mod:
    def __init__(self, path):
        self.path = path
        self.s = open(path, encoding="utf-8").read()

    def quiz(self, items):
        """items: list of (q, options, answer, explain). Appended at the end of the quiz list."""
        i = self.s.index("\ndeeper:")
        add = ""
        for q, opts, ans, exp in items:
            add += (f"\n  - q: {json.dumps(q, ensure_ascii=False)}\n    options: {json.dumps(opts, ensure_ascii=False)}"
                    f"\n    answer: {ans}\n    explain: {json.dumps(exp, ensure_ascii=False)}")
        self.s = self.s[:i] + add + self.s[i:]
        return self

    def before(self, anchor, text):
        assert anchor in self.s, (self.path, anchor)
        self.s = self.s.replace(anchor, text.rstrip("\n") + "\n\n" + anchor, 1)
        return self

    def sub(self, old, new):
        assert old in self.s, (self.path, old[:60])
        self.s = self.s.replace(old, new, 1)
        return self

    def save(self):
        open(self.path, "w", encoding="utf-8").write(self.s)
