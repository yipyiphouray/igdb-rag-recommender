from __future__ import annotations

import argparse
import contextlib
import io
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


DEFAULT_QUERY_PATH = ROOT_DIR / "tests" / "rag_golden_queries.json"
DEFAULT_REPORT_PATH = ROOT_DIR / "docs" / "report" / "rag_retrieval_quality_findings.md"


@dataclass(frozen=True)
class WeightProfile:
    name: str
    semantic_weight: float
    lexical_weight: float


WEIGHT_PROFILES = [
    WeightProfile("semantic_90_lexical_10", 0.9, 0.1),
    WeightProfile("semantic_80_lexical_20", 0.8, 0.2),
    WeightProfile("semantic_70_lexical_30", 0.7, 0.3),
]


def _safe_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return ", ".join(str(item) for item in value if str(item).strip())
    return str(value)


def _result_blob(result: dict[str, Any]) -> str:
    fields = [
        "name",
        "platforms",
        "genres",
        "themes",
        "developers",
        "summary",
        "storyline",
        "rating_band",
    ]
    return " ".join(_safe_text(result.get(field)) for field in fields).lower()


def _platform_blob(result: dict[str, Any]) -> str:
    return _safe_text(result.get("platforms")).lower()


def _contains_any(text: str, terms: list[str]) -> bool:
    if not terms:
        return True
    lowered = text.lower()
    return any(str(term).lower() in lowered for term in terms)


