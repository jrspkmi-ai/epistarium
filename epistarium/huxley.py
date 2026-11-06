"""Huxley F3 alpha: conservative DOCX citation/reference alignment (APA author-date).

This is a structural audit, not a semantic evidence checker.  Unusual citations,
fields, notes and layout require human verification. Originals are never modified.
"""
from __future__ import annotations
from .i18n import tr, display_status, localized, get_language
from pathlib import Path
import re, json, shutil, csv, copy, unicodedata
from urllib.parse import quote
from .common import save_json, save_csv, now_iso, sha256

YEAR=r'(?:18|19|20)\d{2}[a-z]?|n\.d\.'
REF_HEAD=re.compile(r'^(.{2,260}?)\s*\(('+YEAR+r')\)\.?\s*(.+)$',re.I)
GROUP=re.compile(r'\(([^()\n]{3,250})\)')
YEAR_MATCH=re.compile(r'(?<!\w)(?:18|19|20)\d{2}[a-z]?(?!\w)|\bn\.d\.',re.I)
NARRATIVE=re.compile(r'\b([^\W\d_][\w\u0300-\u036f’\-]+(?:\s+et\s+al\.)?(?:\s+(?:&|dan|and)\s+[^\W\d_][\w\u0300-\u036f’\-]+)?)\s*\(('+ '(?:'+YEAR+')' + r'(?:\s*,\s*'+'(?:'+YEAR+')'+r')*)\)',re.I)
REF_HEADERS={'references','reference list','bibliography','daftar pustaka','referensi','kepustakaan'}


def _norm_name(text):
    text=re.sub(r'\bet al\.?\b','',text,flags=re.I).replace('&',' dan ')
    text=re.sub(r'\band\b','dan',text,flags=re.I)
    return re.sub(r'[^\w]+',' ',unicodedata.normalize('NFC',text).casefold()).strip()


def _authors(raw):
    raw=unicodedata.normalize('NFC',raw)
    found=re.findall(r"(?:^|[,;&]\s*|\s+and\s+|\s+dan\s+)([^\W\d_][\w\-'’]*(?:\s+[^\W\d_][\w\-'’]*)*),\s*(?:[^\W\d_]\.?)",raw)
    if found:return found
    return [raw.strip().strip('.,')] if raw.strip() else []


def parse_reference(line,loc):
    m=REF_HEAD.match(line.strip())
    if not m:return None
    authors,year,rest=m.groups()
    names=_authors(authors)
    return {'ref_id':loc,'location':loc,'raw':line.strip(),'authors_raw':authors.strip(),
            'first_author':_norm_name(names[0]) if names else '',
            'authors':names,'year':year.lower(),'title_fragment':rest[:120],
            'doi':(re.search(r'10\.\d{4,9}/[^\s]+',line,re.I).group(0).rstrip('.,')
                   if re.search(r'10\.\d{4,9}/[^\s]+',line,re.I) else None)}


def classify_parenthetical(block):
    """Conservatively separate clear dates, author-date candidates, and review."""
    dates=list(YEAR_MATCH.finditer(block))
    if not dates:return 'NON_CITATION'
    prefix=block[:dates[0].start()].strip(' ,;')
    if not prefix:return 'NON_CITATION'  # possibly a narrative citation
    if re.match(r'^\s*(?:survei|survey|periode|period)\b',block,re.I) and not re.search(r',\s*(?:18|19|20)\d{2}',block):
        return 'NON_CITATION'
    if re.search(r'\b(?:18|19|20)\d{2}\s*[-–—]\s*(?:18|19|20)\d{2}\b',block) and ',' not in block:
        return 'NON_CITATION'
    if re.search(r',\s*(?:(?:18|19|20)\d{2}|n\.d\.)',block,re.I):return 'CITATION'
    return 'AMBIGUOUS_REVIEW'


