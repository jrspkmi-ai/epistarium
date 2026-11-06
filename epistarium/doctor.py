"""Offline environment diagnostics, usable before optional modules import."""
from .i18n import tr, display_status, localized, get_language
from importlib import import_module, metadata
from pathlib import Path
import platform
import sys
import tempfile
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name
import tomllib
from . import __version__

DEPENDENCIES = {"pypdfium2": "pypdfium2", "pypdf": "pypdf", "requests": "requests", "python-docx": "docx", "openpyxl": "openpyxl", "jsonschema": "jsonschema", "defusedxml": "defusedxml"}


@localized
def diagnose(project_root=None):
    root = Path(project_root or Path.cwd())
    checks = {"python": {"ok": sys.version_info >= (3, 11), "version": platform.python_version()}}
    project = root / "pyproject.toml"
    if project.is_file():
        with project.open("rb") as stream:
            requirements = tomllib.load(stream)["project"]["dependencies"]
    else:
        requirements = metadata.requires("epistarium") or []
    specs = {canonicalize_name(r.name): r for r in map(Requirement, requirements) if not r.marker or r.marker.evaluate()}
    for distribution, module in DEPENDENCIES.items():
        try:
            import_module(module)
            version = metadata.version(distribution)
            requirement = specs.get(canonicalize_name(distribution))
            checks[distribution] = {"ok": bool(requirement and version in requirement.specifier), "version": version, "required": str(requirement.specifier) if requirement else "UNDECLARED"}
        except (ImportError, metadata.PackageNotFoundError, OSError) as exc:
            checks[distribution] = {"ok": False, "error": type(exc).__name__}
    try:
        from zoneinfo import ZoneInfo
        ZoneInfo("Asia/Jakarta")
        checks["timezone"] = {"ok": True}
    except Exception as exc:
        checks["timezone"] = {"ok": False, "error": type(exc).__name__}
    try:
        private = root / "private"
        private.mkdir(exist_ok=True)
        with tempfile.TemporaryFile(dir=private) as stream:
            stream.write(b"environment check")
        checks["private_writable"] = {"ok": True}
    except OSError as exc:
        checks["private_writable"] = {"ok": False, "error": type(exc).__name__}
    skills = root / ".agents" / "skills"
    count = len(list(skills.glob("*/SKILL.md")))
    return {"language":get_language(),"version": __version__, "execution_status": "SUCCESS" if all(c["ok"] for c in checks.values()) else "BLOCKED",
            "checks": checks, "skill_count_at_project_root": count,
            "discovery_note": tr('Buka folder dengan pyproject.toml, AGENTS.md dan .agents; aktivasi native setiap host perlu diuji tersendiri.'),
            "network": "NOT_RUN", "semantic_validation": "NOT_ASSESSED"}
