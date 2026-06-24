from __future__ import annotations

import html
import zipfile
from pathlib import Path
from xml.etree import ElementTree

from scrappy.models import RankedOffer


HEADERS = [
    "rank",
    "offer_id",
    "source",
    "source_id",
    "merged_sources",
    "duplicate_reason",
    "decision",
    "review_note",
    "reviewed_at",
    "score",
    "eligible",
    "title",
    "company",
    "location",
    "remote",
    "contract_type",
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
    all_rows = [HEADERS]
    rejected_rows = [HEADERS]
    for index, item in enumerate(ranked, start=1):
        row = _ranked_row(index, item)
        all_rows.append(row)
        if not item.score.eligible:
            rejected_rows.append(row)
    _write_minimal_xlsx(output, {"all_scored": all_rows, "rejected": rejected_rows})


def read_review_rows(path: str | Path, sheet_name: str = "all_scored") -> list[dict[str, str]]:
    with zipfile.ZipFile(path) as archive:
        target = _worksheet_target(archive, sheet_name)
        rows = _read_sheet_rows(archive, target)
    if not rows:
        return []
    headers = [value.strip() for value in rows[0]]
    output: list[dict[str, str]] = []
    for row in rows[1:]:
        padded = row + [""] * (len(headers) - len(row))
        output.append(dict(zip(headers, padded, strict=False)))
    return output


def _ranked_row(index: int, item: RankedOffer) -> list[str]:
    score = item.score
    offer = item.offer
    return [
        str(index),
        str(item.offer_id or ""),
        offer.source,
        offer.source_id,
        "; ".join(item.merged_sources),
        item.duplicate_reason,
        "",
        "",
        "",
        str(score.score),
        str(score.eligible),
        offer.title,
        offer.company,
        offer.location,
        offer.remote,
        offer.contract_type,
        score.location_status,
        score.seniority_status,
        offer.url,
        "; ".join(score.strengths),
        "; ".join(score.gaps),
        "; ".join(score.risks),
        "; ".join(score.reasons),
    ]


def _write_minimal_xlsx(path: Path, sheets: dict[str, list[list[str]]]) -> None:
    sheet_names = list(sheets)
    content_overrides = "\n".join(
        (
            f'<Override PartName="/xl/worksheets/sheet{index}.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        )
        for index, _name in enumerate(sheet_names, start=1)
    )
    workbook_sheets = "".join(
        f'<sheet name="{html.escape(name)}" sheetId="{index}" r:id="rId{index}"/>'
        for index, name in enumerate(sheet_names, start=1)
    )
    workbook_rels = "\n".join(
        (
            f'<Relationship Id="rId{index}" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
            f'Target="worksheets/sheet{index}.xml"/>'
        )
        for index, _name in enumerate(sheet_names, start=1)
    )

    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "[Content_Types].xml",
            f"""<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
{content_overrides}
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
            f"""<?xml version="1.0" encoding="UTF-8"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<sheets>{workbook_sheets}</sheets>
</workbook>""",
        )
        archive.writestr(
            "xl/_rels/workbook.xml.rels",
            """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
""" + workbook_rels + """
</Relationships>""",
        )
        for index, name in enumerate(sheet_names, start=1):
            sheet_rows = _sheet_xml_rows(sheets[name])
            archive.writestr(
                f"xl/worksheets/sheet{index}.xml",
                f"""<?xml version="1.0" encoding="UTF-8"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<sheetData>{''.join(sheet_rows)}</sheetData>
</worksheet>""",
            )


def _sheet_xml_rows(rows: list[list[str]]) -> list[str]:
    sheet_rows = []
    for row_idx, row in enumerate(rows, start=1):
        cells = []
        for col_idx, value in enumerate(row, start=1):
            ref = f"{_column_name(col_idx)}{row_idx}"
            cells.append(
                f'<c r="{ref}" t="inlineStr"><is><t>{html.escape(value or "")}</t></is></c>'
            )
        sheet_rows.append(f'<row r="{row_idx}">{"".join(cells)}</row>')
    return sheet_rows


def _worksheet_target(archive: zipfile.ZipFile, sheet_name: str) -> str:
    main_ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    rel_ns = "{http://schemas.openxmlformats.org/package/2006/relationships}"
    office_rel = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
    workbook = ElementTree.fromstring(archive.read("xl/workbook.xml"))
    rels = ElementTree.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    rel_targets = {
        rel.attrib["Id"]: rel.attrib["Target"]
        for rel in rels.findall(f"{rel_ns}Relationship")
    }
    for sheet in workbook.findall(f"{main_ns}sheets/{main_ns}sheet"):
        if sheet.attrib.get("name") == sheet_name:
            rel_id = sheet.attrib[office_rel]
            return rel_targets[rel_id]
    raise ValueError(f"Sheet not found: {sheet_name}")


def _read_sheet_rows(archive: zipfile.ZipFile, target: str) -> list[list[str]]:
    main_ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    root = ElementTree.fromstring(archive.read(f"xl/{target}"))
    shared_strings = _read_shared_strings(archive)
    output: list[list[str]] = []
    for row in root.findall(f"{main_ns}sheetData/{main_ns}row"):
        values_by_column: dict[int, str] = {}
        for cell in row.findall(f"{main_ns}c"):
            ref = cell.attrib.get("r", "")
            column_index = _column_index("".join(char for char in ref if char.isalpha())) or len(values_by_column) + 1
            values_by_column[column_index] = _cell_value(cell, shared_strings)
        if values_by_column:
            max_column = max(values_by_column)
            output.append([values_by_column.get(index, "") for index in range(1, max_column + 1)])
    return output


def _read_shared_strings(archive: zipfile.ZipFile) -> list[str]:
    try:
        root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
    except KeyError:
        return []
    return ["".join(item.itertext()) for item in root]


def _cell_value(cell: ElementTree.Element, shared_strings: list[str]) -> str:
    main_ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    cell_type = cell.attrib.get("t")
    if cell_type == "s":
        value = cell.find(f"{main_ns}v")
        if value is None or not value.text:
            return ""
        index = int(value.text)
        return shared_strings[index] if index < len(shared_strings) else ""
    return "".join(cell.itertext())


def _column_index(name: str) -> int:
    index = 0
    for char in name:
        index = index * 26 + ord(char.upper()) - 64
    return index


def _column_name(index: int) -> str:
    name = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        name = chr(65 + remainder) + name
    return name
