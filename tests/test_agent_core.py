import io
import io
import sys
import unittest
import zipfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent_core import (  # noqa: E402
    REFERENCE_DATE,
    build_evidence_context,
    documents_from_directory,
    documents_from_uploads,
    validate_brief,
)


class AgentCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs = documents_from_directory(ROOT / "research_pack")

    def test_bundled_pack_has_eight_markdown_sources(self):
        self.assertEqual(len(self.docs), 8)
        self.assertEqual([doc.source_id for doc in self.docs], [f"S{i}" for i in range(1, 9)])
        self.assertTrue(any("revenue" in doc.text.lower() for doc in self.docs))

    def test_metadata_is_extracted(self):
        press_release = next(doc for doc in self.docs if "ir_press_release" in doc.filename)
        self.assertEqual(press_release.published, "2026-08-08")
        self.assertIn("company", press_release.source.lower())
        self.assertIn("Sarvottam Cables", press_release.title)

    def test_evidence_context_contains_ticker_date_and_ids(self):
        context = build_evidence_context("SRVCABLE", self.docs)
        self.assertIn("Ticker supplied by user: SRVCABLE", context)
        self.assertIn(REFERENCE_DATE, context)
        self.assertIn("--- SOURCE S1 ---", context)
        self.assertIn("--- SOURCE S8 ---", context)

    def test_validator_flags_missing_sections_and_invalid_citation(self):
        result = validate_brief("# Snapshot\nRevenue grew [S99].", self.docs)
        joined = " ".join(result)
        self.assertIn("Missing required section: Bull case", joined)
        self.assertIn("Unknown citation ID(s): S99", joined)

    def test_validator_accepts_required_sections_and_valid_citation(self):
        brief = """# Snapshot
The company manufactures cables and reported a solid increase in revenue during its latest quarter, alongside slower growth in operating profit. The figures and quarter references are attributed to the primary release [S1].
# Bull case
The order book increased compared with the prior year and export revenue contribution grew. A new facility is also expected to add capacity, subject to execution and start-up timing [S1].
# Bear case
Operating margins narrowed, showing that input-cost pressure can offset part of the growth in sales. This could persist until customer price adjustments catch up [S1].
# Open questions
Why do revenue figures in two supplied reports differ? Additional reconciled filings and working-capital disclosures would help assess the trend [S1] [S2].
# Sources
- [S1] Primary company filing, latest quarterly results.
- [S2] Secondary news report with a conflicting revenue figure.
"""
        result = validate_brief(brief, self.docs)
        self.assertEqual(result, ["Mechanical checks passed. This does not establish that the claims are factually correct."])

    def test_upload_parser_handles_markdown_frontmatter(self):
        sample = b"---\nsource: Example Exchange\nurl: https://example.test/report\npublished: 2026-09-01\ntype: filing\n---\n# Quarterly report\nRevenue grew."
        docs = documents_from_uploads([("sample.md", sample)])
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0].source, "Example Exchange")
        self.assertEqual(docs[0].published, "2026-09-01")
        self.assertIn("Revenue grew", docs[0].text)

    def test_nested_zip_upload_extracts_pack_and_ignores_assignment_readme(self):
        readme = b"# Super Investing\nThe company is **fictional**. This is the research brief assignment."
        nested_buffer = io.BytesIO()
        with zipfile.ZipFile(nested_buffer, "w", zipfile.ZIP_DEFLATED) as nested_zip:
            nested_zip.writestr("README.md", readme)
            for path in sorted((ROOT / "research_pack").glob("*.md")):
                nested_zip.writestr(f"research_pack/{path.name}", path.read_bytes())
        outer_buffer = io.BytesIO()
        with zipfile.ZipFile(outer_buffer, "w", zipfile.ZIP_DEFLATED) as outer_zip:
            outer_zip.writestr("candidate.zip", nested_buffer.getvalue())

        docs = documents_from_uploads([("download.zip", outer_buffer.getvalue())])
        self.assertEqual(len(docs), 8)
        self.assertTrue(all("README.md" not in doc.filename for doc in docs))
        self.assertTrue(any("ir_press_release" in doc.filename for doc in docs))

    def test_nested_zip_upload_extracts_pack_and_ignores_assignment_readme(self):
        readme = b"# Super Investing\nThe company is **fictional**. This is the research brief assignment."
        nested_buffer = io.BytesIO()
        with zipfile.ZipFile(nested_buffer, "w", zipfile.ZIP_DEFLATED) as nested_zip:
            nested_zip.writestr("README.md", readme)
            for path in sorted((ROOT / "research_pack").glob("*.md")):
                nested_zip.writestr(f"research_pack/{path.name}", path.read_bytes())
        outer_buffer = io.BytesIO()
        with zipfile.ZipFile(outer_buffer, "w", zipfile.ZIP_DEFLATED) as outer_zip:
            outer_zip.writestr("candidate.zip", nested_buffer.getvalue())

        docs = documents_from_uploads([("download.zip", outer_buffer.getvalue())])
        self.assertEqual(len(docs), 8)
        self.assertTrue(all("README.md" not in doc.filename for doc in docs))
        self.assertTrue(any("ir_press_release" in doc.filename for doc in docs))


if __name__ == "__main__":
    unittest.main()
