"""Generate entirely synthetic, redistributable F1 testing fixtures."""
import json
from pathlib import Path
from reportlab.pdfgen import canvas

root = Path(__file__).resolve().parent
(root / "pdfs").mkdir(parents=True, exist_ok=True)
pdf=root/"pdfs"/"contoh_sintetis.pdf"
c=canvas.Canvas(str(pdf),pagesize=(595,842))
c.setFont("Helvetica-Bold",13)
c.drawString(50,760,"Contoh PDF untuk pengujian Vanlan")
c.setFont("Helvetica",11)
c.drawString(50,712,"Ini dokumen sintetis. Bukan artikel jurnal atau hasil penelitian nyata.")
c.drawString(50,672,"Tim riset melakukan wawancara terhadap 20 informan.")
c.drawString(50,635,"Tanggal publikasi laporan internal adalah 12 Mei 2024.")
c.drawString(285,35,"7")
c.showPage()
c.setFont("Helvetica",11)
c.drawString(50,700,"Lampiran yang tidak berhubungan dengan bukti utama.")
c.showPage()
c.save()
claims=[
    {"id":"K001","text":"Peneliti menulis: \"Tim riset melakukan wawancara terhadap 20 informan.\"", "jenis":"kutipan_langsung", "source_pdf":pdf.name,"kutipan_asli":"Tim riset melakukan wawancara terhadap 20 informan."},
    {"id":"K002","text":"Tim riset mewawancarai 200 orang.","jenis":"parafrasa","source_pdf":pdf.name,"evidence_anchor":"Tim riset melakukan wawancara terhadap 20 informan."},
    {"id":"K003","text":"Peneliti menulis \"Laporan diterbitkan pada 20 Mei 2024.\"","jenis":"kutipan_langsung","source_pdf":pdf.name,"kutipan_asli":"Laporan diterbitkan pada 20 Mei 2024."},
    {"id":"K004","text":"Sumber lainnya tidak tersedia.","jenis":"parafrasa","source_pdf":"hilang.pdf"}
]
(root/"claims.json").write_text(json.dumps(claims,ensure_ascii=False,indent=2),encoding="utf-8")
raw={"message":{"items":[
  {"DOI":"10.5555/epistarium-demo-01","title":["Digital Crisis Communication: Synthetic Example"],"author":[{"given":"Demo","family":"Researcher"}],"published":{"date-parts":[[2024,7,1]]},"container-title":["Synthetic Journal"],"type":"journal-article","URL":"https://doi.org/10.5555/epistarium-demo-01"},
  {"DOI":"10.5555/EPISTARIUM-DEMO-01","title":["Digital Crisis Communication: Synthetic Example"],"published":{"date-parts":[[2024,7,1]]},"container-title":["Synthetic Journal"],"type":"journal-article"},
  {"DOI":"10.5555/epistarium-demo-02","title":["Historical work in digital crisis communication"],"published":{"date-parts":[[2011,7,1]]},"container-title":["Synthetic Journal"],"type":"journal-article"}
]}}
(root/"crossref_fixture.json").write_text(json.dumps(raw,ensure_ascii=False,indent=2),encoding="utf-8")
(root/"journals.json").write_text(json.dumps([
 {"title":"Jurnal Simulasi A", "issn":"1234-5678", "year":2023, "article_doi":"10.5555/example"}
],ensure_ascii=False,indent=2),encoding="utf-8")
(root/"index_evidence.json").write_text(json.dumps([
 {"database":"sinta", "title":"Jurnal Simulasi A", "issn":"1234-5678", "rank":"S2", "coverage_start":2021, "coverage_end":2025, "official_url":"https://sinta.kemdiktisaintek.go.id/journals", "checked_at":"2026-11-03","reviewed_by":"Pemeriksa Contoh", "evidence_note":"SIMULASI SAJA, bukan jurnal atau status riil"}
],ensure_ascii=False,indent=2),encoding="utf-8")
print("Contoh sintetis dibuat:", pdf)
