import unittest

from scripts.validate import public_documentation_errors


class PublicDocumentationTests(unittest.TestCase):
    def test_public_setup_and_synthetic_examples_are_allowed(self):
        for text in (
            "https://mcp-api.convai.com/mcp",
            "https://login.convai.com",
            "https://github.com/Conv-AI/ConvAI-Agent-Plugin",
            "support@convai.com",
            "OAuth public client ID chatgpt, no client secret",
            "character:read character:write",
            "11111111-1111-4111-8111-111111111111",
            "cvpat_...",
        ):
            with self.subTest(text=text):
                self.assertEqual(public_documentation_errors(text), [])

    def test_nonproduction_hosts_are_rejected(self):
        for host in (
            "https://fixture-stg.convai.com/mcp",
            "https://fixture-preview.convai.com",
            "https://fixture-dev.convai.com",
        ):
            with self.subTest(host=host):
                self.assertIn(
                    "README.md: references a non-production host",
                    public_documentation_errors(host),
                )

    def test_internal_references_are_rejected(self):
        for text in (
            "https://convaixr.atlassian.net/wiki/example",
            "https://conv-ai.slack.com/archives/example",
            "https://console.cloud.google.com/logs/query",
            "https://admin.internal.convai.com",
            "CORE-1234",
            "prj-cs-test-example",
        ):
            with self.subTest(text=text):
                self.assertIn(
                    "README.md: references internal operational information",
                    public_documentation_errors(text),
                )

    def test_credential_material_is_rejected_without_echoing_it(self):
        for text in (
            "cvpat_" + "0" * 12,
            "cvoat_" + "0" * 12,
            "-----BEGIN PRIVATE KEY-----",
            "AIza" + "0" * 32,
        ):
            with self.subTest(kind=text[:5]):
                result = public_documentation_errors(text)
                self.assertIn("README.md: looks like it contains a credential", result)
                self.assertTrue(all(text not in message for message in result))


if __name__ == "__main__":
    unittest.main()
