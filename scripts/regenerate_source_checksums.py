"""Refresh CHECKSUMS_SHA256.txt for the actual checkout after applying an overlay."""
from pathlib import Path
import hashlib
ROOT=Path(__file__).resolve().parents[1]
from package_release import selected_files
rows=[hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(ROOT).as_posix()
      for p in selected_files(ROOT)]
(ROOT/'CHECKSUMS_SHA256.txt').write_text('\n'.join(rows)+'\n',encoding='utf-8')
print(f'Regenerated {len(rows)} SHA256 rows from this checkout.')
