"""Purpose: Checks public resume analysis API behavior."""

import io
import unittest

from docx import Document

from app import create_app


def make_docx(text):
    document = Document()
    document.add_paragraph(text)
    content = io.BytesIO()
    document.save(content)
    content.seek(0)
    return content


class MatchingApiTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True})
        self.client = self.app.test_client()

    def post(self, url, data=None, **kwargs):
        if "content_type" in kwargs or not isinstance(data, dict):
            return self.client.post(url, data=data, **kwargs)
        return self.client.post(url, json=data, **kwargs)

    def test_health_check(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"status": "ok"})

    def test_authentication_endpoints_are_not_registered(self):
        for endpoint in ("/api/auth/login", "/api/auth/register", "/api/auth/signup"):
            with self.subTest(endpoint=endpoint):
                self.assertEqual(self.client.post(endpoint).status_code, 404)

    def test_analyzes_docx_without_an_account(self):
        response = self.post(
            "/api/matching/analyze",
            data={
                "file": (make_docx("Python SQL developer with 5 years experience."), "resume.docx"),
                "jobDescription": "Need Python, SQL, and Java experience.",
                "jobTitle": "Developer",
            },
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["matchedSkills"], ["Python", "SQL"])
        self.assertEqual(response.json["missingSkills"], ["Java"])
        self.assertEqual(response.json["matchPercentage"], 67)
        self.assertEqual(response.json["experience"], "5 years")
        self.assertNotIn("analysisId", response.json)

    def test_requires_resume_and_job_description(self):
        missing_resume = self.post("/api/matching/analyze", data={"jobDescription": "Python"})
        self.assertEqual(missing_resume.status_code, 400)
        self.assertIn("Select a resume", missing_resume.json["error"])

        missing_description = self.post(
            "/api/matching/analyze",
            data={"file": (make_docx("Python developer"), "resume.docx")},
            content_type="multipart/form-data",
        )
        self.assertEqual(missing_description.status_code, 400)
        self.assertIn("job description", missing_description.json["error"])

    def test_rejects_unsupported_and_invalid_documents(self):
        unsupported = self.post(
            "/api/matching/analyze",
            data={"file": (io.BytesIO(b"resume"), "resume.txt"), "jobDescription": "Python"},
            content_type="multipart/form-data",
        )
        self.assertEqual(unsupported.status_code, 400)

        invalid_pdf = self.post(
            "/api/matching/analyze",
            data={"file": (io.BytesIO(b"not a PDF"), "resume.pdf"), "jobDescription": "Python"},
            content_type="multipart/form-data",
        )
        self.assertEqual(invalid_pdf.status_code, 400)
        self.assertIn("could not be read", invalid_pdf.json["error"])

    def test_rejects_empty_resume_text(self):
        response = self.post(
            "/api/matching/analyze",
            data={"file": (make_docx(""), "resume.docx"), "jobDescription": "Python"},
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 422)
        self.assertIn("searchable PDF or DOCX", response.json["error"])


if __name__ == "__main__":
    unittest.main()
