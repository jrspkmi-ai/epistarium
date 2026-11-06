"""Synthetic regression cases. They are not research evidence."""
import hashlib
import json
import pytest
from openpyxl import load_workbook
from epistarium import huxley, synthia

@pytest.mark.parametrize('name', ['Martinčević', 'Šimić', 'Łukasz'])
def test_author_unicode(name):
    reference = huxley.parse_reference(f'{name}, A. (2023). Example.', 'ref')
    citation = huxley.detect_citations(f'{name} (2023)', 'p')[0]
    assert huxley._score(citation, reference)

@pytest.mark.parametrize('text', ['(survei Juli 2023)', '(periode 2021-2024)'])
def test_date_phrases_are_not_citations(text):
    assert not huxley.detect_citations(text, 'p')

def test_organization_not_excluded():
    assert huxley.detect_citations('Data (2023)', 'p')

def test_export_copy_sanitized_and_original_unchanged(tmp_path):
    raw = '=text\x00\x0b\x1f Šimić 日本語'
    source_hash = hashlib.sha256(raw.encode()).hexdigest()
    row = {'Judul':raw, 'Tahun':'2023'}
    out = tmp_path / 'output.xlsx'
    synthia._export_xlsx([row], [], out)
    wb = load_workbook(out, data_only=False)
    sheet = synthia.literature_sheet(wb)
    values = [cell for cells in sheet.iter_rows() for cell in cells if isinstance(cell.value,str) and 'Šimić' in cell.value]
    assert values and values[0].data_type == 's'
    assert values[0].value == '=text��� Šimić 日本語'
    assert hashlib.sha256(row['Judul'].encode()).hexdigest() == source_hash
    assert json.loads((tmp_path / 'sanitization_audit.json').read_text())['total_replacements'] == 3
    wb.close()

@pytest.mark.parametrize('status,flag,expected', [('PARTIAL',False,3),('PARTIAL',True,0),('BLOCKED',True,4),('SUCCESS',True,0)])
def test_pathfind_partial_exit_preserves_status(monkeypatch, tmp_path, status, flag, expected):
    from epistarium import cli, jorhas
    result = {'manifest':{'status':status}, 'records':[], 'opportunities':[]}
    monkeypatch.setattr(jorhas, 'pathfind', lambda *a, **kw: result)
    argv = ['jorhas-pathfind','--idea','synthetic idea','--out',str(tmp_path / 'run')]
    if flag: argv += ['--allow-partial']
    assert cli.main(argv) == expected
    assert result['manifest']['status'] == status
