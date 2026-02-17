#!/usr/bin/env python3
"""STALWART Report Generator

Automatic report generation for daily, weekly, monthly, and alerts.
Supports both .md (Markdown) and .txt (plain text) formats.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import shutil

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.stalwart.core.bridge import Bridge
    from src.stalwart.core.measurement import Measurement
    from src.stalwart.utils.logger import setup_logger, get_logger
    from src.stalwart.utils.config import load_config
    HAS_STALWART = True
except ImportError:
    HAS_STALWART = False
    print("⚠️  STALWART core not found. Running in standalone mode.")

# Setup logger
logger = get_logger("report_generator")


class ReportGenerator:
    """Generate reports for bridge monitoring."""
    
    def __init__(self, reports_dir: str = "reports"):
        self.reports_dir = Path(reports_dir)
        self.templates_dir = self.reports_dir / "templates"
        self.bridge_data = {}
        
        # Ensure directories exist
        self._ensure_dirs()
    
    def _ensure_dirs(self):
        """Create necessary directories if they don't exist."""
        dirs = [
            self.reports_dir / "daily",
            self.reports_dir / "weekly",
            self.reports_dir / "monthly",
            self.reports_dir / "alerts/critical",
            self.reports_dir / "alerts/warning",
            self.reports_dir / "alerts/info",
            self.reports_dir / "alerts/history",
            self.reports_dir / "archives",
            self.templates_dir
        ]
        
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory: {d}")
    
    def load_template(self, template_name: str) -> str:
        """Load a template file."""
        template_path = self.templates_dir / template_name
        if not template_path.exists():
            logger.error(f"Template not found: {template_path}")
            return ""
        
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def save_report(self, content: str, report_type: str, bridge_id: str, 
                    format: str = 'md', date: Optional[datetime] = None):
        """Save generated report to appropriate directory."""
        if date is None:
            date = datetime.now()
        
        # Determine filename and path
        if report_type == 'daily':
            filename = f"STW-D-{date.strftime('%Y%m%d')}-{bridge_id}.{format}"
            report_dir = self.reports_dir / "daily" / date.strftime('%Y-%m-%d')
        elif report_type == 'weekly':
            week = date.strftime('%Y-W%V')
            filename = f"STW-W-{date.strftime('%Y%V')}-{bridge_id}.{format}"
            report_dir = self.reports_dir / "weekly" / week
        elif report_type == 'monthly':
            filename = f"STW-M-{date.strftime('%Y%m')}-{bridge_id}.{format}"
            report_dir = self.reports_dir / "monthly" / date.strftime('%Y-%m')
        elif report_type == 'alert':
            filename = f"STW-A-{date.strftime('%Y%m%d-%H%M%S')}-{bridge_id}.{format}"
            report_dir = self.reports_dir / "alerts" / "history"
        else:
            logger.error(f"Unknown report type: {report_type}")
            return None
        
        # Create directory and save file
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Report saved: {report_path}")
        
        # Create/update latest symlink
        self._update_latest_link(report_type, report_path)
        
        return report_path
    
    def _update_latest_link(self, report_type: str, report_path: Path):
        """Create or update symlink to latest report."""
        latest_dir = self.reports_dir / report_type / "latest"
        latest_dir.mkdir(parents=True, exist_ok=True)
        
        latest_link = latest_dir / f"latest.{report_path.suffix[1:]}"
        
        # Remove existing symlink if it exists
        if latest_link.exists() or latest_link.is_symlink():
            latest_link.unlink()
        
        # Create new symlink (relative path)
        rel_path = os.path.relpath(report_path, latest_dir)
        os.symlink(rel_path, latest_link)
        logger.debug(f"Updated latest link: {latest_link} -> {rel_path}")
    
    def generate_daily_report(self, bridge_data: Dict[str, Any], 
                              format: str = 'md') -> Optional[str]:
        """Generate daily report."""
        template = self.load_template(f'daily_template.{format}')
        if not template:
            return None
        
        # Fill template with data
        content = self._fill_template(template, bridge_data)
        
        # Save report
        report_path = self.save_report(
            content, 'daily', 
            bridge_data.get('bridge_id', 'unknown'),
            format
        )
        
        return str(report_path) if report_path else None
    
    def generate_weekly_report(self, bridge_data: Dict[str, Any],
                               weekly_stats: Dict[str, Any],
                               format: str = 'md') -> Optional[str]:
        """Generate weekly report with statistics."""
        template = self.load_template(f'weekly_template.{format}')
        if not template:
            return None
        
        # Merge data
        data = {**bridge_data, **weekly_stats}
        content = self._fill_template(template, data)
        
        report_path = self.save_report(
            content, 'weekly',
            bridge_data.get('bridge_id', 'unknown'),
            format
        )
        
        return str(report_path) if report_path else None
    
    def generate_monthly_report(self, bridge_data: Dict[str, Any],
                                monthly_stats: Dict[str, Any],
                                format: str = 'md') -> Optional[str]:
        """Generate monthly report with statistics and predictions."""
        template = self.load_template(f'monthly_template.{format}')
        if not template:
            return None
        
        data = {**bridge_data, **monthly_stats}
        content = self._fill_template(template, data)
        
        report_path = self.save_report(
            content, 'monthly',
            bridge_data.get('bridge_id', 'unknown'),
            format
        )
        
        return str(report_path) if report_path else None
    
    def generate_alert_report(self, alert_data: Dict[str, Any],
                              format: str = 'md') -> Optional[str]:
        """Generate alert report."""
        template = self.load_template(f'alerts_template.{format}')
        if not template:
            return None
        
        content = self._fill_template(template, alert_data)
        
        # Save to appropriate alert subdirectory
        severity = alert_data.get('severity', 'info').lower()
        report_path = self.save_alert_report(content, severity, format)
        
        return str(report_path) if report_path else None
    
    def save_alert_report(self, content: str, severity: str, 
                          format: str = 'md') -> Optional[Path]:
        """Save alert report to severity-specific directory."""
        date = datetime.now()
        filename = f"STW-A-{date.strftime('%Y%m%d-%H%M%S')}.{format}"
        
        # Map severity to directory
        severity_map = {
            'critical': 'critical',
            'caution': 'warning',
            'warning': 'info',
            'info': 'info'
        }
        
        subdir = severity_map.get(severity.lower(), 'info')
        report_dir = self.reports_dir / "alerts" / subdir
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_path = report_dir / filename
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Also save to history
        history_dir = self.reports_dir / "alerts" / "history"
        history_dir.mkdir(parents=True, exist_ok=True)
        history_path = history_dir / filename
        shutil.copy2(report_path, history_path)
        
        logger.info(f"Alert saved: {report_path}")
        return report_path
    
    def _fill_template(self, template: str, data: Dict[str, Any]) -> str:
        """Fill template with data (simple placeholder replacement)."""
        result = template
        
        # Common placeholders
        placeholders = {
            '{{DATE}}': datetime.now().strftime('%Y-%m-%d'),
            '{{TIMESTAMP}}': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            '{{YYYYMMDD}}': datetime.now().strftime('%Y%m%d'),
            '{{YYYYWW}}': datetime.now().strftime('%Y%V'),
            '{{YYYYMM}}': datetime.now().strftime('%Y%m'),
        }
        
        # Add all data items
        for key, value in data.items():
            placeholders[f'{{{{{key}}}}}'] = str(value)
        
        # Replace placeholders
        for placeholder, value in placeholders.items():
            result = result.replace(placeholder, value)
        
        return result
    
    def archive_old_reports(self, days: int = 90):
        """Archive reports older than specified days."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Archive daily reports
        daily_dir = self.reports_dir / "daily"
        for item in daily_dir.iterdir():
            if item.is_dir() and item.name != 'latest':
                try:
                    report_date = datetime.strptime(item.name, '%Y-%m-%d')
                    if report_date < cutoff_date:
                        # Move to archives
                        archive_dir = self.reports_dir / "archives" / report_date.strftime('%Y')
                        archive_dir.mkdir(parents=True, exist_ok=True)
                        
                        dest = archive_dir / f"daily-{item.name}"
                        if not dest.exists():
                            shutil.move(str(item), str(dest))
                            logger.info(f"Archived: {item} -> {dest}")
                except ValueError:
                    continue
        
        logger.info(f"Archiving complete for reports older than {days} days")


def generate_sample_data() -> Dict[str, Any]:
    """Generate sample bridge data for testing."""
    return {
        'bridge_id': 'TEST-001',
        'bridge_name': 'Test Bridge',
        'location': 'Test Location',
        'bridge_type': 'suspension',
        'age': 25,
        'health_status': 'GOOD',
        'health_value': 94.7,
        'health_trend': '↗️ +0.5%',
        'risk_level': 'LOW',
        
        # Parameters
        'afc_value': 0.42,
        'afc_status': 'SAFE',
        'afc_trend': '↗️ +0.02',
        'alsa_value': 0.58,
        'alsa_status': 'WARNING',
        'alsa_trend': '↗️ +0.03',
        'cpii_value': 0.91,
        'cpii_status': 'SAFE',
        'cpii_trend': '➡️ 0.00',
        'ffd_value': 2.3,
        'ffd_status': 'SAFE',
        'ffd_trend': '↗️ +0.1%',
        'lts_value': 18.5,
        'lts_status': 'SAFE',
        'lts_trend': '↘️ -0.5%',
        'ccf_value': 34.2,
        'ccf_status': 'SAFE',
        'ccf_trend': '↗️ +0.3%',
        'tvr_value': 0.88,
        'tvr_status': 'SAFE',
        'tvr_trend': '➡️ 0.00',
        'bd_value': 8.4,
        'bd_status': 'SAFE',
        'bd_trend': '↗️ +0.1mm',
        'sed_value': 42.3,
        'sed_status': 'SAFE',
        'sed_trend': '↗️ +0.2%',
        
        # Alerts
        'alerts_table': '| 2026-02-16 | 14:23 | AFC | WARNING | Flutter coefficient increasing |',
        'alerts_text': '[2026-02-16 14:23] WARNING: AFC increasing',
        'critical_count': 0,
        'caution_count': 1,
        'warning_count': 2,
        'info_count': 5,
        'total_alerts': 8,
        
        # Weekly stats
        'health_avg': 93.5,
        'health_min': 91.2,
        'health_max': 95.1,
        'afc_avg': 0.41,
        'alsa_avg': 0.57,
        'ffd_avg': 2.2,
        
        # Monthly stats
        'last_health': 93.8,
        'health_change': '+0.9',
        'ytd_health': 92.4,
        'last_risk': 'LOW',
        'last_critical': 0,
        'critical_change': '0',
        'ytd_critical': 2,
        
        # Recommendations
        'recommendations': '• Continue routine monitoring\n• Check strain gauge STR-001\n• Schedule monthly inspection',
        'notes': 'All systems operating normally.',
        'action_items': '| HIGH | Replace bearing | Maintenance | 2026-03-01 | PENDING |'
    }


def main():
    """Main entry point for report generator."""
    parser = argparse.ArgumentParser(description='STALWART Report Generator')
    parser.add_argument('--type', '-t', choices=['daily', 'weekly', 'monthly', 'alert', 'all'],
                       default='daily', help='Type of report to generate')
    parser.add_argument('--format', '-f', choices=['md', 'txt', 'both'],
                       default='both', help='Report format')
    parser.add_argument('--bridge', '-b', default='TEST-001',
                       help='Bridge ID')
    parser.add_argument('--data', '-d', help='JSON data file (optional)')
    parser.add_argument('--archive', '-a', type=int, default=0,
                       help='Archive reports older than N days')
    parser.add_argument('--sample', action='store_true',
                       help='Generate sample reports for testing')
    
    args = parser.parse_args()
    
    # Setup logging
    from src.stalwart.utils.logger import setup_logger
    setup_logger(level='INFO', log_file='reports/generator.log')
    
    generator = ReportGenerator()
    
    # Archive old reports if requested
    if args.archive > 0:
        generator.archive_old_reports(args.archive)
        return 0
    
    # Load data
    if args.sample:
        bridge_data = generate_sample_data()
        logger.info("Using sample data for testing")
    elif args.data:
        with open(args.data, 'r') as f:
            bridge_data = json.load(f)
        logger.info(f"Loaded data from {args.data}")
    else:
        bridge_data = generate_sample_data()
        logger.info("Using default sample data")
    
    # Generate reports
    formats = ['md', 'txt'] if args.format == 'both' else [args.format]
    
    if args.type == 'all' or args.type == 'daily':
        for fmt in formats:
            path = generator.generate_daily_report(bridge_data, fmt)
            if path:
                print(f"✅ Daily report ({fmt}): {path}")
    
    if args.type == 'all' or args.type == 'weekly':
        weekly_stats = {
            'week': datetime.now().strftime('%V'),
            'start_date': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
            'end_date': datetime.now().strftime('%Y-%m-%d'),
            'weekly_alerts': '| 2026-02-15 | 09:30 | ALSA | WARNING | Strain increasing |',
            'weekly_alerts_text': '[2026-02-15 09:30] WARNING: ALSA increasing',
            'weekly_recommendations': '• Schedule bearing inspection\n• Review corrosion data'
        }
        for fmt in formats:
            path = generator.generate_weekly_report(bridge_data, weekly_stats, fmt)
            if path:
                print(f"✅ Weekly report ({fmt}): {path}")
    
    if args.type == 'all' or args.type == 'monthly':
        monthly_stats = {
            'month': datetime.now().strftime('%B'),
            'year': datetime.now().strftime('%Y'),
            'executive_summary': 'Bridge performance stable with slight degradation in ALSA.',
            'monthly_trend_chart': '[TREND DATA]',
            'afc_monthly_avg': 0.41,
            'afc_monthly_trend': 'stable',
            'alsa_monthly_avg': 0.59,
            'alsa_monthly_trend': 'increasing',
            'ffd_monthly_avg': 2.4,
            'ffd_monthly_trend': 'stable',
            'lts_monthly_avg': 18.2,
            'lts_monthly_trend': 'stable',
            'ccf_monthly_avg': 34.8,
            'ccf_monthly_trend': 'increasing',
            'tvr_monthly_avg': 0.87,
            'tvr_monthly_trend': 'stable',
            'bd_monthly_avg': 8.6,
            'bd_monthly_trend': 'increasing',
            'sed_monthly_avg': 42.9,
            'sed_monthly_trend': 'stable',
            'afc_concern': 'Low',
            'alsa_concern': 'Medium',
            'ffd_concern': 'Low',
            'lts_concern': 'Low',
            'ccf_concern': 'Low',
            'tvr_concern': 'Low',
            'bd_concern': 'Low',
            'sed_concern': 'Low',
            'significant_events': '• Feb 10: Wind storm, AFC peaked at 0.65\n• Feb 14: Heavy traffic detected',
            'predictions': 'ALSA expected to reach warning level within 2 months if trend continues.',
            'maintenance_recommendations': '• Plan strain gauge replacement for March\n• Schedule corrosion inspection',
            'action_items': '| HIGH | Replace bearing | Maintenance | 2026-03-15 | PENDING |'
        }
        for fmt in formats:
            path = generator.generate_monthly_report(bridge_data, monthly_stats, fmt)
            if path:
                print(f"✅ Monthly report ({fmt}): {path}")
    
    if args.type == 'all' or args.type == 'alert':
        alert_data = {
            'bridge_id': args.bridge,
            'severity': 'WARNING',
            'start_date': datetime.now().strftime('%Y-%m-%d'),
            'end_date': datetime.now().strftime('%Y-%m-%d'),
            'critical_count': 0,
            'critical_percent': 0,
            'caution_count': 1,
            'caution_percent': 12.5,
            'warning_count': 2,
            'warning_percent': 25,
            'info_count': 5,
            'info_percent': 62.5,
            'total_alerts': 8,
            'critical_alerts': 'No critical alerts',
            'critical_alerts_text': 'No critical alerts',
            'caution_alerts': '• AFC exceeded threshold at 14:23',
            'caution_alerts_text': '[14:23] CAUTION: AFC exceeded threshold',
            'warning_alerts': '• ALSA increasing at 09:30\n• Temperature variation high at 11:15',
            'warning_alerts_text': '[09:30] WARNING: ALSA increasing\n[11:15] WARNING: Temperature variation high',
            'info_alerts': '• System check passed\n• Data backup completed',
            'info_alerts_text': 'System check passed\nData backup completed',
            'alert_trend_chart': '[ALERT TREND]',
            'common_alerts': '| AFC | 3 | 37.5% |\n| ALSA | 2 | 25% |',
            'common_alerts_text': 'AFC: 3 (37.5%)\nALSA: 2 (25%)',
            'hourly_analysis': '| 14:00 | 2 | AFC |',
            'alert_recommendations': '• Monitor AFC closely\n• Check ALSA trend'
        }
        for fmt in formats:
            path = generator.generate_alert_report(alert_data, fmt)
            if path:
                print(f"✅ Alert report ({fmt}): {path}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
