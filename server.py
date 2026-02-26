from http.server import HTTPServer, SimpleHTTPRequestHandler
import io
import time

# Install: pip install reportlab
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

class Handler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/generate-report':
            # 模拟处理延迟
            time.sleep(1.5)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/pdf')
            self.send_header('Content-Disposition', 'attachment; filename="marketing-report.pdf"')
            self.end_headers()
            
            pdf = self.generate_pdf()
            self.wfile.write(pdf)
            return
        
        # Serve static files (index.html)
        if self.path == '/':
            self.path = '/index.html'
        return SimpleHTTPRequestHandler.do_GET(self)

    def generate_pdf(self):
        buffer = io.BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=30
        )
        
        styles = getSampleStyleSheet()
        
        # Build content
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'], # 继承基础样式
            fontSize=24,
            spaceAfter=20,
            textColor=colors.HexColor('#1a1a2e'),
            fontName='Helvetica-Bold'
        )
        
        story.append(Paragraph("MARKETING PERFORMANCE REPORT", title_style))
        
        # Date line
        story.append(Paragraph("Generated: January 2025 | Client: Demo Campaign", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Summary table data
        summary_data = [
            ['METRIC', 'VALUE', 'CHANGE'],
            ['Total Ad Spend', '$12,450.00', '—'],
            ['Impressions', '2,340,000', '+23%'],
            ['Clicks', '45,200', '+15%'],
            ['Click-Through Rate', '1.93%', '+0.12%'],
            ['Cost Per Click', '$0.28', '-$0.03'],
            ['Conversions', '892', '+31%'],
            ['Cost Per Acquisition', '$13.95', '-$2.10'],
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 1.8*inch, 1.2*inch])
        
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16213e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige), # 修复：这里应该是数据行的背景，原代码逻辑混乱
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f4f8')]),
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Platform breakdown - 修复数据
        platform_data = [
            ['PLATFORM', 'SPEND', 'IMPRESSIONS', 'CLICKS', 'CTR', 'CONV.'],
            ['Google Ads', '$5,000', '980K', '22,000', '2.2%', '412'],
            ['Meta Ads', '$4,500', '890K', '16,000', '1.8%', '298'],
            ['TikTok Ads', '$2,950', '470K', '6,200', '1.3%', '182']
        ]
        
        platform_table = Table(platform_data)
        platform_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16213e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(platform_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Insights
        insight_style = ParagraphStyle(
            'Insight',
            parent=styles['BodyText'],
            fontSize=10,
            spaceAfter=12,
            leading=14
        )
        
        # 修复文本内容
        insights_text = """
        <b>Key Findings:</b><br/><br/>
        • <b>Top Performer:</b> Google Search campaigns delivered highest conversion rate at 4.2%<br/>
        • <b>Budget Opportunity:</b> TikTok CPA 15% below average — scale recommended<br/>
        • <b>Creative Refresh:</b> Meta CTR declined 5% — new creative assets needed<br/>
        • <b>Audience Insight:</b> Lookalike audiences outperforming interest-based by 22%
        """
        
        story.append(Paragraph(insights_text, insight_style))
        
        doc.build(story)
        pdf_data = buffer.getvalue()
        buffer.close()
        return pdf_data
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

if __name__ == '__main__':
    print("=" * 40)
    print("SERVER RUNNING AT http://localhost:8000")
    print("=" * 40)
    # 修复：添加端口号 8000
    server = HTTPServer(('localhost', 8000), Handler)
    server.serve_forever()
