import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'tools/skills/engineering/wl-compass-local-test/scripts/local-test-down.sh'


class CleanupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='wl-down-fixture-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.base = self.root / 'state'; self.base.mkdir()
        self.artifacts = self.base / 'task/artifacts'; self.artifacts.mkdir(parents=True)
        (self.artifacts / 'evidence.txt').write_text('keep')
        self.bin = self.root / 'bin'; self.bin.mkdir()
        self.calls = self.root / 'calls'
        stubs = {
            'docker': 'printf "docker %s\\n" "$*" >> "$STUB_CALLS"',
            'lsof': 'case "$*" in *cwd*) printf "p424242\\nn%s\\n" "$STUB_CWD";; *) [ "${STUB_LISTEN:-0}" = 1 ] && printf "424242\\n";; esac\nexit 0',
            'ps': 'printf "%s\\n" "${STUB_COMMAND:-java -jar compass-backend-service.jar}"',
        }
        for name, code in stubs.items():
            path = self.bin / name
            path.write_text('#!/bin/bash\n' + code + '\n'); path.chmod(0o755)
        self.env = dict(os.environ, PATH=f'{self.bin}:/usr/bin:/bin', COMPASS_LOCAL_TEST_HOME=str(self.base),
                        STUB_CALLS=str(self.calls), STUB_CWD=str(self.root / 'work/task/backend-service'))

    def run_down(self, *args):
        # Bash kill is a builtin: override/export it too, so even a regression cannot signal a real PID.
        command = 'kill() { printf "kill %s\\n" "$*" >> "$STUB_CALLS"; }; export -f kill; bash "$@"'
        return subprocess.run(['/bin/bash', '-c', command, 'fixture', str(SCRIPT), *args],
                              cwd=self.root, env=self.env, capture_output=True, text=True)

    def call_text(self):
        return self.calls.read_text() if self.calls.exists() else ''

    def test_default_preserves_all_evidence_and_shared_mq(self):
        result = self.run_down('task')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.artifacts / 'evidence.txt').is_file())
        self.assertNotIn('docker', self.call_text())

    def test_explicit_delete_only_removes_selected_fixture(self):
        other = self.base / 'other'; other.mkdir(); (other / 'keep').write_text('other')
        result = self.run_down('task', '--delete-artifacts')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.artifacts.exists())
        self.assertTrue((other / 'keep').exists())
        self.assertNotIn('docker', self.call_text())

    def test_purge_never_implies_evidence_deletion(self):
        result = self.run_down('task', '--purge')
        self.assertNotEqual(result.returncode, 0)  # Shared-user confirmation is mandatory.
        self.assertTrue(self.artifacts.is_dir())
        self.assertEqual(self.call_text(), '')
        result = self.run_down('task', '--purge', '--stop-shared-mq', '--confirm-shared-unused')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(self.artifacts.is_dir())
        self.assertIn('docker stop', self.call_text())
        self.assertIn('docker volume rm wl-rmq-conf', self.call_text())

    def test_shared_stop_requires_confirmation_and_does_not_remove_volumes(self):
        self.assertNotEqual(self.run_down('task', '--stop-shared-mq').returncode, 0)
        self.assertEqual(self.call_text(), '')
        result = self.run_down('task', '--stop-shared-mq', '--confirm-shared-unused')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('docker stop', self.call_text())
        self.assertNotIn('volume rm', self.call_text())
        self.assertTrue(self.artifacts.exists())

    def test_traversal_absolute_reserved_and_unknown_arguments_rejected_before_actions(self):
        for args in (('../task',), ('..',), (str(self.base / 'task'),), ('_last_logs',), ('task', '--unknown'), ('task', 'other')):
            with self.subTest(args=args):
                self.assertNotEqual(self.run_down(*args, '--delete-artifacts').returncode, 0)
                self.assertTrue(self.artifacts.exists())
                self.assertEqual(self.call_text(), '')

    def test_symlink_root_base_and_nested_evidence_are_rejected(self):
        outside = self.root / 'outside'; outside.mkdir(); (outside / 'keep').write_text('safe')
        (self.base / 'linked').symlink_to(outside, target_is_directory=True)
        self.assertNotEqual(self.run_down('linked', '--delete-artifacts').returncode, 0)
        (self.artifacts / 'link').symlink_to(outside, target_is_directory=True)
        self.assertNotEqual(self.run_down('task', '--delete-artifacts').returncode, 0)
        self.assertTrue((outside / 'keep').exists())
        alias = self.root / 'alias'; alias.symlink_to(self.base, target_is_directory=True)
        self.env['COMPASS_LOCAL_TEST_HOME'] = str(alias)
        self.assertNotEqual(self.run_down('task', '--delete-artifacts').returncode, 0)
        self.assertEqual(self.call_text(), '')

    def test_absolute_jar_path_proves_ownership_when_launcher_cwd_is_elsewhere(self):
        self.env['STUB_LISTEN'] = '1'
        self.env['STUB_CWD'] = str(self.root / 'launcher')
        self.env['STUB_COMMAND'] = f'java -jar {self.root}/work/task/backend-service/target/compass-backend-service.jar'
        self.assertEqual(self.run_down('task').returncode, 0)
        self.assertIn('kill 424242', self.call_text())

    def test_only_matching_requirement_process_is_stopped_using_stub_kill(self):
        self.env['STUB_LISTEN'] = '1'
        self.env['STUB_CWD'] = str(self.root / 'work/other/backend-service')
        self.assertEqual(self.run_down('task').returncode, 0)
        self.assertNotIn('kill', self.call_text())
        self.env['STUB_CWD'] = str(self.root / 'work/task/backend-service')
        result = self.run_down('task')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('kill 424242', self.call_text())
        self.assertTrue(self.artifacts.exists())


if __name__ == '__main__':
    unittest.main()
