import unittest
import sys
import types
from unittest.mock import patch, MagicMock

# Pre-inject the Mock for google.generativeai in sys.modules to handle dynamic local imports cleanly
mock_google_genai = MagicMock()
google_mock = types.ModuleType("google")
google_mock.generativeai = mock_google_genai
sys.modules["google"] = google_mock
sys.modules["google.generativeai"] = mock_google_genai

# Pre-inject the Mock for groq
mock_groq = MagicMock()
mock_groq_client = MagicMock()
mock_groq.Groq.return_value = mock_groq_client
sys.modules["groq"] = mock_groq

# Pre-configure config keys before importing agent modules
import config
config.GEMINI_API_KEY = "mock_gemini_key"
config.GROQ_API_KEY = "mock_groq_key"

from agents import sales_agent, support_agent, insight_agent
from utils.validators import SAFE_FALLBACK


class TestSalesAgentBehavior(unittest.TestCase):
    def setUp(self):
        self.user_id = "sales_test_user"
        mock_google_genai.reset_mock()
        mock_groq_client.reset_mock()
        mock_groq_client.chat.completions.create.side_effect = None
        mock_groq_client.chat.completions.create.return_value = None

    def test_sales_agent_formatting_compliance(self):
        # Setup Gemini mock response in the strict formatting style
        mock_model = MagicMock()
        mock_google_genai.GenerativeModel.return_value = mock_model
        
        mock_response = MagicMock()
        mock_response.text = """━━━━━━━━━━━━━━━━━━━━
PRODUCT INTELLIGENCE
━━━━━━━━━━━━━━━━━━━━

Product:
Samsung Galaxy S26 Ultra

Category:
Flagship Smartphone

Brand:
Samsung

KEY SPECIFICATIONS

* Display: 6.8" AMOLED
* Processor: Snapdragon 8 Gen 4
* RAM: 16GB
* Storage: 1TB
* Battery: 5500mAh
* Camera: 200MP Main
* AI Features: Advanced NPU

KEY INSIGHTS

* Superior camera performance
* Excellent battery life
* Premium build quality

BEST FOR

✓ Gaming
✓ Content Creation
✓ Photography
✓ Productivity

KNOWLEDGE SOURCES

✓ Product Database
✓ Wikipedia
✓ Wikidata

CONFIDENCE

96%

━━━━━━━━━━━━━━━━━━━━"""
        mock_model.generate_content.return_value = mock_response

        res = sales_agent.get_reply(self.user_id, "Recommend a premium phone", [])
        
        # Verify formatting compliance
        self.assertIn("PRODUCT INTELLIGENCE", res["reply"])
        self.assertIn("KEY SPECIFICATIONS", res["reply"])
        self.assertIn("KEY INSIGHTS", res["reply"])
        self.assertEqual(res["llm_used"], "gemini")
        self.assertTrue(res["response_validated"])

    def test_sales_agent_failover_to_groq(self):
        # Force Gemini to fail
        mock_model = MagicMock()
        mock_google_genai.GenerativeModel.return_value = mock_model
        mock_model.generate_content.side_effect = Exception("Gemini service down")

        # Mock Groq to succeed
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = "━━━━━━━━━━━━━━━━━━━━\nPRODUCT INTELLIGENCE\n━━━━━━━━━━━━━━━━━━━━\n\nProduct:\nGroq Phone\n\nCategory:\nSmartphone\n\nBrand:\nGroq\n\nKEY SPECIFICATIONS\n\n* AI Features: Groq fallback response\n\nKEY INSIGHTS\n\n* Groq fallback response\n\nBEST FOR\n\n✓ Groq Fallback\n\nKNOWLEDGE SOURCES\n\n✓ Groq Fallback\n\nCONFIDENCE\n\n80%\n\n━━━━━━━━━━━━━━━━━━━━"
        mock_groq_client.chat.completions.create.return_value = mock_completion

        res = sales_agent.get_reply(self.user_id, "Recommend a premium phone", [])
        self.assertEqual(res["llm_used"], "groq")
        self.assertIn("Groq fallback response", res["reply"])

    def test_sales_agent_failover_to_safe_fallback(self):
        # Force Gemini to fail
        mock_model = MagicMock()
        mock_google_genai.GenerativeModel.return_value = mock_model
        mock_model.generate_content.side_effect = Exception("Gemini service down")

        # Force Groq to fail
        mock_groq_client.chat.completions.create.side_effect = Exception("Groq service down")

        res = sales_agent.get_reply(self.user_id, "Give me an enterprise recommendation", [])

        # Check that response switched to SAFE_FALLBACK
        self.assertEqual(res["llm_used"], "error")
        self.assertEqual(res["reply"], SAFE_FALLBACK)
        self.assertTrue(res["response_validated"])


