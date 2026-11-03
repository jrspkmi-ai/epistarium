"""Creates *synthetic* F2 input. All authors, titles and DOIs are invented.
Do not cite these entries as scientific literature.
"""
import json
from pathlib import Path
import fitz

project_root=Path(__file__).resolve().parents[1]
root=Path(__file__).resolve().parent/'f2_synthetic'
pdfs=root/'pdfs';pdfs.mkdir(parents=True,exist_ok=True)

def make(name,doi,text=True,title=None):
    d=fitz.open();p=d.new_page()
    if text:
        lines=[
            'SYNTHETIC TEST DOCUMENT. NOT A REAL JOURNAL ARTICLE.',
            title or 'Generic synthetic test paper',
            'DOI: '+doi,
            'The research problem is how AI-generated content influences trust.',
            'The purpose of this study is to describe communication practices.',
            'The theoretical framework involves social communication theory.',
            'The research question asks how users respond to synthetic news.',
            'The study used a qualitative case study research design.',
            'Data collection used semi-structured interviews with participants.',
            'Purposive sampling recruited twenty participants for this project.',
            'The questionnaire instrument was checked before collection.',
            'Thematic analysis and coding procedure were used in this study.',
            'Results suggest variation in how participants interpret sources.',
            'Limitations include a convenience sample and limited generalizability.',
            'Future research should compare multiple national settings.'
        ]
        for i,line in enumerate(lines):p.insert_text((40,65+i*25),line,fontsize=9)
    else:
        p.draw_rect(fitz.Rect(50,70,350,250),color=(.6,.6,.6),fill=(.4,.4,.4))
    d.save(pdfs/name);d.close()

make('fulltext.pdf','10.1234/epistarium.test.full',title='Synthetic Fulltext Study')
make('wrong_identity.pdf','10.2345/epistarium.other',title='Synthetic Conflict Study')
make('scan.pdf','10.1234/epistarium.test.scan',text=False)

records=[]
for name,suffix,abstract in [
 ('Synthetic Fulltext Study','full',None),
 ('Synthetic Abstract-only Study','abstract','This is only an abstract. No methods/results may be extracted.'),
 ('Synthetic Metadata-only Study','metadata',None),
 ('Synthetic Conflict Study','conflict',None),
 ('Synthetic Missing File Study','missing',None),
 ('Synthetic Scan Study','scan',None)
]:
    records.append({'article_id':'demo-'+suffix,'doi':'10.1234/epistarium.test.'+suffix,
    'title':name,'authors':'Synthetic Author','year':2026,'article_type':'journal-article',
    'available_level':'metadata+abstract_metadata' if abstract else 'metadata','abstract':abstract,
    'source_database':'synthetic_fixture','query_url':'https://example.invalid/no-real-article'})
(root/'candidates.json').write_text(json.dumps({'records':records},indent=2),encoding='utf8')
(root/'library.json').write_text(json.dumps({
'10.1234/epistarium.test.full':{'pdf_path':str((pdfs/'fulltext.pdf').relative_to(project_root)),'version':'publishedVersion','rights_basis':'synthetic_self_created'},
'10.1234/epistarium.test.conflict':{'pdf_path':str((pdfs/'wrong_identity.pdf').relative_to(project_root)),'version':'acceptedVersion','rights_basis':'synthetic_self_created'},
'10.1234/epistarium.test.missing':{'pdf_path':str((pdfs/'not_exist.pdf').relative_to(project_root)),'version':'submittedVersion','rights_basis':'synthetic_self_created'},
'10.1234/epistarium.test.scan':{'pdf_path':str((pdfs/'scan.pdf').relative_to(project_root)),'version':'submittedVersion','rights_basis':'synthetic_self_created'}
},indent=2),encoding='utf8')
print('Wrote synthetic F2 fixture; all examples fictitious:',root)
