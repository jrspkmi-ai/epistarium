"""Negative and boundary tests for Liora/Agresa 0.1.2; all synthetic data."""
from datetime import date
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import json
import pytest
import requests
from epistarium import liora, agresa

DATE=date(2026,11,3)


def cr_item(doi,year=2023,title="Digital crisis communication",precision="day",abstract=False):
    parts=[[year,5,6]] if precision=="day" else [[year]]
    r={"DOI":doi,"title":[title],"author":[{"given":"Budi","family":"Santoso"}],
       "published":{"date-parts":parts},"container-title":["Journal Demo"],"type":"journal-article"}
    if abstract:
        r["abstract"]="<jats:p>Abstract in Crossref metadata, not full text.</jats:p>"
    return r


def evidence(db="scopus",**overrides):
    base={"database":db,"title":"Jurnal Eksperimen","issn":"1111-2222",
          "official_url":{"scopus":"https://www.scopus.com/sources","wos":"https://mjl.clarivate.com/",
                          "sinta":"https://sinta.kemdiktisaintek.go.id/journals"}[db],
          "coverage_start":2022,"coverage_end":2025,"checked_at":"2026-11-03",
          "reviewed_by":"Pemeriksa Sintetis","evidence_note":"Sumber ini simulasi, bukan data nyata"}
    base.update(overrides)
    return base


def journal(**kw):
    r={"title":"Jurnal Eksperimen","issn":"1111-2222","year":2024,"article_doi":"10.5555/mock"}
    r.update(kw)
    return r


def test_liora_empirical_classics_retained_and_ris(tmp_path):
    fixture=tmp_path/"fixture.json"
    fixture.write_text(json.dumps([cr_item("10.5555/old",2012),cr_item("10.5555/new",2025)]))
    rows=liora.search("crisis",tmp_path/"result",scope="empiris",fixture=fixture,as_of=DATE)
    assert all(not r["excluded"] for r in rows)
    assert rows[0]["recency_tag"] == "lebih lama dari lima tahun"
    assert "10.5555/old" in (tmp_path/"result"/"candidates.ris").read_text()
    url=json.loads((tmp_path/"result"/"search_plan.json").read_text())["request_url"]
    assert "filter" not in parse_qs(urlparse(url).query)


def test_liora_phenomenon_default_filters_publication_not_event_date(tmp_path):
    f=tmp_path/"fixture.json"
    f.write_text(json.dumps([cr_item("10.5555/old",2015),cr_item("10.5555/new",2024)]))
    rows=liora.search("crisis",tmp_path/"result",scope="fenomena",fixture=f,as_of=DATE)
    assert rows[0]["excluded"] and not rows[1]["excluded"]
    assert "10.5555/old" not in (tmp_path/"result"/"candidates.ris").read_text()
    p=json.loads((tmp_path/"result"/"search_plan.json").read_text())
    assert p["default_cutoff"] == "2021-11-03"
    assert "tidak membuktikan tanggal FENOMENA" in p["date_basis_warning"]


def test_liora_2021_month_only_uncertain_not_excluded(tmp_path):
    f=tmp_path/"fixture.json"
    x=cr_item("10.5555/part",2021,precision="year")
    f.write_text(json.dumps([x]))
    r=liora.search("crisis",tmp_path/"out",scope="fenomena",fixture=f,as_of=DATE)[0]
    assert r["needs_manual_date_check"] and not r["excluded"]


def test_liora_theory_no_default_date_filter():
    plan=liora.query_plan("Weick sensemaking","teori",as_of=DATE)
    assert plan["default_cutoff"] is None and plan["priority_cutoff"] is None


def test_liora_levels_and_ris_authors(tmp_path):
    f=tmp_path/"fixture.json"
    f.write_text(json.dumps([cr_item("10.5555/example",2025,abstract=True)]))
    r=liora.search("digital",tmp_path/"out",scope="empiris",fixture=f,as_of=DATE)[0]
    assert r["available_level"] == "metadata+abstract_metadata"
    assert r["abstract_available"] and not r["fulltext_read"]
    ris=(tmp_path/"out"/"candidates.ris").read_text()
    assert "AU  - Budi Santoso" in ris and "DO  - 10.5555/example" in ris


