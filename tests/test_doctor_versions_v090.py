from epistarium import doctor

def test_installed_but_outdated_dependency_is_blocked(monkeypatch, tmp_path):
    original = doctor.metadata.version
    monkeypatch.setattr(doctor.metadata, 'version', lambda name: '1.0' if name == 'pypdf' else original(name))
    result = doctor.diagnose()
    assert result['checks']['pypdf']['ok'] is False
    assert result['execution_status'] == 'BLOCKED'
