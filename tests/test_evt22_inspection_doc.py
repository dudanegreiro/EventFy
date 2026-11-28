from pathlib import Path
import re
import unittest


DOCUMENT = Path(__file__).resolve().parents[1] / "INSPECOES.md"


class InspectionDocumentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.content = DOCUMENT.read_text(encoding="utf-8")

    def test_all_requirement_families_have_four_roles(self):
        expected = (
            [f"HU-{number:02d}" for number in range(1, 15)]
            + [f"RF{number:02d}" for number in range(1, 21)]
            + [f"RN{number:02d}" for number in range(1, 14)]
            + [f"RNF-{number:02d}" for number in range(1, 8)]
        )
        for identifier in expected:
            row = next(
                line
                for line in self.content.splitlines()
                if line.startswith(f"| {identifier} |")
            )
            cells = [cell.strip() for cell in row.strip("|").split("|")]
            self.assertEqual(5, len(cells), identifier)
            self.assertTrue(all(cells[1:]), identifier)
            self.assertEqual(4, len(set(cells[1:])), identifier)

    def test_findings_have_classification_rework_and_recheck(self):
        findings = [
            line
            for line in self.content.splitlines()
            if re.match(r"\| INS-\d{2} \|", line)
        ]
        self.assertEqual(12, len(findings))
        allowed = {"Defeito", "Ambiguidade", "Lacuna", "Melhoria"}
        for row in findings:
            cells = [cell.strip() for cell in row.strip("|").split("|")]
            self.assertEqual(9, len(cells), row)
            self.assertIn(cells[2], allowed, row)
            self.assertTrue(cells[5], row)
            self.assertTrue(cells[6], row)
            self.assertTrue(cells[7], row)

    def test_traceability_and_open_status_are_explicit(self):
        self.assertIn("**Status:** Aberta", self.content)
        self.assertIn("todos os achados devem estar", self.content.lower())
        self.assertIn("TC-INS-01", self.content)
        self.assertIn("TC-INS-12", self.content)


if __name__ == "__main__":
    unittest.main()
