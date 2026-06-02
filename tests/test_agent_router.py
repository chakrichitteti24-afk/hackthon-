import unittest

from router.agent_router import route_agent

class AgentRouterTests(unittest.TestCase):
    def test_empty_message_defaults_to_sales(self):
        decision = route_agent("")
        self.assertEqual(decision["agent"], "sales")
        self.assertIn("General inquiry", decision["reasons"][0])
        self.assertGreaterEqual(decision["confidence"], 0.5)

    def test_sales_keywords_route_sales(self):
        decision = route_agent("I need a pricing quote and subscription plan recommendation")
        self.assertEqual(decision["agent"], "sales")
        self.assertEqual(decision["intent"], "purchase")

    def test_support_keywords_route_support(self):
        decision = route_agent("My integration is failing and I keep seeing an error")
        self.assertEqual(decision["agent"], "support")
        self.assertEqual(decision["intent"], "troubleshooting")

    def test_insight_keywords_route_insight(self):
        decision = route_agent("Compare the market trends between these two options")
        self.assertEqual(decision["agent"], "insight")
        self.assertEqual(decision["intent"], "analysis")

    def test_negative_sentiment_routes_support(self):
        decision = route_agent("I am angry and frustrated with this terrible product")
        self.assertEqual(decision["agent"], "support")
        self.assertEqual(decision["sentiment_detected"], "very negative")

if __name__ == "__main__":
    unittest.main()
