# Data dictionary

The canonical keys remain stable across languages. English display files use the labels below.

| Canonical key | English label |
|---|---|
| record_id | Record ID |
| source_id | Source ID |
| jenis_data | Data type |
| kelompok_bukti | Evidence group |
| indikator | Indicator |
| definisi_operasional | Operational definition |
| nilai | Value |
| satuan | Unit |
| pembilang | Numerator |
| penyebut | Denominator |
| organisasi_penerbit | Publisher organization |
| produsen_asli | Original producer |
| judul_sumber | Source title |
| url | URL |
| doi | DOI |
| file_sha256 | File SHA-256 |
| versi | Version |
| tanggal_peristiwa | Event date |
| tanggal_observasi | Observation date |
| periode_referensi | Reference period |
| tanggal_publikasi | Publication date |
| tanggal_pengambilan | Retrieval date |
| geografi | Geography |
| populasi | Population |
| unit_analisis | Unit of analysis |
| cakupan | Coverage |
| sampel | Sample |
| metode_sampling | Sampling method |
| metode_pengumpulan | Collection method |
| metode_perhitungan | Calculation method |
| representativitas | Representativeness |
| level_estimasi | Estimation level |
| bias | Bias |
| tipe_akses | Access type |
| lisensi | License |
| penilaian_mutu | Quality assessment |
| status_verifikasi | Evidence status |
| cuplikan | Excerpt |
| lokasi_bukti | Evidence location |
| kaitan_klaim | Relation to the claim |
| batas_generalisasi | Limits of generalization |
| asal_record | Record origin |
| synthetic | Synthetic |
| issue_codes | Issue codes |
| rights_note | Rights note |
| source_claimed_status | Status claimed by the source |
| nilai_raw | Raw value |
| nilai_parse_error | Value parsing error |

Values copied from sources keep their original language. Fixed issue codes also stay stable. Read the source record and its limits before interpretation.

## Issue codes

The codes remain stable. English reports and display files add the explanations below.

| Code | English explanation |
|---|---|
| BELUM_MEMADAI_UNTUK_RANKING | The evidence is insufficient for ranking. |
| CAKUPAN_GEOGRAFI_BERBEDA | The recorded geography differs from the target. |
| DATA_SINTETIS_BUKAN_BUKTI_EMPIRIS | Synthetic data. Do not use as empirical evidence. |
| DEFINISI_BELUM_DIKETAHUI | The operational definition is unknown. |
| GDELT_CAKUPAN_BERITA_BUKAN_JUMLAH_KEJADIAN | GDELT records news coverage, not event counts. |
| JENIS_DATA_TIDAK_STANDAR | The data type is outside the known categories. |
| KLAIM_REPRESENTATIVITAS_TIDAK_DIDUKUNG | The representativeness claim needs supporting evidence. |
| METODE_SURVEI_TIDAK_LENGKAP | Survey method details are incomplete. |
| NILAI_BUKAN_ANGKA | The value is not a valid number. |
| PENYEBUT_TIDAK_TERSEDIA | The denominator is missing. |
| POPULASI_TIDAK_SAMA | The recorded population differs from the target. |
| PROVENANCE_SUMBERRAWAN | The record lacks a URL, DOI, or file hash. |
| SATUAN_GOOGLE_TRENDS_PERLU_DIKOREKSI | The Google Trends unit needs correction. |
| SATUAN_TIDAK_ADA | The measurement unit is missing. |
| SOURCE_ID_ASAL_TIDAK_DIKENAL | The original source ID is unknown. |
| STATUS_SUMBER_BELUM_DIREVIEW | The source assessment has not received human review. |
| TANGGAL_PERISTIWA_BERBEDA_DARI_PUBLIKASI | The event date differs from the publication date. |
| TIDAK_DAPAT_DIGENERALISASI_PROBABILISTIK | The sampling does not support probability-based population estimates. |
| TIDAK_SEBANDING | The records have different comparison conditions. |
| TRENDS_INDEKS_RELATIF_BUKAN_VOLUME | Google Trends measures a relative index, not absolute volume. |
