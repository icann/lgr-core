from typing import Set, Tuple

from munidata.database import UnicodeDatabase

from lgr.char import Repertoire


def get_permitted_scripts(base_scripts: Set[str]):
    permitted_scripts = base_scripts.copy()
    if 'Katakana' in base_scripts or 'Hiragana' in base_scripts:
        permitted_scripts.update({'Han', 'Latin', 'Katakana', 'Hiragana'})
    elif 'Hangul' in base_scripts:
        permitted_scripts.update({'Han', 'Latin'})
    if 'Han' in base_scripts:
        permitted_scripts.update({'Latin'})

    return permitted_scripts


class BaseMixedScriptsVariantFilter:
    def __init__(self, unidb: UnicodeDatabase) -> None:
        super().__init__()
        self.unidb = unidb
        self.base_scripts: Set[str] = set()

    def cp_in_scripts(self, cp: Tuple[ord], scripts) -> bool:
        for char in cp:
            script = self.unidb.get_script(char)
            if script not in scripts:
                return False
        return True

    def cp_in_base_scripts(self, cp: Tuple[ord]) -> bool:
        return self.cp_in_scripts(cp, self.base_scripts)

    def cp_in_other_scripts(self, cp: Tuple[ord]) -> bool:
        return False


class MixedScriptsVariantFilter(BaseMixedScriptsVariantFilter):
    UNKNOWN_SCRIPT = 'Common'

    def __init__(self, label: Tuple[int], repertoire: Repertoire, unidb: UnicodeDatabase) -> None:
        super().__init__(unidb)
        self.base_scripts: Set[str] = self._get_base_scripts(label)
        self.other_scripts: Set[str] = self._get_scripts_for_variants(label, repertoire)

    def cp_in_other_scripts(self, cp: Tuple[ord]) -> bool:
        return self.cp_in_scripts(cp, self.other_scripts)

    def _get_base_scripts(self, label: Tuple[int]) -> Set[str]:
        scripts = set()
        for c in label:
            script = self.unidb.get_script(c)
            if script != self.UNKNOWN_SCRIPT:
                scripts.add(self.unidb.get_script(c))
        return get_permitted_scripts(scripts)

    def get_filter_for_other_script(self, script):
        f = BaseMixedScriptsVariantFilter(self.unidb)
        f.base_scripts = get_permitted_scripts({script})
        return f

    def _get_scripts_for_variants(self, label: Tuple[int], repertoire: Repertoire) -> Set[str]:
        """
        Get a set of scripts that can be used for variant generation when filtering cross-script variants.

        :param label: The label to generate the variants of.
        :param repertoire: The LGR repertoire
        :return: A set of scripts to keep for computation when filtering cross-script variants.
        """
        scripts = None
        current_label = label

        for c in label:
            scripts_for_char = set()
            for char in repertoire.get_chars_from_prefix(c, only_variants=True):
                # Ensure prefix is valid for label
                if not char.is_prefix_of(current_label):
                    continue

                for v in char.get_variants():
                    for cp in v.cp:
                        scripts_for_char.add(self.unidb.get_script(cp))

            scripts_for_char -= set(self.UNKNOWN_SCRIPT)
            if scripts is None:
                scripts = set(scripts_for_char)
            else:
                scripts.intersection_update(scripts_for_char)
            current_label = current_label[1:]

            if scripts == self.base_scripts:
                # no other scripts than base script
                return set()

        return scripts - self.base_scripts
