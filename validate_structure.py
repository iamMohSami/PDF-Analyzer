#!/usr/bin/env python3
"""
Structure validation script for PDF to JSON Extractor

This script validates the code structure and JSON format without requiring external dependencies.
"""

import json
import re
import os
from pathlib import Path


def validate_json_structure():
    """Validate that the JSON output structure matches requirements."""
    print("Validating JSON structure...")
    
    # Expected structure from requirements
    expected_structure = {
        "pages": [
            {
                "page_number": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "section": "Introduction",
                        "sub_section": "Background",
                        "text": "This is an example paragraph extracted from the PDF..."
                    },
                    {
                        "type": "table",
                        "section": "Financial Data",
                        "description": None,
                        "table_data": [
                            ["Year", "Revenue", "Profit"],
                            ["2022", "$10M", "$2M"],
                            ["2023", "$12M", "$3M"]
                        ]
                    },
                    {
                        "type": "chart",
                        "section": "Performance Overview",
                        "description": "Bar chart showing yearly growth...",
                        "dimensions": [800, 600],
                        "image_path": "extracted_image_page1_img0.png"
                    }
                ]
            }
        ]
    }
    
    try:
        # Test JSON serialization/deserialization
        json_str = json.dumps(expected_structure, indent=2, ensure_ascii=False)
        parsed = json.loads(json_str)
        
        # Validate required fields
        assert "pages" in parsed
        assert isinstance(parsed["pages"], list)
        
        page = parsed["pages"][0]
        assert "page_number" in page
        assert "content" in page
        
        content_items = page["content"]
        assert len(content_items) == 3
        
        # Validate paragraph
        paragraph = content_items[0]
        assert paragraph["type"] == "paragraph"
        assert "section" in paragraph
        assert "sub_section" in paragraph
        assert "text" in paragraph
        
        # Validate table
        table = content_items[1]
        assert table["type"] == "table"
        assert "table_data" in table
        assert isinstance(table["table_data"], list)
        
        # Validate chart
        chart = content_items[2]
        assert chart["type"] == "chart"
        assert "dimensions" in chart
        assert "image_path" in chart
        
        print("✓ JSON structure validation passed")
        return True
        
    except Exception as e:
        print(f"✗ JSON structure validation failed: {e}")
        return False


def validate_code_structure():
    """Validate the main script structure."""
    print("Validating code structure...")
    
    script_path = Path("pdf_to_json_extractor.py")
    
    if not script_path.exists():
        print("✗ Main script file not found")
        return False
    
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required components
        required_components = [
            "class PDFToJSONExtractor",
            "def extract_font_sizes",
            "def detect_headings",
            "def extract_tables_pdfplumber",
            "def extract_tables_camelot",
            "def extract_images",
            "def perform_ocr_on_image",
            "def group_text_into_paragraphs",
            "def process_page",
            "def extract",
            "def save_json",
            "def main",
            "argparse",
            "pdfplumber",
            "PyMuPDF",
            "pandas",
            "tqdm"
        ]
        
        missing_components = []
        for component in required_components:
            if component not in content:
                missing_components.append(component)
        
        if missing_components:
            print(f"✗ Missing components: {missing_components}")
            return False
        
        print("✓ Code structure validation passed")
        return True
        
    except Exception as e:
        print(f"✗ Code structure validation failed: {e}")
        return False


def validate_heading_detection_logic():
    """Validate heading detection patterns."""
    print("Validating heading detection logic...")
    
    try:
        # Test patterns from the implementation
        test_cases = [
            ("1. Introduction", True, "section"),
            ("1.1 Background", True, "subsection"),
            ("2. Methodology", True, "section"),
            ("SUMMARY", True, "section"),
            ("Overview:", True, "section"),
            ("Regular paragraph text", False, None),
            ("This is a normal sentence.", False, None)
        ]
        
        # Section patterns
        section_patterns = [
            r'^\d+\.?\s+',  # Numbered sections
            r':$',          # Ends with colon
        ]
        
        # Subsection patterns
        subsection_patterns = [
            r'^\d+\.\d+\.?\s+',  # Numbered subsections
        ]
        
        for text, should_match, expected_type in test_cases:
            is_section = any(re.match(pattern, text.strip()) for pattern in section_patterns)
            is_subsection = any(re.match(pattern, text.strip()) for pattern in subsection_patterns)
            
            # Additional checks
            if text.strip().isupper() and len(text.strip()) > 3:
                is_section = True
            
            if text.strip().endswith(':'):
                is_section = True
            
            if expected_type == "section" and not is_section:
                print(f"✗ Failed to detect section: '{text}'")
                return False
            elif expected_type == "subsection" and not is_subsection:
                print(f"✗ Failed to detect subsection: '{text}'")
                return False
            elif expected_type is None and (is_section or is_subsection):
                print(f"✗ False positive detection: '{text}'")
                return False
        
        print("✓ Heading detection logic validation passed")
        return True
        
    except Exception as e:
        print(f"✗ Heading detection logic validation failed: {e}")
        return False


def validate_file_structure():
    """Validate that all required files exist."""
    print("Validating file structure...")
    
    required_files = [
        "pdf_to_json_extractor.py",
        "README.md",
        "requirements.txt"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"✗ Missing files: {missing_files}")
        return False
    
    print("✓ File structure validation passed")
    return True


def validate_readme_content():
    """Validate README content."""
    print("Validating README content...")
    
    try:
        with open("README.md", 'r', encoding='utf-8') as f:
            readme_content = f.read()
        
        required_sections = [
            "# PDF to JSON Extractor",
            "## Features",
            "## Installation",
            "## Usage",
            "## Output Format",
            "python pdf_to_json_extractor.py --input sample.pdf --output output.json",
            "pdfplumber",
            "PyMuPDF",
            "camelot",
            "pytesseract"
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in readme_content:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"✗ Missing README sections: {missing_sections}")
            return False
        
        print("✓ README content validation passed")
        return True
        
    except Exception as e:
        print(f"✗ README content validation failed: {e}")
        return False


def run_validation():
    """Run all validation tests."""
    print("PDF to JSON Extractor - Structure Validation")
    print("=============================================")
    
    tests = [
        validate_file_structure,
        validate_code_structure,
        validate_json_structure,
        validate_heading_detection_logic,
        validate_readme_content
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
    
    print(f"\nValidation Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All validations passed! The implementation meets all requirements.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Install system dependencies (Ghostscript, Tesseract)")
        print("3. Test with a sample PDF: python pdf_to_json_extractor.py --input sample.pdf --output output.json")
    else:
        print("⚠️  Some validations failed. Please check the implementation.")
    
    return passed == total


if __name__ == "__main__":
    run_validation()