def test_liora_mocked_live_api_provenance(tmp_path,monkeypatch):
    from epistarium.pathfinder_harvest import LimitedClient
    called=[]
    def mocked(self,url,**kwargs):
        called.append((url,kwargs))
        return json.dumps({"message":{"items":[cr_item("10.5555/mock",2024)]}}).encode(),{'status_code':200}
    monkeypatch.setattr(LimitedClient,'get',mocked)
    r=liora.search("crisis",tmp_path/"out",scope="empiris",as_of=DATE)
    assert r[0]["source_database"] == "Crossref"
    assert len(called)==1 and called[0][1]['provider']=='crossref'
    p=json.loads((tmp_path/"out"/"search_plan.json").read_text())
    assert p["execution"] == "live_crossref"
    # Mocked internet response; not proof of live external access.


def test_liora_request_failure_reports_blocked(tmp_path,monkeypatch):
    def fail(*a,**kw): raise requests.Timeout("simulasi koneksi terputus")
    from epistarium.pathfinder_harvest import LimitedClient
    monkeypatch.setattr(LimitedClient,'get',fail)
    with pytest.raises(RuntimeError,match="tidak berhasil"):
        liora.search("crisis",tmp_path/"out",as_of=DATE)
    x=json.loads((tmp_path/"out"/"search_error.json").read_text())
    assert x["status"] == "BLOCKED" and not (tmp_path/"out"/"candidates.json").exists()


def test_liora_invalid_json_response_blocked(tmp_path,monkeypatch):
    class Reply:
        def raise_for_status(self): pass
        def json(self): return {"message":{"items":"not-list"}}
    from epistarium.pathfinder_harvest import LimitedClient
    monkeypatch.setattr(LimitedClient,'get',lambda *a,**kw:(json.dumps(Reply().json()).encode(),{}))
    with pytest.raises(RuntimeError):
        liora.search("crisis",tmp_path/"out",as_of=DATE)
    assert json.loads((tmp_path/"out"/"search_plan.json").read_text())["execution"] == "blocked"


def test_liora_doi_normalization_and_duplicate(tmp_path):
    f=tmp_path/"fixture.json"
    f.write_text(json.dumps([cr_item("HTTPS://DOI.ORG/10.5555/ABC",2024),cr_item("10.5555/abc",2024)]))
    result=liora.search("digital",tmp_path/"out",scope="empiris",fixture=f,as_of=DATE)
    assert len(result)==1 and result[0]["doi"]=="10.5555/abc"
    removed=json.loads((tmp_path/"out"/"candidates.json").read_text())["deduplicated"]
    assert len(removed)==1


def test_liora_missing_doi_does_not_invent_one(tmp_path):
    f=tmp_path/"fixture.json"
    f.write_text(json.dumps([cr_item("",2024)]))
    r=liora.search("digital",tmp_path/"out",scope="teori",fixture=f,as_of=DATE)[0]
    assert r["doi"]=="" and r["doi_format_status"]=="missing_or_invalid"
    assert "DO  - " not in (tmp_path/"out"/"candidates.ris").read_text()


def test_agresa_conflicting_issn_never_positive():
    rr=agresa.verify_journal(journal(),[evidence(issn="9999-0000")])
    assert rr[0]["status_jurnal"] == "belum dapat diverifikasi"
    assert rr[0]["identity_match"]=="konflik ISSN/judul"
    assert rr[0]["status_artikel"]=="belum dapat diverifikasi"


def test_agresa_conflict_overrides_correct_candidate():
    rr=agresa.verify_journal(journal(),[evidence(),evidence(issn="9999-0000")])
    assert rr[0]["status_jurnal"]=="belum dapat diverifikasi"


def test_agresa_eissn_legitimate_alias_match():
    rr=agresa.verify_journal(journal(issn="1111-2222",eissn="9999-8888"),[evidence(issn="9999-8888",eissn="1111-2222")])
    assert rr[0]["identity_match"]=="issn_match"
    assert rr[0]["status_jurnal"]=="cocok dengan catatan indeks yang diinput"


def test_agresa_title_only_is_inconclusive():
    rr=agresa.verify_journal(journal(issn=""),[evidence(issn="")])
    assert rr[0]["status_jurnal"]=="belum dapat diverifikasi"
    assert rr[0]["identity_match"]=="title_only_missing_issn"


def test_agresa_same_issn_different_title_is_inconclusive():
    rr=agresa.verify_journal(journal(title="Renamed Journal"),[evidence(title="Former Journal")])
    assert rr[0]["status_jurnal"]=="belum dapat diverifikasi"
    assert rr[0]["identity_match"]=="issn_match_title_conflict"


