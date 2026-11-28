from pathlib import Path
import re
import unittest


DOCUMENT = Path(__file__).resolve().parents[1] / "docs" / "VALIDACAO-USUARIO-EVT-24.md"


class ValidationProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.content = DOCUMENT.read_text(encoding="utf-8")

    def section(self, start_heading, end_heading):
        start = self.content.index(start_heading)
        end = self.content.index(end_heading, start)
        return self.content[start:end]

    def test_participant_tasks_avoid_interface_instructions(self):
        tasks = self.section(
            "## 3. Tarefas para o participante",
            "## 4. Registro imparcial das observações",
        )
        task_rows = [
            line for line in tasks.splitlines() if re.match(r"\| \*\*T\d", line)
        ]
        self.assertGreaterEqual(len(task_rows), 3)

        forbidden = re.compile(
            r"\b(?:clique|selecione|pressione|aperte|botão|tela|menu)\b",
            re.IGNORECASE,
        )
        for row in task_rows:
            participant_text = row.split("|")[2]
            self.assertIsNone(forbidden.search(participant_text), row)

    def test_observation_guidance_is_factual_and_nonleading(self):
        observations = self.section(
            "## 4. Registro imparcial das observações",
            "## 5. Itens de validação e rastreabilidade",
        )
        facilitation = self.section(
            "### 2.2 Abertura e postura do facilitador",
            "## 3. Tarefas para o participante",
        )
        self.assertIn("Ação observável ou fala literal", observations)
        self.assertIn("O que você esperava que acontecesse?", facilitation)
        self.assertIn("Não pergunte “Você gostou?”", facilitation)

    def test_validation_rows_include_origin_and_criterion(self):
        traceability = self.section(
            "## 5. Itens de validação e rastreabilidade",
            "## 6. Defeitos",
        )
        rows = [
            line
            for line in traceability.splitlines()
            if re.match(r"\| V-\d{2} \|", line)
        ]
        self.assertGreaterEqual(len(rows), 8)

        for row in rows:
            cells = [cell.strip() for cell in row.strip("|").split("|")]
            self.assertGreaterEqual(len(cells), 6, row)
            self.assertTrue(cells[2], row)
            self.assertTrue(cells[3], row)

    def test_defects_and_new_needs_use_separate_backlog_tables(self):
        defects = self.section("## 6. Defeitos", "## 7. Novas necessidades")
        needs = self.section(
            "## 7. Novas necessidades e mudanças de requisito",
            "## 8. Síntese da sessão e retorno ao backlog",
        )
        self.assertIn("Defeito observado", defects)
        self.assertIn("Necessidade expressa", needs)
        self.assertIn("Ação no backlog", defects)
        self.assertIn("Ação no backlog", needs)

    def test_requirement_changes_return_to_backlog(self):
        follow_up = self.content.split(
            "## 8. Síntese da sessão e retorno ao backlog", 1
        )[1]
        self.assertIn("abrir item de backlog", follow_up)
        self.assertIn("responsável pelo produto", follow_up)

    def test_mobile_nonfunctional_requirement_is_traceable(self):
        traceability = self.section(
            "## 5. Itens de validação e rastreabilidade",
            "## 6. Defeitos",
        )
        self.assertIn("RNF-04", traceability)
        self.assertIn("360 × 640", traceability)


if __name__ == "__main__":
    unittest.main()
