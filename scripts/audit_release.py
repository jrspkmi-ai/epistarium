"""Scan selected release files for excluded paths and recognizable secret forms."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from package_release import ROOT,selected_files

PATTERNS={
 'private_key':re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
 'github_token':re.compile(rb'gh[pousr]_[A-Za-z0-9]{32,}'),
 'openai_key':re.compile(rb'sk-(?:proj-)?[A-Za-z0-9_-]{40,}'),
 'aws_access_id':re.compile(rb'AKIA[0-9A-Z]{16}'),
 'credential_url':re.compile(rb"https?://[^\s/:\"']+:[^\s/@\"']+@[^\s\"'<>]+")}


SYNTHETIC_URLS = {
 'tests/test_f4_pathfinder.py': b'https://' + b'user:pass@example.org/feed',
 'tests/test_liora_agresa_stabilization.py': b'https://' + b'user:pw@scopus.com/source',
}


def scan(root=ROOT):
    findings=[];reviewed=[];files=selected_files(root)
    for path in files:
        content=path.read_bytes()
        for label,pattern in PATTERNS.items():
            for match in pattern.finditer(content):
                relative=path.relative_to(root).as_posix()
                if label=='credential_url' and SYNTHETIC_URLS.get(relative)==match.group(0):
                    reviewed.append({'file':relative,'type':label,'reason':'Exact synthetic URL used to test credential rejection'})
                else:
                    findings.append({'file':relative,'type':label,'value':'REDACTED'})
    return {'status':'FAIL' if findings else 'PASS','selected_file_count':len(files),'recognizable_secret_findings':findings,'reviewed_synthetic_matches':reviewed,
            'excluded_paths':['private','userdata','interviews','respondent-identities','licensed-pdfs','raw-data','.venv','.env','generated-host-adapters'],
            'scope':'Filename exclusions and high-confidence byte patterns only. This is not proof that all private data or malicious content is absent.'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);args=p.parse_args();result=scan()
    Path(args.out).write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,indent=2));raise SystemExit(0 if result['status']=='PASS' else 1)
