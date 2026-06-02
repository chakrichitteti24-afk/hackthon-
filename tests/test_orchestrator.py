import unittest
from unittest.mock import patch

from memory.session_store import clear_session, get_session
from orchestration.orchestrator import orchestrate_message


class OrchestratorTests(unittest.TestCase):
    def setUp(self):
        self.user_id = "test_user"
        clear_session(self.user_id)

    def tearDown(self):
        clear_session(self.user_id)

    @patch("orchestration.orchestrator.extract_profile_from_messages", return_value={"preferred_platform": "web"})
    @patch("orchestration.orchestrator.insight_agent.get_sentiment")
    @patch("orchestration.orchestrator.sales_agent.get_reply")
    @patch("orchestration.orchestrator.search_web", return_value="Latest product pricing and feature details")
    def test_orchestrate_message_routes_sales_and_updates_session(
        self,
        mock_search_web,
        mock_sales_reply,
        mock_insight_sentiment,
        mock_extract_profile,
    ):
        mock_sales_reply.return_value = {"reply": "Sales response", "llm_used": "GROQ", "web_searched": True}
        mock_insight_sentiment.return_value = {
            "reply": "",
            "sentiment": "neutral",
            "score": 2.0,
            "escalate": False,
            "llm_used": "GROQ",
            "web_searched": False,
        }

        response = orchestrate_message(self.user_id, "Please send a pricing quote and roadmap recommendation")

        self.assertEqual(response["agent_type"], "sales")
        self.assertEqual(response["reply"], "Sales response")
        self.assertFalse(response["escalate"])
        self.assertTrue(response["web_searched"])

        session = get_session(self.user_id)
        self.assertEqual(session["agent_type"], "sales")
        self.assertEqual(session["user_profile"]["preferred_platform"], "web")
        self.assertTrue(len(session["activity_log"]) >= 3)

    @patch("orchestration.orchestrator.extract_profile_from_messages", return_value={})
    @patch("orchestration.orchestrator.insight_agent.get_sentiment")
    @patch("orchestration.orchestrator.support_agent.get_reply")
    @patch("orchestration.orchestrator.search_web", return_value="")
    def test_user_requested_agent_support_overrides_routing(
        self,
        mock_search_web,
        mock_support_reply,
        mock_insight_sentiment,
        mock_extract_profile,
    ):
        mock_support_reply.return_value = {"reply": "Support answer", "llm_used": "GROQ", "web_searched": False}
        mock_insight_sentiment.return_value = {
            "reply": "",
            "sentiment": "neutral",
            "score": 3.0,
            "escalate": False,
            "llm_used": "GROQ",
            "web_searched": False,
        }

        response = orchestrate_message(self.user_id, "I cannot login to my account and need help", requested_agent_type="support")

        self.assertEqual(response["agent_type"], "support")
        self.assertEqual(response["reply"], "Support answer")
        self.assertFalse(response["escalate"])

    @patch("orchestration.orchestrator.extract_profile_from_messages", return_value={})
    @patch("orchestration.orchestrator.insight_agent.get_sentiment")
    @patch("orchestration.orchestrator.sales_agent.get_reply")
    @patch("orchestration.orchestrator.route_agent")
    @patch("orchestration.orchestrator.search_web", return_value="")
    def test_orchestrate_message_escalates_on_high_sentiment_score(
        self,
        mock_search_web,
        mock_route_agent,
        mock_sales_reply,
        mock_insight_sentiment,
        mock_extract_profile,
    ):
        mock_route_agent.return_value = {
            "agent": "sales",
            "intent": "purchase",
            "sentiment_detected": "negative",
            "urgency": "high",
            "stage": "consideration",
            "confidence": 0.95,
            "reasons": ["Test mock negative sentiment"]
        }
        mock_sales_reply.return_value = {"reply": "Sales answer", "llm_used": "GROQ", "web_searched": False}
        mock_insight_sentiment.return_value = {
            "reply": "",
            "sentiment": "negative",
            "score": 8.5,
            "escalate": True,
            "llm_used": "GROQ",
            "web_searched": False,
        }

        response = orchestrate_message(self.user_id, "Please send me a quote for a new enterprise plan and pricing details.")

        self.assertEqual(response["agent_type"], "sales")
        self.assertTrue(response["escalate"])
        session = get_session(self.user_id)
        self.assertTrue(session["escalated"])


if __name__ == "__main__":
    unittest.main()
