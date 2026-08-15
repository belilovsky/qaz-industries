from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class CardContextTypographyTests(unittest.TestCase):
    def test_public_card_contexts_are_not_decorative_eyebrows(self) -> None:
        styles = (ROOT / "styles.css").read_text(encoding="utf-8")
        context = (ROOT / "card-context.css").read_text(encoding="utf-8")
        profile_view = (ROOT / "profile-view.js").read_text(encoding="utf-8")

        self.assertIn(".eyebrow{display:block", styles)
        self.assertIn(".eyebrow span{display:none}", styles)
        self.assertIn(".industry-card>b", styles)
        self.assertIn("text-transform:none", styles)
        self.assertIn("text-transform: none;", context)
        self.assertIn(".av-source-registry__record-eyebrow", context)
        self.assertIn(".av-layer-registry__eyebrow", context)
        self.assertNotIn("ПРОВЕРЕННЫЙ ИСТОЧНИК", profile_view)

    def test_every_public_page_loads_the_card_context_override(self) -> None:
        for filename in ("index.html", "industry.html", "benchmarks.html", "publication.html"):
            page = (ROOT / filename).read_text(encoding="utf-8")
            self.assertIn('<link rel="stylesheet" href="card-context.css" />', page)
