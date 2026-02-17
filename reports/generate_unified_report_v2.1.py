#!/usr/bin/env python3
"""STALWART Unified Report v2.1 - Operational Reporting Engineering"""

from pathlib import Path
from datetime import datetime, timedelta
import random

now = datetime.now()
reports_dir = Path("reports/unified")
reports_dir.mkdir(parents=True, exist_ok=True)

# بيانات الجسور مع إضافة الاتجاهات الزمنية
bridges_data = [
    {
        "id": "BR-001",
        "name": "North Bridge",
        "location": "New York, NY",
        "type": "Suspension",
        "age": 45,
        "health": "91%",
        "status": "SAFE",
        "risk": "LOW",
        "data_status": "OK",
        "health_confidence": "HIGH",
        "afc": "0.32", "afc_trend": "→",
        "alsa": "0.45", "alsa_trend": "→",
        "cpii": "0.94", "cpii_trend": "→",
        "ffd": "1.2", "ffd_trend": "→",
        "lts": "12.5", "lts_trend": "→",
        "ccf": "28.3", "ccf_trend": "↗",
        "tvr": "0.92", "tvr_trend": "→",
        "bd": "5.2", "bd_trend": "→",
        "sed": "32.1", "sed_trend": "↗",
        "alerts": "None",
        "alerts_cause": "",
        "reco": "Routine monitoring",
        "reco_window": "30 days",
        "reco_priority": "Low",
        "top_params": ["CCF", "SED"]
    },
    {
        "id": "BR-002",
        "name": "South Bridge",
        "location": "Los Angeles, CA",
        "type": "Cable-stayed",
        "age": 28,
        "health": "98%",
        "status": "SAFE",
        "risk": "LOW",
        "data_status": "OK",
        "health_confidence": "HIGH",
        "afc": "0.21", "afc_trend": "→",
        "alsa": "0.38", "alsa_trend": "→",
        "cpii": "0.97", "cpii_trend": "→",
        "ffd": "0.8", "ffd_trend": "→",
        "lts": "8.2", "lts_trend": "→",
        "ccf": "18.5", "ccf_trend": "→",
        "tvr": "0.95", "tvr_trend": "→",
        "bd": "3.8", "bd_trend": "→",
        "sed": "25.4", "sed_trend": "→",
        "alerts": "None",
        "alerts_cause": "",
        "reco": "Continue routine",
        "reco_window": "60 days",
        "reco_priority": "Low",
        "top_params": ["All stable"]
    },
    {
        "id": "BR-003",
        "name": "East Bridge",
        "location": "Chicago, IL",
        "type": "Arch",
        "age": 62,
        "health": "99%",
        "status": "SAFE",
        "risk": "LOW",
        "data_status": "OK",
        "health_confidence": "HIGH",
        "afc": "0.18", "afc_trend": "→",
        "alsa": "0.29", "alsa_trend": "→",
        "cpii": "0.98", "cpii_trend": "→",
        "ffd": "0.5", "ffd_trend": "→",
        "lts": "6.8", "lts_trend": "→",
        "ccf": "15.2", "ccf_trend": "→",
        "tvr": "0.97", "tvr_trend": "→",
        "bd": "2.9", "bd_trend": "→",
        "sed": "22.8", "sed_trend": "→",
        "alerts": "None",
        "alerts_cause": "",
        "reco": "Excellent",
        "reco_window": "90 days",
        "reco_priority": "Low",
        "top_params": ["All stable"]
    },
    {
        "id": "BR-004",
        "name": "West Bridge",
        "location": "Seattle, WA",
        "type": "Steel girder",
        "age": 38,
        "health": "96%",
        "status": "WARNING",
        "risk": "MEDIUM",
        "data_status": "OK",
        "health_confidence": "MEDIUM",
        "afc": "0.28", "afc_trend": "→",
        "alsa": "0.52", "alsa_trend": "↗ (+6.4%)",
        "cpii": "0.92", "cpii_trend": "↘",
        "ffd": "1.8", "ffd_trend": "↗",
        "lts": "15.3", "lts_trend": "→",
        "ccf": "32.7", "ccf_trend": "↗ (+3.2%)",
        "tvr": "0.89", "tvr_trend": "↘",
        "bd": "6.5", "bd_trend": "↗",
        "sed": "38.9", "sed_trend": "↗ (+4.1%)",
        "alerts": "⚠️ ALSA increasing | CCF rising",
        "alerts_cause": "Repetitive axle loading, possible corrosion acceleration",
        "reco": "Monitor strain gauge STR-004, schedule bearing inspection",
        "reco_window": "14 days",
        "reco_priority": "Medium",
        "top_params": ["ALSA (+6.4%)", "SED (+4.1%)", "CCF (+3.2%)"]
    },
    {
        "id": "TEST-001",
        "name": "Test Bridge",
        "location": "Research Facility",
        "type": "Suspension",
        "age": 25,
        "health": "94.7%",
        "status": "SAFE",
        "risk": "LOW",
        "data_status": "DEGRADED",
        "health_confidence": "LOW",
        "afc": "0.42", "afc_trend": "→",
        "alsa": "0.58", "alsa_trend": "↗",
        "cpii": "0.91", "cpii_trend": "→",
        "ffd": "2.3", "ffd_trend": "→",
        "lts": "18.5", "lts_trend": "→",
        "ccf": "34.2", "ccf_trend": "↗",
        "tvr": "0.88", "tvr_trend": "→",
        "bd": "8.4", "bd_trend": "→",
        "sed": "42.3", "sed_trend": "↗",
        "alerts": "None",
        "alerts_cause": "Sensor calibration drift detected - Data confidence reduced",
        "reco": "Check calibration of strain gauges, schedule sensor maintenance",
        "reco_window": "7 days",
        "reco_priority": "High",
        "top_params": ["ALSA", "SED", "CCF"]
    }
]

