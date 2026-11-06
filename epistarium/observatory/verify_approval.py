"""Compare an authorized local artifact snapshot with the current files."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath

from .store import RUN_ID, read_json


def verify(root,run_id):
    if not isinstance(run_id,str) or not RUN_ID.fullmatch(run_id):raise ValueError('Invalid run ID')
    base=Path(root).expanduser().resolve()
    auth=read_json(base/'runs'/run_id/'release_authorization.json')
    if not isinstance(auth,dict) or auth.get('gate')!='FINAL_ARTIFACT' or auth.get('decision')!='approve':
        raise ValueError('No final release authorization')
    root_out=base/'outputs'/run_id
    if root_out.is_symlink() or not root_out.is_dir():raise ValueError('Output directory unavailable')
    expected=auth.get('artifact_snapshot')
    if not isinstance(expected,list) or len(expected)>1000:raise ValueError('Invalid snapshot')
    mismatches=[];seen=set()
    for item in expected:
        if not isinstance(item,dict) or set(item)!={'path','sha256'}:raise ValueError('Invalid snapshot entry')
        name=item['path']
        if not isinstance(name,str) or '\\' in name or ':' in name or PurePosixPath(name).is_absolute() or any(x in ('','.','..') for x in name.split('/')):
            raise ValueError('Invalid snapshot path')
        if name in seen:raise ValueError('Duplicate snapshot path')
        seen.add(name)
        path=root_out
        for component in PurePosixPath(name).parts:
            path=path/component
            if path.is_symlink():break
        if path.is_symlink() or not path.is_file():
            mismatches.append({'path':name,'reason':'MISSING_OR_SYMLINK'});continue
        h=hashlib.sha256()
        with path.open('rb') as stream:
            for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
        if h.hexdigest()!=item['sha256']:mismatches.append({'path':name,'reason':'HASH_CHANGED'})
    current=set()
    for path in root_out.rglob('*'):
        if path.is_symlink():
            mismatches.append({'path':path.relative_to(root_out).as_posix(),'reason':'SYMLINK_PRESENT'})
        elif path.is_file():current.add(path.relative_to(root_out).as_posix())
    for name in sorted(current-seen):mismatches.append({'path':name,'reason':'ADDED_AFTER_APPROVAL'})
    return {'research_run_id':run_id,'status':'UNCHANGED' if not mismatches else 'CHANGED',
            'checked_artifact_count':len(seen),'mismatches':mismatches,
            'interpretation':'File integrity only. Not identity or evidence verification.'}


def main(argv=None):
    parser=argparse.ArgumentParser(description='Check local approved artifact hashes')
    parser.add_argument('--root',required=True);parser.add_argument('--run-id',required=True)
    args=parser.parse_args(argv)
    try:
        result=verify(args.root,args.run_id)
        print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result['status']=='UNCHANGED' else 3
    except (OSError,ValueError) as exc:
        print(json.dumps({'status':'BLOCKED','reason':str(exc)}));return 4

if __name__=='__main__':raise SystemExit(main())
