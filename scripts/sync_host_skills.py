"""Generate a managed Claude project adapter from the ten canonical skills.

This does not install a plugin, modify user settings, or grant tool permissions.
Only untouched files created by this tool can be updated or removed.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from epistarium import __version__


def digest(content):
    return hashlib.sha256(content).hexdigest()


def sync(project_root=ROOT, action='check'):
    root = Path(project_root).resolve()
    source = root / '.agents/skills'
    target = root / '.claude/skills'
    manifest = root / '.claude/epistarium-skills.json'
    # Refuse redirected sources, parents, or destination files.
    for directory in (root / '.agents', source, root / '.claude', target):
        if directory.is_symlink():
            raise ValueError(f'Symlink directory refused: {directory.name}')
    if manifest.is_symlink():
        raise ValueError('Symlink manifest refused')
    entries = sorted(source.glob('*/SKILL.md'))
    if len(entries) != 10:
        raise ValueError('Expected exactly ten canonical skills')
    expected = {}
    saved = {}
    for skill in entries:
        if skill.parent.is_symlink():
            raise ValueError('Symlink skill source refused')
        for path in sorted(skill.parent.rglob('*')):
            if path.is_symlink():
                raise ValueError('Symlink source refused')
            if path.is_file():
                expected[path.relative_to(source).as_posix()] = path.read_bytes()
    previous = {}
    if manifest.exists():
        saved = json.loads(manifest.read_text(encoding='utf8'))
        if saved.get('generator') != 'epistarium-project-adapter-v1':
            raise ValueError('Unrecognized adapter manifest')
        previous = saved['files']
        if not isinstance(previous, dict):
            raise ValueError('Invalid adapter manifest')
        for rel, sha in previous.items():
            candidate = Path(rel)
            if candidate.is_absolute() or '..' in candidate.parts or candidate.as_posix() != rel:
                raise ValueError('Unsafe adapter manifest path')
            dest = target / candidate
            if dest.is_symlink() or any(p.is_symlink() for p in dest.parents if p.is_relative_to(root)):
                raise ValueError('Symlink target refused')
            if dest.exists() and (not dest.is_file() or digest(dest.read_bytes()) != sha):
                raise ValueError(f'Modified adapter file, preserve it before proceeding: {rel}')
    # Preflight all collisions, including extra files inside an owned skill folder.
    owned_skills = {Path(rel).parts[0] for rel in previous}
    for skill_dir in sorted(target.glob('*')) if target.exists() else []:
        if skill_dir.name not in {p.parent.name for p in entries} | owned_skills:
            continue
        if skill_dir.is_symlink():
            raise ValueError('Symlink skill target refused')
        for path in skill_dir.rglob('*') if skill_dir.is_dir() else [skill_dir]:
            rel = path.relative_to(target).as_posix()
            if path.is_symlink() or (path.is_file() and rel not in previous):
                raise ValueError(f'Unmanaged adapter content: {rel}')
    for rel in expected:
        dest = target / rel
        if dest.with_name(dest.name + '.epistarium-tmp').exists() or dest.with_name(dest.name + '.epistarium-tmp').is_symlink():
            raise ValueError('Temporary adapter path already exists')
        if dest.exists() and rel not in previous:
            raise ValueError(f'Existing unmanaged file: {rel}')
        if dest.is_symlink() or any(p.is_symlink() for p in dest.parents if p.is_relative_to(root)):
            raise ValueError('Symlink target refused')
    hashes = {rel: digest(content) for rel, content in expected.items()}
    stale = hashes != previous or saved.get('version') != __version__ or any(not (target / rel).is_file() for rel in hashes)
    if action == 'check':
        return {'status': 'NOT_INSTALLED' if not manifest.exists() else 'STALE' if stale else 'PASS',
                'version': __version__, 'skill_count': len(entries), 'file_count': len(expected),
                'native_activation': 'NOT_RUN', 'source': '.agents/skills', 'target': '.claude/skills'}
    if action == 'apply':
        for rel in previous.keys() - expected.keys():
            (target / rel).unlink(missing_ok=True)
        for rel, content in expected.items():
            dest = target / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            temporary = dest.with_name(dest.name + '.epistarium-tmp')
            if temporary.exists() or temporary.is_symlink():
                raise ValueError('Temporary adapter path already exists')
            temporary.write_bytes(content)
            temporary.replace(dest)
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(json.dumps({'generator': 'epistarium-project-adapter-v1', 'version': __version__,
                                      'source': '.agents/skills', 'files': hashes}, indent=2) + '\n', encoding='utf8')
        return sync(root, 'check')
    if action == 'remove':
        # Remove only managed files. An unrelated skill folder is never removed.
        for rel in previous:
            (target / rel).unlink(missing_ok=True)
        for directory in sorted(target.rglob('*'), key=lambda p: len(p.parts), reverse=True) if target.exists() else []:
            if directory.is_dir() and directory.parts[len(target.parts)] in owned_skills:
                try:
                    directory.rmdir()
                except OSError:
                    pass
        manifest.unlink(missing_ok=True)
        return {'status': 'REMOVED', 'files_removed': len(previous), 'native_activation': 'NOT_RUN'}
    raise ValueError('Unknown action')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', choices=['claude'], required=True)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--apply', action='store_true')
    group.add_argument('--remove', action='store_true')
    group.add_argument('--check', action='store_true')
    args = parser.parse_args()
    try:
        result = sync(action='apply' if args.apply else 'remove' if args.remove else 'check')
        print(json.dumps(result, indent=2))
        return 0 if result['status'] in ('PASS', 'REMOVED') else 3
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'Adapter blocked: {exc}', file=sys.stderr)
        return 4


if __name__ == '__main__':
    raise SystemExit(main())
