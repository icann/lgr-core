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

    def __init__(self, label: Tuple[int], unidb: UnicodeDatabase) -> None:
        super().__init__()
        self.unidb = unidb
        self.base_scripts: Set[str] = self._get_base_scripts(label)

    def cp_in_scripts(self, cp: Tuple[ord]) -> bool:
        for char in cp:
            script = self.unidb.get_script(char)
            if script not in self.base_scripts:
                return False
        return True

    def _get_base_scripts(self, label: Tuple[int]) -> Set[str]:
        scripts = set()
        for c in label:
            script = self.unidb.get_script(c)
            if script != self.UNKNOWN_SCRIPT:
                scripts.add(self.unidb.get_script(c))
        return get_permitted_scripts(scripts)
