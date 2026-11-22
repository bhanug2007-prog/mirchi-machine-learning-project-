from datetime import date
from unittest import TestCase
from unittest.mock import patch
import os

from backend.knowledge import Question, ask, retrieve


class KnowledgeTest(TestCase):
    def test_retrieval_benchmark(self):
        cases = [
            ("What documents do I need to register at Guntur mandi?", "enam-documents"),
            ("How should I store dried Teja S17 chilli?", "spices-storage"),
            ("గుంటూరు మండీలో నమోదు కోసం ఏ పత్రాలు అవసరం?", "enam-documents"),
            ("ఎండు తేజ S17 మిర్చిని ఎలా నిల్వ చేయాలి?", "spices-storage"),
            ("How are eNAM payments sent to farmers?", "enam-payment"),
            ("Can I spray water on dried chilli before packing?", "spices-packing"),
            ("How do I renew my driving licence?", None),
            ("What documents do I need to register my car?", None),
            ("How should I store potatoes?", None),
            ("Tomorrow price prediction for Teja S17 chilli", None),
        ]
        for question, expected in cases:
            with self.subTest(question=question):
                found = retrieve(question, date(2026, 11, 22))
                self.assertEqual(found[0]["id"] if found else None, expected)

    def test_review_deadline_excludes_old_guidance(self):
        self.assertEqual(retrieve("What documents do I need to register at Guntur mandi?", date(2027, 2, 23)), [])

    def test_citations_and_localized_answers_without_provider(self):
        original_retrieve = retrieve
        with patch.dict(os.environ, {"KNOWLEDGE_OPENAI_API_KEY": ""}), patch(
            "backend.knowledge.retrieve", side_effect=lambda text, _: original_retrieve(text, date(2026, 11, 22))
        ):
            en = ask(Question(question="What documents are needed to register at Guntur mandi?"))
            te = ask(Question(question="What documents are needed to register at Guntur mandi?", language="te"))
        self.assertEqual(en["status"], "answered")
        self.assertIn("general eNAM", en["notes"][0])
        self.assertTrue(en["passages"][0]["url"].startswith("https://www.enam.gov.in/"))
        self.assertEqual(en["passages"][0]["id"], te["passages"][0]["id"])
        self.assertNotEqual(en["passages"][0]["answer"], te["passages"][0]["answer"])