class TestSupportAgentBehavior(unittest.TestCase):
    def setUp(self):
        self.user_id = "support_test_user"
        mock_google_genai.reset_mock()
        mock_groq_client.reset_mock()
        mock_groq_client.chat.completions.create.side_effect = None
        mock_groq_client.chat.completions.create.return_value = None

    def test_support_agent_gemini_primary(self):
        # Setup Gemini mock client response
        mock_model = MagicMock()
        mock_google_genai.GenerativeModel.return_value = mock_model
        
        mock_response = MagicMock()
        mock_response.text = """Category
Troubleshooting

Key Insights
* User cannot login
* SSO authentication error

Recommendations
1. Reset SSO session
2. Verify credentials in identity manager

Knowledge Sources
✓ Support Database

Confidence
90%"""
        mock_model.generate_content.return_value = mock_response

        res = support_agent.get_reply(self.user_id, "SSO login is failing", [])

        self.assertEqual(res["llm_used"], "gemini")
        self.assertIn("Troubleshooting", res["reply"])
        self.assertIn("Reset SSO session", res["reply"])

    def test_support_agent_failover_to_groq(self):
        # Force Gemini to fail
        mock_model = MagicMock()
        mock_google_genai.GenerativeModel.return_value = mock_model
        mock_model.generate_content.side_effect = Exception("Gemini service down")

        # Mock Groq to succeed
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = "Category\nTroubleshooting\n\nKey Insights\n* Groq support response\n\nRecommendations\n1. Contact admin\n\nKnowledge Sources\n✓ Support Database\n\nConfidence\n85%"
        mock_groq_client.chat.completions.create.return_value = mock_completion

        res = support_agent.get_reply(self.user_id, "SSO login is failing", [])
        self.assertEqual(res["llm_used"], "groq")
        self.assertIn("Groq support response", res["reply"])

    def test_support_agent_failover_to_safe_fallback(self):
        # Force Gemini to fail
        mock_model = MagicMock()
        mock_google_genai.GenerativeModel.return_value = mock_model
        mock_model.generate_content.side_effect = Exception("Gemini service down")

        # Force Groq to fail
        mock_groq_client.chat.completions.create.side_effect = Exception("Groq service down")

        res = support_agent.get_reply(self.user_id, "Can you help me reset my key", [])

        self.assertEqual(res["llm_used"], "error")
        self.assertEqual(res["reply"], SAFE_FALLBACK)


class TestInsightAgentBehavior(unittest.TestCase):
    def setUp(self):
        self.user_id = "insight_test_user"
        mock_google_genai.reset_mock()
        mock_groq_client.reset_mock()
        mock_groq_client.chat.completions.create.side_effect = None
        mock_groq_client.chat.completions.create.return_value = None

    def test_insight_agent_sentiment_classification(self):
        # Mock Gemini content generation returning JSON string
        mock_model = MagicMock()
        mock_google_genai.GenerativeModel.return_value = mock_model
        
        mock_response = MagicMock()
        mock_response.text = '{"sentiment": "neutral", "score": 1, "escalate": false, "reply": "Category\\nMarket Analysis\\n\\nKey Insights\\n* Base plan overview\\n\\nRecommendations\\n1. Check pricing tables\\n\\nKnowledge Sources\\n✓ Trend Intelligence\\n\\nConfidence\\n90%"}'
        mock_model.generate_content.return_value = mock_response

        res = insight_agent.get_sentiment(self.user_id, "What is the price of the base plan?", [])
        
        self.assertEqual(res["sentiment"], "neutral")
        self.assertFalse(res["escalate"])
        self.assertEqual(res["score"], 1)

    def test_rule_based_sentiment_fallback_angry(self):
        # Test fallback rule heuristic directly for an angry/frustrated user
        from agents.insight_agent import _rule_based_sentiment
        parsed = _rule_based_sentiment("This broken integration is terrible and worst experience ever!")
        self.assertEqual(parsed["sentiment"], "angry")
        self.assertTrue(parsed["escalate"])
        self.assertGreaterEqual(parsed["score"], 8.0)

    def test_rule_based_sentiment_fallback_neutral(self):
        # Test that informational queries are kept neutral and NOT escalated
        from agents.insight_agent import _rule_based_sentiment
        parsed = _rule_based_sentiment("Show me the price and specifications of the server.")
        self.assertEqual(parsed["sentiment"], "neutral")
        self.assertFalse(parsed["escalate"])
        self.assertEqual(parsed["score"], 2.0)


if __name__ == "__main__":
    unittest.main()