def _contains_none(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return not any(str(term).lower() in lowered for term in terms)


def _excludes_result_names(results: list[dict[str, Any]], names: list[str]) -> bool:
    if not names:
        return True

    result_names = {
        _safe_text(result.get("name")).strip().lower()
        for result in results
        if _safe_text(result.get("name")).strip()
    }
    excluded_names = {str(name).strip().lower() for name in names if str(name).strip()}
    return not result_names.intersection(excluded_names)


def _format_score(value: object) -> str:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return ""
    return f"{parsed:.3f}"


def _load_queries(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError(f"Expected a list of golden queries in {path}")
    return data


def _evaluate_one_query(
    agent: Any,
    query_spec: dict[str, Any],
    profile: WeightProfile,
    top_k: int,
) -> dict[str, Any]:
    query = str(query_spec.get("query", "")).strip()
    trace = io.StringIO()

    try:
        with contextlib.redirect_stdout(trace):
            results = agent.search(
                query=query,
                top_n=top_k,
                semantic_weight=profile.semantic_weight,
                lexical_weight=profile.lexical_weight,
                debug_scores=False,
            )
    except Exception as error:
        return {
            "id": query_spec.get("id", query),
            "query": query,
            "profile": profile.name,
            "passed": False,
            "error": f"{type(error).__name__}: {error}",
            "results": [],
            "trace": trace.getvalue(),
            "checks": {
                "expected_terms": False,
                "platform": False,
                "avoid_terms": False,
                "excluded_names": False,
            },
        }

    expected_terms = list(query_spec.get("expected_terms_any") or [])
    expected_platforms = list(query_spec.get("expected_platforms_any") or [])
    avoid_terms = list(query_spec.get("avoid_terms_any") or [])
    excluded_result_names = list(query_spec.get("excluded_result_names") or [])

    combined_blob = " ".join(_result_blob(result) for result in results)
    platform_blob = " ".join(_platform_blob(result) for result in results)

    expected_terms_pass = _contains_any(combined_blob, expected_terms)
    platform_pass = _contains_any(platform_blob, expected_platforms)
    avoid_pass = _contains_none(combined_blob, avoid_terms)
    excluded_names_pass = _excludes_result_names(results, excluded_result_names)
    passed = bool(results) and expected_terms_pass and platform_pass and avoid_pass and excluded_names_pass

    return {
        "id": query_spec.get("id", query),
        "query": query,
        "profile": profile.name,
        "passed": passed,
        "error": "",
        "results": results,
        "trace": trace.getvalue(),
        "checks": {
            "expected_terms": expected_terms_pass,
            "platform": platform_pass,
            "avoid_terms": avoid_pass,
            "excluded_names": excluded_names_pass,
        },
    }


def _evaluate_profile(
    agent: Any,
    queries: list[dict[str, Any]],
    profile: WeightProfile,
    top_k: int,
) -> dict[str, Any]:
    query_results = [
        _evaluate_one_query(agent=agent, query_spec=query, profile=profile, top_k=top_k)
        for query in queries
    ]
    passed = sum(1 for item in query_results if item["passed"])
    total = len(query_results)
    return {
        "profile": profile,
        "query_results": query_results,
        "passed": passed,
        "total": total,
        "pass_rate": passed / total if total else 0.0,
        "errors": sum(1 for item in query_results if item.get("error")),
    }


def _render_result_rows(results: list[dict[str, Any]]) -> list[str]:
    rows = [
        "| Rank | Game | Year | Platforms | Genres | Themes | Score | Semantic | Lexical |",
        "|---:|---|---:|---|---|---|---:|---:|---:|",
    ]
    for rank, result in enumerate(results[:5], start=1):
        rows.append(
            "| "
            + " | ".join(
                [
                    str(rank),
                    _safe_text(result.get("name")).replace("|", "/"),
                    _safe_text(result.get("release_year")).replace("|", "/"),
                    _safe_text(result.get("platforms")).replace("|", "/")[:100],
                    _safe_text(result.get("genres")).replace("|", "/")[:80],
                    _safe_text(result.get("themes")).replace("|", "/")[:80],
                    _format_score(result.get("primary_rank_score")),
                    _format_score(result.get("normalized_vec")),
                    _format_score(result.get("normalized_bm25")),
                ]
            )
            + " |"
        )
    return rows


def _check_icon(value: bool) -> str:
    return "Pass" if value else "Review"


def _select_best_profile(profile_reports: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not profile_reports:
        return None
    return sorted(
        profile_reports,
        key=lambda item: (item["pass_rate"], -item["errors"], item["passed"]),
        reverse=True,
    )[0]


def _render_report(
    *,
    query_path: Path,
    report_path: Path,
    top_k: int,
    backend: str,
    profile_reports: list[dict[str, Any]],
    run_error: str = "",
) -> str:
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# RAG Retrieval Quality Findings",
        "",
        f"Generated at: `{generated_at}`",
        "",
        "## Purpose",
        "",
        "This report evaluates whether the RAG retrieval engine returns games that match expected user intent across a small golden-query set.",
        "",
        "This is a relevance smoke test, not a perfect objective benchmark. It checks whether top retrieved games contain expected concepts, respect platform constraints when specified, and avoid obvious mismatches.",
        "",
        "## Inputs",
        "",
        f"- Golden-query file: `{query_path.as_posix()}`",
        f"- Top-k reviewed per query: `{top_k}`",
        f"- Backend: `{backend}`",
        "- Engine: `src.rag_engine.RAGAgent` when backend is `chroma`; `src.lightweight_rag_engine.LightweightRAGAgent` when backend is `lightweight`",
        "- Vector artifacts: `data/vector_store/` for Chroma; `data/rag/lightweight/` for lightweight NumPy retrieval",
        "",
    ]

    if run_error:
        lines.extend(
            [
                "## Execution Status",
                "",
                "The evaluation could not complete.",
                "",
                f"```text\n{run_error}\n```",
                "",
            ]
        )
        return "\n".join(lines)

    best = _select_best_profile(profile_reports)

    lines.extend(
        [
            "## Weight Profile Summary",
            "",
            "| Profile | Semantic Weight | Lexical Weight | Passed | Total | Pass Rate | Runtime Errors |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for report in profile_reports:
        profile = report["profile"]
        lines.append(
            f"| `{profile.name}` | {profile.semantic_weight:.2f} | {profile.lexical_weight:.2f} | "
            f"{report['passed']} | {report['total']} | {report['pass_rate']:.1%} | {report['errors']} |"
        )

    if best:
        profile = best["profile"]
        lines.extend(
            [
                "",
                "## Current Recommendation",
                "",
                f"The strongest evaluated profile was `{profile.name}` with a pass rate of `{best['pass_rate']:.1%}`.",
                "",
                "Use this as a tuning signal, not a final truth. Review the failed queries manually before changing production weights.",
                "",
            ]
        )

    for report in profile_reports:
        profile = report["profile"]
        lines.extend(
            [
                "",
                f"## Detailed Results: `{profile.name}`",
                "",
            ]
        )
        for item in report["query_results"]:
            checks = item["checks"]
            lines.extend(
                [
                    f"### {item['id']}",
                    "",
                    f"Query: `{item['query']}`",
                    "",
                    f"Overall: **{_check_icon(item['passed'])}**",
                    "",
                    "| Check | Result |",
                    "|---|---|",
                    f"| Expected terms present | {_check_icon(checks['expected_terms'])} |",
                    f"| Platform constraint | {_check_icon(checks['platform'])} |",
                    f"| Avoid terms absent | {_check_icon(checks['avoid_terms'])} |",
                    f"| Seed/excluded titles absent | {_check_icon(checks['excluded_names'])} |",
                    "",
                ]
            )
            if item.get("error"):
                lines.extend(["Runtime error:", "", f"```text\n{item['error']}\n```", ""])
                continue
            lines.extend(_render_result_rows(item["results"]))
            lines.append("")

    lines.extend(
        [
            "## Interpretation Rules",
            "",
            "- A `Pass` means the top retrieved set contains at least one expected concept and did not violate the explicit avoid checks.",
            "- A `Review` does not automatically mean the engine is wrong. It means the result should be manually inspected.",
            "- Platform failures are more serious than broad concept failures because platform intent is usually a hard user constraint.",
            "- Seed-title failures mean the engine returned a game that the user provided as a reference point instead of an alternative.",
            "- If 0.7/0.3 or 0.8/0.2 beats 0.9/0.1, lexical evidence is probably underweighted.",
            "",
            "## Recommended Next Actions",
            "",
            "1. Manually inspect all `Review` queries.",
            "2. Confirm whether failed results are truly bad or only missing expected vocabulary.",
            "3. Tune semantic/lexical weights only after reviewing the detailed result tables.",
            "4. Expand the golden-query set with real prompts from user testing.",
            "5. Rerun this report after every vector-store rebuild or major retrieval change.",
        ]
    )

    return "\n".join(lines).strip() + "\n"


def _build_agent(backend: str) -> Any:
    normalized_backend = str(backend or "").strip().lower()
    if normalized_backend == "lightweight":
        from src.lightweight_rag_engine import LightweightRAGAgent

        return LightweightRAGAgent()
    if normalized_backend == "chroma":
        from src.rag_engine import RAGAgent

        return RAGAgent()
    raise ValueError(f"Unsupported RAG backend: {backend}")


def run_evaluation(query_path: Path, report_path: Path, top_k: int, backend: str) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        queries = _load_queries(query_path)
        agent = _build_agent(backend)
        profile_reports = [
            _evaluate_profile(agent=agent, queries=queries, profile=profile, top_k=top_k)
            for profile in WEIGHT_PROFILES
        ]
        report = _render_report(
            query_path=query_path,
            report_path=report_path,
            top_k=top_k,
            backend=backend,
            profile_reports=profile_reports,
        )
    except Exception as error:
        report = _render_report(
            query_path=query_path,
            report_path=report_path,
            top_k=top_k,
            backend=backend,
            profile_reports=[],
            run_error=f"{type(error).__name__}: {error}",
        )

    report_path.write_text(report, encoding="utf-8")
    print(f"RAG retrieval quality report written to: {report_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate RAG retrieval quality against golden queries.")
    parser.add_argument("--queries", type=Path, default=DEFAULT_QUERY_PATH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--backend", choices=["lightweight", "chroma"], default="lightweight")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_evaluation(query_path=args.queries, report_path=args.report, top_k=args.top_k, backend=args.backend)
