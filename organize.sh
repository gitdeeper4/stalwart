#!/bin/bash
# STALWART Netlify Organizer Script

echo "📁 STALWART Netlify File Organizer"
echo "=================================="

# Ensure directories exist
mkdir -p public
mkdir -p functions
mkdir -p config
mkdir -p scripts

# Copy HTML files to public (if they exist in parent)
if [ -f ../index.html ]; then
    cp ../index.html public/
    echo "✅ Copied index.html to public/"
fi

if [ -f ../dashboard.html ]; then
    cp ../dashboard.html public/
    echo "✅ Copied dashboard.html to public/"
fi

if [ -f ../documentation.html ]; then
    cp ../documentation.html public/
    echo "✅ Copied documentation.html to public/"
fi

# Copy research paper
if [ -f ../STALWART_Bridge_Safety_Research_Paper.md ]; then
    mkdir -p public/research
    cp ../STALWART_Bridge_Safety_Research_Paper.md public/research/
    echo "✅ Copied research paper to public/research/"
fi

# Copy reports
if [ -d ../reports ]; then
    cp -r ../reports public/
    echo "✅ Copied reports to public/"
fi

echo "=================================="
echo "✅ Organization complete!"
