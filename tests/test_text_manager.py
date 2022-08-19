import unittest
import io
from typing import List, Union, Dict

from choppa.text_manager import TextManager


class TextManagerTest(unittest.TestCase):
    def test_char_sequence(self) -> None:
        manager: TextManager =TextManager(text="text")
        self.assertEqual("text", manager.get_text())
        self.assertEqual(4, manager.buffer_length)
        self.assertFalse(manager.has_more_text())

    
    def test_empty_string(self) -> None:
        manager: TextManager = TextManager("")
        self.assertEqual("", manager.get_text())
        self.assertEqual(0, manager.buffer_length)
        self.assertFalse(manager.has_more_text())

    def test_cannot_read_char_sequence(self) -> None:
        manager: TextManager =TextManager(text="text")
        with self.assertRaises(AssertionError):
            manager.read_text(1)

    def test_reader(self)-> None:
        manager: TextManager = TextManager(reader=io.StringIO("text"), buffer_length=2)
        self.assertEqual(2, manager.buffer_length)

        self.assertEquals("te", manager.get_text())
        self.assertTrue(manager.has_more_text())

        manager.read_text(1)
        self.assertEqual("ex", manager.get_text())
        self.assertTrue(manager.has_more_text())

        manager.read_text(1)
        self.assertEqual("xt", manager.get_text())
        self.assertFalse(manager.has_more_text())

    def test_empty_reader(self) -> None:
        manager: TextManager = TextManager(reader=io.StringIO(""), buffer_length=2)
        self.assertEqual("", manager.get_text())
        self.assertEqual(2, manager.buffer_length)
        self.assertFalse(manager.has_more_text())

    def test_buffer_zero_length(self) -> None:
        with self.assertRaises(AssertionError):
            TextManager(reader=io.StringIO(""))

    def test_incorrect_init(self) -> None:
        with self.assertRaises(AssertionError):
            TextManager(text="foobar", reader=io.StringIO("barfoo"))
            TextManager()

