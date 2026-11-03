from datetime import date
import json
from pathlib import Path
import fitz
import pytest
from reportlab.pdfgen import canvas
from epistarium import vanlan, liora, agresa
from epistarium.common import five_years_ago


def sample_pdf(path):
    c = canvas.Canvas(str(path), pagesize=(595,842))
    c.drawString(50,700,"Dokumen uji penelitian")
    c.drawString(50,650,"Respons organisasi diumumkan pada 12 Mei 2024.")
    c.drawString(50,600,"Penelitian menggunakan wawancara terhadap 20 informan.")
    c.drawString(290,25,"7")
    c.showPage()
    c.drawString(290,25,"8")
    c.drawString(50,700,"Lampiran")
    c.drawString(50,650,"Teks ini identik dengan kutipan berulang.")
    c.drawString(50,600,"Teks ini identik dengan kutipan berulang.")
    c.showPage()
    c.save()


def make_claim(cid, text, anchor, kind="kutipan_langsung", pdf="sample.pdf"):
    return {"id":cid,"text":text,"jenis":kind,"kutipan_asli":anchor if kind=="kutipan_langsung" else "",
            "evidence_anchor":anchor if kind!="kutipan_langsung" else "","source_pdf":pdf}


def test_vanlan_exact_quote_highlight_and_printed_page(tmp_path):
    sample_pdf(tmp_path/"sample.pdf")
    sentence="Respons organisasi diumumkan pada 12 Mei 2024."
    result=vanlan.audit([make_claim("K1",f'Penulis menyebut "{sentence}"',sentence)],tmp_path,tmp_path/"out")
    assert result[0]["status"]=="belum dapat diverifikasi"
    assert result[0]["literal_match_status"]=="cocok"
    assert result[0]["semantic_support_status"]=="belum dinilai"
    assert result[0]["pdf_page"]==1 and result[0]["printed_page"]=="7"
    assert result[0]["highlight"] is True
    doc=fitz.open(tmp_path/"out"/"sample_annotated.pdf")
    assert len(list(doc[0].annots()))==1
    doc.close()


def test_vanlan_wrong_quote(tmp_path):
    sample_pdf(tmp_path/"sample.pdf")
    s="Respons organisasi diumumkan pada 15 Mei 2024."
    r=vanlan.audit([make_claim("K2",s,s)],tmp_path,tmp_path/"out")
    assert r[0]["status"]=="tidak ditemukan" and not r[0]["highlight"]


def test_vanlan_distorted_paraphrase_not_automatically_confirmed(tmp_path):
    sample_pdf(tmp_path/"sample.pdf")
    r=vanlan.audit([make_claim("K3","Penelitian menanyai dua ribu informan.",
                "Penelitian menggunakan wawancara terhadap 20 informan.","parafrasa")],tmp_path,tmp_path/"out")
    assert r[0]["status"]=="belum dapat diverifikasi"
    assert r[0]["highlight"] is True


def test_vanlan_missing_source(tmp_path):
    r=vanlan.audit([make_claim("K4","contoh", "sumber apapun",pdf="hilang.pdf")],tmp_path,tmp_path/"out")
    assert r[0]["status"]=="belum dapat diverifikasi"
    assert not r[0]["highlight"]


def test_vanlan_image_only_pdf(tmp_path):
    pdf=fitz.open()
    p=pdf.new_page()
    pix=fitz.Pixmap(fitz.csRGB,fitz.IRect(0,0,200,100),0)
    pix.clear_with(255)
    p.insert_image(fitz.Rect(50,50,250,150),pixmap=pix)
    pdf.save(tmp_path/"scan.pdf")
    pdf.close()
    r=vanlan.audit([make_claim("K5","Teks hasil scan","Teks hasil scan",pdf="scan.pdf")],tmp_path,tmp_path/"out")
    assert r[0]["status"]=="belum dapat diverifikasi"
    assert "OCR" in r[0]["note"]


def test_vanlan_ambiguous_repeated_text(tmp_path):
    sample_pdf(tmp_path/"sample.pdf")
    s="Teks ini identik dengan kutipan berulang."
    r=vanlan.audit([make_claim("K6",s,s)],tmp_path,tmp_path/"out")
    assert r[0]["highlight"] is False
    assert r[0]["status"] in ("belum dapat diverifikasi", "tidak ditemukan")


def test_vanlan_unmapped_claim_and_path_traversal(tmp_path):
    r=vanlan.audit([{"id":"K7","text":"Sebuah klaim","jenis":"parafrasa"},
                    make_claim("K8","contoh", "Sumber di luar direktori",pdf="../private.pdf")],tmp_path,tmp_path/"out")
    assert all(x["status"]=="belum dapat diverifikasi" for x in r)


def test_vanlan_human_review_requires_identity_and_reason(tmp_path):
    sample_pdf(tmp_path/"sample.pdf")
    c=make_claim("K9","Bukti bertentangan", "Penelitian menggunakan wawancara terhadap 20 informan.","parafrasa")
    r=vanlan.audit([c],tmp_path,tmp_path/"out1",reviews={"K9":{"status":"bertentangan"}})
    assert r[0]["status"] == "belum dapat diverifikasi"
    r=vanlan.audit([c],tmp_path,tmp_path/"out2",reviews={"K9":{"status":"bertentangan", "reviewer":"Pemeriksa 1","reason":"Angka pada PDF berbeda dari klaim."}})
    assert r[0]["status"] == "bertentangan"
    assert r[0]["cakupan_keputusan"].startswith("penilaian manusia")


