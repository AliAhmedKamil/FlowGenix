from metrics_engine import get_metrics
from ai_engine import get_ai_analysis

def generate_report_from_csv(file_path: str) -> dict:
    """
    Main Orchestrator.
    Transforms CSV -> Metrics -> AI Intelligence -> Final Report.
    """
    try:
        # Phase 1: Metric Calculation
        metrics = get_metrics(file_path)
        
        # Phase 2: AI Intelligence
        ai_analysis = get_ai_analysis(metrics)
        
        # Phase 3: Final Assembly
        report = {
            "metrics": metrics,
            "summary": ai_analysis.get("executive_summary", ""),
            "insights": ai_analysis.get("key_insights", []),
            "recommendations": ai_analysis.get("recommendations", [])
        }
        
        return report

    except Exception as e:
        return {
            "error": str(e),
            "metrics": None,
            "summary": None,
            "recommendations": []
        }
