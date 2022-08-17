from typing import Set, Tuple, List

from munidata.database import UnicodeDatabase


def get_permitted_scripts(base_scripts: Set[str]):
    permitted_scripts = base_scripts.copy()
    if 'Katakana' in base_scripts or 'Hiragana' in base_scripts:
        permitted_scripts.update({'Han', 'Latin', 'Katakana', 'Hiragana'})
    elif 'Hangul' in base_scripts:
        permitted_scripts.update({'Han', 'Latin'})
    if 'Han' in base_scripts:
        permitted_scripts.update({'Latin'})

    return permitted_scripts


class MixedScriptsVariantFilter:
    UNKNOWN_SCRIPT = 'Common'

    def __init__(self, unidb: UnicodeDatabase) -> None:
        super().__init__()
        self.unidb = unidb

    def label_in_scripts(self, variant_label: Tuple[ord], base_scripts: Set[str]) -> bool:
        for char in variant_label:
            script = self.unidb.get_script(char)
            if script not in base_scripts:
                return False
        return True

    def get_base_scripts(self, label: Tuple[int]):
        scripts = set()
        for c in label:
            script = self.unidb.get_script(c)
            if script != self.UNKNOWN_SCRIPT:
                scripts.add(self.unidb.get_script(c))
        return get_permitted_scripts(scripts)
