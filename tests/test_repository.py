"""Repository consistency: manifests, frontmatter, package and the skill's own examples.

Run: python -B -m unittest discover -s tests -v
"""
import json
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "evals"))
import check  # noqa: E402

SKILLS = [p for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").is_file()]
ALLOWED_KEYS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    assert m, "SKILL.md sem frontmatter"
    return m.group(1)


def fm_value(fm, key):
    m = re.search(rf"^{key}:\s*(>-?|\|-?)?\s*\n((?:  .*\n?)+)", fm, re.M)
    if m:
        return " ".join(l.strip() for l in m.group(2).splitlines()).strip()
    m = re.search(rf"^{key}:\s*(.+)$", fm, re.M)
    return m.group(1).strip().strip('"') if m else None


class Manifests(unittest.TestCase):
    def setUp(self):
        self.assertEqual(len(SKILLS), 1, "o repositório deve ter exatamente uma skill")
        self.skill = SKILLS[0]
        self.text = (self.skill / "SKILL.md").read_text(encoding="utf-8")
        self.fm = frontmatter(self.text)
        self.plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))

    def test_line_endings_are_lf(self):
        self.assertNotIn("\r\n", (self.skill / "SKILL.md").read_bytes().decode("utf-8"))

    def test_frontmatter_keys(self):
        keys = set(re.findall(r"^([a-z-]+):", self.fm, re.M))
        self.assertTrue(keys <= ALLOWED_KEYS, keys - ALLOWED_KEYS)
        self.assertEqual(fm_value(self.fm, "name"), self.skill.name)

    def test_description_limits(self):
        desc = fm_value(self.fm, "description")
        self.assertLessEqual(len(desc), 1024)
        self.assertNotRegex(desc, r"[<>]")

    def test_versions_match(self):
        version = re.search(r'version:\s*"([^"]+)"', self.fm).group(1)
        self.assertEqual(self.plugin["version"], version)
        entry = [p for p in self.market["plugins"] if p["name"] == self.plugin["name"]]
        self.assertEqual(len(entry), 1)
        self.assertEqual(entry[0]["version"], version)
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertRegex(changelog, rf"## \[{re.escape(version)}\]")

    def test_plugin_name_matches_skill(self):
        self.assertEqual(self.plugin["name"], self.skill.name)

    def test_no_token_promise_in_descriptions(self):
        for text in (self.plugin["description"], self.market["plugins"][0]["description"],
                     fm_value(self.fm, "description")):
            self.assertNotRegex(text.lower(), r"token")


class Examples(unittest.TestCase):
    """The skill's own before/after pairs must pass the checker: no aside dash left,
    no number lost or added, no chatbot preamble. A bad example teaches the bad habit."""

    def pairs(self):
        text = (SKILLS[0] / "SKILL.md").read_text(encoding="utf-8")
        rows = re.findall(r"^\| ([^|]+?) \| ([^|]+?) \|$", text, re.M)  # two-column tables only
        return [(a, b) for a, b in rows if a != "IA" and not set(a) <= set("-")]

    def test_examples_exist(self):
        self.assertGreaterEqual(len(self.pairs()), 4)

    def test_examples_pass_checker(self):
        for src, out in self.pairs():
            r = check.check(src, out)
            self.assertEqual([f for f in r["failures"]], [], f"{src} -> {out}: {r}")


class Package(unittest.TestCase):
    def test_zip_has_skill_at_top(self):
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run([sys.executable, "-B", str(ROOT / "scripts" / "build_zip.py"), "--out", tmp],
                           check=True, capture_output=True)
            zips = list(pathlib.Path(tmp).glob("*.zip"))
            self.assertEqual(len(zips), 1)
            with zipfile.ZipFile(zips[0]) as zf:
                names = zf.namelist()
                data = zf.read(f"{SKILLS[0].name}/SKILL.md")
            self.assertIn(f"{SKILLS[0].name}/SKILL.md", names)
            self.assertFalse([n for n in names if "\\" in n])
            self.assertNotIn(b"\r\n", data)


if __name__ == "__main__":
    unittest.main()
