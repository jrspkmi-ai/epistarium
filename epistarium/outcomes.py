"""Execution and deliverable checks stay separate from evidence assessment."""
from .i18n import tr, display_status, localized, get_language
from pathlib import Path
from .common import sha256


def assess_stage(name, result, required_paths):
    errors=[];artifacts=[]
    for item in required_paths:
        path=Path(item)
        if not path.is_file() or (path.stat().st_size==0 and path.suffix not in ('.diff','.ris')):
            errors.append(tr('Artefak wajib belum tersedia: ')+path.name)
        else:artifacts.append({'path':str(path),'sha256':sha256(path)})
    if name=='Ideon ORIGO':
        if result.get('docx_status')!='CREATED_AND_REOPENED':
            errors.append(tr('DOCX ORIGO gagal dibuat atau dibuka ulang'))
        else:
            docpath=Path(result.get('docx_path') or '')
            if not docpath.is_file():errors.append(tr('DOCX ORIGO yang dilaporkan tidak ditemukan'))
            else:artifacts.append({'path':str(docpath),'sha256':sha256(docpath)})
    if name=='Synthia' and result.get('xlsx_status') not in ('created','not_requested'):
        errors.append(tr('Ekspor XLSX yang diminta gagal: ')+str(result.get('xlsx_status')))
    return {'execution_status':'BLOCKED' if errors else 'SUCCESS',
            'deliverable_status':'INCOMPLETE' if errors else 'COMPLETE',
            'evidence_status':'belum dapat diverifikasi','artifacts':artifacts,
            'warnings':[],'errors':errors}
