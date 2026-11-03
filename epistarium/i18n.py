"""Language for program-owned text. Source text and stable data codes stay intact."""
from contextlib import contextmanager
from contextvars import ContextVar
from functools import lru_cache, wraps
from importlib.resources import files
import json
import locale
import os

_language = ContextVar('epistarium_language', default=None)
SUPPORTED = ('id', 'en')


def resolve_language(value=None, *, environment=True):
    if value is None and environment:
        value = os.environ.get('EPISTARIUM_LANG') or 'auto'
    value = str(value or 'id').lower().replace('_', '-')
    if value == 'auto':
        try:
            name = locale.getlocale()[0]
        except (locale.Error,ValueError):
            name = None
        name = name or os.environ.get('LC_ALL') or os.environ.get('LANG') or 'en'
        return 'id' if name.lower().startswith('id') else 'en'
    value = value.split('-')[0]
    if value not in SUPPORTED:
        raise ValueError('Language must be id, en, or auto. Bahasa harus id, en, atau auto.')
    return value


def get_language():
    return _language.get() or 'id'


@contextmanager
def language_context(language):
    token = _language.set(resolve_language(language))
    try:
        yield get_language()
    finally:
        _language.reset(token)


def localized(function):
    """Add lang= to public APIs and restore the caller's language after a call."""
    @wraps(function)
    def call(*args, lang=None, **kwargs):
        selected = lang
        if selected is None and _language.get() is None:
            spec = kwargs.get('config')
            if spec is None and args and isinstance(args[0], dict):
                spec = args[0]
            if isinstance(spec, dict):
                selected = spec.get('language')
        if selected is None:
            return function(*args, **kwargs)
        with language_context(selected):
            return function(*args, **kwargs)
    return call


@lru_cache(maxsize=1)
def english_catalog():
    return json.loads(files('epistarium').joinpath('data', 'messages.en.json').read_text(encoding='utf8'))


def tr(message, **values):
    """Translate a static template before inserting untouched source values."""
    template = english_catalog().get(message, message) if get_language() == 'en' else message
    return template.format(**values) if values else template


STATUS_LABELS = {
    'statistik resmi':'official statistics',
    'survei':'survey','dataset':'dataset','proksi digital':'digital proxy',
    'dokumentasi kasus':'case documentation','literatur':'literature',
    'statistik resmi atau survei probabilitas':'official statistics or a probability survey',
    'penilaian manusia; bukan hasil mesin pencocokan teks':'imported human assessment, not a text-matching decision',
    'cocok dengan catatan indeks yang diinput':'matches the supplied index record',
    'di luar periode yang tercatat':'outside the recorded period',
    'konflik ISSN/judul':'ISSN or title conflict','ambigu beberapa catatan':'ambiguous records',
    'terverifikasi': 'verified',
    'didukung sebagian': 'partly supported',
    'bertentangan': 'contradicted',
    'tidak ditemukan': 'not found',
    'belum dapat diverifikasi': 'not yet verifiable',
    'inferensi peneliti/AI': 'researcher/AI inference',
    'hipotesis atau rekomendasi': 'hypothesis or recommendation',
    'belum dinilai': 'not assessed',
    'belum diperiksa': 'not checked',
    'belum dipetakan': 'not mapped',
    'belum dapat ditentukan': 'not determined',
    'belum ditentukan': 'not specified',
    'tidak tersedia': 'unavailable',
    'tersedia': 'available',
    'terbatas': 'restricted',
    'belum diverifikasi': 'not verified',
    'cocok': 'matched',
    'sebagian anchor cocok': 'some anchors matched',
    'ambigu atau koordinat tidak valid': 'ambiguous or invalid coordinates',
}


def display_status(value):
    if get_language() != 'en' or not isinstance(value, str):
        return value
    return STATUS_LABELS.get(value, value)


@lru_cache(maxsize=1)
def column_labels():
    return json.loads(files('epistarium').joinpath('data', 'columns.en.json').read_text(encoding='utf8'))


def display_field_value(field, value):
    if get_language() != 'en':
        return value
    if field=='issue_codes' and isinstance(value,list):
        return display_issue_codes(value)
    if field in ('status','status_verifikasi','source_claimed_status','semantic_support_status',
                 'literal_match_status','cakupan_keputusan','jenis_data','kelompok_bukti'):
        return display_status(value)
    return value


@lru_cache(maxsize=1)
def issue_labels():
    return json.loads(files('epistarium').joinpath('data', 'issues.en.json').read_text(encoding='utf8'))


def display_issue_codes(codes):
    if get_language()!='en':
        return ', '.join(codes)
    labels=issue_labels()
    return ' | '.join(code+' ('+labels[code].rstrip('.')+')' if code in labels else code for code in codes)


def normalize_aliases(payload, aliases):
    result = dict(payload)
    for alias, canonical in aliases.items():
        if alias not in payload:
            continue
        if canonical in payload and payload[canonical] != payload[alias]:
            raise ValueError(f'Conflicting fields: {canonical} / {alias}')
        result[canonical] = payload[alias]
        if alias != canonical:
            result.pop(alias,None)
    return result


ORIGO_ALIASES = {
    'idea': 'ide_awal', 'topic': 'topik', 'phenomenon': 'fenomena', 'focus': 'fokus',
    'theory': 'teori_pilihan', 'paradigm': 'paradigma', 'method': 'metode_pilihan',
    'research_question': 'pertanyaan_penelitian', 'unit_of_analysis': 'unit_analisis',
    'data_access': 'akses_data', 'title_count': 'judul_count', 'answers': 'jawaban_21',
    'changes': 'perubahan', 'supervisor_feedback': 'perubahan_pembimbing',
    'discipline': 'bidang_ilmu', 'level': 'jenjang', 'user_notes': 'catatan_pengguna',
}

NODE_ALIASES = {
 'empirical_context':'realitas_fenomena','research_focus':'fokus_penelitian',
 'theoretical_basis':'landasan_teori','method_direction':'arah_metodologi',
 'potential_contribution':'potensi_kebaruan','candidate_titles':'alternatif_judul',
}
