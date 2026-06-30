import re
import os

def md_to_html(md_text):
    # Process code blocks
    # Replace ```language ... ``` with <pre><code>...</code></pre>
    def code_block_sub(match):
        lang = match.group(1) or ""
        code = match.group(2)
        # Escape HTML inside code
        code = code.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return f'<pre><code class="language-{lang}">{code.strip()}</code></pre>'
    
    md_text = re.sub(r'```(\w*)\n(.*?)\n```', code_block_sub, md_text, flags=re.DOTALL)
    
    # Process alerts
    # > [!NOTE] -> <div class="alert alert-note">
    def alert_sub(match):
        alert_type = match.group(1).upper()
        content = match.group(2).strip()
        # Parse inline markdown in alert
        content = inline_formatting(content)
        return f'<div class="alert alert-{alert_type.lower()}"><strong>{alert_type}:</strong> {content}</div>'
    
    md_text = re.sub(r'>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*\n(.*?)(?=\n\n|\n[^\s>])', alert_sub, md_text, flags=re.DOTALL | re.MULTILINE)

    # Process blockquotes (standard)
    md_text = re.sub(r'^>\s*(.*)$', r'<blockquote>\1</blockquote>', md_text, flags=re.MULTILINE)

    # Process Headings
    md_text = re.sub(r'^#\s+(.*)$', r'<h1>\1</h1>', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^##\s+(.*)$', r'<h2>\1</h2>', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^###\s+(.*)$', r'<h3>\1</h3>', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^####\s+(.*)$', r'<h4>\1</h4>', md_text, flags=re.MULTILINE)

    # Process lists
    # Simple list transformation (bullet points)
    # - item -> <li>item</li>
    def list_sub(match):
        items = match.group(0).strip().split('\n')
        list_html = "<ul>\n"
        for item in items:
            # strip leading - or *
            clean_item = re.sub(r'^[\-\*\+]\s+', '', item)
            clean_item = inline_formatting(clean_item)
            list_html += f"  <li>{clean_item}</li>\n"
        list_html += "</ul>"
        return list_html
    
    md_text = re.sub(r'(?:^[\-\*\+]\s+.*(?:\n|$))+', list_sub, md_text, flags=re.MULTILINE)

    # Process ordered lists
    # 1. item -> <li>item</li>
    def olist_sub(match):
        items = match.group(0).strip().split('\n')
        list_html = "<ol>\n"
        for item in items:
            clean_item = re.sub(r'^\d+\.\s+', '', item)
            clean_item = inline_formatting(clean_item)
            list_html += f"  <li>{clean_item}</li>\n"
        list_html += "</ol>"
        return list_html
    
    md_text = re.sub(r'(?:^\d+\.\s+.*(?:\n|$))+', olist_sub, md_text, flags=re.MULTILINE)

    # Process tables
    # | Col1 | Col2 |
    # | --- | --- |
    # | Val1 | Val2 |
    def table_sub(match):
        lines = match.group(0).strip().split('\n')
        if len(lines) < 2:
            return match.group(0)
        
        headers = [h.strip() for h in lines[0].split('|')[1:-1]]
        # Skip lines[1] which is divider
        rows = []
        for line in lines[2:]:
            rows.append([r.strip() for r in line.split('|')[1:-1]])
            
        table_html = "<table>\n<thead>\n<tr>\n"
        for h in headers:
            table_html += f"  <th>{inline_formatting(h)}</th>\n"
        table_html += "</tr>\n</thead>\n<tbody>\n"
        for row in rows:
            table_html += "<tr>\n"
            for cell in row:
                table_html += f"  <td>{inline_formatting(cell)}</td>\n"
            table_html += "</tr>\n"
        table_html += "</tbody>\n</table>"
        return table_html

    md_text = re.sub(r'(?:^\|.*\|(?:\n|$))+', table_sub, md_text, flags=re.MULTILINE)

    # Process Paragraphs
    # Anything that is not an HTML tag, wrap in <p>
    blocks = md_text.split('\n\n')
    for i, block in enumerate(blocks):
        block_stripped = block.strip()
        if not block_stripped:
            continue
        # If it doesn't start with a common block tag, wrap it in <p>
        if not re.match(r'^(<h|<pre|<ul|<ol|<div|<blockquote|<table|---)', block_stripped):
            blocks[i] = f"<p>{inline_formatting(block_stripped)}</p>"
        else:
            # Still format inline elements if it is a heading or list item but handled inside lists
            pass
            
    md_text = '\n\n'.join(blocks)
    
    # Horizontal rule
    md_text = re.sub(r'^---$', '<hr>', md_text, flags=re.MULTILINE)
    
    return md_text

def inline_formatting(text):
    # Images ![alt](src)
    text = re.sub(r'\!\[(.*?)\]\((.*?)\)', r'<img src="\2" alt="\1" style="max-width: 100%; max-height: 250px; border: 1px solid var(--border); border-radius: 6px; margin: 10px 0; display: block;">', text)
    # Bold **text**
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    # Italic *text*
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    # Inline code `code`
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
    # Links [text](url)
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" target="_blank">\1</a>', text)
    return text

def compile_report():
    print("Compiling markdown documents into single HTML report...")
    
    # Read files
    files = ["Answers.md", "Article.md", "Portfolio_VideoCV.md"]
    combined_md = ""
    for f in files:
        if os.path.exists(f):
            with open(f, "r", encoding="utf-8") as file_handle:
                combined_md += file_handle.read() + "\n\n<hr style='margin: 40px 0; border: 0; border-top: 2px dashed #e2e8f0;'>\n\n"
        else:
            print(f"Warning: file {f} not found.")

    html_content = md_to_html(combined_md)
    
    # Full HTML wrapper with custom print styles and beautiful design
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BuildNexTech & Frugal Testing Internship Evaluation Report</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
        
        :root {{
            --bg-primary: #ffffff;
            --text-primary: #1e293b;
            --text-secondary: #475569;
            --accent: #2563eb;
            --accent-light: #eff6ff;
            --border: #e2e8f0;
            --code-bg: #f8fafc;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, sans-serif;
            color: var(--text-primary);
            background-color: var(--bg-primary);
            line-height: 1.6;
            margin: 0;
            padding: 40px 20px;
        }}
        
        .container {{
            max-width: 850px;
            margin: 0 auto;
        }}
        
        h1, h2, h3, h4 {{
            color: #0f172a;
            font-weight: 700;
            margin-top: 1.5em;
            margin-bottom: 0.5em;
        }}
        
        h1 {{
            font-size: 2.2rem;
            border-bottom: 2px solid var(--border);
            padding-bottom: 10px;
            margin-top: 0;
        }}
        
        h2 {{
            font-size: 1.6rem;
            border-bottom: 1px solid var(--border);
            padding-bottom: 8px;
        }}
        
        h3 {{
            font-size: 1.25rem;
        }}
        
        p, li {{
            font-size: 1rem;
            color: var(--text-secondary);
        }}
        
        ul, ol {{
            padding-left: 24px;
            margin-bottom: 1.5em;
        }}
        
        li {{
            margin-bottom: 0.5em;
        }}
        
        code {{
            font-family: 'JetBrains Mono', monospace;
            background-color: var(--code-bg);
            color: #0f172a;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.9em;
            border: 1px solid var(--border);
        }}
        
        pre {{
            background-color: var(--code-bg);
            border: 1px solid var(--border);
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
            margin-bottom: 1.5em;
        }}
        
        pre code {{
            background-color: transparent;
            border: none;
            padding: 0;
            color: inherit;
            font-size: 0.9em;
        }}
        
        blockquote {{
            border-left: 4px solid var(--accent);
            padding-left: 16px;
            margin: 1.5em 0;
            color: var(--text-secondary);
            font-style: italic;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 1.5em;
            font-size: 0.95rem;
        }}
        
        th, td {{
            border: 1px solid var(--border);
            padding: 12px;
            text-align: left;
        }}
        
        th {{
            background-color: var(--code-bg);
            color: #0f172a;
            font-weight: 600;
        }}
        
        /* Alert Boxes styles */
        .alert {{
            padding: 12px 16px;
            border-left: 4px solid;
            border-radius: 4px;
            margin-bottom: 1.5em;
            font-size: 0.95rem;
        }}
        
        .alert-note {{
            background-color: #f0f9ff;
            border-left-color: #0284c7;
            color: #0369a1;
        }}
        
        .alert-tip {{
            background-color: #f0fdf4;
            border-left-color: #16a34a;
            color: #15803d;
        }}
        
        .alert-important {{
            background-color: #faf5ff;
            border-left-color: #8b5cf6;
            color: #6d28d9;
        }}
        
        .alert-warning {{
            background-color: #fffbeb;
            border-left-color: #d97706;
            color: #b45309;
        }}
        
        .alert-caution {{
            background-color: #fdf2f2;
            border-left-color: #dc2626;
            color: #b91c1c;
        }}
        
        /* Print Stylesheet */
        @media print {{
            body {{
                padding: 0;
            }}
            .container {{
                max-width: 100%;
            }}
            h1, h2, h3, h4 {{
                page-break-after: avoid;
            }}
            pre, blockquote, table, .alert {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        {html_content}
    </div>
</body>
</html>
"""
    
    with open("FrugalTestingAssignment_AbhayKumar.html", "w", encoding="utf-8") as out:
        out.write(full_html)
        
    print("Report compiled successfully to FrugalTestingAssignment_AbhayKumar.html!")

if __name__ == "__main__":
    compile_report()