def detect_citations(text,loc,organization_names=None):
    citations=[]; spans=[]
    for g in GROUP.finditer(text):
        part=g.group(1)
        if not YEAR_MATCH.search(part):continue
        count_before=len(citations)
        grouped=';' in part
        for block in part.split(';'):
            if classify_parenthetical(block)!='CITATION':continue
            dates=list(YEAR_MATCH.finditer(block))
            if not dates:continue
            prefix=block[:dates[0].start()].strip(' ,;')
            # A bare date in parentheses is usually from a narrative reference; skip.
            if not prefix or not any(ch.isalpha() for ch in prefix):continue
            name=re.sub(r'^(?:see|lihat|cf\.|misalnya|e\.g\.)\s*','',prefix,flags=re.I).strip()
            if not name or len(name)>90:continue
            for yr in dates:
                if re.search(r'\b(?:p|pp|hlm)\.?\s*$',block[:yr.start()],re.I):continue
                citations.append({'text':f'{name}, {yr.group(0)}','authors_raw':name,
                                  'first_author':_norm_name(re.split(r'\s+(?:&|dan|and)\s+|\s+et\s+al\.?',name,flags=re.I)[0]),
                                  'year':yr.group(0).lower(),'kind':'parenthetical',
                                  'location':loc,'surface':g.group(0),
                                  'highlight_target':(f'{name}, {yr.group(0)}' if grouped else g.group(0)),
                                  'start':g.start(),'end':g.end()})
        if len(citations)>count_before:spans.append((g.start(),g.end()))
    for organization in (organization_names or []):
        pattern=re.compile(r'(?<!\w)'+re.escape(organization)+r'\s*\(('+YEAR+r')\)',re.I)
        for om in pattern.finditer(text):
            if any(a<=om.start()<b for a,b in spans):continue
            citations.append({'text':om.group(0),'authors_raw':organization,
                'first_author':_norm_name(organization),'year':om.group(1).lower(),
                'kind':'narrative_organization','location':loc,
                'surface':om.group(0),'highlight_target':om.group(0),'start':om.start(),'end':om.end()})
            spans.append((om.start(),om.end()))
    for m in NARRATIVE.finditer(text):
        if any(a<=m.start()<b or (m.start()<a<m.end()) for a,b in spans):continue
        name=m.group(1)
        # In multiword names, handle the second surname in a conjunction as first author.
        for year_match in YEAR_MATCH.finditer(m.group(2)):
            citations.append({'text':m.group(0),'authors_raw':name,
                      'first_author':_norm_name(re.split(r'\s+(?:&|dan|and)\s+|\s+et\s+al\.?',name,flags=re.I)[0]),
                      'year':year_match.group(0).lower(),'kind':'narrative',
                      'location':loc,'surface':m.group(0),'highlight_target':m.group(0),
                      'start':m.start(),'end':m.end()})
    return citations


def _locations(doc):
    # Main-body paragraphs and tables are scoped explicitly. Other stories reported as not processed.
    from docx.oxml.ns import qn
    from docx.text.paragraph import Paragraph
    from docx.table import Table
    for i, child in enumerate(doc.element.body.iterchildren()):
        if child.tag==qn('w:p'):
            p=Paragraph(child,doc)
            yield f'body:{i}',p.text,p
        elif child.tag==qn('w:tbl'):
            table=Table(child,doc)
            for ri,row in enumerate(table.rows):
                for ci,cell in enumerate(row.cells):
                    for pi,p in enumerate(cell.paragraphs):
                        yield f'table:{i}:{ri}:{ci}:{pi}',p.text,p


def _has_fields(docx_path):
    import zipfile
    with zipfile.ZipFile(docx_path) as z:
        for filename in z.namelist():
            if filename in ('word/document.xml','word/footnotes.xml','word/endnotes.xml'):
                data=z.read(filename)
                if any(x in data for x in (b'w:instrText',b'w:fldChar',b'CSL_CITATION',b'ADDIN ZOTERO_ITEM',b'Mendeley')):
                    return True
    return False


