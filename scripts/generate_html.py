#!/usr/bin/env python3
"""
Generate HTML from Careerjet Integration Plan Markdown for easy PDF conversion
"""

import os
import re
from datetime import datetime

def read_markdown_file(file_path):
    """Read the markdown file content"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def convert_markdown_to_html(markdown_content):
    """Simple markdown to HTML conversion"""
    
    # Replace headers
    html_content = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', markdown_content, flags=re.MULTILINE)
    html_content = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
    html_content = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', html_content, flags=re.MULTILINE)
    
    # Replace bold text
    html_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_content)
    
    # Replace code blocks
    html_content = re.sub(r'```(\w+)?\n(.*?)\n```', r'<pre><code>\2</code></pre>', html_content, flags=re.DOTALL)
    
    # Replace inline code
    html_content = re.sub(r'`([^`]+)`', r'<code>\1</code>', html_content)
    
    # Replace links
    html_content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html_content)
    
    # Convert line breaks to paragraphs
    paragraphs = html_content.split('\n\n')
    html_paragraphs = []
    
    for para in paragraphs:
        para = para.strip()
        if para:
            # Skip if already has HTML tags
            if not re.match(r'^<[^>]+>', para):
                # Handle lists
                if para.startswith('- ') or para.startswith('* '):
                    items = para.split('\n')
                    list_items = []
                    for item in items:
                        if item.strip().startswith(('- ', '* ')):
                            content = item.strip()[2:]
                            list_items.append(f'<li>{content}</li>')
                    if list_items:
                        html_paragraphs.append(f'<ul>{"".join(list_items)}</ul>')
                elif re.match(r'^\d+\. ', para):
                    items = para.split('\n')
                    list_items = []
                    for item in items:
                        if re.match(r'^\d+\. ', item.strip()):
                            content = re.sub(r'^\d+\. ', '', item.strip())
                            list_items.append(f'<li>{content}</li>')
                    if list_items:
                        html_paragraphs.append(f'<ol>{"".join(list_items)}</ol>')
                else:
                    # Regular paragraph
                    para = para.replace('\n', '<br>')
                    html_paragraphs.append(f'<p>{para}</p>')
            else:
                html_paragraphs.append(para)
    
    return '\n'.join(html_paragraphs)

def create_html_file(markdown_content, output_path):
    """Create a styled HTML file from markdown content"""
    
    html_body = convert_markdown_to_html(markdown_content)
    
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Careerjet Integration Plan</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
            background: #fff;
        }}
        
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-top: 50px;
            margin-bottom: 30px;
            font-size: 2.2em;
            page-break-before: always;
        }}
        
        h1:first-child {{
            margin-top: 0;
            page-break-before: auto;
        }}
        
        h2 {{
            color: #34495e;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 8px;
            margin-top: 40px;
            margin-bottom: 20px;
            font-size: 1.6em;
        }}
        
        h3 {{
            color: #7f8c8d;
            margin-top: 30px;
            margin-bottom: 15px;
            font-size: 1.3em;
        }}
        
        h4 {{
            color: #95a5a6;
            margin-top: 25px;
            margin-bottom: 12px;
            font-size: 1.1em;
        }}
        
        p {{
            margin-bottom: 16px;
            text-align: justify;
        }}
        
        code {{
            background-color: #f8f9fa;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'SF Mono', 'Monaco', 'Cascadia Code', 'Roboto Mono', monospace;
            font-size: 0.9em;
            color: #e83e8c;
        }}
        
        pre {{
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            padding: 20px;
            overflow-x: auto;
            font-family: 'SF Mono', 'Monaco', 'Cascadia Code', 'Roboto Mono', monospace;
            font-size: 0.85em;
            line-height: 1.5;
            margin: 20px 0;
        }}
        
        pre code {{
            background: none;
            padding: 0;
            color: #333;
        }}
        
        ul, ol {{
            padding-left: 25px;
            margin-bottom: 16px;
        }}
        
        li {{
            margin-bottom: 8px;
        }}
        
        strong {{
            font-weight: 600;
            color: #2c3e50;
        }}
        
        a {{
            color: #3498db;
            text-decoration: none;
        }}
        
        a:hover {{
            text-decoration: underline;
        }}
        
        blockquote {{
            border-left: 4px solid #3498db;
            margin: 20px 0;
            padding-left: 20px;
            font-style: italic;
            color: #7f8c8d;
            background-color: #f8f9fa;
            padding: 15px 20px;
            border-radius: 0 4px 4px 0;
        }}
        
        .header-info {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            border: 1px solid #e9ecef;
        }}
        
        .toc {{
            background: #fff;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            margin: 30px 0;
        }}
        
        .page-break {{
            page-break-before: always;
        }}
        
        @media print {{
            body {{
                font-size: 12pt;
                line-height: 1.4;
            }}
            
            h1 {{
                font-size: 18pt;
                page-break-before: always;
            }}
            
            h2 {{
                font-size: 16pt;
                page-break-after: avoid;
            }}
            
            h3 {{
                font-size: 14pt;
                page-break-after: avoid;
            }}
            
            pre {{
                page-break-inside: avoid;
                font-size: 10pt;
            }}
            
            @page {{
                margin: 0.75in;
                @bottom-center {{
                    content: "Careerjet Integration Plan - Page " counter(page);
                    font-size: 10pt;
                    color: #666;
                }}
            }}
        }}
    </style>
</head>
<body>
    <div class="header-info">
        <h1 style="margin-top: 0; border: none; color: #2c3e50;">🚀 Unified Careerjet Integration: Strategic Assessment & Implementation Plan</h1>
        <p><strong>TPM Job Finder POC - Global Career Intelligence Platform Enhancement</strong></p>
        <p><strong>Document Version:</strong> 1.0 | <strong>Date:</strong> {datetime.now().strftime('%B %d, %Y')} | <strong>Project:</strong> TPM Job Finder POC</p>
    </div>
    
    {html_body}
    
    <div style="margin-top: 50px; padding: 20px; background: #f8f9fa; border-radius: 8px; text-align: center;">
        <p><strong>Document Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><em>Ready for Implementation - Phase 1 can begin immediately with existing infrastructure.</em></p>
    </div>
</body>
</html>"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)

def main():
    """Main function to convert markdown to HTML"""
    
    # File paths
    markdown_file = "Careerjet_Integration_Plan.md"
    html_file = "Careerjet_Integration_Plan.html"
    
    # Check if markdown file exists
    if not os.path.exists(markdown_file):
        print(f"❌ Error: {markdown_file} not found!")
        return 1
    
    print(f"📄 Converting {markdown_file} to HTML for PDF conversion...")
    
    # Read markdown content
    try:
        markdown_content = read_markdown_file(markdown_file)
        print(f"✅ Read markdown file ({len(markdown_content):,} characters)")
    except Exception as e:
        print(f"❌ Error reading markdown file: {e}")
        return 1
    
    # Generate HTML file
    try:
        create_html_file(markdown_content, html_file)
        print(f"✅ HTML file created: {html_file}")
    except Exception as e:
        print(f"❌ Error creating HTML file: {e}")
        return 1
    
    # Verify HTML file was created
    if os.path.exists(html_file):
        file_size = os.path.getsize(html_file)
        print(f"✅ HTML created successfully: {html_file} ({file_size:,} bytes)")
        print()
        print("🔧 To convert to PDF:")
        print("1. Open the HTML file in a web browser (Chrome, Safari, Firefox)")
        print("2. Print the page (Cmd+P)")
        print("3. Select 'Save as PDF' as destination")
        print("4. Adjust settings as needed (margins, scale, etc.)")
        print("5. Save as 'Careerjet_Integration_Plan.pdf'")
        print()
        print("💡 Alternative: Use online HTML to PDF converters")
        return 0
    else:
        print("❌ HTML file was not created")
        return 1

if __name__ == "__main__":
    exit(main())
