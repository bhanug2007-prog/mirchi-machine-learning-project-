"""
generate_blueprint_pdf.py
=========================
Installs reportlab (if missing) and compiles the MirchiMandi project blueprint
into a beautiful, printable PDF document: 'MirchiMandi_Project_Blueprint.pdf'.
Uses standard ASCII characters for maximum PDF compatibility.
"""

import os
import sys
import subprocess

# Ensure reportlab is installed
try:
    import reportlab
except ImportError:
    print("Installing reportlab library for PDF generation...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
    import reportlab

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

def build_pdf(filename="MirchiMandi_Project_Blueprint.pdf"):
    print(f"Building PDF: {filename}...")
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=54, leftMargin=54,
        topMargin=54, bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Styles for Premium Corporate Look
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=28,
        leading=34,
        textColor=colors.HexColor('#a50000'), # Chilli Red
        alignment=TA_CENTER
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#5e3f3a'),
        alignment=TA_CENTER
    )
    
    meta_style = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#777777'),
        alignment=TA_CENTER
    )

    h1_style = ParagraphStyle(
        'Heading1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#a50000'),
        spaceBefore=15,
        spaceAfter=10,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'Heading2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#1b1c1c'),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=15,
        textColor=colors.HexColor('#1b1c1c'),
        spaceAfter=8,
        alignment=TA_LEFT
    )

    bullet_style = ParagraphStyle(
        'BulletText',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    story = []
    
    # ------------------ COVER PAGE ------------------
    story.append(Spacer(1, 100))
    story.append(Paragraph("[ MirchiMandi ]", ParagraphStyle('Logo', fontName='Helvetica-Bold', fontSize=24, textColor=colors.HexColor('#a50000'), alignment=TA_CENTER, leading=30)))
    story.append(Spacer(1, 20))
    story.append(Paragraph("MirchiMandi", title_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Agricultural Price Intelligence & Transport Arbitrage Platform", subtitle_style))
    story.append(Spacer(1, 8))
    
    # Corrected second positional parameter for style instead of keyword CoverMeta
    p_style = ParagraphStyle('M', parent=subtitle_style, fontSize=10, textColor=colors.HexColor('#777777'))
    story.append(Paragraph("Empowering Andhra Pradesh Farmers with Real-Time Price Transparency", p_style))
    
    story.append(Spacer(1, 180))
    story.append(Paragraph("Project Architecture & Blueprint Proposal", ParagraphStyle('CoverSub', parent=subtitle_style, fontName='Helvetica-Bold', fontSize=12)))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"Generated on: July 14, 2026<br/>Developed for Andhra Pradesh Chilli Cultivators", meta_style))
    story.append(PageBreak())
    
    # ------------------ PAGE 2: EXEC SUMMARY & DATA ------------------
    story.append(Paragraph("1. Executive Summary", h1_style))
    story.append(Paragraph(
        "<b>The Core Problem:</b> Many small and medium-scale farmers cultivating dried red chillies in the Guntur and Prakasam regions of Andhra Pradesh face significant information asymmetry. While they grow premium, high-value seed varieties like <b>Teja S17, 334 Sannam, Byadgi, 341, DD Deluxe, and Armoor</b>, official government portals like Agmarknet only list generic classifications ('Red New', 'Red Top').",
        body_style
    ))
    story.append(Paragraph(
        "Brokers operating local cold storage (AC) yards leverage this lack of granular data to purchase crops below Guntur Mandi market values, costing farmers Rs 2,000 to Rs 3,000 per quintal in lost profits. For a 100-quintal yield, a farmer easily loses Rs 2,00,000 to Rs 3,00,000.",
        body_style
    ))
    story.append(Paragraph(
        "<b>The Solution:</b> MirchiMandi is a data-driven agricultural intelligence platform that:<br/>"
        "1. <b>Automates Daily variety-specific data syncs</b> from a public Google Sheets repository that mirrors the official Guntur Mirchi Yard prices.<br/>"
        "2. <b>Calculates Pincode-to-Pincode Transportation Costs</b> (Tractor/Trolley/Truck rates + labor handling fee) to show if transporting crops is profitable.<br/>"
        "3. <b>Applies Time-Series Machine Learning Models</b> to recommend whether farmers should sell their crops today or wait based on 7-day price forecasting trends.",
        body_style
    ))
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("2. Platform Architecture & Data Ingestion", h1_style))
    story.append(Paragraph(
        "To avoid heavy Selenium browser dependencies (which frequently crash on servers), we reverse-engineered the Guntur Mirchi rates portal and exposed its direct REST Google Sheets API:<br/>"
        "• <b>Endpoint:</b> Google Sheets API v4 batchGet<br/>"
        "• <b>Spreadsheet ID:</b> 1dwhlEIQ_H0NcAIT-SSg1sM_ZpsT2KZNUvc2fqWI9lYU<br/>"
        "• <b>Ranges Fetched:</b> 'Consolidated Prices' (varieties) & 'Fatki Table' (byproducts)<br/>"
        "The daily auto-sync script runs in under 3 seconds, pulling the latest date's row, mapping it to structural database records, and pushing it to Supabase.",
        body_style
    ))
    story.append(PageBreak())
    
    # ------------------ PAGE 3: TRANSPORT CALCULATOR & ML ------------------
    story.append(Paragraph("3. Transport Arbitrage & Logistics Calculations", h1_style))
    story.append(Paragraph(
        "A major feature of MirchiMandi is calculating whether the price difference between local village brokers (at AC yards) and the central Guntur APMC market justifies the cost of hiring transport.",
        body_style
    ))
    story.append(Paragraph("<b>Logistics Fare & Labor Model:</b>", h2_style))
    story.append(Paragraph("• <b>Tractor:</b> Base Rs 1,500 + Rs 35/km (Capacity: up to 100 quintals)", bullet_style))
    story.append(Paragraph("• <b>Trolley (Tata Ace):</b> Base Rs 800 + Rs 25/km (Capacity: up to 30 quintals)", bullet_style))
    story.append(Paragraph("• <b>Truck (Lorry):</b> Base Rs 3,000 + Rs 45/km (Capacity: up to 250 quintals)", bullet_style))
    story.append(Paragraph("• <b>Labor (Hamali):</b> Rs 40 per quintal (Rs 20 loading + Rs 20 unloading charge)", bullet_style))
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Arbitrage Math Formulas:</b>", h2_style))
    story.append(Paragraph(
        "<i>Total Logistics Cost = Base Fare + (Distance x Per Km Rate) + (Quintals x Rs 40)</i><br/>"
        "<i>Net Mandi Profit = (Quintals x Mandi Price) - Total Logistics Cost</i><br/>"
        "<i>Net Arbitrage Gain = Net Mandi Profit - (Quintals x Broker Price)</i>",
        body_style
    ))

    story.append(Spacer(1, 10))
    story.append(Paragraph("4. Machine Learning Forecasting Models", h1_style))
    story.append(Paragraph(
        "We train 11 different regression and ensemble models on 1,200+ days of historical data per variety. Lags, rolling statistics, momentum, and sin/cos seasonality encodings are built daily.",
        body_style
    ))
    
    # Model Comparison Table - Removed non-ASCII currency/emojis
    table_data = [
        ['Rank', 'Model Name', 'MAE (Rs)', 'R2 Score', 'Status'],
        ['1', 'Lasso Regression', 'Rs 204', '0.9922', 'Best (Saved)'],
        ['2', 'Ridge Regression', 'Rs 214', '0.9918', 'Backup'],
        ['3', 'Linear Regression', 'Rs 215', '0.9918', 'Baseline'],
        ['4', 'LightGBM', 'Rs 395', '0.9854', 'Ensemble'],
        ['5', 'Random Forest', 'Rs 430', '0.9812', 'Ensemble']
    ]
    t = Table(table_data, colWidths=[40, 150, 80, 80, 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#a50000')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('TOPPADDING', (0,0), (-1,0), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f6f3f2'), colors.white]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#eae7e7')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
    ]))
    story.append(t)
    
    story.append(Spacer(1, 20))
    story.append(Paragraph("5. Deployment Guide", h1_style))
    story.append(Paragraph(
        "• <b>Backend API:</b> FastAPI deployed on Render.com (`uvicorn main:app --host 0.0.0.0 --port 8000`) connected to Supabase.<br/>"
        "• <b>Frontend:</b> React Vite web application deployed on Vercel.",
        body_style
    ))
    
    doc.build(story)
    print("PDF Generation complete!")

if __name__ == "__main__":
    build_pdf()
