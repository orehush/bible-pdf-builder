"""Print-size presets compile into valid PrinceXML-ready CSS."""
import re
import unittest
from pathlib import Path

from kulish.builder.print_profiles import PROFILES, css_values
from kulish.builder.renderer import css_with_absolute_resources

CSS_PATH = Path(__file__).resolve().parents[1] / "src/kulish/styles/styles.css"


class PrintProfilesTests(unittest.TestCase):
    def test_page_dimensions_and_margins(self):
        for name, profile in PROFILES.items():
            with self.subTest(name=name):
                css = css_with_absolute_resources(CSS_PATH, name)
                self.assertIn(f"size: {profile.width_mm:g}mm {profile.height_mm:g}mm;", css)
                self.assertIn(f"margin-top: {profile.top_mm:g}mm;", css)
                self.assertIn(f"margin-bottom: {profile.bottom_mm:g}mm;", css)
                self.assertIn(f"margin-left: {profile.inner_mm:g}mm;", css)
                self.assertIn(f"margin-right: {profile.outer_mm:g}mm;", css)
                self.assertNotRegex(css, r"\\{\\{[a-z_]+\\}\\}")
                self.assertIn(f"font-size: {profile.font_pt:g}pt;", css)

    def test_large_margins(self):
        p = PROFILES["large"]
        self.assertEqual((p.width_mm, p.height_mm), (165, 235))
        self.assertEqual((p.inner_mm, p.outer_mm, p.top_mm, p.bottom_mm), (13, 12, 14, 14))

    def test_pocket_dimensions(self):
        p = PROFILES["pocket-size"]
        self.assertEqual((p.width_mm, p.height_mm), (80, 130))

    def test_unknown_profile_rejected(self):
        with self.assertRaises(ValueError):
            css_values("unknown")


if __name__ == "__main__":
    unittest.main()
