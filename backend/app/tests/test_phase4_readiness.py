from __future__ import annotations

import unittest
from unittest.mock import patch

from app.services.evaluation import phase4_readiness


class Phase4ReadinessTests(unittest.TestCase):
    def test_report_is_ready_only_when_every_dependency_is_ready(self):
        ready = {
            "status": "connected",
            "ready": True,
        }
        with (
            patch.object(phase4_readiness, "_check_database", return_value=ready),
            patch.object(phase4_readiness, "_check_qdrant", return_value=ready),
            patch.object(phase4_readiness, "_check_neo4j", return_value=ready),
            patch.object(phase4_readiness, "_check_llm_provider", return_value=ready),
            patch.object(phase4_readiness, "_check_embedding_provider", return_value=ready),
        ):
            report = phase4_readiness.run_phase4_readiness()
        self.assertTrue(report["ready"])
        self.assertEqual(report["blocked_checks"], [])
        self.assertTrue(report["safety"]["read_only"])
        self.assertFalse(report["safety"]["secrets_emitted"])

    def test_one_blocked_service_keeps_overall_readiness_false(self):
        ready = {"status": "connected", "ready": True}
        blocked = {"status": "unreachable", "ready": False}
        with (
            patch.object(phase4_readiness, "_check_database", return_value=ready),
            patch.object(phase4_readiness, "_check_qdrant", return_value=ready),
            patch.object(phase4_readiness, "_check_neo4j", return_value=blocked),
            patch.object(phase4_readiness, "_check_llm_provider", return_value=ready),
            patch.object(phase4_readiness, "_check_embedding_provider", return_value=ready),
        ):
            report = phase4_readiness.run_phase4_readiness()
        self.assertFalse(report["ready"])
        self.assertEqual(report["blocked_checks"], ["neo4j"])

    def test_exception_is_sanitized_and_other_checks_continue(self):
        ready = {"status": "connected", "ready": True}
        with (
            patch.object(phase4_readiness, "_check_database", side_effect=RuntimeError("sensitive-url")),
            patch.object(phase4_readiness, "_check_qdrant", return_value=ready),
            patch.object(phase4_readiness, "_check_neo4j", return_value=ready),
            patch.object(phase4_readiness, "_check_llm_provider", return_value=ready),
            patch.object(phase4_readiness, "_check_embedding_provider", return_value=ready),
        ):
            report = phase4_readiness.run_phase4_readiness()
        self.assertFalse(report["ready"])
        self.assertEqual(report["checks"]["database"]["error_type"], "RuntimeError")
        self.assertNotIn("sensitive-url", json.dumps(report))


if __name__ == "__main__":
    import json
    unittest.main()
