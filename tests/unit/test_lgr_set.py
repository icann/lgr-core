# -*- coding: utf-8 -*-
"""
test_lgr_set.py - Unit testing of LGR tools/merge_set module.
"""
from __future__ import unicode_literals

import unittest
import re
import os
from datetime import date

from lgr.action import Action
from lgr.rule import Rule
from lgr.matcher import RuleMatcher, ClassMatcher, StartMatcher
from lgr.classes import Class, UnionClass
from lgr.core import LGR

from lgr.parser.xml_parser import XMLParser

from lgr.tools.merge_set import (rename_action,
                                 rename_rule,
                                 rename_class,
                                 merge_actions,
                                 merge_rules,
                                 merge_version,
                                 merge_description,
                                 merge_metadata,
                                 merge_references,
                                 merge_chars,
                                 merge_lgr_set)

RESOURCE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'inputs', 'set')


class TestLGRSet(unittest.TestCase):

    def setUp(self):
        parser = XMLParser(os.path.join(RESOURCE_DIR, 'lgr-script1.xml'))
        self.lgr_1 = parser.parse_document()
        parser = XMLParser(os.path.join(RESOURCE_DIR, 'lgr-script2.xml'))
        self.lgr_2 = parser.parse_document()
        self.lgr_set = [self.lgr_1, self.lgr_2]

    def test_rename_action_not_msr2(self):
        action = Action(match='rule-name', disp='invalid')
        action_xml = """<action disp="invalid" match="rule-name"/>"""
        new_action, new_action_xml = rename_action(action, action_xml, 'fr')

        self.assertEqual(new_action.match, 'fr-rule-name')
        self.assertIsNotNone(re.search(r'''match="fr-rule-name"''', new_action_xml))

        action = Action(not_match='rule-name', disp='invalid')
        action_xml = """<action disp="invalid" not-match="rule-name"/>"""
        new_action, new_action_xml = rename_action(action, action_xml, 'fr')

        self.assertEqual(new_action.not_match, 'fr-rule-name')
        self.assertIsNotNone(re.search(r'''not-match="fr-rule-name"''', new_action_xml))

    def test_rename_action_msr2(self):
        action = Action(match='leading-combining-mark', disp='invalid')
        action_xml = """<action disp="invalid" match="leading-combining-mark"/>"""
        new_action, new_action_xml = rename_action(action, action_xml, 'fr')

        self.assertEqual(new_action.match, 'Common-leading-combining-mark')
        self.assertIsNotNone(re.search(r'''match="Common-leading-combining-mark"''', new_action_xml))

        action = Action(not_match='leading-combining-mark', disp='invalid')
        action_xml = """<action disp="invalid" not-match="leading-combining-mark"/>"""
        new_action, new_action_xml = rename_action(action, action_xml, 'fr')

        self.assertEqual(new_action.not_match, 'Common-leading-combining-mark')
        self.assertIsNotNone(re.search(r'''not-match="Common-leading-combining-mark"''', new_action_xml))

    def test_merge_actions(self):
        merged_lgr = LGR()

        lgr = LGR()
        lgr.add_action(Action(match='rule-name', disp='invalid'))
        lgr.actions_xml.append("""<action disp="invalid" match="rule-name"/>""")

        merge_actions(lgr, 'fr', merged_lgr)

        self.assertEqual(len(merged_lgr.actions), 1)
        self.assertEqual(len(merged_lgr.actions_xml), 1)
        self.assertEqual(merged_lgr.actions[0].match, 'fr-rule-name')

        # Default action should not be merged
        lgr = LGR()
        lgr.add_action(Action(disp='invalid', comment="Default action for invalid", any_variant=['invalid']))
        lgr.actions_xml.append("""<action disp="invalid" match="rule-name"/>""")

        merge_actions(lgr, 'fr', merged_lgr)

        self.assertEqual(len(merged_lgr.actions), 1)
        self.assertEqual(len(merged_lgr.actions_xml), 1)
        self.assertEqual(merged_lgr.actions[0].match, 'fr-rule-name')

    def test_rename_rule_not_msr2(self):
        rule = Rule(name='rule-name')
        rule.add_child(RuleMatcher(Rule(by_ref='rule2-name'), count=42))
        rule_xml = """<rule name="rule-name"><rule by-ref="rule2-name" count=42/></rule>"""
        new_rule_name, new_rule_xml = rename_rule(rule, rule_xml, 'fr')

        self.assertEqual(new_rule_name, 'fr-rule-name')
        self.assertIsNotNone(re.search(r'''name="fr-rule-name"''', new_rule_xml))
        self.assertIsNotNone(re.search(r'''by-ref="fr-rule2-name" count=42''', new_rule_xml))

    def test_rename_rule_msr2(self):
        rule = Rule(name='leading-combining-mark')
        rule.add_child(RuleMatcher(Rule(by_ref='rule2-name'), count=42))
        rule_xml = """<rule name="leading-combining-mark"><rule by-ref="rule2-name" count=42/></rule>"""
        new_rule_name, new_rule_xml = rename_rule(rule, rule_xml, 'fr')

        self.assertEqual(new_rule_name, 'Common-leading-combining-mark')
        self.assertIsNotNone(re.search(r'''name="Common-leading-combining-mark"''', new_rule_xml))
        self.assertIsNotNone(re.search(r'''by-ref="fr-rule2-name" count=42''', new_rule_xml))

        rule = Rule(name='rule-name')
        rule.add_child(RuleMatcher(Rule(by_ref='leading-combining-mark'), count=42))
        rule_xml = """
<rule name="rule-name"><rule by-ref="leading-combining-mark" count=42/></rule>
        """
        new_rule_name, new_rule_xml = rename_rule(rule, rule_xml, 'fr')

        self.assertEqual(new_rule_name, 'fr-rule-name')
        self.assertIsNotNone(re.search(r'''name="fr-rule-name"''', new_rule_xml))
        self.assertIsNotNone(re.search(r'''by-ref="Common-leading-combining-mark" count=42''', new_rule_xml))

    def test_rename_rule_with_anonymous_class(self):
        rule = Rule(name='rule-name')
        anonymous_class = UnionClass()
        anonymous_class.add_child(Class(by_ref='class-by-ref'))
        anonymous_class.add_child(Class(from_tag='class-from-tag'))
        rule.add_child(ClassMatcher(anonymous_class))
        rule_xml = """
<rule name="rule-name">
    <union>
        <class by-ref="class-by-ref"/>
        <class from-tag="class-from-tag"/>
    </union>
</rule>
"""
        new_rule_name, new_rule_xml = rename_rule(rule, rule_xml, 'fr')

        self.assertEqual(new_rule_name, 'fr-rule-name')
        self.assertIsNotNone(re.search(r'''name="fr-rule-name"''', new_rule_xml))
        self.assertIsNotNone(re.search(r'''by-ref="fr-class-by-ref"''', new_rule_xml))
        self.assertIsNotNone(re.search(r'''from-tag="fr-class-from-tag"''', new_rule_xml))

    def test_merge_rules(self):
        merged_lgr = LGR()

        lgr = LGR()
        rule = Rule(name='rule-name')
        anonymous_class = UnionClass()
        anonymous_class.add_child(Class(codepoints=[0x0061]))
        anonymous_class.add_child(Class(codepoints=[0x0062]))
        rule.add_child(ClassMatcher(anonymous_class))
        rule_xml = """
<rule name="rule-name">
    <union>
        <class>0x0061</class>
        <class>0x0062</class>
    </union>
</rule>
"""
        lgr.add_rule(rule)
        lgr.rules_xml.append(rule_xml)

        merge_rules(lgr, 'fr', merged_lgr)

        self.assertEqual(len(merged_lgr.rules), 1)
        self.assertEqual(len(merged_lgr.rules_xml), 1)
        self.assertEqual(merged_lgr.rules[0], 'fr-rule-name')

        # Merging is idempotent
        merge_rules(lgr, 'fr', merged_lgr)
        self.assertEqual(len(merged_lgr.rules), 1)
        self.assertEqual(len(merged_lgr.rules_xml), 1)
        self.assertEqual(merged_lgr.rules[0], 'fr-rule-name')

        # Not with different script
        merge_rules(lgr, 'en', merged_lgr)
        self.assertEqual(len(merged_lgr.rules), 2)
        self.assertEqual(len(merged_lgr.rules_xml), 2)
        self.assertEqual(merged_lgr.rules[1], 'en-rule-name')

        # Nor with MSR2
        lgr = LGR()
        rule = Rule(name='leading-combining-mark')
        rule.add_child(StartMatcher())
        anonymous_class = UnionClass()
        anonymous_class.add_child(Class(unicode_property="gc:Mn"))
        anonymous_class.add_child(Class(unicode_property="gc:Mc"))
        lgr.add_rule(rule)
        lgr.rules_xml.append("""
<rule name="leading-combining-mark" comment="WLE Rule1: default WLE rule matching labels with leading combining marks ⍟">
    <start />
    <union>
        <class property="gc:Mn" />
        <class property="gc:Mc" />
    </union>
</rule>
""")

        merge_rules(lgr, 'fr', merged_lgr)
        self.assertEqual(len(merged_lgr.rules), 3)
        self.assertEqual(len(merged_lgr.rules_xml), 3)
        self.assertEqual(merged_lgr.rules[2], 'Common-leading-combining-mark')

        merge_rules(lgr, 'fr', merged_lgr)
        self.assertEqual(len(merged_lgr.rules), 3)
        self.assertEqual(len(merged_lgr.rules_xml), 3)
        self.assertEqual(merged_lgr.rules[2], 'Common-leading-combining-mark')

    def test_rename_class(self):
        clz = UnionClass(name='class-name')
        clz.add_child(Class(by_ref='class-by-ref'))
        clz.add_child(Class(from_tag='class-from-tag'))
        clz_xml = """
<union name="class-name">
    <class by-ref="class-by-ref"/>
    <class from-tag="class-from-tag"/>
</union>
"""
        new_class_name, new_class_xml = rename_class(clz, clz_xml, 'fr')

        self.assertEqual(new_class_name, 'fr-class-name')
        self.assertIsNotNone(re.search(r'''name="fr-class-name"''', new_class_xml))
        self.assertIsNotNone(re.search(r'''by-ref="fr-class-by-ref"''', new_class_xml))
        self.assertIsNotNone(re.search(r'''from-tag="fr-class-from-tag"''', new_class_xml))

    def test_merge_version(self):
        version = merge_version(self.lgr_set)
        self.assertEqual(set(version.value.split('|')), {'1', '2'})
        self.assertEqual(set(version.comment.split('|')), {'LGR 1 for fr script', 'LGR 2 for khmer script'})

    def test_merge_description(self):
        description = merge_description(self.lgr_set)

        merged_description_placeholder = """
Script: '{script}' - MIME-type: '{type}':
{value}
"""
        self.assertEqual(set(description.value.split('----\n')),
                         {merged_description_placeholder.format(script='fr',
                                                                type='text/plain',
                                                                value=self.lgr_1.metadata.description.value),
                          merged_description_placeholder.format(script='und-Khmer',
                                                                type='text/html',
                                                                value=self.lgr_2.metadata.description.value)})
        self.assertEqual(description.description_type, 'text/enriched')

    def test_merge_metadata(self):
        metadata = merge_metadata(self.lgr_set)
        self._test_merged_metadata(metadata)

    def test_merge_references(self):
        merged_lgr = LGR()

        reference_mapping = {}
        merge_references(self.lgr_1, 'fr', merged_lgr, reference_mapping)

        self.assertEqual(len(reference_mapping), 1)
        self.assertIn('fr', reference_mapping)
        self.assertEqual(reference_mapping['fr'], {})

        merge_references(self.lgr_2, 'und-Khmer', merged_lgr, reference_mapping)

        self.assertEqual(len(reference_mapping), 2)
        self.assertIn('und-Khmer', reference_mapping)
        self.assertEqual(reference_mapping['und-Khmer'], {
            '0': '3',
            '1': '4',  # Generated
        })

    def test_merge_chars(self):
        merged_lgr = LGR()

        # Need to merge references first - OK since tested in previous test
        reference_mapping = {}
        merge_references(self.lgr_1, 'fr', merged_lgr, reference_mapping)
        merge_references(self.lgr_2, 'und-Khmer', merged_lgr, reference_mapping)

        merge_chars(self.lgr_1, 'fr', merged_lgr, reference_mapping)

        # Simple variant changed to blocked
        cp = merged_lgr.get_char(0x0041)
        self.assertIn('1', cp.references)

        variants = list(cp.get_variants())
        self.assertEqual(len(variants), 1)
        var = variants[0]
        self.assertEqual(var.cp, (0x0061, )),
        self.assertEqual(var.type, 'blocked')

        # Complete merge
        merge_chars(self.lgr_2, 'und-Khmer', merged_lgr, reference_mapping)

        self._test_merged_chars(merged_lgr)

    def test_merge_lgrs(self):
        merged_lgr = merge_lgr_set(self.lgr_set, 'LGR Set')

        self._test_merged_chars(merged_lgr)
        self._test_merged_metadata(merged_lgr.metadata)

        self.assertEqual(merged_lgr.name, 'LGR Set')

    def _test_merged_chars(self, merged_lgr):
        # Overlapping char with variant changed to blocked
        cp = merged_lgr.get_char(0x0061)

        variants = list(cp.get_variants())
        self.assertEqual(len(variants), 2)
        var = variants[0]
        self.assertEqual(var.cp, (0x0041, )),
        self.assertEqual(var.type, 'blocked')
        var = variants[1]
        self.assertEqual(var.cp, (0x1782,)),
        self.assertEqual(var.type, 'blocked')

        # Transitive variants added to original codepoint
        cp = merged_lgr.get_char(0x0041)

        variants = list(cp.get_variants())
        self.assertEqual(len(variants), 2)
        var = variants[0]
        self.assertEqual(var.cp, (0x0061, )),
        self.assertEqual(var.type, 'blocked')
        var = variants[1]
        self.assertEqual(var.cp, (0x1782,)),
        self.assertEqual(var.type, 'blocked')
        self.assertEqual(var.comment, 'New variant for merge to keep transitivity')

        # Test renaming of tags
        cp = merged_lgr.get_char(0x17A1)
        self.assertIn('und-Khmer-base-only', cp.tags)
        self.assertIn('und-Khmer-consonant', cp.tags)

        # Test renaming of when/not-when
        cp = merged_lgr.get_char((0x17D2, 0x178A))
        self.assertEqual(cp.when, 'und-Khmer-follows-consonant')

        variants = list(cp.get_variants())
        var = variants[0]
        self.assertEqual(var.when, 'und-Khmer-follows-consonant')

        cp = merged_lgr.get_char((0x17D2, 0x178F))
        self.assertEqual(cp.not_when, 'und-Khmer-follows-consonant')

        variants = list(cp.get_variants())
        var = variants[0]
        self.assertEqual(var.not_when, 'und-Khmer-follows-consonant')

        # Test reference handling
        cp = merged_lgr.get_char(0x1783)
        self.assertSetEqual(set(cp.references), {'2', '4'})

        # On variant
        cp = merged_lgr.get_char(0x0061)

        var = list(cp.get_variants())[-1]
        self.assertSetEqual(set(var.references), {'3'})

        # Test tags handling
        cp = merged_lgr.get_char(0x0063)
        self.assertListEqual(cp.tags, ['fr-first-tag', 'und-Khmer-second-tag'])

    def _test_merged_metadata(self, metadata):
        self.assertEqual(len(metadata.scopes), 1)
        scope = metadata.scopes[0]
        self.assertEqual(scope.value, '.')
        self.assertEqual(scope.scope_type, 'domain')

        self.assertEqual(len(metadata.languages), 2)
        self.assertNotEqual(metadata.languages[0], metadata.languages[1])
        for lang in metadata.languages:
            self.assertIn(lang, ['fr', 'und-Khmer'])

        self.assertEqual(metadata.validity_start, '2017-06-01')
        self.assertEqual(metadata.validity_end, '2020-06-01')
        self.assertEqual(metadata.unicode_version, '6.3.0')
        self.assertEqual(metadata.date, date.today().isoformat())

if __name__ == '__main__':
    import logging
    logging.getLogger('lgr').addHandler(logging.NullHandler())
    unittest.main()
