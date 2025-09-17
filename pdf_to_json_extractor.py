#!/usr/bin/env python3
"""
PDF to JSON Extractor

A comprehensive tool for extracting structured content from PDF files and exporting
to JSON format while preserving page hierarchy, sections, subsections, and content types.

Author: AI Assistant
Version: 1.0.0
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import logging

# Third-party imports
import pdfplumber
import fitz  # PyMuPDF
import pandas as pd
from tqdm import tqdm

# Optional imports for advanced features
try:
    import camelot
    CAMELOT_AVAILABLE = True
except ImportError:
    CAMELOT_AVAILABLE = False
    logging.warning("Camelot not available. Advanced table extraction disabled.")

try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logging.warning("OCR libraries not available. OCR functionality disabled.")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PDFToJSONExtractor:
    """
    Main class for extracting structured content from PDF files.
    """
    
    def __init__(self, input_path: str, output_path: str, ocr_enabled: bool = False, 
                 image_output_dir: Optional[str] = None):
        """
        Initialize the PDF extractor.
        
        Args:
            input_path: Path to input PDF file
            output_path: Path to output JSON file
            ocr_enabled: Whether to enable OCR for images
            image_output_dir: Directory to save extracted images
        """
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.ocr_enabled = ocr_enabled
        self.image_output_dir = Path(image_output_dir) if image_output_dir else None
        
        # Validate inputs
        if not self.input_path.exists():
            raise FileNotFoundError(f"Input PDF file not found: {input_path}")
        
        # Create output directory if needed
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create image output directory if specified
        if self.image_output_dir:
            self.image_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize data structures
        self.extracted_data = {"pages": []}
        self.current_section = None
        self.current_subsection = None
        
    def extract_font_sizes(self, page) -> List[float]:
        """
        Extract all font sizes from a page for analysis.
        
        Args:
            page: pdfplumber page object
            
        Returns:
            List of font sizes found on the page
        """
        font_sizes = []
        for char in page.chars:
            if char.get('size'):
                font_sizes.append(char['size'])
        return font_sizes
    
    def detect_headings(self, page, font_sizes: List[float]) -> Dict[str, str]:
        """
        Detect section and subsection headings based on font size and text patterns.
        
        Args:
            page: pdfplumber page object
            font_sizes: List of font sizes from the page
            
        Returns:
            Dictionary mapping text to heading type ('section' or 'subsection')
        """
        if not font_sizes:
            return {}
        
        median_font_size = sorted(font_sizes)[len(font_sizes) // 2]
        large_font_threshold = median_font_size * 1.3
        
        headings = {}
        
        # Group characters into words and lines
        words = page.extract_words()
        lines = []
        current_line = []
        current_y = None
        
        for word in words:
            if current_y is None or abs(word['top'] - current_y) < 5:
                current_line.append(word)
                current_y = word['top']
            else:
                if current_line:
                    lines.append(current_line)
                current_line = [word]
                current_y = word['top']
        
        if current_line:
            lines.append(current_line)
        
        # Analyze each line for headings
        for line in lines:
            if not line:
                continue
                
            text = ' '.join([word['text'] for word in line])
            avg_font_size = sum([word.get('size', 0) for word in line]) / len(line)
            
            # Check for section heading patterns
            is_section = False
            is_subsection = False
            
            # Pattern 1: Large font size
            if avg_font_size > large_font_threshold:
                is_section = True
            
            # Pattern 2: Numbered sections (1., 2., etc.)
            if re.match(r'^\d+\.?\s+', text.strip()):
                is_section = True
            
            # Pattern 3: Numbered subsections (1.1, 1.2, etc.)
            if re.match(r'^\d+\.\d+\.?\s+', text.strip()):
                is_subsection = True
            
            # Pattern 4: ALL CAPS text
            if text.strip().isupper() and len(text.strip()) > 3:
                is_section = True
            
            # Pattern 5: Text ending with colon
            if text.strip().endswith(':'):
                is_section = True
            
            # Pattern 6: Short lines in title case
            if len(text.strip()) < 50 and text.strip().istitle():
                is_section = True
            
            # Assign heading type
            if is_subsection:
                headings[text.strip()] = 'subsection'
            elif is_section:
                headings[text.strip()] = 'section'
        
        return headings
    
    def extract_tables_pdfplumber(self, page) -> List[Dict]:
        """
        Extract tables using pdfplumber.
        
        Args:
            page: pdfplumber page object
            
        Returns:
            List of table dictionaries
        """
        tables = []
        extracted_tables = page.extract_tables()
        
        for i, table in enumerate(extracted_tables):
            if table and len(table) > 1:  # Ensure table has header and data
                table_data = []
                for row in table:
                    if row:  # Skip empty rows
                        table_data.append([cell or '' for cell in row])
                
                if table_data:
                    tables.append({
                        'table_data': table_data,
                        'method': 'pdfplumber'
                    })
        
        return tables
    
    def extract_tables_camelot(self, page_num: int) -> List[Dict]:
        """
        Extract tables using camelot (fallback method).
        
        Args:
            page_num: Page number (0-indexed)
            
        Returns:
            List of table dictionaries
        """
        if not CAMELOT_AVAILABLE:
            return []
        
        tables = []
        try:
            # Extract tables from specific page
            camelot_tables = camelot.read_pdf(str(self.input_path), pages=str(page_num + 1))
            
            for table in camelot_tables:
                if not table.df.empty:
                    table_data = table.df.values.tolist()
                    tables.append({
                        'table_data': table_data,
                        'method': 'camelot'
                    })
        except Exception as e:
            logger.warning(f"Camelot table extraction failed for page {page_num + 1}: {e}")
        
        return tables
    
    def extract_images(self, page_num: int) -> List[Dict]:
        """
        Extract images from PDF page using PyMuPDF.
        
        Args:
            page_num: Page number (0-indexed)
            
        Returns:
            List of image dictionaries
        """
        images = []
        
        try:
            doc = fitz.open(str(self.input_path))
            page = doc[page_num]
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                # Get image data
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)
                
                # Check if image is large enough to be considered a chart
                if pix.width * pix.height > 10000:  # Threshold for chart detection
                    # Save image if output directory specified
                    image_path = None
                    if self.image_output_dir:
                        image_filename = f"extracted_image_page{page_num + 1}_img{img_index}.png"
                        image_path = self.image_output_dir / image_filename
                        pix.save(str(image_path))
                    
                    images.append({
                        'dimensions': [pix.width, pix.height],
                        'image_path': str(image_path) if image_path else None,
                        'area_percentage': (pix.width * pix.height) / (page.rect.width * page.rect.height) * 100
                    })
                
                pix = None  # Free memory
            
            doc.close()
            
        except Exception as e:
            logger.warning(f"Image extraction failed for page {page_num + 1}: {e}")
        
        return images
    
    def perform_ocr_on_image(self, image_path: str) -> str:
        """
        Perform OCR on an image to extract text.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Extracted text from OCR
        """
        if not OCR_AVAILABLE or not self.ocr_enabled:
            return ""
        
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            logger.warning(f"OCR failed for image {image_path}: {e}")
            return ""
    
    def group_text_into_paragraphs(self, page) -> List[str]:
        """
        Group extracted text into paragraphs.
        
        Args:
            page: pdfplumber page object
            
        Returns:
            List of paragraph texts
        """
        text = page.extract_text()
        if not text:
            return []
        
        # Split into paragraphs (double newlines)
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        # Further split by single newlines if paragraphs are too long
        final_paragraphs = []
        for para in paragraphs:
            if len(para) > 500:  # Long paragraph, split by single newlines
                lines = [line.strip() for line in para.split('\n') if line.strip()]
                current_para = ""
                for line in lines:
                    if len(current_para + line) > 500:
                        if current_para:
                            final_paragraphs.append(current_para.strip())
                        current_para = line
                    else:
                        current_para += " " + line if current_para else line
                if current_para:
                    final_paragraphs.append(current_para.strip())
            else:
                final_paragraphs.append(para)
        
        return final_paragraphs
    
    def process_page(self, page_num: int, page) -> Dict:
        """
        Process a single page and extract all content.
        
        Args:
            page_num: Page number (0-indexed)
            page: pdfplumber page object
            
        Returns:
            Dictionary containing page data
        """
        logger.info(f"Processing page {page_num + 1}")
        
        # Extract font sizes for heading detection
        font_sizes = self.extract_font_sizes(page)
        headings = self.detect_headings(page, font_sizes)
        
        # Extract content
        paragraphs = self.group_text_into_paragraphs(page)
        tables = self.extract_tables_pdfplumber(page)
        
        # Fallback to camelot if pdfplumber found no tables
        if not tables:
            tables = self.extract_tables_camelot(page_num)
        
        images = self.extract_images(page_num)
        
        # Build page content
        page_content = []
        
        # Process paragraphs
        for para_text in paragraphs:
            # Check if this paragraph is a heading
            para_type = 'paragraph'
            section = self.current_section
            subsection = self.current_subsection
            
            # Check if paragraph matches any detected heading
            for heading_text, heading_type in headings.items():
                if heading_text in para_text:
                    if heading_type == 'section':
                        self.current_section = heading_text
                        section = heading_text
                        self.current_subsection = None
                        subsection = None
                    elif heading_type == 'subsection':
                        self.current_subsection = heading_text
                        subsection = heading_text
            
            page_content.append({
                'type': para_type,
                'section': section,
                'sub_section': subsection,
                'text': para_text
            })
        
        # Process tables
        for table in tables:
            page_content.append({
                'type': 'table',
                'section': self.current_section,
                'sub_section': self.current_subsection,
                'description': None,
                'table_data': table['table_data']
            })
        
        # Process images/charts
        for img in images:
            description = None
            if img['image_path'] and self.ocr_enabled:
                description = self.perform_ocr_on_image(img['image_path'])
            
            page_content.append({
                'type': 'chart',
                'section': self.current_section,
                'sub_section': self.current_subsection,
                'description': description,
                'dimensions': img['dimensions'],
                'image_path': img['image_path']
            })
        
        return {
            'page_number': page_num + 1,
            'content': page_content
        }
    
    def extract(self) -> Dict:
        """
        Extract content from PDF and return structured data.
        
        Returns:
            Dictionary containing extracted data
        """
        logger.info(f"Starting extraction from {self.input_path}")
        
        try:
            with pdfplumber.open(self.input_path) as pdf:
                total_pages = len(pdf.pages)
                logger.info(f"Found {total_pages} pages")
                
                for page_num, page in enumerate(tqdm(pdf.pages, desc="Processing pages")):
                    page_data = self.process_page(page_num, page)
                    self.extracted_data['pages'].append(page_data)
        
        except Exception as e:
            logger.error(f"Error during PDF extraction: {e}")
            raise
        
        logger.info("Extraction completed successfully")
        return self.extracted_data
    
    def save_json(self) -> None:
        """
        Save extracted data to JSON file.
        """
        logger.info(f"Saving results to {self.output_path}")
        
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(self.extracted_data, f, indent=2, ensure_ascii=False)
        
        logger.info("JSON file saved successfully")


def main():
    """
    Main function to run the PDF to JSON extractor.
    """
    parser = argparse.ArgumentParser(
        description="Extract structured content from PDF files and export to JSON format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pdf_to_json_extractor.py --input sample.pdf --output output.json
  python pdf_to_json_extractor.py --input sample.pdf --output output.json --ocr --image-out extracted_images
  python pdf_to_json_extractor.py -i report.pdf -o report.json --ocr
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Path to input PDF file'
    )
    
    parser.add_argument(
        '--output', '-o',
        required=True,
        help='Path to output JSON file'
    )
    
    parser.add_argument(
        '--ocr',
        action='store_true',
        help='Enable OCR for image-based content'
    )
    
    parser.add_argument(
        '--image-out',
        help='Directory to save extracted images (optional)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate OCR availability
    if args.ocr and not OCR_AVAILABLE:
        logger.error("OCR requested but required libraries not available. Install pytesseract and Pillow.")
        sys.exit(1)
    
    try:
        # Initialize extractor
        extractor = PDFToJSONExtractor(
            input_path=args.input,
            output_path=args.output,
            ocr_enabled=args.ocr,
            image_output_dir=args.image_out
        )
        
        # Extract content
        extractor.extract()
        
        # Save results
        extractor.save_json()
        
        logger.info("PDF to JSON extraction completed successfully!")
        
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
