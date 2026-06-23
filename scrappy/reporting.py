from __future__ import annotations

import html
import zipfile
from pathlib import Path

from scrappy.models import RankedOffer


HEADERS = [
    "rank",
    "score",
    "eligible",
    "title",
    "company",
    "location_status",
    "seniority_status",
    "url",
    "strengths",
    "gaps",
    "risks",
    "reasons",
]


def print_console(ranked: list[RankedOffer]) -> None:
    if not ranked:
        print("No ranked offers yet.")
        return
    for index, item in enumerate(ranked, start=1):
        offer = item.offer
        score = item.score
        print(f"{index}. [{score.score}/100] {offer.title} - {offer.company or 'unknown company'}")
        print(f"   eligible={score.eligible} location={score.location_status} seniority={score.seniority_status}")
        print(f"   url={offer.url}")
        if score.strengths:
            print("   strengths: " + "; ".join(score.strengths[:3]))
        if score.gaps:
            print("   gaps: " + "; ".join(score.gaps[:3]))


def write_xlsx(path: str | Path, ranked: list[RankedOffer]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    rows = [HEADERS]
    for index, item in enumerate(ranked, start=1):
        score = item.score
        offer = item.offer
        rows.append(
            [
                str(index),
                str(score.score),
                str(score.eligible),
                offer.title,
                offer.company,
                score.location_status,
                score.seniority_status,
                offer.url,
                "; ".join(score.strengths),
                "; ".join(score.gaps),
                "; ".join(score.risks),
                "; ".join(score.reasons),
            ]
        )
    _write_minimal_xlsx(output, rows)


def _write_minimal_xlsx(path: Path, rows: list[list[str]]) -> None:
    sheet_rows = []
    for row_idx, row in enumerate(rows, start=1):
        cells = []
        for col_idx, value in enumerate(row, start=1):
            ref = f"{_column_name(col_idx)}{row_idx}"
            cells.append(
                f'<c r="{ref}" t="inlineStr"><is><t>{html.escape(value or "")}</t></is></c>'
            )
        sheet_rows.append(f'<row r="{row_idx}">{"".join(cells)}</row>')

    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "[Content_Types].xml",
            """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>""",
        )
        archive.writestr(
            "_rels/.rels",
            """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>""",
        )
        archive.writestr(
            "xl/workbook.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<sheets><sheet name="Top offers" sheetId="1" r:id="rId1"/></sheets>
</workbook>""",
        )
        archive.writestr(
            "xl/_rels/workbook.xml.rels",
            """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
</Relationships>""",
        )
        archive.writestr(
            "xl/worksheets/sheet1.xml",
            f"""<?xml version="1.0" encoding="UTF-8"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<sheetData>{''.join(sheet_rows)}</sheetData>
</worksheet>""",
        )


def _column_name(index: int) -> str:
    name = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        name = chr(65 + remainder) + name
    return name
