"""Package the candidate and checksums, excluding private and generated state."""
from pathlib import Path
import argparse
import hashlib
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from epistarium import __version__

EXCLUDED = {'.git', '.venv', 'venv', 'env', 'private', 'userdata', '__pycache__', '.pytest_cache',
            'build', 'raw-pdfs', 'raw-data', 'sensitive-data', 'interviews', 'respondent-identities',
            'licensed-pdfs', 'private-reports', 'tmp', '.cache', '.claude', '.cursor', '.opencode', '.windsurf'}
SECRET_NAMES = {'credentials.json', 'secrets.json', '.DS_Store'}
SECRET_SUFFIXES = {'.pyc', '.pyo', '.key', '.pem', '.p12', '.pfx'}


def selected_files(root=ROOT):
    selected = []
    for path in sorted(root.rglob('*')):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(root)
        if any(p in EXCLUDED or p.startswith('.venv') or p.endswith('.egg-info') or p.startswith('private-') for p in relative.parts):
            continue
        if path.name in SECRET_NAMES or path.suffix.lower() in SECRET_SUFFIXES or path.name.startswith('.env'):
            continue
        if relative.as_posix() == 'CHECKSUMS_SHA256.txt':
            continue
        if relative.parts[0] == 'dist' and path.name != f'epistarium-{__version__}-py3-none-any.whl':
            continue
        if relative.parts[0] == 'artifacts':
            continue
        selected.append(path)
    return selected


def package(output):
    output = Path(output).resolve()
    if output.is_relative_to(ROOT):
        raise ValueError('Save the archive outside the project root')
    selected = selected_files(ROOT)
    if len([p for p in selected if p.name == 'SKILL.md']) != 10:
        raise ValueError('Expected ten canonical skills in the archive')
    for required in ('LICENSE', 'THIRD_PARTY_NOTICES.md', 'RELEASE.json', f'dist/epistarium-{__version__}-py3-none-any.whl'):
        if ROOT / required not in selected:
            raise ValueError(f'Required release file missing: {required}')
    manifest = ROOT / 'CHECKSUMS_SHA256.txt'
    manifest.write_text('\n'.join(hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.relative_to(ROOT).as_posix()
                                 for p in selected) + '\n', encoding='utf8')
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in selected + [manifest]:
            info = zipfile.ZipInfo(f'EPISTARIUM_v{__version__}/' + path.relative_to(ROOT).as_posix(), date_time=(2026, 11, 4, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise ValueError('Archive CRC check failed')
    return output


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--out', required=True)
    print(package(p.parse_args().out))
