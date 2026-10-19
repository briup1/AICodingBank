#!/usr/bin/env python3
"""Local role task ledger (Python 3.12, stdlib only; macOS/Linux).

create --file package.json; dispatch ID; recover ID; dispatch ID --resume
--confirm-continue; checkpoint ID ...; accept ID --note 'PM verification'.
PM rework: rework ID --note REASON --next-action ACTION (records only);
then dispatch ID --resume --confirm-continue to explicitly send the revision.
Groups: group-create --file group.json ({id, project, goal, inputs}); group-list;
group-show GROUP; members [--group GROUP]; join GROUP MEMBER --role ABS_ROLE_MD;
member-ready MEMBER --instance NAME --session PATH --join-id ID;
assign TASK --member MEMBER; leave MEMBER --summary TEXT.
join/assign/leave uncertainty requires --resume --confirm-continue; no auto replay.
Join uses a NEW independent Tab in explicit HERDR_WORKSPACE_ID, never UI focus.
Left members never revive; join with a new member id to read group summaries.
All commands accept --state-dir BEFORE the subcommand. Package keys are id,
project (absolute directory), role (absolute manual file or fixed name), goal,
non_goals, allowed_paths (absolute), inputs, acceptance; the last four are lists.

Only explicit dispatch controls Herdr, and only inside HERDR_ENV=1. Recover is
read-only: it returns a package/checkpoint/evidence/next-action summary, not a Pi
conversation replay. Session pointers are references, not full conversations.
Role and one-level delegation limits are prompt contracts, NOT a permission
sandbox. PM authorization is a human contract, not authenticated by this CLI.
Never put credentials, full transcripts or customer data in task packages.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
import uuid


DEFAULT_STATE_DIR = Path(__file__).resolve().parents[2] / '.local/records/role-runtime'
PACKAGE_KEYS = ('id', 'project', 'role', 'goal', 'non_goals', 'allowed_paths',
                'inputs', 'acceptance')
ID_PATTERN = re.compile(r'[\w-]{1,100}\Z')


class RuntimeError_(Exception):
    """An actionable, fail-closed CLI error."""


def require(condition, message):
    if not condition:
        raise RuntimeError_(message)


def nonblank(value):
    return isinstance(value, str) and bool(value.strip())


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def absolute_path(value):
    require(nonblank(value) and Path(value).is_absolute(),
            'Paths must be absolute, non-empty strings')
    return str(Path(value).resolve())


def validate_package(data):
    require(isinstance(data, dict), 'Task package must be a JSON object')
    require(set(data) == set(PACKAGE_KEYS),
            'Package keys must be exactly: ' + ', '.join(PACKAGE_KEYS))
    require(isinstance(data['id'], str) and ID_PATTERN.fullmatch(data['id']),
            'id must contain 1-100 letters, digits, underscores or hyphens')
    require(nonblank(data['goal']), 'goal is required')
    result = dict(data)
    result['project'] = absolute_path(data['project'])
    require(Path(result['project']).is_dir(), 'project must be an existing directory')
    role = data['role']
    require(nonblank(role), 'role is required')
    if Path(role).is_absolute():
        result['role'] = absolute_path(role)
        require(Path(result['role']).is_file(), 'Role manual must be an existing file')
    else:
        require(ID_PATTERN.fullmatch(role), 'role must be a fixed name or absolute manual path')
    for key in ('non_goals', 'allowed_paths', 'inputs', 'acceptance'):
        require(isinstance(data[key], list) and all(nonblank(x) for x in data[key]),
                f'{key} must be a list of non-empty strings')
        result[key] = list(data[key])
    require(result['allowed_paths'] and result['acceptance'],
            'allowed_paths and acceptance must not be empty')
    result['allowed_paths'] = [absolute_path(p) for p in result['allowed_paths']]
    return result


class Store:
    def __init__(self, directory=DEFAULT_STATE_DIR):
        self.directory = Path(directory).resolve()
        self.path = self.directory / 'state.json'

    def read(self):
        if not self.path.exists():
            return {'version': 1, 'tasks': {}, 'instances': {}, 'events': [],
                    'groups': {}, 'members': {}}
        try:
            data = json.loads(self.path.read_text(encoding='utf-8'))
        except (ValueError, OSError) as exc:
            raise RuntimeError_(f'Cannot read ledger; not resetting it: {exc}') from exc
        require(isinstance(data, dict) and data.get('version') == 1
                and isinstance(data.get('tasks'), dict)
                and isinstance(data.get('instances'), dict)
                and isinstance(data.get('events'), list), 'Invalid ledger; not resetting it')
        for key in ('groups', 'members'):
            require(isinstance(data.setdefault(key, {}), dict), f'Invalid ledger {key}')
        return data

    def save(self, data):
        # Replace only after a complete, fsynced write; keep the lock inode stable.
        fd, name = tempfile.mkstemp(prefix='.state-', dir=self.directory)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as output:
                json.dump(data, output, ensure_ascii=False, indent=2)
                output.write('\n')
                output.flush()
                os.fsync(output.fileno())
            os.replace(name, self.path)
            directory_fd = os.open(self.directory, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        finally:
            if os.path.exists(name):
                os.unlink(name)

    @contextmanager
    def transaction(self):
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        with (self.directory / 'state.lock').open('a', encoding='utf-8') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            data = self.read()
            yield data
            self.save(data)


def task_for(data, task_id):
    require(task_id in data['tasks'], f'Unknown task: {task_id}')
    return data['tasks'][task_id]


def event(data, task, kind, **details):
    data['events'].append({'at': timestamp(), 'task': task['id'], 'kind': kind, **details})
    task['updated_at'] = timestamp()


def create(store, package):
    task = validate_package(package)
    with store.transaction() as data:
        require(task['id'] not in data['tasks'], 'Duplicate task id (never overwritten)')
        task.update(status='created', evidence=[], next_action='PM dispatch',
                    instance=None, checkpoints=[], attempts=[], dispatch_owner=None,
                    acceptance_note=None)
        data['tasks'][task['id']] = task
        event(data, task, 'created')
    return task


def recover(store, task_id):
    task = task_for(store.read(), task_id)
    interrupted = task['status'] == 'dispatching' and not owner_alive(task['dispatch_owner'])
    return {'package': {key: task[key] for key in PACKAGE_KEYS},
            'status': 'needs-reconcile' if interrupted else task['status'],
            'persisted_status': task['status'], 'instance': task['instance'],
            'group': task.get('group'), 'member': task.get('member'),
            'pending_instance': task.get('pending_instance'),
            'latest_attempt': task['attempts'][-1] if task['attempts'] else None,
            'latest_checkpoint': task['checkpoints'][-1] if task['checkpoints'] else None,
            'evidence': task['evidence'], 'next_action': task['next_action'],
            'acceptance_note': task['acceptance_note'],
            'latest_rework': task.get('reworks', [])[-1] if task.get('reworks') else None,
            'recovery_semantics': 'Summary only; session is a reference, no full Pi replay. '
                                  'PM must explicitly confirm continuation. '
                                  'Unknown delivery is not permission to repeat side effects.'}


def checkpoint(store, task_id, *, status, summary, evidence, next_action,
               instance, session, dispatch_id):
    require(status in {'ready', 'submitted', 'blocked'}, 'Invalid checkpoint status')
    require(nonblank(summary) and nonblank(next_action), 'summary and next_action are required')
    require(isinstance(evidence, list) and all(nonblank(x) for x in evidence),
            'evidence must be a list of references')
    with store.transaction() as data:
        task = task_for(data, task_id)
        bound = task['instance']
        require(bound and bound['name'] == instance
                and bound['session']['value'] == session
                and task['attempts'][-1]['id'] == dispatch_id, 'Stale or mismatched checkpoint identity')
        require(task['status'] not in {'created', 'accepted', 'rework'},
                'Task cannot checkpoint before an explicit dispatch in this status')
        require(task['status'] != 'submitted' or status == 'submitted',
                'Submitted task cannot move back to execution')
        if status == 'submitted':
            require(evidence, 'Submission requires evidence references')
        item = {'at': timestamp(), 'status': status, 'summary': summary,
                'evidence': evidence, 'next_action': next_action, 'dispatch_id': dispatch_id}
        task['checkpoints'].append(item)
        task['evidence'] = list(dict.fromkeys(task['evidence'] + evidence))
        task.update(status=status, next_action=next_action)
        event(data, task, 'checkpoint', checkpoint=item)
    return task


def accept(store, task_id, note):
    require(nonblank(note), 'PM acceptance note is required')
    with store.transaction() as data:
        task = task_for(data, task_id)
        require(task['status'] == 'submitted' and task['evidence'],
                'Only a submitted task with evidence can be accepted')
        require(not task['dispatch_owner'], 'Dispatch still running; wait for it to finish')
        if task.get('member'):
            member = member_for(data, task['member'])
            require(not member['operation_owner'], 'Member operation still running')
            require(member['status'] in {'busy', 'needs-reconcile'}
                    and member['operation'] == 'assign' and member['current_task'] == task_id,
                    'Member requires reconciliation before acceptance')
            member.update(status='ready', current_task=None)
            group_event(data, 'member', member, 'task-accepted', task=task_id)
        task.update(status='accepted', acceptance_note=note, next_action='None; PM accepted')
        event(data, task, 'accepted', note=note)
    return task


def rework(store, task_id, note, next_action):
    require(nonblank(note) and nonblank(next_action), 'PM rework note and next_action are required')
    with store.transaction() as data:
        task = task_for(data, task_id)
        require(task['status'] == 'submitted', 'Only submitted tasks can be returned for rework')
        require(not task['dispatch_owner'], 'Dispatch still running; wait for it to finish')
        item = {'at': timestamp(), 'note': note, 'next_action': next_action,
                'dispatch_id': task['attempts'][-1]['id']}
        task.setdefault('reworks', []).append(item)
        task.update(status='rework', next_action=next_action)
        event(data, task, 'rework-requested', rework=item)
    return task


class Herdr:
    def __init__(self, executable='herdr', timeout_ms=30000):
        self.executable = executable
        self.timeout_ms = timeout_ms

    def run(self, *args, help_text=False):
        try:
            result = subprocess.run([self.executable, *args], capture_output=True,
                                    text=True, timeout=self.timeout_ms / 1000 + 5,
                                    check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise RuntimeError_(f'Herdr outcome unknown: {type(exc).__name__}') from exc
        require(result.returncode == 0, 'Herdr command failed; inspect Herdr before continuing')
        if help_text:
            return result.stdout
        try:
            payload = json.loads(result.stdout)
        except ValueError as exc:
            raise RuntimeError_('Herdr returned invalid JSON; outcome unknown') from exc
        require(isinstance(payload, dict) and payload.get('ok') is not False
                and not payload.get('error') and isinstance(payload.get('result'), dict),
                'Unrecognized or failed Herdr response; outcome unknown')
        return payload['result']

    def check_help(self):
        for command, tokens in (
            (('pane', 'split'), ('--current', '--direction', 'down', 'right', '--cwd', '--no-focus')),
            (('agent', 'start'), ('--kind', 'pi', '--pane', 'AGENT_ARG')),
            (('agent', 'list'), ('agent list',)),
            (('agent', 'get'), ('agent get', '<target>')),
            (('agent', 'prompt'), ('<TARGET>', '<TEXT>', '--wait', '--timeout')),
        ):
            help_text = self.run(*command, '--help', help_text=True)
            require(all(token in help_text for token in tokens),
                    'Installed Herdr does not support the required CLI contract')

    def agents(self):
        agents = self.run('agent', 'list').get('agents')
        require(isinstance(agents, list) and all(isinstance(a, dict) for a in agents),
                'Invalid agent list; not starting a replacement')
        return agents

    def get(self, record):
        agent = self.run('agent', 'get', record['name']).get('agent')
        require(isinstance(agent, dict) and identity_matches(record, agent),
                'agent get identity mismatch; do not send or replace automatically')
        return agent


def session_pointer(agent):
    value = agent.get('agent_session')
    require(isinstance(value, dict) and nonblank(value.get('value')), 'Missing agent session pointer')
    return value


def identity_matches(record, agent):
    return (agent.get('agent') == 'pi' and agent.get('name') == record['name']
            and agent.get('pane_id') == record['pane']
            and agent.get('cwd') == record['project']
            and agent.get('agent_session') == record['session'])


def idle(agent):
    return agent.get('interactive_ready') is True and agent.get('agent_status') in {'idle', 'done'}


def owner_alive(pid):
    if not pid:
        return False
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def prompt_text(store, task_id, attempt_id):
    summary = recover(store, task_id)
    instance = summary['instance']
    command = [sys.executable, str(Path(__file__).resolve()), '--state-dir',
               str(store.directory), 'checkpoint', task_id, '--instance', instance['name'],
               '--session', instance['session']['value'], '--dispatch-id', attempt_id]
    return (
        'You are the execution role named in this task, not the project manager. '
        'Do not create subagents, invoke delegation entrypoints, or switch identity. '
        'Read the role manual by its path only when needed; do not copy all context. '
        'Write ONLY the task allowed_paths plus your own checkpoint in this ledger. '
        'These are behavioral limits, not permission isolation. Do not manipulate other tasks.\n'
        'Use this CLI to explicitly checkpoint ready after handoff, blocked on blockers, '
        'and submitted with evidence on delivery. Herdr idle/done is NOT completion.\n'
        'Checkpoint command prefix: ' + shlex.join(command) + '\n'
        'Append --status ready|blocked|submitted --summary TEXT --next-action TEXT '
        '[--evidence REFERENCE (repeatable)]. Never store a full conversation.\n'
        'Continuation is summary-based, NOT automatic Pi conversation replay. '
        'If prior delivery or side effects are uncertain, reconcile first; never repeat them blindly.\n'
        + json.dumps(summary, ensure_ascii=False, indent=2)
    )


def dispatch(store, task_id, herdr, *, resume=False, confirm_continue=False, direction='down',
             member_id=None):
    require(os.environ.get('HERDR_ENV') == '1', 'dispatch requires HERDR_ENV=1')
    require(direction in {'down', 'right'}, 'Invalid split direction')
    require(resume == confirm_continue, 'Continuation requires BOTH --resume and --confirm-continue')
    attempt_id = uuid.uuid4().hex
    with store.transaction() as data:
        task = task_for(data, task_id)
        require(task['status'] not in {'submitted', 'accepted'}, 'Submitted/accepted tasks cannot dispatch')
        require(not owner_alive(task['dispatch_owner']), 'A dispatch process is still alive; reconcile later')
        require(task['status'] == 'created' or resume,
                'Already dispatched or uncertain; PM must --resume --confirm-continue')
        if member_id:
            member = member_for(data, member_id)
            require(not owner_alive(member['operation_owner']), 'Member operation still running')
            require(not member['operation_owner'] or (resume and member['operation'] == 'assign'),
                    'Interrupted member operation; explicitly resume that operation first')
            require(task['project'] == member['project'] and task['role'] == member['role'],
                    'Task project/role must exactly match the member')
            require((not task.get('member') and not task['attempts'])
                    or task.get('member') == member_id, 'Task already belongs to another execution path')
            require(member['status'] == 'ready'
                    or (resume and member['status'] in {'busy', 'needs-reconcile'}
                        and member.get('current_task') == task_id
                        and member.get('operation') == 'assign'),
                    'Member must acknowledge member-ready before assignment')
            require(not any(t.get('member') == member_id and t['id'] != task_id
                            and t['status'] != 'accepted' for t in data['tasks'].values()),
                    'Member has an unaccepted task')
            task.update(group=member['group'], member=member_id, instance=member['instance'].copy())
            member.update(status='busy', current_task=task_id, operation='assign',
                          operation_owner=os.getpid())
            group_event(data, 'member', member, 'assigning', task=task_id)
        else:
            require(not task.get('member'), 'Group tasks must use assign --member')
            for other in data['tasks'].values():
                if (not other.get('group') and other['id'] != task_id
                        and other['project'] == task['project'] and other['role'] == task['role']
                        and other['attempts'] and other['status'] != 'accepted'):
                    raise RuntimeError_('Another unaccepted task owns this project/role')
        task.update(status='dispatching', dispatch_owner=os.getpid())
        task['attempts'].append({'id': attempt_id, 'at': timestamp(), 'resume': resume})
        event(data, task, 'dispatching', dispatch_id=attempt_id, confirmed=confirm_continue)

    def update(kind, **changes):
        with store.transaction() as data:
            current = task_for(data, task_id)
            require(current['attempts'][-1]['id'] == attempt_id, 'Dispatch generation changed')
            current.update(changes)
            event(data, current, kind, dispatch_id=attempt_id)

    try:
        herdr.check_help()
        agents = herdr.agents()
        data = store.read()
        task = task_for(data, task_id)
        if member_id:
            bound = member_for(data, member_id)['instance']
            registered = data['instances'].get(bound['name'])
            require(registered == bound and registered.get('member') == member_id
                    and registered.get('group') == task['group'], 'Member instance registration mismatch')
            require(any(identity_matches(bound, a) for a in agents),
                    'Member instance missing/changed; reconcile manually, never auto-replace')
            candidates = [registered]
        else:
            candidates = [r for r in data['instances'].values()
                          if r['project'] == task['project'] and r['role'] == task['role']
                          and not r.get('group') and not r.get('member') and not r.get('retired')]
        require(len(candidates) <= 1, 'Ambiguous registered instances; reconcile manually')
        record = candidates[0] if candidates else None
        if record:
            matches = [a for a in agents if identity_matches(record, a)]
            if len(matches) == 1:
                require(idle(herdr.get(record)),
                        'Registered instance is busy/blocked/not ready; never preempt')
                require(not any(t['id'] != task_id and t['status'] != 'accepted'
                                and t['instance'] and t['instance']['name'] == record['name']
                                for t in data['tasks'].values()), 'Instance has an unresolved task')
            else:
                require(resume and confirm_continue,
                        'Registered instance missing/identity mismatch; PM must confirm replacement')
                with store.transaction() as current:
                    current['instances'][record['name']]['retired'] = True
                    event(current, current['tasks'][task_id], 'instance-retired', name=record['name'])
                record = None
        if record is None:
            # Never adopt existing unregistered agents, even if role/cwd look suitable.
            name = 'role-' + uuid.uuid4().hex[:27]
            split = herdr.run('pane', 'split', '--current', '--direction', direction,
                              '--cwd', task['project'], '--no-focus')
            pane = split.get('pane', {}).get('pane_id')
            require(isinstance(pane, (str, int)) and not isinstance(pane, bool)
                    and bool(str(pane)), 'Missing split pane id; inspect Herdr, never auto-close panes')
            update('pane-created', pending_instance={'name': name, 'pane': pane,
                                                    'project': task['project']})
            started = herdr.run('agent', 'start', name, '--kind', 'pi', '--pane', str(pane),
                                '--', '--thinking', 'high')
            agent, argv = started.get('agent'), started.get('argv')
            require(isinstance(agent, dict), 'Missing started agent identity')
            record = {'name': name, 'pane': pane, 'project': task['project'],
                      'cwd': task['project'], 'role': task['role'],
                      'session': session_pointer(agent), 'retired': False}
            # Persist returned identity even if the post-start validation fails.
            with store.transaction() as current:
                current['instances'][name] = record
                current['tasks'][task_id]['instance'] = record.copy()
                event(current, current['tasks'][task_id], 'instance-started', name=name)
            require(isinstance(argv, list) and all(isinstance(x, str) for x in argv),
                    'Missing actual start argv')
            thinking = [i for i, value in enumerate(argv) if value == '--thinking']
            require(len(thinking) == 1 and thinking[0] + 1 < len(argv)
                    and argv[thinking[0] + 1] == 'high'
                    and not any(x.startswith('--thinking=') for x in argv)
                    and argv and Path(argv[0]).name == 'pi', 'Pi/high not verified in actual argv')
            require(identity_matches(record, agent) and idle(agent), 'Started instance identity/readiness mismatch')
            with store.transaction() as current:
                current['instances'][name]['high_verified'] = True
                event(current, current['tasks'][task_id], 'pi-high-verified', argv=argv)
        require(record.get('high_verified') or store.read()['instances'][record['name']].get('high_verified'),
                'Instance has no verified Pi/high start; manual reconciliation needed')
        update('instance-bound', instance=store.read()['instances'][record['name']].copy())
        # Re-read live identity immediately before sending; no reliance on old idle snapshots.
        matches = [a for a in herdr.agents() if identity_matches(record, a)]
        require(len(matches) == 1, 'Instance changed before prompt; not sent')
        require(idle(herdr.get(record)), 'Instance became busy/not ready before prompt; not sent')
        update('prompt-sending')  # Durable before any possibly ambiguous input delivery.
        herdr.run('agent', 'prompt', record['name'], prompt_text(store, task_id, attempt_id),
                  '--wait', '--timeout', str(herdr.timeout_ms))
        with store.transaction() as current:
            task = task_for(current, task_id)
            if task['status'] == 'dispatching':
                task.update(status='assigned', next_action='Role must checkpoint ready/submitted/blocked')
            task.pop('pending_instance', None)
            event(current, task, 'prompt-returned')
    except Exception as exc:
        update('needs-reconcile', status='needs-reconcile',
               next_action='PM inspect delivery/identity, then explicitly confirm continuation. '
                           f'Reason: {exc}')
        raise
    finally:
        with store.transaction() as data:
            current = task_for(data, task_id)
            current['dispatch_owner'] = None
            event(data, current, 'dispatch-ended', dispatch_id=attempt_id)
            if member_id:
                member = member_for(data, member_id)
                member.update(operation_owner=None, status='needs-reconcile'
                              if current['status'] == 'needs-reconcile' else 'busy')
                group_event(data, 'member', member, 'assignment-ended', task=task_id)
    return task_for(store.read(), task_id)


def group_event(data, entity, obj, kind, **details):
    data['events'].append({'at': timestamp(), entity: obj['id'], 'kind': kind, **details})
    obj['updated_at'] = timestamp()


def group_for(data, group_id):
    require(group_id in data['groups'], f'Unknown group: {group_id}')
    return data['groups'][group_id]


def member_for(data, member_id):
    require(member_id in data['members'], f'Unknown member: {member_id}')
    return data['members'][member_id]


def group_create(store, package):
    require(isinstance(package, dict) and set(package) == {'id', 'project', 'goal', 'inputs'},
            'Group package keys must be exactly: id, project, goal, inputs')
    require(isinstance(package['id'], str) and ID_PATTERN.fullmatch(package['id']), 'Invalid group id')
    require(nonblank(package['goal']) and isinstance(package['inputs'], list)
            and all(nonblank(x) for x in package['inputs']), 'Group goal/inputs are required')
    group = dict(package, project=absolute_path(package['project']))
    require(Path(group['project']).is_dir(), 'Group project must be an existing directory')
    with store.transaction() as data:
        require(group['id'] not in data['groups'], 'Duplicate group id')
        data['groups'][group['id']] = group
        group_event(data, 'group', group, 'group-created')
    return group


def member_view(member):
    result = dict(member, persisted_status=member['status'])
    if member['operation_owner'] and not owner_alive(member['operation_owner']):
        result.update(status='needs-reconcile',
                      next_action=f'Interrupted {member["operation"]}; PM inspect and explicitly resume '
                                  'that command with --resume --confirm-continue. Do not repeat side effects blindly.')
    return result


def group_show(store, group_id):
    data = store.read()
    group = group_for(data, group_id)
    members = [member_view(m) for m in data['members'].values() if m['group'] == group_id]
    return {'group': group, 'members': members,
            'departed_summaries': [{'member': m['id'], 'role': m['role'], 'summary': m['summary']}
                                  for m in members if m['status'] == 'left'],
            'accepted_tasks': [{'id': t['id'], 'member': t.get('member'),
                                'summary': t['checkpoints'][-1]['summary'] if t['checkpoints'] else t['goal'],
                                'evidence': t['evidence'], 'acceptance_note': t['acceptance_note']}
                               for t in data['tasks'].values()
                               if t.get('group') == group_id and t['status'] == 'accepted']}


def group_help(herdr, *, closing=False):
    commands = (
        (('tab', 'get'), ('tab get', '<tab_id>')),
        (('tab', 'list'), ('tab list', '--workspace')),
        (('tab', 'close'), ('tab close', '<tab_id>')),
        (('pane', 'list'), ('pane list', '--workspace')),
        (('agent', 'get'), ('agent get', '<target>')),
        (('agent', 'list'), ('agent list',)),
    ) if closing else (
        (('tab', 'create'), ('--workspace', '--cwd', '--label', '--no-focus')),
        (('agent', 'start'), ('--kind', 'pi', '--pane', 'AGENT_ARG')),
        (('agent', 'get'), ('agent get', '<target>')),
        (('agent', 'prompt'), ('<TARGET>', '<TEXT>', '--wait', '--timeout')),
    )
    for command, tokens in commands:
        help_text = herdr.run(*command, '--help', help_text=True)
        require(all(token in help_text for token in tokens), 'Unsupported Herdr group CLI contract')


def check_high(argv):
    require(isinstance(argv, list) and argv and all(isinstance(x, str) for x in argv),
            'Missing actual start argv')
    positions = [i for i, arg in enumerate(argv) if arg == '--thinking']
    require(Path(argv[0]).name == 'pi' and len(positions) == 1
            and positions[0] + 1 < len(argv) and argv[positions[0] + 1] == 'high'
            and not any(x.startswith('--thinking=') for x in argv), 'Pi/high not verified')


def member_update(store, member_id, kind, **changes):
    with store.transaction() as data:
        member = member_for(data, member_id)
        member.update(changes)
        group_event(data, 'member', member, kind)


def member_prompt(store, member_id):
    member = member_for(store.read(), member_id)
    record = member['instance']
    snapshot = group_show(store, member['group'])
    summary = {key: snapshot[key] for key in ('group', 'departed_summaries', 'accepted_tasks')}
    command = [sys.executable, str(Path(__file__).resolve()), '--state-dir', str(store.directory)]
    ready = command + ['member-ready', member_id, '--instance', record['name'],
                       '--session', record['session']['value'], '--join-id', member['attempts'][-1]['id']]
    return ('You are an execution role, not PM. Do not create subagents, invoke delegation entrypoints, '
            'or switch identity. These are behavioral rules, NOT permission isolation.\n'
            'This is group membership onboarding ONLY, not a task. Do not implement or write project files. '
            'Read your role manual as needed at: ' + member['role'] + '\n'
            'Group reference command: ' + shlex.join(command + ['group-show', member['group']]) + '\n'
            'Acknowledge onboarding ONLY with: ' + shlex.join(ready) + '\n'
            'member-ready is not task completion; wait for PM assignment. Do not replay previous work. '
            'Write only your membership acknowledgment in this ledger. Summary only, no full conversation.\n'
            + json.dumps(summary, ensure_ascii=False, indent=2))


def join(store, group_id, member_id, role, herdr, *, resume=False, confirm_continue=False):
    require(os.environ.get('HERDR_ENV') == '1', 'join requires HERDR_ENV=1')
    workspace = os.environ.get('HERDR_WORKSPACE_ID')
    require(nonblank(workspace), 'join requires explicit HERDR_WORKSPACE_ID; never use UI focus')
    require(resume == confirm_continue, 'Use BOTH --resume and --confirm-continue')
    require(isinstance(member_id, str) and ID_PATTERN.fullmatch(member_id), 'Invalid member id')
    role = absolute_path(role)
    require(Path(role).is_file(), 'join role must be an existing absolute role manual file')
    with store.transaction() as data:
        group = group_for(data, group_id)
        if member_id in data['members']:
            member = member_for(data, member_id)
            require(member['group'] == group_id and member['role'] == role,
                    'Member id has a different group/role identity')
            require(member['status'] != 'left', 'Left member cannot rejoin; use a NEW member id')
            require(member['workspace'] == workspace, 'Member workspace differs from HERDR_WORKSPACE_ID')
            require(not owner_alive(member['operation_owner']), 'Member operation is still running')
            require(member['operation'] == 'join', 'Member already assigned/leaving; use the matching command')
            interrupted = bool(member['operation_owner'])
            if member['status'] in {'ready', 'awaiting-ready'} and not resume and not interrupted:
                return member  # A duplicate join is not a new prompt or new tab.
            require(resume and (member['status'] in {'joining', 'awaiting-ready', 'needs-reconcile'}
                               or (interrupted and member['status'] == 'ready')),
                    'Uncertain join; inspect group-show, then --resume --confirm-continue')
            require(member['instance'] and member['instance'].get('high_verified'),
                    'Partial creation cannot be replayed; reconcile the recorded tab/name manually')
        else:
            require(not resume, 'Cannot resume an unknown member')
            member = {'id': member_id, 'group': group_id, 'project': group['project'],
                      'role': role, 'workspace': workspace, 'instance': None, 'tab_id': None,
                      'root_pane': None, 'created_tab': False, 'attempts': [], 'summary': None,
                      'current_task': None, 'operation_owner': None}
            data['members'][member_id] = member
        member.update(status='joining', operation='join', operation_owner=os.getpid())
        member['attempts'].append({'id': uuid.uuid4().hex, 'at': timestamp(), 'resume': resume})
        group_event(data, 'member', member, 'joining', join_id=member['attempts'][-1]['id'])
    try:
        group_help(herdr)
        member = member_for(store.read(), member_id)
        if member['instance'] is None:
            name = 'role-' + uuid.uuid4().hex[:27]
            member_update(store, member_id, 'tab-creating', pending_name=name)
            created = herdr.run('tab', 'create', '--workspace', workspace, '--cwd', member['project'],
                                '--label', f'{group_id}/{Path(role).parent.name}/{member_id}', '--no-focus')
            tab, root = created.get('tab'), created.get('root_pane')
            require(isinstance(tab, dict) and isinstance(root, dict)
                    and nonblank(tab.get('tab_id')) and nonblank(root.get('pane_id')),
                    'Missing created tab/root pane; inspect manually, never retry creation automatically')
            member_update(store, member_id, 'tab-created', tab_id=tab['tab_id'],
                          root_pane=root['pane_id'], created_tab=True)
            require(tab.get('workspace_id') == workspace and root.get('workspace_id') == workspace
                    and root.get('tab_id') == tab['tab_id'] and tab.get('pane_count') == 1,
                    'Created tab/root workspace or ownership mismatch')
            started = herdr.run('agent', 'start', name, '--kind', 'pi', '--pane', root['pane_id'],
                                '--', '--thinking', 'high')
            agent = started.get('agent')
            require(isinstance(agent, dict), 'Missing started member identity')
            record = {'name': name, 'pane': root['pane_id'], 'project': member['project'],
                      'cwd': member['project'], 'role': role, 'session': session_pointer(agent),
                      'group': group_id, 'member': member_id, 'tab_id': tab['tab_id'],
                      'workspace': workspace, 'created_tab': True, 'retired': False}
            with store.transaction() as data:
                require(name not in data['instances']
                        and not any(r['pane'] == record['pane'] or r['session'] == record['session']
                                    for r in data['instances'].values()),
                        'Duplicate registered member instance identity')
                data['instances'][name] = record
                data['members'][member_id]['instance'] = record.copy()
                group_event(data, 'member', data['members'][member_id], 'member-started')
            check_high(started.get('argv'))
            require(identity_matches(record, agent) and idle(agent), 'Member start identity/readiness mismatch')
            with store.transaction() as data:
                data['instances'][name]['high_verified'] = True
                data['members'][member_id]['instance']['high_verified'] = True
                group_event(data, 'member', data['members'][member_id], 'member-high-verified')
        member = member_for(store.read(), member_id)
        record = member['instance']
        require(record == store.read()['instances'].get(record['name']), 'Member registration mismatch')
        require(idle(herdr.get(record)), 'Member busy/blocked/not ready; no onboarding prompt sent')
        member_update(store, member_id, 'join-prompt-sending')
        herdr.run('agent', 'prompt', record['name'], member_prompt(store, member_id),
                  '--wait', '--timeout', str(herdr.timeout_ms))
        with store.transaction() as data:
            member = member_for(data, member_id)
            if member['status'] == 'joining':
                member['status'] = 'awaiting-ready'
            group_event(data, 'member', member, 'join-prompt-returned')
    except Exception as exc:
        member_update(store, member_id, 'join-needs-reconcile', status='needs-reconcile',
                      next_action='PM inspect delivery; join GROUP MEMBER --role PATH --resume '
                                  f'--confirm-continue only after reconciliation. Reason: {exc}')
        raise
    finally:
        member_update(store, member_id, 'join-ended', operation_owner=None)
    return member_for(store.read(), member_id)


def member_ready(store, member_id, instance, session, join_id):
    with store.transaction() as data:
        member = member_for(data, member_id)
        record = member['instance']
        require(record and record.get('high_verified') and record['name'] == instance
                and record['session']['value'] == session
                and member['attempts'][-1]['id'] == join_id, 'Stale/mismatched member-ready identity')
        require(member['status'] not in {'left', 'leaving'} and member['operation'] != 'leave',
                'Leaving/left member cannot acknowledge ready')
        if member.get('current_task') or member['status'] in {'busy', 'ready'}:
            return member  # Delayed/repeated receipts must never reset active work.
        require(member['operation'] == 'join'
                and member['status'] in {'joining', 'awaiting-ready', 'needs-reconcile'},
                'Member is not awaiting onboarding')
        member.update(status='ready', next_action='PM assign a task')
        group_event(data, 'member', member, 'member-ready', join_id=join_id)
    return member


def tab_snapshot(herdr, workspace):
    tabs = herdr.run('tab', 'list', '--workspace', workspace).get('tabs')
    panes = herdr.run('pane', 'list', '--workspace', workspace).get('panes')
    require(isinstance(tabs, list) and all(isinstance(t, dict) and nonblank(t.get('tab_id')) for t in tabs)
            and isinstance(panes, list)
            and all(isinstance(p, dict) and nonblank(p.get('pane_id')) and nonblank(p.get('tab_id'))
                    for p in panes), 'Cannot verify tab/pane membership; refuse to close')
    return tabs, panes


def leave(store, member_id, summary, herdr, *, resume=False, confirm_continue=False):
    require(os.environ.get('HERDR_ENV') == '1', 'leave requires HERDR_ENV=1')
    require(nonblank(summary), 'leave requires a handoff summary')
    require(resume == confirm_continue, 'Use BOTH --resume and --confirm-continue')
    with store.transaction() as data:
        member = member_for(data, member_id)
        require(member['status'] != 'left', 'Member already left; use a NEW member id for re-entry')
        require(not owner_alive(member['operation_owner']), 'Member operation is still running')
        require(not member['operation_owner'] or resume,
                'Interrupted operation; PM must inspect and --resume --confirm-continue before leave')
        tasks = [t for t in data['tasks'].values() if t.get('member') == member_id]
        require(all(t['status'] == 'accepted' and not t['dispatch_owner'] for t in tasks),
                'All bound tasks must be accepted and all send processes finished before leave')
        if member['operation'] == 'leave':
            require(resume and summary == member['summary'],
                    'Uncertain leave; retain summary and use --resume --confirm-continue')
        require(member['created_tab'] and member['instance'] and member['instance'].get('high_verified'),
                'No verified owned member tab/instance to close; inspect partial startup manually')
        member.update(status='leaving', operation='leave', operation_owner=os.getpid(), summary=summary)
        group_event(data, 'member', member, 'leaving', summary=summary)
    try:
        group_help(herdr, closing=True)
        member = member_for(store.read(), member_id)
        record = member['instance']
        require(record == store.read()['instances'].get(record['name'])
                and record.get('member') == member_id and record.get('group') == member['group']
                and record.get('created_tab') and record['pane'] == member['root_pane']
                and record['tab_id'] == member['tab_id'], 'Owned tab registration mismatch')
        tabs, panes = tab_snapshot(herdr, member['workspace'])
        matching_tabs = [t for t in tabs if t['tab_id'] == member['tab_id']]
        matching_panes = [p for p in panes if p['tab_id'] == member['tab_id']]
        if not matching_tabs and not matching_panes:
            require(resume and member.get('close_attempted'),
                    'Tab absent before verified close; manual reconciliation required')
        else:
            require(len(matching_tabs) == 1 and len(matching_panes) == 1
                    and matching_panes[0]['pane_id'] == record['pane']
                    and matching_tabs[0].get('workspace_id') == member['workspace']
                    and matching_panes[0].get('workspace_id') == member['workspace'],
                    'Tab contains other panes or changed ownership; refuse to close')
            tab = herdr.run('tab', 'get', member['tab_id']).get('tab')
            require(isinstance(tab, dict) and tab.get('tab_id') == member['tab_id']
                    and tab.get('workspace_id') == member['workspace'] and tab.get('pane_count') == 1,
                    'Cannot prove tab has only the registered root pane')
            agents = herdr.agents()
            require(not any((a.get('tab_id') == member['tab_id'] or a.get('pane_id') == record['pane'])
                            and not identity_matches(record, a) for a in agents),
                    'Another agent occupies the tab')
            require(idle(herdr.get(record)), 'Member identity changed/busy/blocked; refuse to close')
            # Recheck membership after the agent query; external UI changes are not lockable here.
            tabs, panes = tab_snapshot(herdr, member['workspace'])
            require([p['pane_id'] for p in panes if p['tab_id'] == member['tab_id']] == [record['pane']]
                    and len([t for t in tabs if t['tab_id'] == member['tab_id']
                             and t.get('pane_count') == 1]) == 1,
                    'Tab membership changed before close; refuse to close')
            member_update(store, member_id, 'tab-close-sending', close_attempted=True)
            herdr.run('tab', 'close', member['tab_id'])
            tabs, panes = tab_snapshot(herdr, member['workspace'])
            require(not any(t['tab_id'] == member['tab_id'] for t in tabs)
                    and not any(p['tab_id'] == member['tab_id'] for p in panes),
                    'Close not confirmed; leave remains needs-reconcile')
        with store.transaction() as data:
            member = member_for(data, member_id)
            member.update(status='left', next_action='New member id required for re-entry')
            data['instances'][record['name']]['retired'] = True
            group_event(data, 'member', member, 'left', summary=summary)
    except Exception as exc:
        member_update(store, member_id, 'leave-needs-reconcile', status='needs-reconcile',
                      next_action='PM inspect tab; leave MEMBER --summary SAME_TEXT --resume '
                                  f'--confirm-continue after reconciliation. Reason: {exc}')
        raise
    finally:
        member_update(store, member_id, 'leave-ended', operation_owner=None)
    return member_for(store.read(), member_id)


def parser():
    result = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    result.add_argument('--state-dir', type=Path, default=DEFAULT_STATE_DIR)
    commands = result.add_subparsers(dest='command', required=True)
    create_cmd = commands.add_parser('create', help='Register a JSON task package (never dispatches)')
    create_cmd.add_argument('--file', required=True, type=Path)
    commands.add_parser('list', help='Read local task summaries; no Herdr calls')
    group_cmd = commands.add_parser('group-create', help='Register {id, project, goal, inputs} JSON')
    group_cmd.add_argument('--file', required=True, type=Path)
    commands.add_parser('group-list', help='Read all group records')
    group_cmd = commands.add_parser('group-show', help='Group, members and minimal handoff summaries')
    group_cmd.add_argument('group')
    members_cmd = commands.add_parser('members', help='Read members; never controls Herdr')
    members_cmd.add_argument('--group')
    for name in ('join', 'assign', 'leave'):
        cmd = commands.add_parser(name)
        if name == 'join':
            cmd.add_argument('group')
            cmd.add_argument('member')
            cmd.add_argument('--role', required=True, help='Absolute path to role manual')
        elif name == 'assign':
            cmd.add_argument('id')
            cmd.add_argument('--member', required=True)
        else:
            cmd.add_argument('member')
            cmd.add_argument('--summary', required=True)
        cmd.add_argument('--resume', action='store_true')
        cmd.add_argument('--confirm-continue', action='store_true')
        cmd.add_argument('--timeout-ms', type=int, default=30000)
    ready_cmd = commands.add_parser('member-ready', help='Onboarding receipt only, NOT task completion')
    ready_cmd.add_argument('member')
    for field in ('instance', 'session', 'join-id'):
        ready_cmd.add_argument('--' + field, required=True)
    for name in ('show', 'recover', 'checkpoint', 'dispatch', 'accept', 'rework'):
        cmd = commands.add_parser(name)
        cmd.add_argument('id')
        if name == 'checkpoint':
            cmd.add_argument('--status', required=True, choices=['ready', 'submitted', 'blocked'])
            for field in ('summary', 'next-action', 'instance', 'session', 'dispatch-id'):
                cmd.add_argument('--' + field, required=True)
            cmd.add_argument('--evidence', action='append', default=[])
        elif name == 'dispatch':
            cmd.add_argument('--resume', action='store_true')
            cmd.add_argument('--confirm-continue', action='store_true')
            cmd.add_argument('--direction', choices=['down', 'right'], default='down')
            cmd.add_argument('--timeout-ms', type=int, default=30000)
        elif name == 'accept':
            cmd.add_argument('--note', required=True, help='PM acceptance rationale/evidence review')
        elif name == 'rework':
            cmd.add_argument('--note', required=True, help='PM reason for rejecting this submission')
            cmd.add_argument('--next-action', required=True, help='Required revision; does not send a prompt')
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    store = Store(args.state_dir)
    try:
        if hasattr(args, 'timeout_ms'):
            require(1 <= args.timeout_ms <= 300000, 'timeout-ms must be between 1 and 300000')
        if args.command == 'group-create':
            value = group_create(store, json.loads(args.file.read_text(encoding='utf-8')))
        elif args.command == 'group-list':
            value = list(store.read()['groups'].values())
        elif args.command == 'group-show':
            value = group_show(store, args.group)
        elif args.command == 'members':
            data = store.read()
            if args.group:
                group_for(data, args.group)
            value = [member_view(m) for m in data['members'].values()
                     if not args.group or m['group'] == args.group]
        elif args.command == 'member-ready':
            value = member_ready(store, args.member, args.instance, args.session, args.join_id)
        elif args.command in {'join', 'assign', 'leave'}:
            herdr = Herdr(timeout_ms=args.timeout_ms)
            options = {'resume': args.resume, 'confirm_continue': args.confirm_continue}
            if args.command == 'join':
                value = join(store, args.group, args.member, args.role, herdr, **options)
            elif args.command == 'assign':
                value = dispatch(store, args.id, herdr, member_id=args.member, **options)
            else:
                value = leave(store, args.member, args.summary, herdr, **options)
        elif args.command == 'create':
            value = create(store, json.loads(args.file.read_text(encoding='utf-8')))
        elif args.command == 'list':
            value = [{key: t[key] for key in ('id', 'project', 'role', 'status', 'next_action')}
                     for t in store.read()['tasks'].values()]
        elif args.command == 'show':
            value = task_for(store.read(), args.id)
        elif args.command == 'recover':
            value = recover(store, args.id)
        elif args.command == 'checkpoint':
            value = checkpoint(store, args.id, status=args.status, summary=args.summary,
                               evidence=args.evidence, next_action=args.next_action,
                               instance=args.instance, session=args.session, dispatch_id=args.dispatch_id)
        elif args.command == 'accept':
            value = accept(store, args.id, args.note)
        elif args.command == 'rework':
            value = rework(store, args.id, args.note, args.next_action)
        else:
            require(1 <= args.timeout_ms <= 300000, 'timeout-ms must be between 1 and 300000')
            value = dispatch(store, args.id, Herdr(timeout_ms=args.timeout_ms),
                             resume=args.resume, confirm_continue=args.confirm_continue,
                             direction=args.direction)
        print(json.dumps(value, ensure_ascii=False, indent=2))
        return 0
    except (RuntimeError_, OSError, ValueError) as exc:
        print(f'role-runtime: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
