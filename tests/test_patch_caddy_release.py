from __future__ import annotations

import unittest

from scripts.patch_caddy_release import patch


SOURCE = '''qaz.industries {
  header {
    X-Qaz-Release "old-qaz"
  }
  @qaz_industries_health path /api/health
  respond @qaz_industries_health `{"status":"ok","service":"qaz-industries","release":"old-qaz"}` 200
}

qaz.support {
  header {
    X-Qaz-Release "qaz-support-current"
  }
}
'''

SOURCE_WITH_HTTP_REDIRECT = '''http://qaz.industries, http://www.qaz.industries {
  redir https://qaz.industries{uri} permanent
}

''' + SOURCE


class PatchCaddyReleaseTests(unittest.TestCase):
    def test_changes_only_the_qaz_industries_block(self) -> None:
        result = patch(SOURCE_WITH_HTTP_REDIRECT, "20260809T123000Z-a1b2c3d4e5f6")

        self.assertIn('X-Qaz-Industries-Release "20260809T123000Z-a1b2c3d4e5f6"', result)
        self.assertIn('"service":"qaz-industries","release":"20260809T123000Z-a1b2c3d4e5f6"', result)
        self.assertIn("Content-Security-Policy", result)
        self.assertIn("https://fonts.googleapis.com", result)
        self.assertIn("https://fonts.gstatic.com", result)
        self.assertIn('Cross-Origin-Opener-Policy "same-origin"', result)
        self.assertIn('header @qaz_industries_health Cache-Control "no-store"', result)
        self.assertIn('@qaz_industries_release path /release.json', result)
        self.assertIn('header @qaz_industries_release Cache-Control "no-store"', result)
        self.assertIn('X-Qaz-Release "qaz-support-current"', result)
        self.assertIn('http://qaz.industries, http://www.qaz.industries {', result)
        support = result[result.index("qaz.support {") :]
        self.assertNotIn("Qaz-Industries", support)

    def test_rejects_ambiguous_qaz_blocks(self) -> None:
        with self.assertRaisesRegex(ValueError, "exactly one top-level"):
            patch(SOURCE + SOURCE, "20260809T123000Z-a1b2c3d4e5f6")

    def test_rejects_invalid_release(self) -> None:
        with self.assertRaisesRegex(ValueError, "release identifier"):
            patch(SOURCE, "not/a-release")


if __name__ == "__main__":
    unittest.main()