UNIFIED_TEMPLATE_V2_1 = """================================================================================
                    STALWART BRIDGE MONITORING SYSTEM
                 UNIFIED OPERATIONAL REPORT v2.1
================================================================================
Report Date    : {date}
Generated      : {timestamp}
Report Classification: OPERATIONAL / DECISION-SUPPORT
Total Bridges  : {total_bridges}
================================================================================

SYSTEM OVERVIEW
================================================================================
• Overall system stability: {system_stability}
• Structural risk assessment: {structural_risk}
• Data integrity status: {data_integrity}
• Bridges under observation: {observation_count}
• No evacuation conditions identified
================================================================================

SUMMARY TABLE
================================================================================
ID       | Name           | Health | Status  | Risk   | Data    | Confid | Key Alert
---------|----------------|--------|---------|--------|---------|--------|------------------
{table_rows}

================================================================================
DETAILED BRIDGE REPORTS
================================================================================
{detailed_reports}

================================================================================
STATISTICS & TRENDS
================================================================================
Total Bridges Monitored : {total_bridges}
Bridges in SAFE status  : {safe_count}
Bridges in WARNING status: {warning_count}
Bridges in CRITICAL status: {critical_count}

Average Health Score    : {avg_health}%
Data Status OK          : {data_ok_count}
Data Status DEGRADED    : {data_degraded_count}

================================================================================
TOP CONTRIBUTING PARAMETERS (By Bridge)
================================================================================
{top_parameters}

================================================================================
RECOMMENDATIONS SUMMARY (Prioritized)
================================================================================
{recommendations}

================================================================================
End of Report - STALWART v2.1 (Operational Edition)
Contact: gitdeeper@gmail.com
Report Classification: Decision-Support / Internal Use Only
================================================================================
"""

def generate_table_row(bridge):
    """Generate a single row for the summary table."""
    name_short = bridge['name'][:12].ljust(12)
    alert_short = bridge['alerts'][:15] if bridge['alerts'] != "None" else "None"
    return f"{bridge['id']} | {name_short} | {bridge['health']} | {bridge['status']} | {bridge['risk']} | {bridge['data_status']} | {bridge['health_confidence']} | {alert_short}"

def generate_detailed_report(bridge):
    """Generate detailed report for a single bridge with trends."""
    trend_summary = f"""
TREND SUMMARY (7 days):
• ALSA: {bridge['alsa_trend']} {bridge.get('alsa', '')}
• SED:  {bridge['sed_trend']} {bridge.get('sed', '')}
• CCF:  {bridge['ccf_trend']} {bridge.get('ccf', '')}"""

    return f"""
BRIDGE: {bridge['id']} - {bridge['name']}
--------------------------------------------------------------------------------
Location          : {bridge['location']}
Type              : {bridge['type']}
Age               : {bridge['age']} years
Health            : {bridge['health']}
Status            : {bridge['status']}
Risk Level        : {bridge['risk']}
Data Status       : {bridge['data_status']}
Health Confidence : {bridge['health_confidence']}
{trend_summary}

NINE PARAMETERS (with trends):
--------------------------------------------------------------------------------
1. AFC (Aeroelastic Flutter)    : {bridge['afc']} {bridge['afc_trend']}
2. ALSA (Strain Accumulation)   : {bridge['alsa']} {bridge['alsa_trend']}
3. CPII (Cable Integrity)       : {bridge['cpii']} {bridge['cpii_trend']}
4. FFD (Frequency Drift)        : {bridge['ffd']}% {bridge['ffd_trend']}
5. LTS (Thermal Stress)         : {bridge['lts']}% {bridge['lts_trend']}
6. CCF (Corrosion)              : {bridge['ccf']}% {bridge['ccf_trend']}
7. TVR (Vibration)              : {bridge['tvr']} {bridge['tvr_trend']}
8. BD (Displacement)            : {bridge['bd']} mm {bridge['bd_trend']}
9. SED (Strain Energy)          : {bridge['sed']}% {bridge['sed_trend']}

TOP CONTRIBUTORS:
{', '.join(bridge['top_params'])}

ALERTS & CAUSAL ANALYSIS:
--------------------------------------------------------------------------------
{alerts_display(bridge)}

RECOMMENDATIONS:
--------------------------------------------------------------------------------
• {bridge['reco']}
  Action window: {bridge['reco_window']}
  Priority: {bridge['reco_priority']}
--------------------------------------------------------------------------------
"""