def _scope_extras(docx_path):
    import zipfile
    with zipfile.ZipFile(docx_path) as z:
        names=z.namelist()
        return {'footnotes':'NOT_PROCESSED' if 'word/footnotes.xml' in names else 'NOT_PRESENT',
                'endnotes':'NOT_PROCESSED' if 'word/endnotes.xml' in names else 'NOT_PRESENT',
                'headers_footers':'NOT_PROCESSED' if any(re.match(r'word/(header|footer)\d+\.xml',x) for x in names) else 'NOT_PRESENT',
                'tables':'PROCESSED_MAIN_BODY', 'figures_text':'NOT_PROCESSED',
                'appendices':'MAIN_BODY_ONLY_IF_FOLLOWS_REFERENCE_HEADING_RULE'}


def _score(c,ref):
    if c['first_author']!=ref['first_author']:return False
    yr=c['year'];ry=ref['year']
    if yr!=ry:return False
    names=_norm_name(c['authors_raw'])
    # A two-author citation MUST match both surnames, regardless of & / dan / and.
    if ' dan ' in names:
        pieces=names.split(' dan ')
        if len(ref['authors'])!=2 or len(pieces)!=2 or _norm_name(ref['authors'][1])!=pieces[1]:return False
    elif 'et al' not in c['authors_raw'].lower() and len(ref['authors'])>1:
        # Single-author short form cannot safely match a multi-author work in APA7.
        return False
    if 'et al' in c['authors_raw'].lower() and len(ref['authors']) < 3:
        # APA 7 uses et al. for 3+ authors. Mark ambiguous/unsupported rather than force match.
        return False
    return True


def _candidate_search(missing, *, online=False, fixture=None):
    if not online and fixture is None:return [],{'status':'NOT_REQUESTED'}
    candidates=[]; logs=[]
    if fixture is not None:
        data=json.loads(Path(fixture).read_text(encoding='utf8')) if isinstance(fixture,(str,Path)) else fixture
        for c in missing:
            key=c['first_author']+'|'+c['year']
            for item in data.get(key,[]):
                candidates.append({'citation_text':c['text'],'provider':'offline_fixture','record':item,
                                   'status':'DRAFT-PERLU-VERIFIKASI'})
        return candidates,{'status':'OFFLINE_FIXTURE','provider':'synthetic_fixture'}
    from .pathfinder_harvest import LimitedClient
    client=LimitedClient(max_requests=10,max_bytes=2_000_000)
    for c in missing[:10]:
        query=f"{c['authors_raw']} {c['year']}"
        url='https://api.crossref.org/works?rows=3&query.bibliographic='+quote(query)
        try:
            raw,_=client.get(url,provider='crossref')
            for x in json.loads(raw).get('message',{}).get('items',[])[:3]:
                candidates.append({'citation_text':c['text'],'provider':'Crossref','record':{
                    'DOI':x.get('DOI'),'title':(x.get('title') or [None])[0],
                    'author':x.get('author',[]),'published':x.get('published',{})},
                    'query_url':url,'status':'DRAFT-PERLU-VERIFIKASI'})
            logs.append({'url':url,'status':'HTTP_OK','checked_at':now_iso()})
        except Exception as exc:
            logs.append({'url':url,'status':'ACCESS_FAILED','error':type(exc).__name__,'checked_at':now_iso()})
    return candidates,{'status':'PARTIAL_OR_COMPLETE','attempts':logs}


