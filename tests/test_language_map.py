import unittest
from choppa.structures import LanguageMap


class LanguageMapTest(unittest.TestCase):
    def test_matches(self):
        language_map: LanguageMap = LanguageMap("PL.*", None)
        self.assertTrue(language_map.matches("PL_pl"))
        self.assertFalse(language_map.matches("EN_us"))
