import tempfile
import unittest
from pathlib import Path
from skill_inventory import scan


class InventoryTest(unittest.TestCase):
    def test_aliases_share_source_but_names_do_not_merge(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            source = root / 'source' / 'review'
            source.mkdir(parents=True)
            (source / 'SKILL.md').write_text('---\nname: review\ndescription: Review code\n---\n', encoding='utf-8')
            a = root / 'a'; a.mkdir(); (a / 'review').symlink_to(source, target_is_directory=True)
            b = root / 'b'; b.mkdir(); (b / 'review').symlink_to(source, target_is_directory=True)
            other = root / 'other' / 'review'; other.mkdir(parents=True)
            (other / 'SKILL.md').write_text('---\nname: review\ndescription: Another\n---\n', encoding='utf-8')
            (a / 'broken').symlink_to(root / 'missing')
            result = scan([('A', a), ('B', b), ('C', other.parent)])
            self.assertEqual(len(result['skills']), 2)
            linked = next(x for x in result['skills'] if len(x['entries']) == 2)
            self.assertTrue(all(e['symlink'] for e in linked['entries']))
            self.assertEqual(len(result['warnings']), 1)


if __name__ == '__main__':
    unittest.main()
