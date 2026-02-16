"""품질 Agent 노드 함수들"""

import json
import logging
from typing import Dict, Any, List

from langchain_core.messages import HumanMessage, SystemMessage
from agents.base import create_llm
from config import (
    AGENT_LLM_TEMPERATURE, QUALITY_Z_SCORE_THRESHOLD,
    QUALITY_MAX_ANOMALIES_TO_INTERPRET,
)

logger = logging.getLogger(__name__)


def validate_files_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """데이터 파일 존재 여부를 확인합니다."""
    from agents.tools.quality_tools import check_file_existence
    result = check_file_existence.invoke({})
    return {"file_check": result}


def validate_schema_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """데이터 스키마를 검증합니다."""
    from agents.tools.quality_tools import check_data_structure
    result = check_data_structure.invoke({})
    return {"schema_validation": result}


def check_ranges_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """데이터 품질 (범위, 중복, 일관성)을 검사합니다."""
    from agents.tools.quality_tools import check_data_quality
    result = check_data_quality.invoke({})

    duplicate_check = {}
    range_violations = {}
    if isinstance(result, dict):
        for key in ["batter", "pitcher"]:
            if key in result:
                entry = result[key]
                duplicate_check[key] = entry.get("duplicates", 0) if isinstance(entry, dict) else 0
        range_violations = result

    return {
        "range_violations": range_violations,
        "duplicate_check": duplicate_check,
    }


def detect_anomalies_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """통계적 이상치를 탐지합니다."""
    from agents.tools.quality_tools import detect_statistical_anomalies

    all_anomalies = []
    for player_type in ["batter", "pitcher"]:
        anomalies = detect_statistical_anomalies.invoke({
            "player_type": player_type,
            "z_threshold": QUALITY_Z_SCORE_THRESHOLD,
        })
        if anomalies and not (isinstance(anomalies[0], dict) and "error" in anomalies[0]):
            all_anomalies.extend(anomalies)

    return {"anomalies": all_anomalies}


def interpret_anomalies_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """LLM을 사용하여 이상치를 해석합니다."""
    anomalies = state.get("anomalies", [])
    lang = state.get("lang", "ko")

    if not anomalies:
        return {"anomaly_interpretations": []}

    llm = create_llm(temperature=AGENT_LLM_TEMPERATURE, max_tokens=4000)
    if llm is None:
        return {"anomaly_interpretations": [
            {"anomaly": a, "interpretation": "LLM 미사용", "is_real_record": None}
            for a in anomalies[:QUALITY_MAX_ANOMALIES_TO_INTERPRET]
        ]}

    lang_map = {"ko": "한국어", "en": "English", "ja": "日本語"}
    language = lang_map.get(lang, "한국어")

    # 상위 이상치만 해석
    top_anomalies = anomalies[:QUALITY_MAX_ANOMALIES_TO_INTERPRET]

    response = llm.invoke([
        SystemMessage(content=f"""You are an MLB data quality analyst. Respond in {language}.
For each anomaly, determine if it's a real baseball record or likely a data error.
Consider that some extreme values are legitimate (e.g., a player with very few at-bats can have unusual averages).
Return a JSON array of objects with: player_name, metric, verdict ("real_record" or "likely_error"), reasoning."""),
        HumanMessage(content=f"이상치 목록:\n{json.dumps(top_anomalies, ensure_ascii=False)}"),
    ])

    try:
        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        interpretations = json.loads(raw)
        return {"anomaly_interpretations": interpretations}
    except Exception:
        return {"anomaly_interpretations": [
            {"raw_response": response.content}
        ]}


def assemble_report_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """품질 검증 결과를 종합 보고서로 조립합니다."""
    lang = state.get("lang", "ko")
    file_check = state.get("file_check", {})
    schema = state.get("schema_validation", {})
    anomalies = state.get("anomalies", [])
    interpretations = state.get("anomaly_interpretations", [])

    # 품질 점수 계산
    score = 100.0
    if not all(file_check.values()):
        score -= 30
    if anomalies:
        score -= min(len(anomalies) * 2, 30)

    dup = state.get("duplicate_check", {})
    total_dups = sum(v for v in dup.values() if isinstance(v, (int, float)))
    if total_dups > 0:
        score -= min(total_dups * 5, 20)

    score = max(score, 0)

    # 보고서 생성
    report_lines = [
        "# 데이터 품질 보고서\n" if lang == "ko"
        else "# Data Quality Report\n" if lang == "en"
        else "# データ品質レポート\n",
        f"## 품질 점수: {score:.0f}/100\n",
        "### 파일 상태",
        f"- 타자 데이터: {'✅' if file_check.get('batter', False) else '❌'}",
        f"- 투수 데이터: {'✅' if file_check.get('pitcher', False) else '❌'}",
        "",
    ]

    if schema:
        report_lines.append("### 데이터 구조")
        report_lines.append(f"```\n{json.dumps(schema, ensure_ascii=False, indent=2, default=str)[:500]}\n```\n")

    if anomalies:
        report_lines.append(f"### 이상치 탐지 ({len(anomalies)}건)")
        for a in anomalies[:10]:
            report_lines.append(
                f"- {a.get('player_name', '?')} ({a.get('season', '?')}): "
                f"{a.get('metric', '?')} = {a.get('value', '?')} (z={a.get('z_score', '?')})"
            )

    if interpretations:
        report_lines.append("\n### AI 이상치 해석")
        for interp in interpretations[:10]:
            if isinstance(interp, dict) and "verdict" in interp:
                emoji = "✅" if interp.get("verdict") == "real_record" else "⚠️"
                report_lines.append(
                    f"- {emoji} {interp.get('player_name', '?')}: "
                    f"{interp.get('reasoning', '')[:100]}"
                )

    recommendations = []
    if total_dups > 0:
        recommendations.append("중복 레코드를 제거하세요")
    if anomalies:
        error_count = sum(
            1 for i in interpretations
            if isinstance(i, dict) and i.get("verdict") == "likely_error"
        )
        if error_count > 0:
            recommendations.append(f"데이터 오류로 판단된 {error_count}건을 확인하세요")
    if not recommendations:
        recommendations.append("데이터 품질이 양호합니다")

    report_lines.append("\n### 권장 사항")
    for r in recommendations:
        report_lines.append(f"- {r}")

    return {
        "quality_score": score,
        "report_markdown": "\n".join(report_lines),
        "recommendations": recommendations,
    }