def alerts_display(bridge):
    """Format alerts with causal analysis."""
    if bridge['alerts'] == "None":
        return "No active alerts"
    return f"{bridge['alerts']}\nObserved trend: {bridge.get('alsa_trend', '')}\nLikely cause: {bridge['alerts_cause']}"

def generate_top_parameters(bridges):
    """Generate top contributing parameters summary."""
    lines = []
    for b in bridges:
        if b['top_params'] != ["All stable"]:
            lines.append(f"• {b['id']}: {', '.join(b['top_params'])}")
    return "\n".join(lines) if lines else "• All parameters within normal ranges"

def generate_recommendations_priority(bridges):
    """Generate prioritized recommendations."""
    # Sort by priority: High > Medium > Low
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    sorted_bridges = sorted(bridges, key=lambda x: priority_order.get(x['reco_priority'], 3))
    
    lines = []
    for b in sorted_bridges:
        if b['reco_priority'] != "Low" or b['alerts'] != "None":
            lines.append(f"[{b['reco_priority']}] {b['id']}: {b['reco']} (within {b['reco_window']})")
    
    # Add low priority at the end
    for b in bridges:
        if b['reco_priority'] == "Low" and b['alerts'] == "None":
            lines.append(f"[Low] {b['id']}: {b['reco']}")
    
    return "\n".join(lines)

# Generate report data
table_rows = []
detailed_reports = []
safe_count = 0
warning_count = 0
critical_count = 0
data_ok_count = 0
data_degraded_count = 0
health_sum = 0.0

for bridge in bridges_data:
    table_rows.append(generate_table_row(bridge))
    detailed_reports.append(generate_detailed_report(bridge))
    
    if bridge['status'] == "SAFE":
        safe_count += 1
    elif bridge['status'] == "WARNING":
        warning_count += 1
    elif bridge['status'] == "CRITICAL":
        critical_count += 1
    
    if bridge['data_status'] == "OK":
        data_ok_count += 1
    else:
        data_degraded_count += 1
    
    health_val = float(bridge['health'].replace('%', ''))
    health_sum += health_val

avg_health = health_sum / len(bridges_data)

# System overview determination
if warning_count == 0 and data_degraded_count == 0:
    system_stability = "NORMAL"
    structural_risk = "No critical risks detected"
    data_integrity = "FULL"
elif warning_count <= 1 and data_degraded_count <= 1:
    system_stability = "MONITOR"
    structural_risk = "Early-warning observation active"
    data_integrity = "PARTIAL"
else:
    system_stability = "CAUTION"
    structural_risk = "Multiple warnings detected"
    data_integrity = "DEGRADED"

# Create the final report
final_report = UNIFIED_TEMPLATE_V2_1.format(
    date=now.strftime('%Y-%m-%d'),
    timestamp=now.strftime('%Y-%m-%d %H:%M:%S'),
    total_bridges=len(bridges_data),
    system_stability=system_stability,
    structural_risk=structural_risk,
    data_integrity=data_integrity,
    observation_count=warning_count,
    table_rows="\n".join(table_rows),
    detailed_reports="".join(detailed_reports),
    safe_count=safe_count,
    warning_count=warning_count,
    critical_count=critical_count,
    avg_health=f"{avg_health:.1f}",
    data_ok_count=data_ok_count,
    data_degraded_count=data_degraded_count,
    top_parameters=generate_top_parameters(bridges_data),
    recommendations=generate_recommendations_priority(bridges_data)
)

# Save the unified report
report_file = reports_dir / f"STW-UNIFIED-{now.strftime('%Y%m%d')}-v2.1.txt"
with open(report_file, 'w', encoding='utf-8') as f:
    f.write(final_report)

print("=" * 80)
print("📊 STALWART UNIFIED REPORT v2.1 - OPERATIONAL EDITION")
print("=" * 80)
print(f"✅ Report generated: {report_file}")
print("\n📋 NEW FEATURES:")
print("   • SYSTEM OVERVIEW with stability assessment")
print("   • TREND SUMMARY for each bridge (7-day)")
print("   • DATA STATUS & HEALTH CONFIDENCE")
print("   • CAUSAL ANALYSIS for alerts")
print("   • TOP CONTRIBUTING PARAMETERS")
print("   • PRIORITIZED RECOMMENDATIONS")
print("=" * 80)

# Display executive summary
print("\n📋 EXECUTIVE SUMMARY:")
print("-" * 40)
print(f"System Stability: {system_stability}")
print(f"Bridges: {safe_count} SAFE, {warning_count} WARNING")
print(f"Data Integrity: {data_ok_count} OK, {data_degraded_count} DEGRADED")
print(f"Average Health: {avg_health:.1f}%")
print("=" * 80)
