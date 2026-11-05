"""Verify candidate CRC, payload checksums, paths, persona count, and wheel metadata."""
from pathlib import Path,PurePosixPath
import argparse,hashlib,io,json,stat,zipfile
from email.parser import BytesParser
from package_release import EXCLUDED,SECRET_NAMES,SECRET_SUFFIXES
from epistarium import __version__


def verify(path):
    archive=Path(path);errors=[]
    with zipfile.ZipFile(archive) as z:
        names=z.namelist();prefix=f'EPISTARIUM_v{__version__}/'
        if len(names)!=len(set(names)):errors.append('duplicate archive entries')
        if z.testzip() is not None:errors.append('CRC failure')
        for info in z.infolist():
            p=PurePosixPath(info.filename)
            if not info.filename.startswith(prefix) or p.is_absolute() or '..' in p.parts or '\\' in info.filename or ':' in info.filename:
                errors.append('unsafe archive path')
            if any(part in EXCLUDED or part.endswith('.egg-info') or part.startswith('.venv') or part.startswith('private-') for part in p.parts):
                errors.append('excluded path in archive')
            if p.name in SECRET_NAMES or p.suffix in SECRET_SUFFIXES or p.name.startswith('.env'):
                errors.append('excluded file in archive')
            if stat.S_ISLNK(info.external_attr>>16):errors.append('symlink in archive')
        manifest=z.read(prefix+'CHECKSUMS_SHA256.txt').decode()
        checked=[]
        for line in manifest.splitlines():
            expected,relative=line.split('  ',1);checked.append(prefix+relative)
            if hashlib.sha256(z.read(prefix+relative)).hexdigest()!=expected:errors.append('payload hash mismatch: '+relative)
        if set(checked)!=(set(names)-{prefix+'CHECKSUMS_SHA256.txt'}):errors.append('manifest coverage mismatch')
        if len(checked)!=len(set(checked)):errors.append('duplicate manifest entries')
        skills=[n for n in names if n.endswith('/SKILL.md')]
        if len(skills)!=10 or any(not n.startswith(prefix+'.agents/skills/') for n in skills):errors.append('persona count/location mismatch')
        release=json.loads(z.read(prefix+'RELEASE.json'))
        if release['version']!=__version__ or release['status']!='RELEASE_CANDIDATE' or release['public_release_gate'] not in ('PENDING_CROSS_OS_CI','GO_BERSYARAT'):errors.append('release metadata mismatch')
        wheelname=prefix+f'dist/epistarium-{__version__}-py3-none-any.whl'
        wheelcontent=z.read(wheelname)
        with zipfile.ZipFile(io.BytesIO(wheelcontent)) as wheel:
            member=next(n for n in wheel.namelist() if n.endswith('.dist-info/METADATA'))
            metadata=BytesParser().parsebytes(wheel.read(member))
            if metadata['Version']!=__version__ or metadata['License-Expression']!='MIT':errors.append('wheel metadata mismatch')
            if any(n.endswith(('.so','.dll','.pyd','.dylib')) for n in wheel.namelist()):errors.append('unexpected bundled native dependency')
            if not any(n.endswith('/licenses/third_party/SimpleEnglish/LICENSE') for n in wheel.namelist()):errors.append('SimpleEnglish notice missing from wheel')
    return {'status':'FAIL' if errors else 'PASS','archive':archive.name,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
            'file_count':len(names),'payload_hash_count':len(checked),'skill_count':len(skills),'wheel_sha256':hashlib.sha256(wheelcontent).hexdigest(),'errors':errors}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('archive');p.add_argument('--out');args=p.parse_args();result=verify(args.archive)
    value=json.dumps(result,indent=2)
    if args.out:Path(args.out).write_text(value+'\n',encoding='utf8')
    print(value);raise SystemExit(0 if result['status']=='PASS' else 1)
