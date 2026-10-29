"""Focused role-runtime tests. All Herdr operations use a temporary fake executable."""

from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / 'tools/scripts/role_runtime.py'
spec = importlib.util.spec_from_file_location('role_runtime', SCRIPT)
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)

# This subprocess fixture implements only the contract consumed by the runtime.
FAKE_HERDR = r'''
import fcntl
import json
import os
from pathlib import Path
import sys
import time

root = Path(os.environ['FAKE_ROOT'])
args = sys.argv[1:]
if '--help' in args:
    if os.environ.get('FAKE_MODE') == 'bad-help':
        print('unsupported')
    else:
        print('agent list agent get <target> --current --direction down right --cwd --no-focus '
              '--kind pi --pane AGENT_ARG <TARGET> <TEXT> --wait --timeout '
              'tab get <tab_id> tab list pane list tab close --workspace --label')
    raise SystemExit(0)
with (root / 'fake.lock').open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    path = root / 'fake.json'
    state = json.loads(path.read_text()) if path.exists() else {'agents': [], 'calls': []}
    state.setdefault('tabs', [])
    state.setdefault('panes', [])
    state['calls'].append(args)
    mode = os.environ.get('FAKE_MODE', '')
    if args[:2] == ['agent', 'list']:
        result = {'agents': [{k: v for k, v in a.items() if k != 'interactive_ready'}
                             for a in state['agents']]}
    elif args[:2] == ['agent', 'get']:
        agent = dict(next(a for a in state['agents'] if a['name'] == args[2]))
        if mode == 'get-failed':
            raise SystemExit(3)
        if mode == 'get-mismatch':
            agent['agent_session'] = {'value': 'unexpected-session'}
        if mode == 'get-blocked':
            agent['agent_status'] = 'blocked'
        if mode == 'get-missing-ready':
            agent.pop('interactive_ready', None)
        result = {'agent': agent}
    elif args[:2] == ['pane', 'split']:
        result = {'pane': {'pane_id': 'pane-' + str(len(state['calls']))}}
    elif args[:2] == ['tab', 'create']:
        workspace = args[args.index('--workspace') + 1]
        cwd = args[args.index('--cwd') + 1]
        tab_id = 'tab-' + str(len(state['calls']))
        tab = {'tab_id': tab_id, 'workspace_id': workspace, 'pane_count': 1,
               'label': args[args.index('--label') + 1]}
        pane = {'pane_id': 'root-' + tab_id, 'workspace_id': workspace, 'tab_id': tab_id, 'cwd': cwd}
        state['tabs'].append(tab)
        state['panes'].append(pane)
        result = {'tab': tab, 'root_pane': pane}
    elif args[:2] == ['tab', 'list']:
        workspace = args[args.index('--workspace') + 1]
        result = {'tabs': [t for t in state['tabs'] if t['workspace_id'] == workspace]}
    elif args[:2] == ['pane', 'list']:
        workspace = args[args.index('--workspace') + 1]
        result = {'panes': [p for p in state['panes'] if p['workspace_id'] == workspace]}
    elif args[:2] == ['tab', 'get']:
        result = {'tab': next(t for t in state['tabs'] if t['tab_id'] == args[2])}
    elif args[:2] == ['tab', 'close']:
        if mode == 'close-failed':
            path.write_text(json.dumps(state))
            raise SystemExit(8)
        if mode != 'close-noop':
            panes = [p['pane_id'] for p in state['panes'] if p['tab_id'] == args[2]]
            state['tabs'] = [t for t in state['tabs'] if t['tab_id'] != args[2]]
            state['panes'] = [p for p in state['panes'] if p['tab_id'] != args[2]]
            state['agents'] = [a for a in state['agents'] if a['pane_id'] not in panes]
        result = {'type': 'tab_closed'}
        if mode == 'close-ambiguous':
            path.write_text(json.dumps(state))
            raise SystemExit(9)
    elif args[:2] == ['agent', 'start']:
        name = args[2]
        if len(name) > 32:
            raise SystemExit(4)
        pane = args[args.index('--pane') + 1]
        root_pane = next((p for p in state['panes'] if p['pane_id'] == pane), None)
        if root_pane:
            cwd = root_pane['cwd']
        else:
            split = next(c for c in reversed(state['calls']) if c[:2] == ['pane', 'split'])
            cwd = split[split.index('--cwd') + 1]
        agent = {'agent': 'pi', 'name': name, 'pane_id': pane, 'cwd': cwd,
                 'agent_session': {'value': '/sessions/' + name, 'path-kind': 'path'},
                 'agent_status': 'idle', 'interactive_ready': True}
        if root_pane:
            agent.update(tab_id=root_pane['tab_id'], workspace_id=root_pane['workspace_id'])
        state['agents'].append(agent)
        if mode == 'wrong-cwd':
            agent['cwd'] = '/wrong-project'
        if mode == 'missing-session':
            agent.pop('agent_session')
        if mode == 'not-ready':
            agent['interactive_ready'] = False
        result = {'agent': agent, 'argv': ['pi', '--thinking', 'low' if mode == 'low' else 'high']}
    elif args[:2] == ['agent', 'prompt']:
        result = {'agent': next(a for a in state['agents'] if a['name'] == args[2])}
    else:
        raise SystemExit(2)
    path.write_text(json.dumps(state))
if args[:2] == ['agent', 'prompt']:
    (root / 'prompt-entered').write_text(args[3])
    if mode == 'fail-prompt':
        raise SystemExit(7)
    if mode == 'bad-json':
        print('not-json')
        raise SystemExit(0)
    if mode == 'sleep':
        parent = os.getppid()
        deadline = time.monotonic() + 30
        while os.getppid() == parent and time.monotonic() < deadline:
            time.sleep(.02)
print(json.dumps({'result': result}))
'''


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.state_dir = self.root / 'state'
        self.store = runtime.Store(self.state_dir)
        fake = self.root / 'herdr'
        fake.write_text('#!' + sys.executable + '\n' + FAKE_HERDR)
        fake.chmod(0o700)
        self.env = dict(os.environ, HERDR_ENV='1', HERDR_WORKSPACE_ID='workspace-explicit',
                        FAKE_ROOT=str(self.root),
                        PATH=str(self.root) + os.pathsep + os.environ.get('PATH', ''))
        self.environment = patch.dict(os.environ, self.env)
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def package(self, task_id='one', **changes):
        value = dict(id=task_id, project=str(self.root), role='developer', goal='Implement approved task',
                     non_goals=['No deployment'], allowed_paths=[str(self.root / 'output.py')],
                     inputs=['approved requirement reference'], acceptance=['Focused tests pass'])
        value.update(changes)
        return value

    def create(self, task_id='one', **changes):
        return runtime.create(self.store, self.package(task_id, **changes))

    def dispatch(self, task_id='one', **kwargs):
        return runtime.dispatch(self.store, task_id, runtime.Herdr(), **kwargs)

    def state(self):
        return self.store.read()

    def fake_state(self):
        path = self.root / 'fake.json'
        return json.loads(path.read_text()) if path.exists() else {'agents': [], 'calls': []}

    def change_agent(self, **fields):
        data = self.fake_state()
        data['agents'][-1].update(fields)
        (self.root / 'fake.json').write_text(json.dumps(data))

    def report(self, status='submitted', **changes):
        task = self.state()['tasks']['one']
        args = dict(status=status, summary='Focused test result', evidence=['/tmp/test-result.log'],
                    next_action='PM review', instance=task['instance']['name'],
                    session=task['instance']['session']['value'], dispatch_id=task['attempts'][-1]['id'])
        args.update(changes)
        return runtime.checkpoint(self.store, 'one', **args)

    def cli(self, *args, check=True, env=None, full=True):
        result = subprocess.run([sys.executable, str(SCRIPT), '--state-dir', str(self.state_dir),
                                 *(['--full'] if full else []), *args],
                                capture_output=True, text=True, env=env or self.env, timeout=15)
        if check:
            self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def process(self, *args, env=None):
        return subprocess.Popen([sys.executable, str(SCRIPT), '--state-dir', str(self.state_dir), *args],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                env=env or self.env)

    def wait_prompt(self):
        deadline = time.monotonic() + 5
        while not (self.root / 'prompt-entered').exists():
            if time.monotonic() > deadline:
                self.fail('Fake prompt not entered')
            time.sleep(.02)

    def test_package_validation_and_duplicate_preserve_history(self):
        for changes in ({'goal': ''}, {'project': '.'}, {'role': '../developer'},
                        {'acceptance': []}, {'allowed_paths': ['relative']},
                        {'inputs': 'not-list'}, {'id': 'bad/id'}, {'extra': True}):
            with self.subTest(changes=changes), self.assertRaises(runtime.RuntimeError_):
                runtime.create(self.store, self.package(**changes))
        self.create()
        before = self.store.path.read_bytes()
        with self.assertRaises(runtime.RuntimeError_):
            self.create()
        self.assertEqual(before, self.store.path.read_bytes())
        self.create('two')
        self.assertEqual([e['task'] for e in self.state()['events']], ['one', 'two'])

    def test_manual_path_and_default_ignored_location(self):
        manual = self.root / 'ROLE.md'
        manual.write_text('Read this only when needed')
        task = self.create(role=str(manual))
        self.assertEqual(task['role'], str(manual))
        self.assertIn('/.local/records/', str(runtime.DEFAULT_STATE_DIR))

    def test_corrupt_state_is_not_replaced(self):
        self.state_dir.mkdir()
        self.store.path.write_text('{broken')
        with self.assertRaises(runtime.RuntimeError_):
            self.create()
        self.assertEqual(self.store.path.read_text(), '{broken')

    def test_atomic_failure_keeps_old_state(self):
        self.create()
        before = self.store.path.read_bytes()
        with patch.object(runtime.os, 'replace', side_effect=OSError('disk failure')):
            with self.assertRaises(OSError):
                self.create('two')
        self.assertEqual(before, self.store.path.read_bytes())
        self.assertFalse(list(self.state_dir.glob('.state-*')))

    def test_read_commands_do_not_create_state_or_call_herdr(self):
        self.assertEqual(json.loads(self.cli('list').stdout), [])
        self.assertFalse(self.state_dir.exists())
        self.create()
        before = self.store.path.read_bytes()
        self.cli('show', 'one')
        recovered = json.loads(self.cli('recover', 'one').stdout)
        self.assertIn('no full Pi replay', recovered['recovery_semantics'])
        self.assertEqual(self.store.path.read_bytes(), before)
        self.assertFalse((self.root / 'fake.json').exists())

    def test_dispatch_gate_help_and_confirm_flags(self):
        self.create()
        with patch.dict(os.environ, HERDR_ENV='0'):
            with self.assertRaises(runtime.RuntimeError_):
                self.dispatch()
        for flags in ({'resume': True}, {'confirm_continue': True}):
            with self.assertRaises(runtime.RuntimeError_):
                self.dispatch(**flags)
        with patch.dict(os.environ, FAKE_MODE='bad-help'):
            with self.assertRaises(runtime.RuntimeError_):
                self.dispatch()
        self.assertEqual(self.state()['tasks']['one']['status'], 'needs-reconcile')
        self.assertEqual(self.fake_state()['calls'], [])

    def test_dispatch_argv_prompt_identity_and_explicit_delivery(self):
        self.create()
        task = self.dispatch(direction='right')
        calls = self.fake_state()['calls']
        split = next(c for c in calls if c[:2] == ['pane', 'split'])
        self.assertEqual(split, ['pane', 'split', '--current', '--direction', 'right',
                                 '--cwd', str(self.root), '--no-focus'])
        start = next(c for c in calls if c[:2] == ['agent', 'start'])
        self.assertEqual(start[-3:], ['--', '--thinking', 'high'])
        self.assertLessEqual(len(start[2]), 32)
        self.assertTrue(start[2].startswith('role-'))
        self.assertTrue(any(c[:2] == ['agent', 'get'] for c in calls))
        self.assertEqual(task['status'], 'assigned')
        prompt = next(c for c in calls if c[:2] == ['agent', 'prompt'])
        self.assertEqual(prompt[-3:], ['--wait', '--timeout', '30000'])
        for fragment in ('Do not create subagents', 'not permission isolation', 'checkpoint',
                         'allowed_paths', '--dispatch-id', 'NOT completion', 'summary-based'):
            self.assertIn(fragment, prompt[3])
        self.assertEqual(task['instance']['session']['path-kind'], 'path')
        with self.assertRaises(runtime.RuntimeError_):
            runtime.accept(self.store, 'one', 'idle is not evidence')
        with self.assertRaises(runtime.RuntimeError_):
            self.dispatch()
        self.report('ready', evidence=[])
        self.report()
        with self.assertRaises(runtime.RuntimeError_):
            runtime.accept(self.store, 'one', ' ')
        runtime.accept(self.store, 'one', 'PM inspected test evidence against acceptance')
        self.assertEqual(self.state()['tasks']['one']['status'], 'accepted')

    def test_checkpoint_validation_latest_recovery_and_stale_identity(self):
        self.create()
        self.dispatch()
        for changes in ({'session': 'wrong'}, {'instance': 'wrong'},
                        {'dispatch_id': 'old'}, {'evidence': []}):
            with self.subTest(changes=changes), self.assertRaises(runtime.RuntimeError_):
                self.report(**changes)
        self.report('ready', evidence=[], summary='Handoff acknowledged')
        self.report('blocked', summary='Need input', next_action='PM provide input')
        summary = runtime.recover(self.store, 'one')
        self.assertEqual(summary['latest_checkpoint']['summary'], 'Need input')
        self.assertEqual(summary['evidence'], ['/tmp/test-result.log'])
        self.assertEqual(summary['next_action'], 'PM provide input')
        self.report()
        with self.assertRaises(runtime.RuntimeError_):
            self.report('ready')

    def test_reuses_only_registered_accepted_idle_instance(self):
        self.create()
        first = self.dispatch()['instance']
        self.report()
        runtime.accept(self.store, 'one', 'PM accepted evidence')
        self.create('two')
        second = self.dispatch('two')['instance']
        self.assertEqual(first, second)
        self.assertEqual(sum(c[:2] == ['agent', 'start'] for c in self.fake_state()['calls']), 1)

    def test_busy_blocked_unknown_and_not_ready_never_preempt(self):
        for fields in ({'agent_status': 'working'}, {'agent_status': 'blocked'},
                       {'agent_status': 'unknown'}, {'interactive_ready': False}):
            with self.subTest(fields=fields):
                # Each case first restores the registered instance to idle.
                if 'one' not in self.state()['tasks']:
                    self.create()
                    self.dispatch()
                self.change_agent(agent_status='idle', interactive_ready=True)
                self.change_agent(**fields)
                before = len(self.fake_state()['calls'])
                with self.assertRaises(runtime.RuntimeError_):
                    self.dispatch(resume=True, confirm_continue=True)
                new_calls = self.fake_state()['calls'][before:]
                self.assertTrue(all(c[:2] in (['agent', 'list'], ['agent', 'get']) for c in new_calls))

    def test_same_project_role_unaccepted_excludes_other_task(self):
        self.create()
        self.dispatch()
        self.create('two')
        with self.assertRaises(runtime.RuntimeError_):
            self.dispatch('two')
        self.report()
        with self.assertRaises(runtime.RuntimeError_):
            self.dispatch('two')
        self.assertEqual(self.state()['tasks']['two']['status'], 'created')

    def test_identity_mismatch_requires_explicit_replacement(self):
        self.create()
        first = self.dispatch()['instance']
        self.report()
        runtime.accept(self.store, 'one', 'PM accepted')
        self.create('two')
        self.change_agent(agent_session={'value': 'another-session', 'path-kind': 'path'})
        with self.assertRaises(runtime.RuntimeError_):
            self.dispatch('two')
        replacement = self.dispatch('two', resume=True, confirm_continue=True)['instance']
        self.assertNotEqual(first['name'], replacement['name'])
        self.assertTrue(self.state()['instances'][first['name']]['retired'])
        self.assertEqual(len(self.fake_state()['agents']), 2)  # old pane untouched

    def test_list_has_no_ready_get_verifies_each_prompt_and_reuse(self):
        self.create()
        first = self.dispatch()['instance']
        listed = runtime.Herdr().agents()
        self.assertNotIn('interactive_ready', listed[0])
        self.assertTrue(runtime.Herdr().get(first)['interactive_ready'])
        self.report()
        runtime.accept(self.store, 'one', 'PM accepted')
        self.create('two')
        before = len(self.fake_state()['calls'])
        self.assertEqual(self.dispatch('two')['instance']['name'], first['name'])
        calls = self.fake_state()['calls'][before:]
        self.assertEqual(sum(c[:2] == ['agent', 'get'] for c in calls), 2)
        prompt_index = next(i for i, c in enumerate(calls) if c[:2] == ['agent', 'prompt'])
        self.assertEqual(calls[prompt_index - 1], ['agent', 'get', first['name']])

    def test_get_failure_identity_readiness_and_blocked_do_not_send_or_replace(self):
        self.create()
        self.dispatch()
        for mode in ('get-failed', 'get-mismatch', 'get-missing-ready', 'get-blocked'):
            with self.subTest(mode=mode):
                before = len(self.fake_state()['calls'])
                with patch.dict(os.environ, FAKE_MODE=mode):
                    with self.assertRaises(runtime.RuntimeError_):
                        self.dispatch(resume=True, confirm_continue=True)
                calls = self.fake_state()['calls'][before:]
                self.assertFalse(any(c[:2] in (['pane', 'split'], ['agent', 'start'],
                                              ['agent', 'prompt']) for c in calls))
                self.assertEqual(self.state()['tasks']['one']['status'], 'needs-reconcile')

    def test_pm_rework_is_record_only_requires_explicit_resume_and_fresh_submission(self):
        self.create()
        self.dispatch()
        self.report()
        previous = self.state()['tasks']['one']
        calls = len(self.fake_state()['calls'])
        result = self.cli('rework', 'one', '--note', 'Acceptance failed: missing assertion',
                          '--next-action', 'Add failing-edge assertion and resubmit')
        task = json.loads(result.stdout)
        self.assertEqual(task['status'], 'rework')
        self.assertEqual(task['evidence'], previous['evidence'])
        self.assertEqual(task['checkpoints'], previous['checkpoints'])
        self.assertEqual(len(self.fake_state()['calls']), calls)
        recovered = runtime.recover(self.store, 'one')
        self.assertEqual(recovered['latest_rework']['note'], 'Acceptance failed: missing assertion')
        self.assertEqual(recovered['next_action'], 'Add failing-edge assertion and resubmit')
        with self.assertRaises(runtime.RuntimeError_):
            self.dispatch()
        with self.assertRaises(runtime.RuntimeError_):
            self.report()  # old execution cannot undo the PM return
        with self.assertRaises(runtime.RuntimeError_):
            runtime.accept(self.store, 'one', 'Old submission is no longer acceptable')
        self.dispatch(resume=True, confirm_continue=True)
        prompt = (self.root / 'prompt-entered').read_text()
        self.assertIn('Acceptance failed: missing assertion', prompt)
        self.assertIn('Add failing-edge assertion and resubmit', prompt)
        with self.assertRaises(runtime.RuntimeError_):
            self.report(dispatch_id=previous['attempts'][-1]['id'])
        self.report('ready', evidence=[])
        self.report(evidence=['/tmp/revised-test-result.log'])
        runtime.accept(self.store, 'one', 'PM checked revised assertion and evidence')
        self.assertEqual(self.state()['tasks']['one']['status'], 'accepted')
        self.assertEqual(len(self.state()['tasks']['one']['reworks']), 1)

    def test_rework_validates_status_note_next_action_and_dispatch_completion(self):
        self.create()
        with self.assertRaises(runtime.RuntimeError_):
            runtime.rework(self.store, 'one', 'Reason', 'Revise')
        self.dispatch()
        self.report()
        before = self.store.path.read_bytes()
        for note, action in (('', 'Revise'), ('Reason', ' ')):
            with self.assertRaises(runtime.RuntimeError_):
                runtime.rework(self.store, 'one', note, action)
        self.assertEqual(self.store.path.read_bytes(), before)
        with self.store.transaction() as data:
            data['tasks']['one']['dispatch_owner'] = os.getpid()
        with self.assertRaises(runtime.RuntimeError_):
            runtime.rework(self.store, 'one', 'Reason', 'Revise')
        with self.store.transaction() as data:
            data['tasks']['one']['dispatch_owner'] = None
        runtime.accept(self.store, 'one', 'PM accepted')
        with self.assertRaises(runtime.RuntimeError_):
            runtime.rework(self.store, 'one', 'Reason', 'Revise')

    def test_each_identity_component_is_required(self):
        record = dict(name='name', pane='pane', project=str(self.root),
                      session={'value': 'session', 'path-kind': 'path'})
        agent = dict(agent='pi', name='name', pane_id='pane', cwd=str(self.root),
                     agent_session=record['session'])
        self.assertTrue(runtime.identity_matches(record, agent))
        for key in agent:
            changed = dict(agent, **{key: None})
            self.assertFalse(runtime.identity_matches(record, changed), key)

    def test_unregistered_existing_agent_is_not_adopted(self):
        outsider = dict(agent='pi', name='outsider', cwd=str(self.root), pane_id='do-not-touch',
                        agent_session={'value': 'outsider'}, agent_status='idle', interactive_ready=True)
        (self.root / 'fake.json').write_text(json.dumps({'agents': [outsider], 'calls': []}))
        self.create()
        result = self.dispatch()
        self.assertNotEqual(result['instance']['name'], 'outsider')
        calls = self.fake_state()['calls']
        self.assertFalse(any('do-not-touch' in c or 'outsider' in c for c in calls))
        self.assertFalse(any('close' in c for c in calls))

    def test_low_thinking_is_not_sent_or_later_reused(self):
        self.create()
        with patch.dict(os.environ, FAKE_MODE='low'):
            with self.assertRaises(runtime.RuntimeError_):
                self.dispatch()
        with self.assertRaises(runtime.RuntimeError_):
            self.dispatch(resume=True, confirm_continue=True)
        self.assertFalse(any(c[:2] == ['agent', 'prompt'] for c in self.fake_state()['calls']))

    def test_prompt_failure_and_invalid_json_never_automatically_resend(self):
        self.create()
        with patch.dict(os.environ, FAKE_MODE='fail-prompt'):
            with self.assertRaises(runtime.RuntimeError_):
                self.dispatch()
        task = self.state()['tasks']['one']
        self.assertEqual(task['status'], 'needs-reconcile')
        count = len(self.fake_state()['calls'])
        with self.assertRaises(runtime.RuntimeError_):
            self.dispatch()
        runtime.recover(self.store, 'one')
        self.assertEqual(count, len(self.fake_state()['calls']))
        with patch.dict(os.environ, FAKE_MODE='bad-json'):
            with self.assertRaises(runtime.RuntimeError_):
                self.dispatch(resume=True, confirm_continue=True)
        self.assertEqual(self.state()['tasks']['one']['status'], 'needs-reconcile')

    def test_start_partial_identity_and_readiness_fail_closed(self):
        for index, mode in enumerate(('wrong-cwd', 'missing-session', 'not-ready')):
            task_id = f'bad-{index}'
            self.create(task_id, role=f'role-{index}')
            with patch.dict(os.environ, FAKE_MODE=mode):
                with self.assertRaises(runtime.RuntimeError_):
                    self.dispatch(task_id)
            task = self.state()['tasks'][task_id]
            self.assertEqual(task['status'], 'needs-reconcile')
            self.assertIsNotNone(task['pending_instance']['pane'])
        self.assertFalse(any(c[:2] == ['agent', 'prompt'] for c in self.fake_state()['calls']))

    def test_transport_timeout_during_prompt_persists_uncertainty(self):
        self.create()
        original = runtime.subprocess.run
        def run(command, **kwargs):
            if command[1:3] == ['agent', 'prompt'] and '--help' not in command:
                task = self.state()['tasks']['one']
                self.assertEqual(task['status'], 'dispatching')
                self.assertEqual(self.state()['events'][-1]['kind'], 'prompt-sending')
                raise subprocess.TimeoutExpired(command[:3], 1)
            return original(command, **kwargs)
        with patch.object(runtime.subprocess, 'run', side_effect=run):
            with self.assertRaises(runtime.RuntimeError_):
                self.dispatch()
        self.assertEqual(self.state()['tasks']['one']['status'], 'needs-reconcile')
        self.assertIsNone(self.state()['tasks']['one']['dispatch_owner'])
        with self.assertRaises(runtime.RuntimeError_):
            self.dispatch()

    def test_parallel_create_no_lost_events_and_duplicate_rejected(self):
        files = []
        for i in range(10):
            file = self.root / f'{i}.json'
            file.write_text(json.dumps(self.package(str(i))))
            files.append(file)
        processes = [self.process('create', '--file', str(file)) for file in files]
        for process in processes:
            out, err = process.communicate(timeout=10)
            self.assertEqual(process.returncode, 0, err + out)
        self.assertEqual(len(self.state()['tasks']), 10)
        self.assertEqual(len(self.state()['events']), 10)
        processes = [self.process('create', '--file', str(files[0])) for _ in range(3)]
        for process in processes:
            process.communicate(timeout=10)
            self.assertEqual(process.returncode, 1)
        self.assertEqual(len(self.state()['events']), 10)

    def test_live_dispatch_not_stolen_killed_dispatch_needs_confirmed_summary_resume(self):
        self.create()
        env = dict(self.env, FAKE_MODE='sleep')
        process = self.process('dispatch', 'one', env=env)
        try:
            self.wait_prompt()
            state = self.state()
            self.assertEqual(state['tasks']['one']['status'], 'dispatching')
            self.assertEqual(state['tasks']['one']['dispatch_owner'], process.pid)
            for args in (('dispatch', 'one'), ('dispatch', 'one', '--resume', '--confirm-continue')):
                result = self.cli(*args, check=False)
                self.assertEqual(result.returncode, 1)
            self.create('two')
            self.assertEqual(self.cli('dispatch', 'two', check=False).returncode, 1)
            # Kill the controller only, never a real Herdr agent/pane.
            process.kill()
            process.wait(timeout=5)
            process.stdout.close()
            process.stderr.close()
            self.assertEqual(self.cli('dispatch', 'one', check=False).returncode, 1)
            before = self.store.path.read_bytes()
            recovered = json.loads(self.cli('recover', 'one').stdout)
            self.assertEqual(self.store.path.read_bytes(), before)
            self.assertIsNotNone(recovered['instance'])
            self.assertEqual(recovered['status'], 'needs-reconcile')
            self.assertEqual(recovered['persisted_status'], 'dispatching')
            resumed = json.loads(self.cli('dispatch', 'one', '--resume', '--confirm-continue').stdout)
            self.assertEqual(resumed['status'], 'assigned')
            calls = self.fake_state()['calls']
            self.assertEqual(sum(c[:2] == ['agent', 'start'] for c in calls), 1)
            self.assertEqual(sum(c[:2] == ['agent', 'prompt'] for c in calls), 2)
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate(timeout=5)

    def test_dead_instance_replacement_carries_checkpoint_and_evidence(self):
        self.create()
        first = self.dispatch()['instance']
        self.report('blocked', summary='Partial implementation saved', next_action='PM reconcile external effect')
        data = self.fake_state()
        data['agents'] = []
        (self.root / 'fake.json').write_text(json.dumps(data))
        resumed = self.dispatch(resume=True, confirm_continue=True)
        self.assertNotEqual(resumed['instance']['name'], first['name'])
        prompt = (self.root / 'prompt-entered').read_text()
        self.assertIn('Partial implementation saved', prompt)
        self.assertIn('/tmp/test-result.log', prompt)
        self.assertIn('PM reconcile external effect', prompt)
        summary = json.loads(prompt[prompt.index('{\n'):])
        self.assertEqual(summary['next_action'], 'PM reconcile external effect')
        self.assertEqual(len(self.state()['tasks']['one']['checkpoints']), 1)

    def test_checkpoint_can_run_while_dispatch_waits_without_lost_update(self):
        self.create()
        def send(*args, **kwargs):
            # Verify the durable dispatching record before input submission.
            if args[:2] == ('agent', 'prompt') and '--help' not in args:
                self.assertEqual(self.state()['tasks']['one']['status'], 'dispatching')
                self.report()
                return {}
            return original(*args, **kwargs)
        herdr = runtime.Herdr()
        original = herdr.run
        with patch.object(herdr, 'run', side_effect=send):
            task = runtime.dispatch(self.store, 'one', herdr)
        self.assertEqual(task['status'], 'submitted')
        runtime.accept(self.store, 'one', 'PM reviewed simultaneous delivery')
        kinds = [e['kind'] for e in self.state()['events']]
        self.assertLess(kinds.index('prompt-sending'), kinds.index('checkpoint'))
        self.assertLess(kinds.index('checkpoint'), kinds.index('accepted'))

    def setup_group(self, group_id='group-one'):
        manual = self.root / 'developer' / 'ROLE.md'
        manual.parent.mkdir(exist_ok=True)
        manual.write_text('Execution role; read only when needed')
        runtime.group_create(self.store, dict(id=group_id, project=str(self.root),
                                            goal='Approved project goal', inputs=['/tmp/group-input.md']))
        return str(manual)

    def join_member(self, member='dev-one', group='group-one', role=None, **options):
        role = role or str(self.root / 'developer/ROLE.md')
        return runtime.join(self.store, group, member, role, runtime.Herdr(), **options)

    def ready_member(self, member='dev-one'):
        obj = self.state()['members'][member]
        record = obj['instance']
        return runtime.member_ready(self.store, member, record['name'], record['session']['value'],
                                    obj['attempts'][-1]['id'])

    def assign_task(self, task='one', member='dev-one', **options):
        return runtime.dispatch(self.store, task, runtime.Herdr(), member_id=member, **options)

    def submit_accept(self, task='one'):
        obj = self.state()['tasks'][task]
        runtime.checkpoint(self.store, task, status='submitted', summary='Verified task summary ' + task,
                           evidence=['/tmp/evidence-' + task], next_action='PM acceptance',
                           instance=obj['instance']['name'], session=obj['instance']['session']['value'],
                           dispatch_id=obj['attempts'][-1]['id'])
        return runtime.accept(self.store, task, 'PM checked ' + task)

    def leave_member(self, member='dev-one', summary='Implementation handed over', **options):
        return runtime.leave(self.store, member, summary, runtime.Herdr(), close_tab=True, **options)

    def test_auto_member_id_preflight_and_retained_workstation(self):
        role = self.setup_group()
        first = runtime.join(self.store, 'group-one', None, role, runtime.Herdr())
        self.assertTrue(first['id'].startswith('member-'))
        calls = len(self.fake_state()['calls'])
        with self.assertRaisesRegex(runtime.RuntimeError_, 'Existing members'):
            runtime.join(self.store, 'group-one', None, role, runtime.Herdr())
        self.assertEqual(len(self.fake_state()['calls']), calls)
        before = self.store.path.read_bytes()
        result = json.loads(self.cli('preflight', '--project', str(self.root), full=False).stdout)
        self.assertEqual(result['members'][0]['id'], first['id'])
        self.assertEqual(self.store.path.read_bytes(), before)
        self.assertEqual(len(self.fake_state()['calls']), calls)
        denied = self.cli('leave', first['id'], '--summary', 'keep visible', check=False, full=False)
        self.assertNotEqual(denied.returncode, 0)
        self.assertIn('retained by default', denied.stderr)
        self.assertEqual(self.store.path.read_bytes(), before)
        self.assertEqual(len(self.fake_state()['calls']), calls)

    def test_default_mutation_receipt_is_small_and_full_read_remains(self):
        package = self.root / 'package.json'
        package.write_text(json.dumps(self.package('compact')))
        result = json.loads(self.cli('create', '--file', str(package), full=False).stdout)
        self.assertEqual(result['status'], 'created')
        self.assertNotIn('inputs', result)
        self.assertNotIn('attempts', result)
        detail = json.loads(self.cli('show', 'compact', full=False).stdout)
        self.assertIn('inputs', detail)

    def test_group_schema_legacy_records_and_read_only_commands(self):
        self.create('role-runtime-smoke')
        legacy = self.state()
        legacy.pop('groups')
        legacy.pop('members')
        self.store.save(legacy)
        before = self.store.path.read_bytes()
        result = json.loads(self.cli('show', 'role-runtime-smoke').stdout)
        self.assertEqual(result['id'], 'role-runtime-smoke')
        self.assertEqual(json.loads(self.cli('members').stdout), [])
        self.assertEqual(json.loads(self.cli('group-list').stdout), [])
        self.assertEqual(self.store.path.read_bytes(), before)
        for bad in ({}, dict(id='bad', project='relative', goal='goal', inputs=[]),
                    dict(id='bad', project=str(self.root), goal='', inputs=[])):
            with self.assertRaises(runtime.RuntimeError_):
                runtime.group_create(self.store, bad)
        self.setup_group()
        self.assertIn('role-runtime-smoke', self.state()['tasks'])
        self.assertEqual(self.state()['events'][0]['kind'], 'created')
        before = self.store.path.read_bytes()
        self.cli('group-show', 'group-one')
        self.cli('members', '--group', 'group-one')
        self.assertEqual(self.store.path.read_bytes(), before)
        self.assertFalse((self.root / 'fake.json').exists())

    def test_join_new_tab_explicit_workspace_no_task_and_no_split(self):
        role = self.setup_group()
        member = self.join_member()
        self.assertEqual(member['status'], 'awaiting-ready')
        self.assertEqual(self.state()['tasks'], {})
        calls = self.fake_state()['calls']
        tab = next(c for c in calls if c[:2] == ['tab', 'create'])
        self.assertEqual(tab, ['tab', 'create', '--workspace', 'workspace-explicit', '--cwd', str(self.root),
                               '--label', 'developer', '--no-focus'])
        self.assertFalse(any(c[:2] == ['pane', 'split'] for c in calls))
        start = next(c for c in calls if c[:2] == ['agent', 'start'])
        self.assertEqual(start[start.index('--pane') + 1], member['root_pane'])
        self.assertLessEqual(len(start[2]), 32)
        prompt = (self.root / 'prompt-entered').read_text()
        self.assertIn('onboarding ONLY, not a task', prompt)
        self.assertTrue(prompt.startswith('初始化 developer\n'))
        self.assertIn('必须先实际读取', prompt)
        self.assertIn('读取失败时不得执行就绪回执', prompt)
        self.assertIn('当前没有分配任务，等待项目经理派单', prompt)
        self.assertIn('Do not create subagents', prompt)
        self.assertIn('NOT permission isolation', prompt)
        self.assertIn(role, prompt)
        self.assertIn('member-ready', prompt)
        self.assertIn('group-show', prompt)
        self.assertIn(member['attempts'][-1]['id'], prompt)
        self.assertNotIn('checkpoint', prompt)
        before = self.fake_state()['calls']
        repeated = self.join_member()
        self.assertEqual(repeated['instance'], member['instance'])
        self.assertEqual(before, self.fake_state()['calls'])

    def test_join_requires_herdr_workspace_manual_and_unique_identity(self):
        role = self.setup_group()
        for env in ({'HERDR_ENV': '0'}, {'HERDR_WORKSPACE_ID': ''}):
            with patch.dict(os.environ, env), self.assertRaises(runtime.RuntimeError_):
                self.join_member()
        with self.assertRaises(runtime.RuntimeError_):
            self.join_member(role='developer')
        self.assertEqual(self.state()['members'], {})
        self.join_member()
        self.setup_group('other-group')
        with self.assertRaises(runtime.RuntimeError_):
            self.join_member(group='other-group')
        with patch.dict(os.environ, HERDR_WORKSPACE_ID='other-workspace'):
            with self.assertRaises(runtime.RuntimeError_):
                self.join_member()
        self.assertEqual(len(self.fake_state()['tabs']), 1)

    def test_group_assignment_requires_ready_matches_project_role_and_two_rounds(self):
        role = self.setup_group()
        self.join_member()
        self.create(role=role)
        with self.assertRaises(runtime.RuntimeError_):
            self.assign_task()
        self.assertEqual(self.state()['tasks']['one']['status'], 'created')
        self.ready_member()
        self.create('wrong-role')
        with self.assertRaises(runtime.RuntimeError_):
            self.assign_task('wrong-role')
        other = self.root / 'other-project'
        other.mkdir()
        self.create('wrong-project', role=role, project=str(other))
        with self.assertRaises(runtime.RuntimeError_):
            self.assign_task('wrong-project')
        first = self.assign_task()
        self.assertEqual(first['group'], 'group-one')
        self.assertEqual(first['member'], 'dev-one')
        self.assertEqual(self.ready_member()['status'], 'busy')
        self.create('two', role=role)
        with self.assertRaises(runtime.RuntimeError_):
            self.assign_task('two')
        self.submit_accept()
        self.assertEqual(self.state()['members']['dev-one']['status'], 'ready')
        second = self.assign_task('two')
        self.assertEqual(first['instance']['name'], second['instance']['name'])
        self.submit_accept('two')
        self.assertEqual(len(self.fake_state()['tabs']), 1)
        self.assertEqual(len(self.state()['tasks']['one']['attempts']), 1)

    def test_group_isolation_and_legacy_dispatch_cannot_use_group_instance(self):
        role = self.setup_group()
        self.join_member()
        self.ready_member()
        self.setup_group('other-group')
        self.join_member('dev-two', 'other-group')
        self.ready_member('dev-two')
        self.create(role=role)
        first = self.assign_task()
        self.create('two', role=role)
        second = self.assign_task('two', 'dev-two')
        self.assertNotEqual(first['instance']['name'], second['instance']['name'])
        self.create('legacy', role=role)
        legacy = self.dispatch('legacy')
        self.assertNotIn(legacy['instance']['name'], {first['instance']['name'], second['instance']['name']})
        self.assertFalse(legacy.get('group'))
        with self.assertRaises(runtime.RuntimeError_):
            self.dispatch(resume=True, confirm_continue=True)
        with self.assertRaises(runtime.RuntimeError_):
            self.assign_task(member='dev-two', resume=True, confirm_continue=True)

    def test_member_ready_rejects_stale_receipts_never_completes_task(self):
        self.setup_group()
        member = self.join_member()
        record = member['instance']
        for changes in ({'instance': 'other'}, {'session': 'other'}, {'join_id': 'old'}):
            options = dict(instance=record['name'], session=record['session']['value'],
                           join_id=member['attempts'][-1]['id'])
            options.update(changes)
            with self.assertRaises(runtime.RuntimeError_):
                runtime.member_ready(self.store, 'dev-one', **options)
        result = self.ready_member()
        self.assertEqual(result['status'], 'ready')
        self.assertEqual(self.ready_member()['status'], 'ready')
        self.assertEqual(self.state()['tasks'], {})

    def test_join_prompt_uncertainty_no_repeat_and_explicit_resume_reuses_tab(self):
        self.setup_group()
        with patch.dict(os.environ, FAKE_MODE='fail-prompt'):
            with self.assertRaises(runtime.RuntimeError_):
                self.join_member()
        self.assertEqual(self.state()['members']['dev-one']['status'], 'needs-reconcile')
        before = self.fake_state()['calls']
        with self.assertRaises(runtime.RuntimeError_):
            self.join_member()
        self.cli('group-show', 'group-one')
        self.assertEqual(before, self.fake_state()['calls'])
        member = self.join_member(resume=True, confirm_continue=True)
        self.assertEqual(member['status'], 'awaiting-ready')
        self.assertEqual(len(member['attempts']), 2)
        self.assertEqual(len(self.fake_state()['tabs']), 1)
        self.ready_member()

    def test_assignment_timeout_no_repeat_and_explicit_resume_same_member(self):
        role = self.setup_group()
        self.join_member()
        self.ready_member()
        self.create(role=role)
        original = runtime.subprocess.run
        def run(command, **kwargs):
            if command[1:3] == ['agent', 'prompt'] and '--help' not in command:
                task = self.state()['tasks']['one']
                self.assertEqual(task['status'], 'dispatching')
                self.assertEqual(self.state()['members']['dev-one']['status'], 'busy')
                raise subprocess.TimeoutExpired(command[:3], 1)
            return original(command, **kwargs)
        with patch.object(runtime.subprocess, 'run', side_effect=run):
            with self.assertRaises(runtime.RuntimeError_):
                self.assign_task()
        member = self.state()['members']['dev-one']
        self.assertEqual(member['status'], 'needs-reconcile')
        self.assertEqual(self.state()['tasks']['one']['status'], 'needs-reconcile')
        self.assertEqual(self.ready_member()['status'], 'needs-reconcile')
        before = self.fake_state()['calls']
        with self.assertRaises(runtime.RuntimeError_):
            self.assign_task()
        self.assertEqual(before, self.fake_state()['calls'])
        resumed = self.assign_task(resume=True, confirm_continue=True)
        self.assertEqual(resumed['instance']['name'], member['instance']['name'])
        self.submit_accept()

    def test_join_transport_timeout_does_not_resend_without_confirmation(self):
        self.setup_group()
        original = runtime.subprocess.run
        def run(command, **kwargs):
            if command[1:3] == ['agent', 'prompt'] and '--help' not in command:
                member = self.state()['members']['dev-one']
                self.assertEqual(member['status'], 'joining')
                self.assertEqual(self.state()['events'][-1]['kind'], 'join-prompt-sending')
                raise subprocess.TimeoutExpired(command[:3], 1)
            return original(command, **kwargs)
        with patch.object(runtime.subprocess, 'run', side_effect=run):
            with self.assertRaises(runtime.RuntimeError_):
                self.join_member()
        member = self.state()['members']['dev-one']
        self.assertEqual(member['status'], 'needs-reconcile')
        self.assertIsNone(member['operation_owner'])
        before = self.fake_state()['calls']
        with self.assertRaises(runtime.RuntimeError_):
            self.join_member()
        self.assertEqual(before, self.fake_state()['calls'])
        self.join_member(resume=True, confirm_continue=True)
        self.assertEqual(len(self.fake_state()['tabs']), 1)

    def test_group_rework_keeps_binding_and_requires_fresh_delivery(self):
        role = self.setup_group()
        self.join_member()
        self.ready_member()
        self.create(role=role)
        self.assign_task()
        self.report()
        runtime.rework(self.store, 'one', 'Missing edge case', 'Add edge case')
        with self.assertRaises(runtime.RuntimeError_):
            self.assign_task()
        with self.assertRaises(runtime.RuntimeError_):
            self.leave_member()
        self.assign_task(resume=True, confirm_continue=True)
        self.assertIn('Missing edge case', (self.root / 'prompt-entered').read_text())
        self.submit_accept()
        self.assertEqual(self.state()['members']['dev-one']['status'], 'ready')

    def test_member_assign_get_identity_failure_never_sends_or_replaces(self):
        role = self.setup_group()
        self.join_member()
        self.ready_member()
        self.create(role=role)
        before = len(self.fake_state()['calls'])
        with patch.dict(os.environ, FAKE_MODE='get-mismatch'):
            with self.assertRaises(runtime.RuntimeError_):
                self.assign_task()
        calls = self.fake_state()['calls'][before:]
        self.assertFalse(any(c[:2] in (['agent', 'prompt'], ['tab', 'create'], ['pane', 'split']) for c in calls))
        self.assertEqual(len(self.fake_state()['tabs']), 1)

    def test_leave_requires_all_tasks_accepted_no_active_send_and_summary(self):
        role = self.setup_group()
        self.join_member()
        self.ready_member()
        self.create(role=role)
        self.assign_task()
        for status in ('assigned', 'submitted'):
            if status == 'submitted':
                self.report()
            with self.assertRaises(runtime.RuntimeError_):
                self.leave_member()
        self.submit_accept()
        for env in ({'HERDR_ENV': '0'},):
            with patch.dict(os.environ, env), self.assertRaises(runtime.RuntimeError_):
                self.leave_member()
        with self.assertRaises(runtime.RuntimeError_):
            self.leave_member(summary=' ')
        with self.store.transaction() as data:
            data['members']['dev-one']['operation_owner'] = os.getpid()
        with self.assertRaises(runtime.RuntimeError_):
            self.leave_member()
        self.assertFalse(any(c[:2] == ['tab', 'close'] for c in self.fake_state()['calls']))

    def test_leave_closes_only_owned_single_root_tab_and_new_member_reads_summary(self):
        role = self.setup_group()
        old = self.join_member()
        self.ready_member()
        self.create(role=role)
        self.assign_task()
        self.submit_accept()
        left = self.leave_member(summary='Keep decision X; next validate Y')
        self.assertEqual(left['status'], 'left')
        self.assertEqual(self.fake_state()['tabs'], [])
        self.assertTrue(self.state()['instances'][old['instance']['name']]['retired'])
        with self.assertRaises(runtime.RuntimeError_):
            self.join_member(resume=True, confirm_continue=True)
        new = self.join_member('dev-new')
        self.assertNotEqual(new['instance']['name'], old['instance']['name'])
        prompt = (self.root / 'prompt-entered').read_text()
        self.assertIn('Keep decision X; next validate Y', prompt)
        self.assertIn('Verified task summary one', prompt)
        self.assertIn('/tmp/evidence-one', prompt)
        self.assertNotIn('Implement approved task', prompt)
        calls = self.fake_state()['calls']
        self.assertEqual([c for c in calls if c[:2] == ['tab', 'close']], [['tab', 'close', old['tab_id']]])
        self.assertFalse(any(c[:2] in (['pane', 'split'], ['pane', 'close']) for c in calls))

    def test_leave_identity_mismatch_or_other_pane_prevents_close(self):
        self.setup_group()
        member = self.join_member()
        self.ready_member()
        self.change_agent(agent_session={'value': 'wrong-session'})
        with self.assertRaises(runtime.RuntimeError_):
            self.leave_member()
        self.assertFalse(any(c[:2] == ['tab', 'close'] for c in self.fake_state()['calls']))
        self.change_agent(agent_session=member['instance']['session'])
        fake = self.fake_state()
        fake['panes'].append(dict(pane_id='user-pane', tab_id=member['tab_id'],
                                  workspace_id=member['workspace']))
        fake['tabs'][0]['pane_count'] = 2
        (self.root / 'fake.json').write_text(json.dumps(fake))
        with self.assertRaises(runtime.RuntimeError_):
            self.leave_member(resume=True, confirm_continue=True)
        self.assertFalse(any(c[:2] == ['tab', 'close'] for c in self.fake_state()['calls']))
        self.assertEqual(self.state()['members']['dev-one']['status'], 'needs-reconcile')

    def test_close_failure_and_ambiguous_close_are_readable_and_confirmable(self):
        self.setup_group()
        self.join_member()
        self.ready_member()
        with patch.dict(os.environ, FAKE_MODE='close-failed'):
            with self.assertRaises(runtime.RuntimeError_):
                self.leave_member()
        member = self.state()['members']['dev-one']
        self.assertEqual(member['status'], 'needs-reconcile')
        self.assertEqual(member['summary'], 'Implementation handed over')
        before = self.store.path.read_bytes()
        self.cli('group-show', 'group-one')
        self.assertEqual(before, self.store.path.read_bytes())
        with self.assertRaises(runtime.RuntimeError_):
            self.leave_member()
        with patch.dict(os.environ, FAKE_MODE='close-ambiguous'):
            with self.assertRaises(runtime.RuntimeError_):
                self.leave_member(resume=True, confirm_continue=True)
        self.assertEqual(self.fake_state()['tabs'], [])
        count = sum(c[:2] == ['tab', 'close'] for c in self.fake_state()['calls'])
        result = self.leave_member(resume=True, confirm_continue=True)
        self.assertEqual(result['status'], 'left')
        self.assertEqual(count, sum(c[:2] == ['tab', 'close'] for c in self.fake_state()['calls']))

    def test_close_noop_or_additional_agent_never_marks_left(self):
        self.setup_group()
        member = self.join_member()
        self.ready_member()
        fake = self.fake_state()
        extra = dict(fake['agents'][0], name='user-agent', pane_id='user-pane',
                     agent_session={'value': 'user-session'})
        fake['agents'].append(extra)
        (self.root / 'fake.json').write_text(json.dumps(fake))
        with self.assertRaises(runtime.RuntimeError_):
            self.leave_member()
        self.assertFalse(any(c[:2] == ['tab', 'close'] for c in self.fake_state()['calls']))
        fake = self.fake_state()
        fake['agents'] = [a for a in fake['agents'] if a['name'] != 'user-agent']
        (self.root / 'fake.json').write_text(json.dumps(fake))
        with patch.dict(os.environ, FAKE_MODE='close-noop'):
            with self.assertRaises(runtime.RuntimeError_):
                self.leave_member(resume=True, confirm_continue=True)
        self.assertEqual(self.state()['members']['dev-one']['status'], 'needs-reconcile')
        self.assertEqual(self.fake_state()['tabs'][0]['tab_id'], member['tab_id'])
        self.assertEqual(self.leave_member(resume=True, confirm_continue=True)['status'], 'left')

    def test_concurrent_group_create_preserves_events_and_duplicates_fail(self):
        file = self.root / 'group.json'
        file.write_text(json.dumps(dict(id='parallel', project=str(self.root), goal='Goal', inputs=[])))
        processes = [self.process('group-create', '--file', str(file)) for _ in range(4)]
        results = []
        for process in processes:
            process.communicate(timeout=10)
            results.append(process.returncode)
        self.assertEqual(sorted(results), [0, 1, 1, 1])
        self.assertEqual(list(self.state()['groups']), ['parallel'])
        self.assertEqual(len(self.state()['events']), 1)

    def test_partial_join_never_recreates_or_closes_unverified_tab(self):
        self.setup_group()
        with patch.dict(os.environ, FAKE_MODE='low'):
            with self.assertRaises(runtime.RuntimeError_):
                self.join_member()
        self.assertEqual(self.state()['members']['dev-one']['status'], 'needs-reconcile')
        with self.assertRaises(runtime.RuntimeError_):
            self.join_member(resume=True, confirm_continue=True)
        with self.assertRaises(runtime.RuntimeError_):
            self.leave_member()
        self.assertEqual(len(self.fake_state()['tabs']), 1)
        self.assertFalse(any(c[:2] == ['tab', 'close'] for c in self.fake_state()['calls']))

    def test_concurrent_join_and_assign_reservations_and_member_ready_during_join(self):
        role = self.setup_group()
        env = dict(self.env, FAKE_MODE='sleep')
        process = self.process('join', 'group-one', 'dev-one', '--role', role, env=env)
        try:
            self.wait_prompt()
            self.assertEqual(self.state()['members']['dev-one']['status'], 'joining')
            result = self.cli('join', 'group-one', 'dev-one', '--role', role, check=False)
            self.assertEqual(result.returncode, 1)
            self.ready_member()
            self.create(role=role)
            self.assertEqual(self.cli('assign', 'one', '--member', 'dev-one', check=False).returncode, 1)
            process.kill()
            process.wait(timeout=5)
            process.stdout.close()
            process.stderr.close()
            # Even a ready receipt cannot erase uncertainty from a dead join controller.
            recovered = json.loads(self.cli('group-show', 'group-one').stdout)['members'][0]
            self.assertEqual(recovered['status'], 'needs-reconcile')
            self.assertEqual(recovered['persisted_status'], 'ready')
            self.assertEqual(self.cli('assign', 'one', '--member', 'dev-one', check=False).returncode, 1)
            self.assertEqual(self.cli('join', 'group-one', 'dev-one', '--role', role, check=False).returncode, 1)
            self.join_member(resume=True, confirm_continue=True)
            self.ready_member()
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate(timeout=5)
        (self.root / 'prompt-entered').unlink()
        process = self.process('assign', 'one', '--member', 'dev-one', env=env)
        try:
            self.wait_prompt()
            self.create('two', role=role)
            self.assertEqual(self.cli('assign', 'two', '--member', 'dev-one', check=False).returncode, 1)
            self.assertEqual(self.cli('leave', 'dev-one', '--summary', 'no', check=False).returncode, 1)
            process.kill()
            process.wait(timeout=5)
            process.stdout.close()
            process.stderr.close()
            self.assertEqual(self.cli('assign', 'one', '--member', 'dev-one', check=False).returncode, 1)
            self.assertEqual(json.loads(self.cli('assign', 'one', '--member', 'dev-one',
                                                 '--resume', '--confirm-continue').stdout)['status'], 'assigned')
            self.assertEqual(len(self.fake_state()['tabs']), 1)
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate(timeout=5)

    def test_group_cli_and_no_join_direction_option(self):
        file = self.root / 'group.json'
        file.write_text(json.dumps(dict(id='cli-group', project=str(self.root), goal='CLI group', inputs=[])))
        result = self.cli('group-create', '--file', str(file))
        self.assertEqual(json.loads(result.stdout)['id'], 'cli-group')
        manual = self.root / 'ROLE.md'
        manual.write_text('Role instructions')
        self.assertEqual(self.cli('join', 'cli-group', 'cli-member', '--role', str(manual),
                                  '--direction', 'right', check=False).returncode, 2)
        result = self.cli('join', 'cli-group', 'cli-member', '--role', str(manual))
        member = json.loads(result.stdout)
        record = member['instance']
        self.cli('member-ready', 'cli-member', '--instance', record['name'],
                 '--session', record['session']['value'], '--join-id', member['attempts'][-1]['id'])
        self.assertEqual(len(json.loads(self.cli('members', '--group', 'cli-group').stdout)), 1)
        self.assertEqual(json.loads(self.cli('leave', 'cli-member', '--summary', 'No task assigned',
                                            '--close-tab').stdout)['status'], 'left')

    def test_main_errors_are_clear_and_no_shell_used(self):
        with redirect_stderr(io.StringIO()) as err, redirect_stdout(io.StringIO()):
            self.assertEqual(runtime.main(['--state-dir', str(self.state_dir), 'show', 'missing']), 1)
        self.assertIn('Unknown task', err.getvalue())
        with patch.object(runtime.subprocess, 'run') as run:
            run.return_value = subprocess.CompletedProcess([], 0, '{"result": {}}', '')
            runtime.Herdr().run('agent', 'prompt', 'name', '$(touch /tmp/never); a b')
            args, kwargs = run.call_args
            self.assertIsInstance(args[0], list)
            self.assertEqual(args[0][-1], '$(touch /tmp/never); a b')
            self.assertNotIn('shell', kwargs)


if __name__ == '__main__':
    unittest.main()
