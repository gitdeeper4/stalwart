# STALWART Netlify Configuration

This directory contains the Netlify configuration for the STALWART Bridge Monitoring System.

## 📁 Structure

- `public/` - Static files (HTML, CSS, JS)
- `functions/` - Netlify serverless functions
- `config/` - Configuration files
- `scripts/` - Build and deployment scripts

## 🔗 Live Site

- Main site: https://stalwart-bridge.netlify.app
- Dashboard: https://stalwart-bridge.netlify.app/dashboard
- API: https://stalwart-bridge.netlify.app/api

## 🚀 Deployment

The site is automatically deployed when changes are pushed to the main branch.

## 📊 Serverless Functions

The following functions are available:
- `get-bridges` - Fetch bridge data
- `get-metrics` - Get computed metrics
- `get-alerts` - Retrieve active alerts
- `generate-report` - Generate daily/weekly/monthly reports

## 🔧 Configuration

Edit `netlify.toml` for build settings and redirects.

## 📝 Notes

- All API routes are prefixed with `/api/`
- Static files are served from `/public`
- Functions are in `/functions`

---
**STALWART v2.0.0** - Bridge Health Monitoring System
