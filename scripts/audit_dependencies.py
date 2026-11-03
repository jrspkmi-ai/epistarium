"""Inventory installed metadata and license hashes, not a legal or CVE verdict."""
from importlib import metadata
from pathlib import Path
import argparse
import hashlib
import json
import platform
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name


def inventory():
    installed = {canonicalize_name(d.metadata['Name']): d for d in metadata.distributions()}
    runtime, queue = set(), ['epistarium']
    while queue:
        name = queue.pop()
        if name in runtime or name not in installed:
            continue
        runtime.add(name)
        for req in installed[name].requires or []:
            parsed = Requirement(req)
            if parsed.marker is None or parsed.marker.evaluate({'extra': ''}):
                queue.append(canonicalize_name(parsed.name))
    entries = []
    for name, dist in sorted(installed.items()):
        m, licenses = dist.metadata, []
        for rel in dist.files or []:
            filename = Path(str(rel)).name.lower()
            if filename.startswith(('license', 'copying', 'notice')) and ('.dist-info/' in str(rel) or len(Path(str(rel)).parts) <= 3):
                path = Path(dist.locate_file(rel))
                if path.is_file():
                    licenses.append({'file': str(rel), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        entries.append({'name': m['Name'], 'version': dist.version,
                        'role': 'original-project' if name == 'epistarium' else 'runtime' if name in runtime else 'test-build-environment',
                        'license_expression': m.get('License-Expression'), 'license_field': m.get('License'),
                        'license_classifiers': [c for c in m.get_all('Classifier', []) if c.startswith('License')],
                        'project_urls': m.get_all('Project-URL', []), 'homepage': m.get('Home-page'),
                        'requirements': dist.requires or [], 'license_files': licenses,
                        'evidence': 'installed metadata and file hashes', 'legal_compatibility': 'NOT_ASSESSED'})
    return {'python': platform.python_version(), 'platform': platform.platform(), 'distribution_count': len(entries),
            'runtime_dependency_count': len(runtime - {'epistarium'}), 'distributions': entries,
            'conditional_dependency': {'requirement': "tzdata>=2024.1; sys_platform == 'win32'", 'execution_status': 'NOT_RUN',
                                       'source': 'https://github.com/python/tzdata/blob/master/LICENSE'},
            'scope': 'Installed distributions, not future resolver outcomes or all vendored native components.'}


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--out', required=True)
    result = inventory()
    Path(p.parse_args().out).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({k: result[k] for k in ('distribution_count', 'runtime_dependency_count', 'python')}, indent=2))
