#!/usr/bin/env python3
"""Generate TXT reports for all bridges (easy to read with naked eye)."""

from pathlib import Path
from datetime import datetime

bridges = ["BR-001", "BR-002", "BR-003", "BR-004", "TEST-001"]

now = datetime.now()
daily_dir = Path(f"reports/daily/{now.strftime('%Y-%m-%d')}")
daily_dir.mkdir(parents=True, exist_ok=True)

# قالب التقرير النصي - سهل القراءة
TXT_TEMPLATE = """===========================================
STALWART BRIDGE MONITORING SYSTEM
===========================================
DAILY REPORT - {date}
===========================================

BRIDGE INFORMATION
-------------------------------------------
Bridge ID      : {bridge}
Bridge Name    : {bridge_name}
Location       : {location}
Type           : {bridge_type}
Age            : {age} years

HEALTH SUMMARY
-------------------------------------------
Overall Health : {health}
Status         : {status}
Risk Level     : {risk_level}

NINE PARAMETERS
-------------------------------------------
1. AFC (Aeroelastic Flutter)    : {afc}
2. ALSA (Strain Accumulation)   : {alsa}
3. CPII (Cable Integrity)       : {cpii}
4. FFD (Frequency Drift)        : {ffd}%
5. LTS (Thermal Stress)         : {lts}%
6. CCF (Corrosion)              : {ccf}%
7. TVR (Vibration)              : {tvr}
8. BD (Displacement)            : {bd} mm
9. SED (Strain Energy)          : {sed}%

ALERTS
-------------------------------------------
{alerts}

RECOMMENDATIONS
-------------------------------------------
{recommendations}

===========================================
Report generated: {timestamp}
STALWART v2.0.0 - AI Edition
Contact: gitdeeper@gmail.com
===========================================
"""

# بيانات مختلفة لكل جسر
bridge_data = {
    "BR-001": {
        "name": "North Bridge",
        "location": "New York, NY",
        "type": "Suspension",
        "age": 45,
        "health": "91%",
        "status": "SAFE",
        "risk": "LOW",
        "afc": "0.32",
        "alsa": "0.45",
        "cpii": "0.94",
        "ffd": "1.2",
        "lts": "12.5",
        "ccf": "28.3",
        "tvr": "0.92",
        "bd": "5.2",
        "sed": "32.1",
        "alerts": "No active alerts",
        "reco": "Routine monitoring only"
    },
    "BR-002": {
        "name": "South Bridge",
        "location": "Los Angeles, CA",
        "type": "Cable-stayed",
        "age": 28,
        "health": "98%",
        "status": "SAFE",
        "risk": "LOW",
        "afc": "0.21",
        "alsa": "0.38",
        "cpii": "0.97",
        "ffd": "0.8",
        "lts": "8.2",
        "ccf": "18.5",
        "tvr": "0.95",
        "bd": "3.8",
        "sed": "25.4",
        "alerts": "No active alerts",
        "reco": "Continue routine inspections"
    },
    "BR-003": {
        "name": "East Bridge",
        "location": "Chicago, IL",
        "type": "Arch",
        "age": 62,
        "health": "99%",
        "status": "SAFE",
        "risk": "LOW",
        "afc": "0.18",
        "alsa": "0.29",
        "cpii": "0.98",
        "ffd": "0.5",
        "lts": "6.8",
        "ccf": "15.2",
        "tvr": "0.97",
        "bd": "2.9",
        "sed": "22.8",
        "alerts": "No active alerts",
        "reco": "Excellent condition"
    },
    "BR-004": {
        "name": "West Bridge",
        "location": "Seattle, WA",
        "type": "Steel girder",
        "age": 38,
        "health": "96%",
        "status": "SAFE",
        "risk": "LOW",
        "afc": "0.28",
        "alsa": "0.52",
        "cpii": "0.92",
        "ffd": "1.8",
        "lts": "15.3",
        "ccf": "32.7",
        "tvr": "0.89",
        "bd": "6.5",
        "sed": "38.9",
        "alerts": "⚠️ Warning: Slight increase in ALSA",
        "reco": "Monitor strain gauge STR-004 closely"
    },
    "TEST-001": {
        "name": "Test Bridge",
        "location": "Research Facility",
        "type": "Suspension",
        "age": 25,
        "health": "94.7%",
        "status": "SAFE",
        "risk": "LOW",
        "afc": "0.42",
        "alsa": "0.58",
        "cpii": "0.91",
        "ffd": "2.3",
        "lts": "18.5",
        "ccf": "34.2",
        "tvr": "0.88",
        "bd": "8.4",
        "sed": "42.3",
        "alerts": "ALSA in warning range",
        "reco": "Check calibration of strain gauges"
    }
}

print("📝 Generating TXT reports for all bridges...")
print("=" * 50)

for bridge in bridges:
    data = bridge_data.get(bridge, bridge_data["TEST-001"])
    
    txt_file = daily_dir / f"STW-D-{now.strftime('%Y%m%d')}-{bridge}.txt"
    
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(TXT_TEMPLATE.format(
            date=now.strftime('%Y-%m-%d'),
            bridge=bridge,
            bridge_name=data["name"],
            location=data["location"],
            bridge_type=data["type"],
            age=data["age"],
            health=data["health"],
            status=data["status"],
            risk_level=data["risk"],
            afc=data["afc"],
            alsa=data["alsa"],
            cpii=data["cpii"],
            ffd=data["ffd"],
            lts=data["lts"],
            ccf=data["ccf"],
            tvr=data["tvr"],
            bd=data["bd"],
            sed=data["sed"],
            alerts=data["alerts"],
            recommendations=data["reco"],
            timestamp=now.strftime('%Y-%m-%d %H:%M:%S')
        ))
    
    print(f"✅ Created: {txt_file}")

print("\n" + "=" * 50)
print("🎉 All TXT reports generated successfully!")
print("📁 Location: reports/daily/2026-02-16/")
