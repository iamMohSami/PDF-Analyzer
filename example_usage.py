#!/usr/bin/env python3
"""
Example usage of the PDF to JSON Extractor

This script demonstrates how to use the PDFToJSONExtractor class programmatically.
"""

import json
from pdf_to_json_extractor import PDFToJSONExtractor


def example_basic_extraction():
    """Example of basic PDF extraction without OCR or image saving."""
    print("=== Basic Extraction Example ===")
    
    extractor = PDFToJSONExtractor(
        input_path="sample.pdf",
        output_path="output_basic.json",
        ocr_enabled=False,
        image_output_dir=None
    )
    
    try:
        # Extract content
        data = extractor.extract()
        
        # Save to JSON
        extractor.save_json()
        
        # Print summary
        total_pages = len(data['pages'])
        total_content_blocks = sum(len(page['content']) for page in data['pages'])
        
        print(f"Successfully extracted {total_content_blocks} content blocks from {total_pages} pages")
        
    except Exception as e:
        print(f"Extraction failed: {e}")


def example_advanced_extraction():
    """Example of advanced PDF extraction with OCR and image saving."""
    print("\n=== Advanced Extraction Example ===")
    
    extractor = PDFToJSONExtractor(
        input_path="sample.pdf",
        output_path="output_advanced.json",
        ocr_enabled=True,
        image_output_dir="extracted_images"
    )
    
    try:
        # Extract content
        data = extractor.extract()
        
        # Save to JSON
        extractor.save_json()
        
        # Analyze results
        total_pages = len(data['pages'])
        paragraphs = 0
        tables = 0
        charts = 0
        
        for page in data['pages']:
            for content in page['content']:
                if content['type'] == 'paragraph':
                    paragraphs += 1
                elif content['type'] == 'table':
                    tables += 1
                elif content['type'] == 'chart':
                    charts += 1
        
        print(f"Extraction Summary:")
        print(f"  Pages: {total_pages}")
        print(f"  Paragraphs: {paragraphs}")
        print(f"  Tables: {tables}")
        print(f"  Charts: {charts}")
        
    except Exception as e:
        print(f"Extraction failed: {e}")


def example_custom_processing():
    """Example of custom processing of extracted data."""
    print("\n=== Custom Processing Example ===")
    
    extractor = PDFToJSONExtractor(
        input_path="sample.pdf",
        output_path="output_custom.json",
        ocr_enabled=False
    )
    
    try:
        # Extract content
        data = extractor.extract()
        
        # Custom processing: Extract all section headings
        sections = set()
        subsections = set()
        
        for page in data['pages']:
            for content in page['content']:
                if content.get('section'):
                    sections.add(content['section'])
                if content.get('sub_section'):
                    subsections.add(content['sub_section'])
        
        print("Document Structure:")
        print("Sections:")
        for section in sorted(sections):
            print(f"  - {section}")
        
        print("Subsections:")
        for subsection in sorted(subsections):
            print(f"  - {subsection}")
        
        # Save processed data
        extractor.save_json()
        
    except Exception as e:
        print(f"Processing failed: {e}")


if __name__ == "__main__":
    print("PDF to JSON Extractor - Example Usage")
    print("=====================================")
    
    # Note: These examples assume you have a 'sample.pdf' file in the current directory
    # Replace 'sample.pdf' with your actual PDF file path
    
    try:
        example_basic_extraction()
        example_advanced_extraction()
        example_custom_processing()
        
    except FileNotFoundError:
        print("\nError: 'sample.pdf' not found.")
        print("Please place a PDF file named 'sample.pdf' in the current directory")
        print("or modify the file paths in the examples.")
    
    except Exception as e:
        print(f"\nUnexpected error: {e}")