def test_liora_date_scope_and_query():
    assert five_years_ago(date(2026,11,3)) == date(2021,11,3)
    assert five_years_ago(date(2028,2,29)) == date(2023,2,28)
    p=liora.query_plan("komunikasi krisis", "fenomena", as_of=date(2026,11,3))
    assert p["default_cutoff"]=="2021-11-03"
    assert liora.query_plan("Weick", "teori", as_of=date(2026,11,3))["default_cutoff"] is None
    assert "from-pub-date%3A2021-11-03" in liora.crossref_url("komunikasi krisis",p["default_cutoff"])


def test_liora_dedup_and_exports(tmp_path):
    a={"DOI":"10.5555/ABC","title":["Digital Crisis Communication"],"author":[{"given":"A","family":"B"}],"published":{"date-parts":[[2024,5,3]]},"container-title":["Test Journal"],"type":"journal-article"}
    b=dict(a)
    b["DOI"]="10.5555/abc"
    c=dict(a)
    c["DOI"]="10.5555/old"
    c["published"]={"date-parts":[[2011,1,1]]}
    fixture=tmp_path/"crossref.json"
    fixture.write_text(json.dumps({"message":{"items":[a,b,c]}}),encoding="utf-8")
    out=liora.search("digital crisis",tmp_path/"out",fixture=fixture,as_of=date(2026,11,3))
    assert len(out)==2
    assert out[0]["available_level"]=="metadata" and not out[0]["fulltext_read"]
    assert out[1]["excluded"] is True
    assert (tmp_path/"out"/"candidates.ris").exists()
    assert "10.5555/ABC" not in (tmp_path/"out"/"candidates.ris").read_text()


def test_agresa_official_domain_and_period_and_article_boundary(tmp_path):
    e=[{"database":"scopus","title":"Jurnal Uji","issn":"1234-5678","official_url":"https://www.scopus.com/sources","coverage_start":2022,"coverage_end":2024,"checked_at":"2026-11-03","reviewed_by":"Pemeriksa X","evidence_note":"Simulasi entri dari daftar resmi"}]
    r=agresa.audit([{"title":"Jurnal Uji","issn":"1234-5678","year":2023,"article_doi":"10.1234/x"},
                   {"title":"Jurnal Uji","issn":"1234-5678","year":2025,"article_doi":"10.1234/y"}],e,tmp_path/"out")
    assert r[0]["status_jurnal"]=="cocok dengan catatan indeks yang diinput"
    assert r[0]["status_artikel"]=="belum dapat diverifikasi"
    assert r[3]["status_jurnal"]=="di luar periode yang tercatat"
    assert all(x["database"]!="wos" or x["status_jurnal"]=="belum dapat diverifikasi" for x in r)
    assert not agresa.official_url("scopus","https://scopus.com.attacker.example/a")


def test_agresa_conflicting_sources_do_not_auto_assert():
    e={"database":"sinta","title":"Jurnal Uji","official_url":"https://sinta.kemdiktisaintek.go.id/journals/detail/123","issn":"1111-2222","rank":"S2","coverage_start":2020,"coverage_end":2026,"checked_at":"2026-11-03","reviewed_by":"X","evidence_note":"simulasi"}
    r=agresa.verify_journal({"title":"Jurnal Uji","issn":"1111-2222","year":2025},[e,e])
    assert r[-1]["status_jurnal"]=="belum dapat diverifikasi" and "Lebih dari satu" in r[-1]["note"]


def test_liora_exact_date_cutoff_and_uncertain_boundary(tmp_path):
    base={"title":["Title"],"container-title":["Journal"],"type":"journal-article"}
    data=[dict(base,DOI="10.5555/old", published={"date-parts":[[2021,6,1]]}),
          dict(base,DOI="10.5555/new",published={"date-parts":[[2021,12,1]]}),
          dict(base,DOI="10.5555/unknown",published={"date-parts":[[2021]]})]
    f=tmp_path/"crossref.json"
    f.write_text(json.dumps(data),encoding="utf-8")
    results=liora.search("a test",tmp_path/"out",scope="fenomena",fixture=f,as_of=date(2026,11,3))
    bydoi={r["doi"]:r for r in results}
    assert bydoi["10.5555/old"]["excluded"]
    assert not bydoi["10.5555/new"]["excluded"]
    assert not bydoi["10.5555/unknown"]["excluded"]
    assert bydoi["10.5555/unknown"]["needs_manual_date_check"]


def test_csv_formula_safe(tmp_path):
    from epistarium.common import save_csv
    csv_file=tmp_path/"safe.csv"
    save_csv(csv_file,[{"name":"=IMPORTXML(\"evil\",\"//a\")", "year":2024}],["name","year"])
    assert "'=IMPORTXML" in csv_file.read_text(encoding="utf-8-sig")