def test_agresa_wos_collection_and_article_status():
    no_col=agresa.verify_journal(journal(),[evidence("wos")])[1]
    assert no_col["status_jurnal"]=="belum dapat diverifikasi"
    yes_col=agresa.verify_journal(journal(),[evidence("wos",wos_collection="SSCI")])[1]
    assert yes_col["status_jurnal"]=="cocok dengan catatan indeks yang diinput"
    assert yes_col["status_artikel"]=="belum dapat diverifikasi"
    assert yes_col["wos_collection"]=="SSCI"


def test_agresa_sinta_rank_period_required():
    not_proven=agresa.verify_journal(journal(),[evidence("sinta",rank="S2")])[2]
    assert not_proven["status_jurnal"]=="belum dapat diverifikasi"
    rr=agresa.verify_journal(journal(),[evidence("sinta",rank="S2",period_type="accreditation")])[2]
    assert rr["status_jurnal"]=="cocok dengan catatan indeks yang diinput"
    assert rr["status_artikel"]=="belum dapat diverifikasi"
    no_rank=agresa.verify_journal(journal(),[evidence("sinta",period_type="accreditation")])[2]
    assert no_rank["status_jurnal"]=="belum dapat diverifikasi"


def test_agresa_sinta_rank_history_selects_year_and_conflict():
    r=agresa.verify_journal(journal(year=2025),[evidence("sinta",period_type="accreditation",rank_periods=[
      {"rank":"S2","coverage_start":2021,"coverage_end":2024},
      {"rank":"S3","coverage_start":2025,"coverage_end":2026}])])[2]
    assert r["status_jurnal"]=="cocok dengan catatan indeks yang diinput"
    assert r["rank"]=="S3" and r["coverage_start"]==2025
    overlap=agresa.verify_journal(journal(year=2024),[evidence("sinta",period_type="accreditation",rank_periods=[
      {"rank":"S2","coverage_start":2021,"coverage_end":2025},
      {"rank":"S3","coverage_start":2024,"coverage_end":2026}])])[2]
    assert overlap["status_jurnal"]=="belum dapat diverifikasi"
    assert "tumpang tindih" in overlap["note"]


def test_agresa_period_and_bad_timestamp():
    a=agresa.verify_journal(journal(year=2021),[evidence()])[0]
    assert a["status_jurnal"]=="di luar periode yang tercatat"
    b=agresa.verify_journal(journal(),[evidence(coverage_start=2025,coverage_end=2020)])[0]
    assert b["status_jurnal"]=="belum dapat diverifikasi"
    c=agresa.verify_journal(journal(),[evidence(checked_at="invalid-date")])[0]
    assert c["status_jurnal"]=="belum dapat diverifikasi"


def test_agresa_article_record_still_only_user_supplied():
    rec={"doi":"10.5555/mock","official_url":"https://www.scopus.com/record/abc","reviewed_by":"Demo",
         "checked_at":"2026-11-03","evidence_note":"Simulasi, bukan indeks nyata"}
    r=agresa.verify_journal(journal(),[evidence(article_record=rec)])[0]
    assert r["status_jurnal"]=="cocok dengan catatan indeks yang diinput"
    assert "belum diverifikasi independen" in r["status_artikel"]
    r2=agresa.verify_journal(journal(),[evidence(article_record={**rec,"doi":"10.5555/wrong"})])[0]
    assert r2["status_artikel"]=="belum dapat diverifikasi"


def test_agresa_url_disguises_rejected():
    assert not agresa.official_url("scopus","https://scopus.com.evil.net/source")
    assert not agresa.official_url("scopus","https://user:pw@scopus.com/source")
    assert not agresa.official_url("scopus","http://scopus.com/source")
    assert not agresa.official_url("scopus","https://scopus.com:9876/source")


def test_crossskill_metadata_does_not_become_index_verification(tmp_path):
    f=tmp_path/"fixture.json"
    f.write_text(json.dumps([cr_item("10.5555/abc",2024)]))
    r=liora.search("crisis",tmp_path/"liora",scope="empiris",fixture=f,as_of=DATE)[0]
    x=agresa.verify_journal(journal(title=r["journal"],issn="",year=r["year"],article_doi=r["doi"]),[])
    assert all(v["status_jurnal"]=="belum dapat diverifikasi" for v in x)
