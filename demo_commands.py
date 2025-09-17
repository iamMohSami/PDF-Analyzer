#!/usr/bin/env python3
"""
Demo script showing expected command line usage for PDF to JSON Extractor

This script demonstrates the command line interface without actually running the extractor.
"""

import subprocess
import sys
from pathlib import Path


def show_help():
    """Show the help message for the extractor."""
    print("PDF to JSON Extractor - Help")
    print("=============================")
    print()
    print("Usage: python pdf_to_json_extractor.py [OPTIONS]")
    print()
    print("Required arguments:")
    print("  --input, -i PATH     Path to input PDF file")
    print("  --output, -o PATH    Path to output JSON file")
    print()
    print("Optional arguments:")
    print("  --ocr                Enable OCR for image-based content")
    print("  --image-out PATH     Directory to save extracted images")
    print("  --verbose, -v        Enable verbose logging")
    print("  --help, -h           Show this help message")
    print()
    print("Examples:")
    print("  python pdf_to_json_extractor.py --input sample.pdf --output output.json")
    print("  python pdf_to_json_extractor.py --input sample.pdf --output output.json --ocr --image-out extracted_images")
    print("  python pdf_to_json_extractor.py -i report.pdf -o report.json --verbose")


def demo_commands():
    """Demonstrate various command line usage examples."""
    print("PDF to JSON Extractor - Command Examples")
    print("=========================================")
    print()
    
    examples = [
        {
            "description": "Basic extraction (minimal command)",
            "command": "python pdf_to_json_extractor.py --input sample.pdf --output output.json"
        },
        {
            "description": "Extraction with OCR enabled",
            "command": "python pdf_to_json_extractor.py --input sample.pdf --output output.json --ocr"
        },
        {
            "description": "Full extraction with OCR and image saving",
            "command": "python pdf_to_json_extractor.py --input sample.pdf --output output.json --ocr --image-out extracted_images"
        },
        {
            "description": "Verbose processing for debugging",
            "command": "python pdf_to_json_extractor.py --input sample.pdf --output output.json --verbose"
        },
        {
            "description": "Short form arguments",
            "command": "python pdf_to_json_extractor.py -i report.pdf -o report.json -v"
        },
        {
            "description": "Processing a large document with all features",
            "command": "python pdf_to_json_extractor.py --input large_document.pdf --output structured_data.json --ocr --image-out charts_and_diagrams --verbose"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example['description']}:")
        print(f"   {example['command']}")
        print()
    
    print("Note: Replace 'sample.pdf' with your actual PDF file path")
    print("Note: The --ocr flag requires Tesseract to be installed")
    print("Note: The --image-out flag will create the directory if it doesn't exist")


def show_expected_output():
    """Show example of expected JSON output structure."""
    print("Expected JSON Output Structure")
    print("==============================")
    print()
    
    example_output = {
        "pages": [
            {
                "page_number": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "section": "Introduction",
                        "sub_section": "Background",
                        "text": "This document provides an overview of our financial performance..."
                    },
                    {
                        "type": "table",
                        "section": "Financial Data",
                        "sub_section": "Quarterly Results",
                        "description": None,
                        "table_data": [
                            ["Quarter", "Revenue", "Profit", "Growth"],
                            ["Q1 2023", "$2.5M", "$500K", "15%"],
                            ["Q2 2023", "$2.8M", "$600K", "12%"],
                            ["Q3 2023", "$3.1M", "$700K", "11%"],
                            ["Q4 2023", "$3.4M", "$800K", "10%"]
                        ]
                    },
                    {
                        "type": "chart",
                        "section": "Performance Overview",
                        "sub_section": None,
                        "description": "Revenue growth chart showing quarterly performance",
                        "dimensions": [800, 600],
                        "image_path": "extracted_images/extracted_image_page1_img0.png"
                    }
                ]
            },
            {
                "page_number": 2,
                "content": [
                    {
                        "type": "paragraph",
                        "section": "Methodology",
                        "sub_section": None,
                        "text": "Our analysis methodology follows industry best practices..."
                    }
                ]
            }
        ]
    }
    
    import json
    print(json.dumps(example_output, indent=2))


def show_installation_steps():
    """Show installation steps."""
    print("Installation Steps")
    print("==================")
    print()
    print("1. Install Python dependencies:")
    print("   pip install pdfplumber PyMuPDF pandas tqdm")
    print()
    print("2. Install optional dependencies:")
    print("   pip install camelot-py[cv] pytesseract Pillow")
    print()
    print("3. Install system dependencies:")
    print("   Windows: Download Ghostscript and Tesseract from their official websites")
    print("   macOS: brew install ghostscript tesseract")
    print("   Linux: sudo apt-get install ghostscript tesseract-ocr")
    print()
    print("4. Test the installation:")
    print("   python pdf_to_json_extractor.py --help")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            show_help()
        elif sys.argv[1] == "--examples":
            demo_commands()
        elif sys.argv[1] == "--output":
            show_expected_output()
        elif sys.argv[1] == "--install":
            show_installation_steps()
        else:
            print("Unknown option. Use --help for available options.")
    else:
        print("PDF to JSON Extractor - Demo")
        print("============================")
        print()
        print("Available demo options:")
        print("  --help      Show help message")
        print("  --examples  Show command examples")
        print("  --output    Show expected JSON output")
        print("  --install   Show installation steps")
        print()
        print("Example: python demo_commands.py --examples")
