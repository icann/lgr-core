from typing import List
from unittest import TestCase

from lgr.char import Repertoire
from lgr.mixed_scripts_variant_filter import MixedScriptsVariantFilter, get_permitted_scripts
from lgr.tools.utils import parse_single_cp_input
from tests.unit.unicode_database_mock import UnicodeDatabaseMock


def to_chars(label):
    return tuple(ord(c) for c in label)


class TestMixedScriptVariantFilter(TestCase):
    UNKNOWN_SCRIPT = 'Common'
    c_label = '赤a'  # han - latin (chinese)
    j_label = 'テゃa'  # han - katakana - hiragana - latin (japanese)
    k_label = '보a'  # han - hangul - latin (korean)

    CHINEESE_SCRIPTS_SET = {'Han', 'Latin'}
    JAPENEESE_SCRIPTS_SET = {'Han', 'Katakana', 'Hiragana', 'Latin'}
    KOREAN_SCRIPTS_SET = {'Han', 'Hangul', 'Latin'}

    def setUp(self) -> None:
        super().setUp()
        self.maxDiff = None
        self.unidb = UnicodeDatabaseMock()
        self.repertoire = Repertoire()
        self.repertoire.add_char((ord('a'),))
        self.repertoire.add_char((ord('á'),))
        self.repertoire.add_char((ord('ά'),))
        self.repertoire.add_char((ord('а'),))
        self.repertoire.add_char((ord('α'),))
        self.repertoire.add_variant((ord('a'),), (ord('á'),))
        self.repertoire.add_variant((ord('a'),), (ord('ά'),))
        self.repertoire.add_variant((ord('a'),), (ord('а'),))
        self.repertoire.add_variant((ord('a'),), (ord('α'),))
        self.repertoire.add_variant((ord('á'),), (ord('a'),))
        self.repertoire.add_variant((ord('á'),), (ord('ά'),))
        self.repertoire.add_variant((ord('á'),), (ord('а'),))
        self.repertoire.add_variant((ord('á'),), (ord('α'),))
        self.repertoire.add_variant((ord('ά'),), (ord('a'),))
        self.repertoire.add_variant((ord('ά'),), (ord('á'),))
        self.repertoire.add_variant((ord('ά'),), (ord('а'),))
        self.repertoire.add_variant((ord('ά'),), (ord('α'),))
        self.repertoire.add_variant((ord('а'),), (ord('a'),))
        self.repertoire.add_variant((ord('а'),), (ord('á'),))
        self.repertoire.add_variant((ord('а'),), (ord('ά'),))
        self.repertoire.add_variant((ord('а'),), (ord('α'),))
        self.repertoire.add_variant((ord('α'),), (ord('a'),))
        self.repertoire.add_variant((ord('α'),), (ord('á'),))
        self.repertoire.add_variant((ord('α'),), (ord('ά'),))
        self.repertoire.add_variant((ord('α'),), (ord('а'),))
        self.repertoire.add_char((ord('b'),))
        self.repertoire.add_char((ord('β'),))
        self.repertoire.add_variant((ord('b'),), (ord('β'),))
        self.repertoire.add_variant((ord('β'),), (ord('b'),))
        self.repertoire.add_char((ord('ゃ'),))
        self.repertoire.add_char((ord('赤'),))
        self.repertoire.add_char((ord('テ'),))
        self.repertoire.add_char((ord('보'),))
        self.repertoire.add_char((ord('œ'),))
        self.repertoire.add_char((ord('c'),))
        self.repertoire.add_char((ord('o'),))
        self.repertoire.add_char((ord('m'),))
        self.repertoire.add_char((ord('u'),))
        self.repertoire.add_char((ord('f'),))

    def test_C_permitted_scripts(self):
        self.assertCountEqual(get_permitted_scripts({'Han'}), self.CHINEESE_SCRIPTS_SET)

    def test_J1_permitted_scripts(self):
        self.assertCountEqual(get_permitted_scripts({'Katakana'}), self.JAPENEESE_SCRIPTS_SET)

    def test_J2_permitted_scripts(self):
        self.assertCountEqual(get_permitted_scripts({'Hiragana'}), self.JAPENEESE_SCRIPTS_SET)

    def test_K_permitted_scripts(self):
        self.assertCountEqual(get_permitted_scripts({'Hangul'}), self.KOREAN_SCRIPTS_SET)

    def test_conversion_hypothesis(self):
        script = self.unidb.get_script(ord('á'))  # á in latin
        assert script == 'Latin'
        script = self.unidb.get_script(ord('ά'))  # ά in Greek
        assert script == 'Greek'
        script = self.unidb.get_script(ord('а'))  # а in Cyrillic
        assert script == 'Cyrillic'
        script = self.unidb.get_script(ord('α'))  # α (alpha) in Greek
        assert script == 'Greek'
        cp = parse_single_cp_input('U+03B1')
        assert script == self.unidb.get_script(cp)

    def test_base_scripts(self):
        fltr = MixedScriptsVariantFilter(to_chars('com'), self.repertoire, self.unidb)
        self.assertCountEqual(fltr.base_scripts, {'Latin'})

    def test_C_base_scripts(self):
        fltr = MixedScriptsVariantFilter(to_chars(self.c_label), self.repertoire, self.unidb)
        self.assertCountEqual(fltr.base_scripts, self.CHINEESE_SCRIPTS_SET)

    def test_J_base_scripts(self):
        fltr = MixedScriptsVariantFilter(to_chars(self.j_label), self.repertoire, self.unidb)
        self.assertCountEqual(fltr.base_scripts, self.JAPENEESE_SCRIPTS_SET)

    def test_K_base_scripts(self):
        fltr = MixedScriptsVariantFilter(to_chars(self.k_label), self.repertoire, self.unidb)
        self.assertCountEqual(fltr.base_scripts, self.KOREAN_SCRIPTS_SET)

    def test_base_scripts_special_char(self):
        fltr = MixedScriptsVariantFilter(to_chars('œuf'), self.repertoire, self.unidb)
        self.assertCountEqual(fltr.base_scripts, {'Latin'})

    def test_other_scripts(self):
        fltr = MixedScriptsVariantFilter(to_chars('ab'), self.repertoire, self.unidb)
        self.assertCountEqual(fltr.other_scripts, {'Greek'})

        fltr = MixedScriptsVariantFilter(to_chars('abc'), self.repertoire, self.unidb)
        self.assertCountEqual(fltr.other_scripts, {})


    def test_filter(self):
        self.filter_base(label='a', chars=['á', 'ά', 'α', 'a', '赤', 'テ', 'ゃ', '보'], expected_list=['a', 'á'])

    def test_C_filter(self):
        self.filter_base(label='赤', chars=['á', 'ά', 'α', 'a', '赤', 'テ', 'ゃ', '보'], expected_list=['a', 'á', '赤'])

    def test_J_filter(self):
        self.filter_base(label='テゃ', chars=['á', 'ά', 'α', 'a', '赤', 'テ', 'ゃ', '보'],
                         expected_list=['á', 'a', '赤', 'テ', 'ゃ'])

    def test_K_filter(self):
        self.filter_base(label='보', chars=['á', 'ά', 'α', 'a', '赤', 'テ', 'ゃ', '보'],
                         expected_list=['á', 'a', '赤', '보'])

    def test_special_char_filter(self):
        self.filter_base(label='œ', chars=['œ', 'oe'], expected_list=['œ', 'oe'])

    def filter_base(self, label: str, chars: List[str], expected_list: List[str]):
        fltr = MixedScriptsVariantFilter(to_chars(label), self.repertoire, self.unidb)
        filtered_list = [c for c in chars if fltr.cp_in_base_scripts(to_chars(c))]
        self.assertCountEqual(filtered_list, expected_list)
