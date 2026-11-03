"""PDFium/pypdf checks with generated synthetic PDFs and no network."""
import hashlib
from pathlib import Path

import pytest
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import reportlab
from pypdf import PdfReader, PdfWriter
from epistarium import pdf_backend, vanlan
from epistarium.retho import inspect_pdf
from epistarium.domares import _extract_pdf


def make(path, *, repeat=False, columns=False, unicode=False, rotated=False, footer=False):
    c = canvas.Canvas(str(path), pagesize=(595,842))
    c.drawString(40,715,'First line of evidence on the PDF page.')
    c.drawString(40,697,'Second line of evidence on the PDF page.')
    if repeat: c.drawString(40,670,'First line of evidence on the PDF page.')
    if columns: c.drawString(320,715,'Right column independent evidence here.')
    if unicode:
        pdfmetrics.registerFont(TTFont('Vera-v071',str(Path(reportlab.__file__).parent/'fonts/Vera.ttf')))
        c.setFont('Vera-v071',12)
        c.drawString(40,650,'Café Unicode evidence is visible here.')
    if footer: c.drawString(290,23,'7')
    c.showPage()
    if footer:
        c.drawString(290,23,'8');c.showPage()
    c.save()
    if rotated:
        r=PdfReader(str(path));w=PdfWriter();w.add_page(r.pages[0].rotate(90))
        with path.open('wb') as out:w.write(out)


def claim(anchor):
    return {'id':'K1','text':'Researcher paraphrase requiring review.', 'jenis':'parafrasa',
            'source_pdf':'source.pdf','evidence_anchor':anchor}


def test_multiline_and_two_columns_do_not_cross_or_guess(tmp_path):
    p=tmp_path/'source.pdf';make(p,columns=True)
    with pdf_backend.open(p) as doc:
        assert len(doc[0].search_for('First line of evidence on the PDF page.')) == 1
        assert not doc[0].search_for('First line of evidence on the PDF page. Right column independent')
        assert len(doc[0].search_for('First line of evidence on the PDF page. Second line of evidence on the PDF page.')) == 2
    r=vanlan.audit([claim('First line of evidence on the PDF page.')],tmp_path,tmp_path/'out')[0]
    assert r['highlight'] and len(r['evidence_locations'][0]['rects']) == 1
    assert r['status']=='belum dapat diverifikasi'
    multi=vanlan.audit([claim('First line of evidence on the PDF page.\nSecond line of evidence on the PDF page.')],tmp_path,tmp_path/'out-multi')[0]
    assert multi['highlight'] and len(multi['evidence_locations'][0]['rects']) == 2
    crossed=vanlan.audit([claim('Second line of evidence on the PDF page. Right column independent evidence here.')],tmp_path,tmp_path/'out-cross')[0]
    assert not crossed['highlight']


def test_repetition_refuses_highlight(tmp_path):
    make(tmp_path/'source.pdf',repeat=True)
    r=vanlan.audit([claim('First line of evidence on the PDF page.')],tmp_path,tmp_path/'out')[0]
    assert not r['highlight'] and not list((tmp_path/'out').glob('*annotated.pdf'))


def test_rotation_printed_page_and_original_hash(tmp_path):
    p=tmp_path/'source.pdf';make(p,rotated=True)
    before=hashlib.sha256(p.read_bytes()).hexdigest()
    r=vanlan.audit([claim('First line of evidence on the PDF page.')],tmp_path,tmp_path/'out')[0]
    assert r['pdf_page']==1 and r['printed_page'] is None
    assert r['pdf_sha256']==before and hashlib.sha256(p.read_bytes()).hexdigest()==before
    assert r['highlight']
    ann=PdfReader(str(tmp_path/'out/source_annotated.pdf')).pages[0].get('/Annots')
    assert len(ann)==1


def test_printed_page_and_scanned_pdf(tmp_path):
    p=tmp_path/'source.pdf';make(p,footer=True)
    assert _extract_pdf(p)[0]['printed_page']=='7'
    assert inspect_pdf(p)['pdf_valid']
    scan=Path(__file__).resolve().parents[1]/'examples/f2_synthetic/pdfs/scan.pdf'
    assert not inspect_pdf(scan)['machine_text_accessible']
    with pdf_backend.open(scan) as doc: assert not doc[0].search_for('No visible machine text')


def test_corrupt_pdf_is_rejected(tmp_path):
    p=tmp_path/'source.pdf';p.write_bytes(b'%PDF-1.7\nthis is corrupt')
    assert inspect_pdf(p)['pdf_valid'] is False
    r=vanlan.audit([claim('First line of evidence on the PDF page.')],tmp_path,tmp_path/'out')[0]
    assert not r['highlight'] and r['status']=='belum dapat diverifikasi'


def test_unicode_pdf_location(tmp_path):
    p=tmp_path/'source.pdf';make(p,unicode=True)
    r=vanlan.audit([claim('Café Unicode evidence is visible here.')],tmp_path,tmp_path/'out')[0]
    assert r['highlight']