def _highlight_span(paragraph, start, end):
    """Highlight exact char span across *plain-text* runs; preserve per-run formatting.

    Returns anchored Run objects for a native Word comment. Unsafe constructs
    (hyperlinks, drawings, citation fields) are never reconstructed.
    """
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.text.run import Run
    runs=list(paragraph.runs)
    text=''.join(r.text for r in runs)
    if text!=paragraph.text or start<0 or end>len(text) or start>=end:
        return []
    selection=[];offset=0
    for run in runs:
        raw=run.text; begin=offset; finish=offset+len(raw);offset=finish
        lo=max(0,start-begin);hi=min(len(raw),end-begin)
        if lo>=hi:continue
        if any(e.tag not in (qn('w:rPr'),qn('w:t')) for e in run._r):return []
        if len([e for e in run._r if e.tag==qn('w:t')])!=1:return []
        selection.append((run,lo,hi))
    if not selection:return []
    highlighted=[]
    for run,lo,hi in selection:
        raw=run.text; parent=run._r.getparent();idx=parent.index(run._r)
        for i,part in enumerate((raw[:lo],raw[lo:hi],raw[hi:])):
            if not part:continue
            element=OxmlElement('w:r')
            if run._r.rPr is not None:element.append(copy.deepcopy(run._r.rPr))
            if i==1:
                rpr=element.find(qn('w:rPr'))
                if rpr is None:rpr=OxmlElement('w:rPr');element.insert(0,rpr)
                old=rpr.find(qn('w:highlight'))
                if old is not None:rpr.remove(old)
                high=OxmlElement('w:highlight');high.set(qn('w:val'),'yellow');rpr.append(high)
            node=OxmlElement('w:t');node.text=part
            if part[0].isspace() or part[-1].isspace():node.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
            element.append(node);parent.insert(idx,element);idx+=1
            if i==1:highlighted.append(Run(element,paragraph))
        parent.remove(run._r)
    return highlighted


def _find_actual_span(c, full_text):
    """Resolve an exact within-paragraph occurrence, not a guessed match."""
    start,end=c['start'],c['end']
    if not 0<=start<end<=len(full_text):return None
    needle=c['highlight_target']
    segment=full_text[start:end]
    position=segment.find(needle)
    if position>=0:return (start+position,start+position+len(needle))
    if c['kind']=='narrative' and segment==c['surface']:
        return start,end
    return None



