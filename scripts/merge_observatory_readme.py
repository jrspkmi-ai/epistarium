"""Safely insert Observatory quick starts into current GitHub READMEs without replacing brand artwork."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SNIPPETS={
'README.md':'''## Live Research Observatory (v0.8.0)

Monitor real Jorhas Python steps, ten persona statuses, evidence record counts, artifacts and approval gates locally, using a compact bilingual interface (EN default, ID available) with dark and light modes. A completed execution is **not** semantic verification.

```bash
python -m epistarium observatory --open
```

For a real local Path Finding run, add `--idea "Your research topic" --mode pathfind`. An automatically opened browser requires a desktop environment and browser-launch permission. See [Observatory documentation](docs/en/observatory/README.md) and [panduan Indonesia](docs/id/observatory/README.md). The dashboard is not a ChatGPT web plugin.

''',
'README.id.md':'''## Research Observatory langsung (v0.8.0)

Pantau langkah Python Jorhas yang benar-benar berjalan, status sepuluh persona, jumlah rekaman bukti, artefak, dan gerbang persetujuan melalui antarmuka lokal dwi-bahasa (bawaan EN, dapat memilih ID) dengan mode gelap dan terang. Eksekusi selesai **tidak berarti** pembuktian semantik selesai.

```bash
python -m epistarium observatory --open
```

Untuk menjalankan Path Finding lokal, tambahkan `--idea "Topik penelitian" --mode pathfind`. Pembukaan browser otomatis memerlukan lingkungan desktop dan izin sistem. Lihat [panduan Observatory Bahasa Indonesia](docs/id/observatory/README.md) atau [English guide](docs/en/observatory/README.md). Dashboard ini bukan plugin ChatGPT web.

'''
}
for name,snippet in SNIPPETS.items():
    path=ROOT/name;text=path.read_text(encoding='utf-8')
    if '## Live Research Observatory (v0.8.0)' in text or '## Research Observatory langsung (v0.8.0)' in text:
        print(name+': already merged');continue
    anchor='<!-- section: installation -->'
    if anchor not in text:raise RuntimeError(name+': compatible README anchor not found; no file modified')
    text=text.replace(anchor,snippet+anchor,1)
    text=text.replace('v0.7.1 RELEASE_CANDIDATE','v0.8.0 RELEASE_CANDIDATE',1)
    text=text.replace('version 0.7.1 release ZIP asset','version 0.8.0 release ZIP asset',1)
    text=text.replace('ZIP rilis versi 0.7.1','ZIP rilis versi 0.8.0',1)
    text=text.replace('Release gate: GO_BERSYARAT.', 'Release gate: PENDING_CROSS_OS_CI.', 1)
    text=text.replace('Gerbang rilis: GO_BERSYARAT.', 'Gerbang rilis: PENDING_CROSS_OS_CI.', 1)
    path.write_text(text,encoding='utf-8');print(name+': merged')
