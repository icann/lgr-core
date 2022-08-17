from typing import List, Tuple
from unittest import TestCase

from lgr.mixed_scripts_variant_filter import MixedScriptsVariantFilter, get_permitted_scripts
from lgr.tools.utils import parse_single_cp_input
from tests.unit.unicode_database_mock import UnicodeDatabaseMock


def to_chars(label):
    return tuple(ord(c) for c in label)


class TestMixedScriptVariantFilter(TestCase):
    UNKNOWN_SCRIPT = 'Common'
    c_label = '赤a'  # han - latin (chineese)
    c_label_variants = ['赤á', '赤ά', '赤α', '赤а', '赤a']
    j_label = 'テゃa'  # han - katakana - hiragana - latin (japaneese)
    j_label_variants = ['テゃá', 'テゃά', 'テゃα', 'テゃа', 'テゃa']
    k_label = '보a'  # han - hangul - latin (korean)
    k_label_variants = ['보á', '보ά', '보α', '보а', '보a']

    CHINEESE_SCRIPTS_SET = {'Han', 'Latin'}
    JAPENEESE_SCRIPTS_SET = {'Han', 'Katakana', 'Hiragana', 'Latin'}
    KOREAN_SCRIPTS_SET = {'Han', 'Hangul', 'Latin'}

    def setUp(self) -> None:
        super().setUp()
        self.maxDiff = None
        self.unidb = UnicodeDatabaseMock()
        self.filter = MixedScriptsVariantFilter(self.unidb)

    def test_C_permitted_scripts(self):
        self.assertCountEqual(get_permitted_scripts({'Han'}), self.CHINEESE_SCRIPTS_SET)

    def test_J1_permitted_scripts(self):
        self.assertCountEqual(get_permitted_scripts({'Katakana'}), self.JAPENEESE_SCRIPTS_SET)

    def test_J2_permitted_scripts(self):
        self.assertCountEqual(get_permitted_scripts({'Hiragana'}), self.JAPENEESE_SCRIPTS_SET)

    def test_K_permitted_scripts(self):
        self.assertCountEqual(get_permitted_scripts({'Hangul'}), self.KOREAN_SCRIPTS_SET)

    def test_conversion_hypothesis(self):
        latin = self.unidb.get_script(ord('á'))  # á in latin
        assert latin == 'Latin'
        latin = self.unidb.get_script(ord('ά'))  # ά in Greek
        assert latin == 'Greek'
        latin = self.unidb.get_script(ord('а'))  # а in Cyrillic
        assert latin == 'Cyrillic'
        greek = self.unidb.get_script(ord('α'))  # α (alpha) in Greek
        assert greek == 'Greek'
        cp = parse_single_cp_input('U+03B1')
        assert greek == self.unidb.get_script(cp)

    def test_get_base_scripts(self):
        base_scripts = self.filter.get_base_scripts(to_chars('com'))
        self.assertCountEqual(base_scripts, {'Latin'})

    def test_C_get_base_scripts(self):
        base_scripts = self.filter.get_base_scripts(to_chars(self.c_label))
        self.assertCountEqual(base_scripts, self.CHINEESE_SCRIPTS_SET)

    def test_J_get_base_scripts(self):
        base_scripts = self.filter.get_base_scripts(to_chars(self.j_label))
        self.assertCountEqual(base_scripts, self.JAPENEESE_SCRIPTS_SET)

    def test_K_get_base_scripts(self):
        base_scripts = self.filter.get_base_scripts(to_chars(self.k_label))
        self.assertCountEqual(base_scripts, self.KOREAN_SCRIPTS_SET)

    def test_get_base_scripts_special_char(self):
        base_scripts = self.filter.get_base_scripts(to_chars('œuf'))
        self.assertCountEqual(base_scripts, {'Latin'})

    def test_filter(self):
        self.filter_base(label='a', variants=['á', 'ά', 'α', 'a'], expected_list=['a', 'á'])

    def test_C_filter(self):
        self.filter_base(label='赤a', variants=self.c_label_variants, expected_list=['赤a', '赤á'])

    def test_J_filter(self):
        self.filter_base(label='テゃa', variants=self.j_label_variants, expected_list=['テゃá', 'テゃa'])

    def test_K_filter(self):
        self.filter_base(label='보a', variants=self.k_label_variants, expected_list=['보á', '보a'])

    def test_special_char_filter(self):
        self.filter_base(label='œ', variants=['œ', 'oe'], expected_list=['œ', 'oe'])

    def filter_base(self, label: str, variants: List[str], expected_list: List[str]):
        filtered_list = self.filter_mixed_script_variants(
            to_chars(label),
            [to_chars(v) for v in variants])
        self.assertCountEqual(filtered_list, [to_chars(e) for e in expected_list])

    def filter_mixed_script_variants(self, label: Tuple[int], variants: List[Tuple[int]]):
        base_scripts = self.filter.get_base_scripts(label)
        filtered_variants = set()
        for v in variants:
            if self.filter.label_in_scripts(v, base_scripts):
                filtered_variants.add(v)
        return filtered_variants