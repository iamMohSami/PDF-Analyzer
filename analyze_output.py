#!/usr/bin/env python3
"""
Simple script to analyze the JSON output from PDF extraction
"""

import json

def analyze_json_output(filename):
    """Analyze the JSON output and provide summary statistics."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Basic statistics
        total_pages = len(data['pages'])
        total_content_blocks = sum(len(page['content']) for page in data['pages'])
        
        # Count by type
        paragraphs = 0
        tables = 0
        charts = 0
        
        sections = set()
        subsections = set()
        
        for page in data['pages']:
            for content in page['content']:
                if content['type'] == 'paragraph':
                    paragraphs += 1
                elif content['type'] == 'table':
                    tables += 1
                elif content['type'] == 'chart':
                    charts += 1
                
                if content.get('section'):
                    sections.add(content['section'])
                if content.get('sub_section'):
                    subsections.add(content['sub_section'])
        
        print("PDF Extraction Analysis")
        print("=======================")
        print(f"Total pages: {total_pages}")
        print(f"Total content blocks: {total_content_blocks}")
        print(f"Paragraphs: {paragraphs}")
        print(f"Tables: {tables}")
        print(f"Charts/Images: {charts}")
        print(f"Unique sections: {len(sections)}")
        print(f"Unique subsections: {len(subsections)}")
        
        print("\nSections found:")
        for section in sorted(sections):
            print(f"  - {section}")
        
        if subsections:
            print("\nSubsections found:")
            for subsection in sorted(subsections):
                print(f"  - {subsection}")
        
        # Sample content from first few pages
        print("\nSample content from first 3 pages:")
        for i, page in enumerate(data['pages'][:3]):
            print(f"\nPage {page['page_number']}:")
            for j, content in enumerate(page['content'][:2]):  # First 2 content blocks per page
                if content['type'] == 'paragraph':
                    text_preview = content['text'][:100] + "..." if len(content['text']) > 100 else content['text']
                    print(f"  {j+1}. Paragraph: {text_preview}")
                elif content['type'] == 'table':
                    rows = len(content['table_data'])
                    cols = len(content['table_data'][0]) if content['table_data'] else 0
                    print(f"  {j+1}. Table: {rows} rows x {cols} columns")
                elif content['type'] == 'chart':
                    dims = content['dimensions']
                    print(f"  {j+1}. Chart: {dims[0]}x{dims[1]} pixels")
        
    except Exception as e:
        print(f"Error analyzing file: {e}")

if __name__ == "__main__":
    analyze_json_output("fund_factsheet_output.json")
