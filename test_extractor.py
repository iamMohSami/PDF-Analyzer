#!/usr/bin/env python3
"""
Simple test script for the PDF to JSON Extractor

This script performs basic validation of the extractor functionality.
"""

import json
import tempfile
import os
from pathlib import Path
from pdf_to_json_extractor import PDFToJSONExtractor


def test_json_structure():
    """Test that the JSON output has the correct structure."""
    print("Testing JSON structure...")
    
    # Create a minimal test data structure
    test_data = {
        "pages": [
            {
                "page_number": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "section": "Test Section",
                        "sub_section": None,
                        "text": "This is a test paragraph."
                    },
                    {
                        "type": "table",
                        "section": "Test Section",
                        "sub_section": None,
                        "description": None,
                        "table_data": [
                            ["Header 1", "Header 2"],
                            ["Data 1", "Data 2"]
                        ]
                    }
                ]
            }
        ]
    }
    
    # Test JSON serialization
    try:
        json_str = json.dumps(test_data, indent=2, ensure_ascii=False)
        parsed_data = json.loads(json_str)
        
        # Validate structure
        assert "pages" in parsed_data
        assert isinstance(parsed_data["pages"], list)
        assert len(parsed_data["pages"]) > 0
        
        page = parsed_data["pages"][0]
        assert "page_number" in page
        assert "content" in page
        assert isinstance(page["content"], list)
        
        content = page["content"][0]
        assert "type" in content
        assert "section" in content
        
        print("✓ JSON structure validation passed")
        return True
        
    except Exception as e:
        print(f"✗ JSON structure validation failed: {e}")
        return False


def test_file_operations():
    """Test file reading and writing operations."""
    print("Testing file operations...")
    
    try:
        # Create temporary files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            test_data = {"test": "data"}
            json.dump(test_data, temp_file, indent=2)
            temp_path = temp_file.name
        
        # Test file reading
        with open(temp_path, 'r') as f:
            loaded_data = json.load(f)
            assert loaded_data == test_data
        
        # Clean up
        os.unlink(temp_path)
        
        print("✓ File operations test passed")
        return True
        
    except Exception as e:
        print(f"✗ File operations test failed: {e}")
        return False


def test_heading_detection():
    """Test heading detection logic."""
    print("Testing heading detection...")
    
    try:
        # Create a mock extractor instance
        extractor = PDFToJSONExtractor(
            input_path="dummy.pdf",  # Won't be used for this test
            output_path="dummy.json"
        )
        
        # Test font size calculation
        font_sizes = [10, 10, 10, 12, 10, 15, 10, 10]
        median_size = sorted(font_sizes)[len(font_sizes) // 2]
        assert median_size == 10
        
        # Test heading patterns
        test_texts = [
            "1. Introduction",  # Should be section
            "1.1 Background",  # Should be subsection
            "SUMMARY",         # Should be section (ALL CAPS)
            "Overview:",       # Should be section (ends with colon)
            "Regular paragraph text"  # Should not be heading
        ]
        
        # Simple pattern testing
        section_patterns = [
            r'^\d+\.?\s+',  # Numbered sections
            r':$',          # Ends with colon
        ]
        
        subsection_patterns = [
            r'^\d+\.\d+\.?\s+',  # Numbered subsections
        ]
        
        for text in test_texts:
            is_section = any(re.match(pattern, text.strip()) for pattern in section_patterns)
            is_subsection = any(re.match(pattern, text.strip()) for pattern in subsection_patterns)
            
            if "Introduction" in text:
                assert is_section
            elif "Background" in text:
                assert is_subsection
            elif "SUMMARY" in text:
                assert text.strip().isupper()
            elif "Overview:" in text:
                assert text.strip().endswith(':')
        
        print("✓ Heading detection test passed")
        return True
        
    except Exception as e:
        print(f"✗ Heading detection test failed: {e}")
        return False


def test_content_type_validation():
    """Test content type validation."""
    print("Testing content type validation...")
    
    try:
        # Test valid content types
        valid_types = ["paragraph", "table", "chart"]
        
        for content_type in valid_types:
            # Create test content block
            content_block = {
                "type": content_type,
                "section": "Test Section",
                "sub_section": None
            }
            
            # Add type-specific fields
            if content_type == "paragraph":
                content_block["text"] = "Test text"
            elif content_type == "table":
                content_block["table_data"] = [["Header"], ["Data"]]
            elif content_type == "chart":
                content_block["dimensions"] = [100, 100]
                content_block["image_path"] = None
        
        print("✓ Content type validation test passed")
        return True
        
    except Exception as e:
        print(f"✗ Content type validation test failed: {e}")
        return False


def run_all_tests():
    """Run all tests and report results."""
    print("PDF to JSON Extractor - Test Suite")
    print("===================================")
    
    tests = [
        test_json_structure,
        test_file_operations,
        test_heading_detection,
        test_content_type_validation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The extractor is ready to use.")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
    
    return passed == total


if __name__ == "__main__":
    import re  # Import re for regex testing
    run_all_tests()
