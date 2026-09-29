"""
LeadFlow — Agentic Analytics Pipeline
Three-agent architecture: Analytics → Insight → Action
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Optional

from app.analytics_engine.metrics import MetricsCalculator, PipelineMetrics
from app.ai.gemini_service import GeminiService
from app.ai.prompts import (
    INSIGHT_GENERATION_PROMPT,
    ACTION_RECOMMENDATION_PROMPT,
    QUERY_RESPONSE_PROMPT,
)
from pymongo.database import Database

logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    """Result from a single agent run."""
    agent_name: str
    status: str  # "completed" | "failed" | "skipped"
    duration_seconds: float = 0.0
    summary: str = ""
    data: Any = None
    error: Optional[str] = None


@dataclass
class AnalyticsReport:
    """Full agentic analytics report."""
    metrics: Optional[PipelineMetrics] = None
    patterns: list[dict[str, Any]] = field(default_factory=list)
    recommendations: list[dict[str, Any]] = field(default_factory=list)
    agent_results: list[AgentResult] = field(default_factory=list)
    total_duration: float = 0.0
    generated_at: datetime = field(default_factory=datetime.utcnow)


class AnalyticsAgent:
    """
    Agent 1: Computes deterministic metrics from MongoDB.
    Does NOT call Gemini.
    """

    def __init__(self, db: Database) -> None:
        self.calculator = MetricsCalculator(db)

    def run(self, callback: Optional[Callable] = None) -> AgentResult:
        start = time.time()
        if callback:
            callback("Analytics Agent: Computing metrics...")
        try:
            metrics = self.calculator.compute_all()
            duration = time.time() - start
            return AgentResult(
                agent_name="Analytics Agent",
                status="completed",
                duration_seconds=round(duration, 2),
                summary=f"{metrics.total_leads} leads analyzed, {metrics.analyzed_calls} calls processed",
                data=metrics,
            )
        except Exception as e:
            return AgentResult(
                agent_name="Analytics Agent",
                status="failed",
                duration_seconds=time.time() - start,
                error=str(e),
            )


class InsightAgent:
    """
    Agent 2: Uses Gemini to identify patterns from verified metrics.
    Only called with pre-computed data — never raw queries.
    """

    def __init__(self, gemini: GeminiService, db: Database) -> None:
        self.gemini = gemini
        self.db = db

    def run(
        self,
        metrics: PipelineMetrics,
        callback: Optional[Callable] = None,
    ) -> AgentResult:
        start = time.time()
        if callback:
            callback("Insight Agent: Identifying patterns...")

        try:
            # Build metrics summary for Gemini context
            metrics_dict = {
                "total_leads": metrics.total_leads,
                "leads_by_status": metrics.leads_by_status,
                "avg_lead_score": metrics.avg_lead_score,
                "high_priority_count": metrics.high_priority_count,
                "conversion_rate": metrics.conversion_rate,
                "sentiment_distribution": metrics.sentiment_distribution,
                "intent_distribution": metrics.intent_distribution,
                "overdue_followups": metrics.overdue_followups,
                "followup_completion_rate": metrics.followup_completion_rate,
                "score_high": metrics.score_high,
                "score_medium": metrics.score_medium,
                "score_low": metrics.score_low,
            }

            # Get recent call summaries for context
            recent = list(self.db.call_analyses.find(
                {}, {"analysis.summary": 1, "analysis.objections": 1, "analysis.intent": 1}
            ).sort("created_at", -1).limit(10))

            call_data = []
            for doc in recent:
                a = doc.get("analysis", {})
                call_data.append({
                    "summary": a.get("summary", ""),
                    "intent": a.get("intent", ""),
                    "objections": a.get("objections", []),
                })

            prompt = INSIGHT_GENERATION_PROMPT.format(
                metrics=json.dumps(metrics_dict, indent=2),
                call_data=json.dumps(call_data, indent=2),
            )

            result = self.gemini.generate_json(prompt)
            patterns = result.get("patterns", [])

            duration = time.time() - start
            return AgentResult(
                agent_name="Insight Agent",
                status="completed",
                duration_seconds=round(duration, 2),
                summary=f"{len(patterns)} patterns identified",
                data=patterns,
            )
        except Exception as e:
            logger.error(f"Insight Agent error: {e}")
            return AgentResult(
                agent_name="Insight Agent",
                status="failed",
                duration_seconds=time.time() - start,
                error=str(e),
            )


class ActionAgent:
    """
    Agent 3: Generates manager-facing recommendations.
    Recommendations only — does not autonomously execute actions.
    """

    def __init__(self, gemini: GeminiService) -> None:
        self.gemini = gemini

    def run(
        self,
        metrics: PipelineMetrics,
        patterns: list[dict],
        callback: Optional[Callable] = None,
    ) -> AgentResult:
        start = time.time()
        if callback:
            callback("Action Agent: Generating recommendations...")

        try:
            metrics_dict = {
                "total_leads": metrics.total_leads,
                "high_priority_count": metrics.high_priority_count,
                "overdue_followups": metrics.overdue_followups,
                "conversion_rate": metrics.conversion_rate,
                "avg_lead_score": metrics.avg_lead_score,
                "followup_completion_rate": metrics.followup_completion_rate,
            }

            prompt = ACTION_RECOMMENDATION_PROMPT.format(
                patterns=json.dumps(patterns, indent=2),
                metrics=json.dumps(metrics_dict, indent=2),
            )

            result = self.gemini.generate_json(prompt)
            recommendations = result.get("recommendations", [])

            duration = time.time() - start
            return AgentResult(
                agent_name="Action Agent",
                status="completed",
                duration_seconds=round(duration, 2),
                summary=f"{len(recommendations)} recommendations generated",
                data=recommendations,
            )
        except Exception as e:
            logger.error(f"Action Agent error: {e}")
            return AgentResult(
                agent_name="Action Agent",
                status="failed",
                duration_seconds=time.time() - start,
                error=str(e),
            )


class AnalyticsOrchestrator:
    """
    Orchestrates the three-agent pipeline.
    Analytics Agent (no AI) → Insight Agent (AI) → Action Agent (AI)
    """

    def __init__(self, db: Database, gemini: GeminiService) -> None:
        self.analytics_agent = AnalyticsAgent(db)
        self.insight_agent = InsightAgent(gemini, db)
        self.action_agent = ActionAgent(gemini)
        self.gemini = gemini
        self.db = db

    def run_full_pipeline(
        self,
        callback: Optional[Callable[[str, str], None]] = None,
    ) -> AnalyticsReport:
        """
        Run all three agents in sequence.
        callback(agent_name, status_message) for progress updates.
        """
        report = AnalyticsReport()
        pipeline_start = time.time()

        def _cb(msg: str):
            if callback:
                callback("pipeline", msg)
            logger.info(f"[Orchestrator] {msg}")

        # Agent 1
        _cb("Starting Analytics Agent...")
        result1 = self.analytics_agent.run(_cb)
        report.agent_results.append(result1)

        if result1.status != "completed" or result1.data is None:
            report.total_duration = time.time() - pipeline_start
            return report

        metrics: PipelineMetrics = result1.data
        report.metrics = metrics

        # Agent 2
        _cb("Starting Insight Agent...")
        result2 = self.insight_agent.run(metrics, _cb)
        report.agent_results.append(result2)
        patterns = result2.data or []
        report.patterns = patterns

        # Agent 3
        _cb("Starting Action Agent...")
        result3 = self.action_agent.run(metrics, patterns, _cb)
        report.agent_results.append(result3)
        report.recommendations = result3.data or []

        report.total_duration = round(time.time() - pipeline_start, 2)
        _cb(f"Pipeline completed in {report.total_duration}s")

        return report

    def answer_query(self, question: str) -> str:
        """
        Answer a user query using CRM data + Gemini.
        Data is fetched from MongoDB first, then Gemini interprets.
        """
        try:
            metrics = MetricsCalculator(self.db).compute_all()
            metrics_dict = {
                "total_leads": metrics.total_leads,
                "leads_by_status": metrics.leads_by_status,
                "avg_lead_score": metrics.avg_lead_score,
                "high_priority_count": metrics.high_priority_count,
                "conversion_rate": metrics.conversion_rate,
                "sentiment_distribution": metrics.sentiment_distribution,
                "overdue_followups": metrics.overdue_followups,
                "common_objections": metrics.common_objections,
                "intent_distribution": metrics.intent_distribution,
            }

            # Fetch relevant context
            high_score_no_followup = self.db.leads.count_documents({
                "lead_score": {"$gte": 70},
                "next_followup": None,
            })

            context = {
                "high_score_leads_without_followup": high_score_no_followup,
                "recent_objections": metrics.common_objections[:5],
                "executive_performance": metrics.executive_performance[:5],
            }

            prompt = QUERY_RESPONSE_PROMPT.format(
                metrics=json.dumps(metrics_dict, indent=2),
                context=json.dumps(context, indent=2),
                question=question,
            )

            return self.gemini.generate(prompt)
        except Exception as e:
            logger.error(f"Query answer failed: {e}")
            return f"Unable to answer query at this time. Error: {e}"
