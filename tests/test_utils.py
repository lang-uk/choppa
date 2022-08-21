import unittest
from choppa.utils import remove_block_quotes, finitize


class UtilsTest(unittest.TestCase):
    def test_remove_block_quotes(self) -> None:
        QUOTED_PATTERN: str = "\\Q\\a\\Qaa\\\\Ebb\\Q\\E\\Qcc\\Edd"
        EXPECTED_UNQUOTED_PATTERN: str = "\\\\\\a\\\\\\Q\\a\\a\\\\bb\\c\\cdd"

        self.assertEqual(EXPECTED_UNQUOTED_PATTERN, remove_block_quotes(QUOTED_PATTERN))

    def testFinitize(self) -> None:
        INFINITE_PATTERN: str = "a*b\\*\\\\+c+d\\+\\\\\\\\*e++f{1,4}+g{3,}+h{1}+\\Qa+\\E"
        EXPECTED_FINITE_PATTERN: str = (
            "a{0,100}b\\*\\\\{1,100}c{1,100}d\\+\\\\\\\\{0,100}e{1,100}+f{1,4}+g{3,100}+h{1}+\\a\\+"
        )
        self.assertEqual(EXPECTED_FINITE_PATTERN, finitize(INFINITE_PATTERN, 100))