@localized
def audit(source,out_dir, *, annotate=False, online=False, candidate_fixture=None):
    from docx import Document
    source=Path(source)
    if not source.is_file() or source.suffix.lower()!='.docx':raise ValueError(tr('Input Huxley harus DOCX yang tersedia'))
    out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    doc=Document(source)
    entries=list(_locations(doc));refstart=None
    for i,(loc,text,p) in enumerate(entries):
        if text.strip().casefold() in REF_HEADERS:
            refstart=i;break
    refs=[];cit=[];unparsed=[];classification_review=[]
    if refstart is not None:
        for loc,text,p in entries[refstart+1:]:
            if not text.strip():continue
            r=parse_reference(text,loc)
            if r:refs.append(r)
            else:unparsed.append({'location':loc,'text':text,'status':'MANUAL_REVIEW'})
    organizations=[r['authors'][0] for r in refs if len(r['authors'])==1 and len(r['authors'][0].split())>=2]
    for loc,text,p in (entries if refstart is None else entries[:refstart]):
        cit += detect_citations(text,loc,organization_names=organizations)
        for group in GROUP.finditer(text):
            for block in group.group(1).split(';'):
                if YEAR_MATCH.search(block) and classify_parenthetical(block)=='AMBIGUOUS_REVIEW':
                    classification_review.append({'location':loc,'surface':group.group(0),'status':'AMBIGUOUS_REVIEW'})
    cited_ids=set()
    for i,c in enumerate(cit,1):
        c['citation_id']=f'C{i:03d}'
        possibilities=[r for r in refs if _score(c,r)]
        if len(possibilities)==1:
            c.update(status='MATCHED',matched_ref_ids=[possibilities[0]['ref_id']]);cited_ids.add(possibilities[0]['ref_id'])
        elif len(possibilities)>1:
            c.update(status='AMBIGUOUS',matched_ref_ids=[r['ref_id'] for r in possibilities])
        else:
            # If first author/year without suffix collides with a/b entries, flag ambiguous.
            ambiguity=[r for r in refs if r['first_author']==c['first_author']
                       and r['year'].rstrip('abcdefghijklmnopqrstuvwxyz')==c['year']]
            if ambiguity and all(r['year']!=c['year'] for r in ambiguity):c.update(status='AMBIGUOUS',matched_ref_ids=[r['ref_id'] for r in ambiguity])
            else:c.update(status='MANUAL_REVIEW' if refstart is None or unparsed else 'UNMATCHED_CITATION',matched_ref_ids=[])
    for r in refs:
        r['status']='MATCHED' if r['ref_id'] in cited_ids else 'UNCITED_REFERENCE'
    # If only ambiguous citations point to entry, status requires manual review, not definite uncited.
    amb_ids={x for c in cit if c['status']=='AMBIGUOUS' for x in c['matched_ref_ids']}
    for r in refs:
        if r['ref_id'] in amb_ids and r['status']=='UNCITED_REFERENCE':r['status']='MANUAL_REVIEW'
    missing=[c for c in cit if c['status']=='UNMATCHED_CITATION']
    candidates,search_log=_candidate_search(missing,online=online,fixture=candidate_fixture)
    docx_field=_has_fields(source)
    annotated=None;highlighted=[];highlighted_references=[];anchored_comments=[]
    if annotate:
        dest=out/(source.stem+'_audit_copy.docx')
        if docx_field:
            shutil.copy2(source,dest)
            annotation_status='SKIPPED_DYNAMIC_FIELDS_PRESERVED_BYTE_FOR_BYTE'
        else:
            para_by_loc={loc:(txt,p) for loc,txt,p in entries}
            # Each distinct physical anchor is highlighted once. Multiple logical
            # year citations pointing at the same narrative span share an anchor.
            targets=[]
            for c in cit:
                if c['status'] not in {'AMBIGUOUS','UNMATCHED_CITATION','MANUAL_REVIEW'}:continue
                loc=c['location'];item=para_by_loc.get(loc)
                span=_find_actual_span(c,item[0]) if item else None
                if span:targets.append((loc,span[0],span[1],'citation',c['citation_id'],c['status']))
            for ref in refs:
                if ref['status'] != 'UNCITED_REFERENCE':continue
                loc=ref['location'];item=para_by_loc.get(loc)
                if item:targets.append((loc,0,len(item[0]),'reference',ref['ref_id'],ref['status']))
            # Process rightmost first so original text offsets remain valid even
            # after splitting XML runs. Do not claim success if anchoring fails.
            targets.sort(key=lambda x:(x[0],x[1],x[2]),reverse=True)
            highlighted_spans={}
            for loc,start,end,kind,rid,status in targets:
                key=(loc,start,end)
                if key in highlighted_spans:
                    anchored=highlighted_spans[key]
                else:
                    _,paragraph=para_by_loc[loc]
                    anchored=_highlight_span(paragraph,start,end)
                    if anchored:
                        highlighted_spans[key]=anchored
                        phrase=paragraph.text[start:end]
                        message=(tr('Sitasi tidak ditemukan pasangannya dalam daftar pustaka; periksa identitas sumber.')
                                if status=='UNMATCHED_CITATION' else
                                tr('Identitas sitasi belum pasti; perlu pemeriksaan manusia.')
                                if status in ('AMBIGUOUS','MANUAL_REVIEW') else
                                tr('Tidak ditemukan kutipan untuk referensi ini dalam korpus utama yang diperiksa.'))
                        try:
                            doc.add_comment(anchored,message,author='EPISTARIUM Huxley',initials='HUX')
                            anchored_comments.append({'location':loc,'start':start,'end':end,'type':kind,'message':message})
                        except Exception:
                            pass  # Comment failure is recorded by count, never fabricated.
                if anchored:
                    if kind=='citation':highlighted.append(rid)
                    else:highlighted_references.append(rid)
            doc.save(dest)
            annotation_status='PRECISE_HIGHLIGHT_WITH_NATIVE_COMMENTS' if anchored_comments else ('PARTIAL_PRECISE_HIGHLIGHT' if highlighted or highlighted_references else 'NO_PRECISE_RUN_MATCH_ISSUE_LIST_ONLY')
        annotated=str(dest)
    else:annotation_status='NOT_REQUESTED'
    report={'schema_version':'f3.huxley.0.1','generated_at':now_iso(),'source_docx':str(source),
            'source_sha256':sha256(source),'citation_style':'APA7_AUTHOR_DATE_PARTIAL',
            'coverage':{'main_body':'PROCESSED','reference_heading_found':refstart is not None,
                        'reference_entries_parsed':len(refs),'unparsed_references':unparsed,**_scope_extras(source)},
            'citation_fields_detected':docx_field,'citations':cit,'references':refs,'proposed_additions':candidates,
            'classification_review':classification_review,
            'metadata_search':search_log,'annotation':{'status':annotation_status,'file':annotated,
                'highlighted_citation_ids':highlighted,'highlighted_reference_ids':highlighted_references,
                'native_comments':'CREATED_AND_ANCHORED' if anchored_comments else ('SKIPPED_DYNAMIC_FIELDS' if docx_field else 'NONE_OR_NOT_IMPLEMENTED'),
                'comment_anchors':anchored_comments},
            'limitations':[tr('Cocok bibliografi bukan bukti sumber mendukung klaim; serahkan ke Vanlan.'),
                           tr('Detektor author-date belum mencakup seluruh variasi APA 7 dan catatan kaki.'),
                           tr('Field sitasi dinamis sengaja tidak disentuh.'),
                           tr('Sumber tanpa judul heading pustaka atau sitasi tersebar di lampiran memerlukan audit manual.')]}
    save_json(out/'huxley_audit.json',report)
    save_csv(out/'sitasi.csv',cit,['citation_id','text','kind','location','year','status','matched_ref_ids'])
    save_csv(out/'daftar_pustaka.csv',refs,['ref_id','raw','year','doi','status'])
    save_json(out/'referensi_kandidat_DRAFT.json',{'records':candidates,'status':'DRAFT_PERLU_VERIFIKASI'})
    lines=[tr('# Huxley: audit sitasi dan daftar pustaka'),'',
           tr('Sitasi ditemukan: {v0}; referensi terurai: {v1}; entri tidak dikenali: {v2}.',v0=f'{len(cit)}', v1=f'{len(refs)}', v2=f'{len(unparsed)}'),
           tr('Field dinamis: {v0}; anotasi: {v1}.',v0=f'{docx_field}', v1=f'{annotation_status}'),'',
           tr('## Temuan sitasi'),'']
    for c in cit:lines.append(tr('- {v0} {v1}: **{v2}** `{v3}` → {v4}',v0=c['citation_id'],v1=c['location'],v2=c['status'],v3=c['text'],v4=', '.join(c['matched_ref_ids']) or tr('tanpa pasangan')))
    lines+=['',tr('## Entri daftar pustaka'),'']
    for r in refs:lines.append(f"- {r['ref_id']}: {r['status']} | {r['raw']}")
    lines+=['',tr('## Lingkup dan keterbatasan'),'',tr('Komentar Word native dibuat hanya pada lokasi teks yang dapat ditambatkan. Field dinamis dibiarkan byte-identik dan kasus tak terjangkau ditandai dalam laporan.'),'',
            tr('Pemeriksaan dukungan substansi: **BELUM DILAKUKAN**. Integrasi Vanlan diperlukan.')]
    (out/'laporan_huxley.md').write_text('\n'.join(lines),encoding='utf8')
    return report
