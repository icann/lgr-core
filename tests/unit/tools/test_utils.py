from unittest import TestCase
from unittest.mock import Mock

from lgr.tools.utils import get_rz_label_script


class TestGetRZLabelScript(TestCase):
    def setUp(self):
        self.unidb = Mock()

    def test_returns_script_name(self):
        label = 'test'
        self.unidb.get_script.return_value = 'Latn'

        result = get_rz_label_script(label, self.unidb)

        self.assertEqual(result, 'und-Latn')
        self.unidb.get_script.assert_called_with('t', alpha4=True)

    def test_returns_jpan_when_label_uses_hira_or_kana(self):
        label = 'テスト'
        self.unidb.get_script.return_value = 'Kana'

        result = get_rz_label_script(label, self.unidb)

        self.assertEqual(result, 'und-Jpan')
        self.unidb.get_script.assert_called_with('テ', alpha4=True)

    def test_returns_kore_when_label_uses_hang(self):
        label = '테스트'
        self.unidb.get_script.return_value = 'Hang'

        result = get_rz_label_script(label, self.unidb)

        self.assertEqual(result, 'und-Kore')
        self.unidb.get_script.assert_called_with('테', alpha4=True)

    def test_returns_jpan_when_label_mixes_hani_with_hira_or_kana(self):
        label = '侃々ドットしっぺい'
        self.unidb.get_script.side_effect = ['Hani', 'Hani', 'Kana']

        result = get_rz_label_script(label, self.unidb)

        self.assertEqual(result, 'und-Jpan')
        self.assertEqual(self.unidb.get_script.call_count, 3)

    def test_returns_hani_when_not_mixed_with_hira_or_kana(self):
        label = '侃侃'
        self.unidb.get_script.side_effect = ['Hani', 'Hani']

        result = get_rz_label_script(label, self.unidb)

        self.assertEqual(result, 'und-Hani')
        self.assertEqual(self.unidb.get_script.call_count, 2)

    def test_returns_zyyy_when_label_contains_only_common_script_characters(self):
        label = 'ーー'
        self.unidb.get_script.side_effect = ['Zyyy', 'Zyyy']

        result = get_rz_label_script(label, self.unidb)

        self.assertEqual(result, 'und-Zyyy')
        self.assertEqual(self.unidb.get_script.call_count, 2)

    def test_returns_jpan_when_label_mixes_common_with_hira_or_kana(self):
        label = 'ーマルマル'
        self.unidb.get_script.side_effect = ['Zyyy', 'Kana']

        result = get_rz_label_script(label, self.unidb)

        self.assertEqual(result, 'und-Jpan')
        self.assertEqual(self.unidb.get_script.call_count, 2)

    def test_returns_none_when_label_is_empty(self):
        label = ''

        result = get_rz_label_script(label, self.unidb)

        self.assertEqual(result, None)
        self.unidb.get_script.assert_not_called()
