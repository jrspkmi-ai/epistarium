"""Conservative PDFium reader and pypdf annotation writer.

Coordinates exposed to the caller are top-left page coordinates. Native PDF
coordinates are retained separately for annotations, including rotated pages.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pypdfium2 as pdfium
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Highlight
from pypdf.generic import ArrayObject, FloatObject, TextStringObject, NameObject


class FileDataError(ValueError):
    pass


EmptyFileError = FileDataError


@dataclass(frozen=True)
class Rect:
    x0: float
    y0: float
    x1: float
    y1: float

    @property
    def width(self): return self.x1 - self.x0

    @property
    def height(self): return self.y1 - self.y0

    def contains(self, other):
        return self.x0 - .02 <= other.x0 < other.x1 <= self.x1 + .02 and self.y0 - .02 <= other.y0 < other.y1 <= self.y1 + .02

    def intersects(self, other):
        return self.x0 < other.x1 and other.x0 < self.x1 and self.y0 < other.y1 and other.y0 < self.y1


@dataclass(frozen=True)
class Quad:
    rect: Rect
    native: tuple[float, float, float, float]


class Annotation:
    def __init__(self, page, quads):
        self.page, self.quads, self.content = page, quads, ""

    def set_info(self, *, content): self.content = content

    def update(self): pass


class Page:
    def __init__(self, doc, number):
        self.doc, self.number = doc, number
        self.raw = doc.raw[number]
        self.textpage = self.raw.get_textpage()
        width, height = self.raw.get_size()
        self.rect = Rect(0, 0, width, height)
        self.rotation = self.raw.get_rotation()
        media = self.raw.get_mediabox()
        self.native_width, self.native_height = media[2]-media[0], media[3]-media[1]
        self.annotations = []

    def get_text(self, mode="text", sort=False):
        if mode == "text":
            return self.textpage.get_text_bounded().replace("\r\n", "\n")
        if mode == "blocks":
            h = self.rect.height
            regions = ((0, .19*h), (.19*h, .82*h), (.82*h, h))
            blocks = []
            for y0, y1 in regions:
                value = self.textpage.get_text_bounded(bottom=h-y1, top=h-y0).replace("\r\n", "\n")
                if value.strip(): blocks.append((0, y0, self.rect.width, y1, value))
            return blocks
        raise ValueError("Unsupported text mode")

    def get_label(self):
        return self.doc.labels[self.number]

    def search_for(self, phrase, quads=True):
        if not phrase: return []
        found = []
        searcher = self.textpage.search(phrase)
        try:
            while (hit := searcher.get_next()) is not None:
                start, count = hit
                if start < 0 or count <= 0: continue
                rectangles = []
                for i in range(start, start + count):
                    try:
                        box = self.textpage.get_charbox(i)
                    except Exception:
                        return []
                    if box[2] > box[0] and box[3] > box[1]: rectangles.append(box)
                if not rectangles: return []
                # Preserve each visual line; do not bridge columns or unrelated lines.
                lines = []
                for box in rectangles:
                    if (lines and abs(lines[-1][0][1] - box[1]) <= 4
                            and lines[-1][-1][0] - 3 <= box[0] <= lines[-1][-1][2] + 25):
                        lines[-1].append(box)
                    else:
                        lines.append([box])
                for line in lines:
                    l = min(b[0] for b in line); b = min(v[1] for v in line)
                    r = max(v[2] for v in line); t = max(v[3] for v in line)
                    if self.rotation == 90:
                        visual = Rect(b, l, t, r)
                    elif self.rotation == 180:
                        visual = Rect(self.native_width-r, b, self.native_width-l, t)
                    elif self.rotation == 270:
                        visual = Rect(self.native_height-t, self.native_width-r,
                                      self.native_height-b, self.native_width-l)
                    else:
                        visual = Rect(l, self.native_height-t, r, self.native_height-b)
                    found.append(Quad(visual, (l,b,r,t)))
        finally:
            searcher.close()
        return found

    def add_highlight_annot(self, quads):
        annot = Annotation(self, quads)
        self.annotations.append(annot)
        return annot


class Document:
    def __init__(self, path):
        self.path = Path(path)
        try:
            self.raw = pdfium.PdfDocument(str(path))
            self.needs_pass = False
            self.labels = PdfReader(str(path), strict=False).page_labels
            self.pages = [Page(self, i) for i in range(len(self.raw))]
        except Exception as exc:
            if hasattr(self, "raw"): self.raw.close()
            raise FileDataError(str(exc)) from exc

    def __len__(self): return len(self.pages)
    def __getitem__(self, i): return self.pages[i]
    def __iter__(self): return iter(self.pages)
    def __enter__(self): return self
    def __exit__(self, *_): self.close()

    def close(self):
        for page in self.pages:
            page.textpage.close(); page.raw.close()
        self.raw.close()

    def save(self, path, **_):
        reader = PdfReader(str(self.path), strict=False)
        writer = PdfWriter()
        writer.append_pages_from_reader(reader)
        for page in self.pages:
            for annot in page.annotations:
                for quad in annot.quads:
                    l,b,r,t = quad.native
                    points = ArrayObject([FloatObject(v) for v in (l,t,r,t,l,b,r,b)])
                    item = Highlight(rect=(l,b,r,t), quad_points=points, highlight_color="ffff00", printing=True)
                    item[NameObject("/Contents")] = TextStringObject(annot.content)
                    writer.add_annotation(page.number, item)
        with Path(path).open("wb") as output: writer.write(output)


def open(path): return Document(path)
