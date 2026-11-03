"""The regression suite is offline; live-provider validation is a separate task."""
import socket
import pytest


@pytest.fixture(autouse=True)
def prevent_external_connections(monkeypatch):
    def blocked(*args,**kwargs):
        raise AssertionError('Tes regresi tidak boleh membuka koneksi jaringan')
    monkeypatch.setattr(socket.socket,'connect',blocked)
    monkeypatch.setattr(socket.socket,'connect_ex',blocked)
