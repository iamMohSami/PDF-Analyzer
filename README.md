# PDF to JSON Extracto

A comprehensive Python tool for extracting structured content from PDF files and exporting to JSON format while preserving page hierarchy, sections, subsections, and content types.

## Features

- **Hierarchical Content Extraction**: Preserves page → section → subsection → content block structure
- **Multiple Content Types**: Extracts paragraphs, tables, and charts/images
- **Smart Heading Detection**: Uses font size analysis and text patterns to identify sections/subsections
- **Advanced Table Extraction**: Primary extraction with pdfplumber, fallback to camelot
- **Image/Chart Extraction**: Extracts images using PyMuPDF with configurable size thresholds
- **OCR Support**: Optional OCR for image-based content using Tesseract
- **Clean JSON Output**: Well-structured JSON with proper indentation
- **Robust Error Handling**: Graceful handling of various PDF formats and edge cases

## Installation

### Prerequisites

This tool requires Python 3.8+ and several external dependencies:

#### System Dependencies

**Windows:**
```bash
# Install Ghostscript (required for camelot)
# Download from: https://www.ghostscript.com/download/gsdnld.html

# Install Tesseract (required for OCR)
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

**macOS:**
```bash
# Install Ghostscript
brew install ghostscript

# Install Tesseract
brew install tesseract
```

**Linux (Ubuntu/Debian):**
```bash
# Install Ghostscript
sudo apt-get install ghostscript

# Install Tesseract
sudo apt-get install tesseract-ocr
```

#### Python Dependencies

Create a virtual environment and install the required packages:

```bash
# Create virtual environment
python -m venv pdf_extractor_env

# Activate virtual environment
# Windows:
pdf_extractor_env\Scripts\activate
# macOS/Linux:
source pdf_extractor_env/bin/activate

# Install required packages
pip install pdfplumber PyMuPDF pandas tqdm

# Optional: Install camelot for advanced table extraction
pip install camelot-py[cv]

# Optional: Install OCR dependencies
pip install pytesseract Pillow
```

### Complete Installation Script

For a complete setup, you can use this script:

```bash
# Install all dependencies (including optional ones)
pip install pdfplumber PyMuPDF pandas tqdm camelot-py[cv] pytesseract Pillow
```

## Usage

### Basic Usage

```bash
python pdf_to_json_extractor.py --input sample.pdf --output output.json
```

### Advanced Usage

```bash
# Extract with OCR and save images
python pdf_to_json_extractor.py --input sample.pdf --output output.json --ocr --image-out extracted_images

# Verbose output
python pdf_to_json_extractor.py --input sample.pdf --output output.json --verbose
```

### Command Line Arguments

| Argument | Short | Required | Description |
|----------|-------|----------|-------------|
| `--input` | `-i` | Yes | Path to input PDF file |
| `--output` | `-o` | Yes | Path to output JSON file |
| `--ocr` | | No | Enable OCR for image-based content |
| `--image-out` | | No | Directory to save extracted images |
| `--verbose` | `-v` | No | Enable verbose logging |

## Output Format

The tool generates a structured JSON file with the following format:

```json
{
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
          "sub_section": null,
          "description": null,
          "table_data": [
            ["Year", "Revenue", "Profit"],
            ["2022", "$10M", "$2M"],
            ["2023", "$12M", "$3M"]
          ]
        },
        {
          "type": "chart",
          "section": "Performance Overview",
          "sub_section": null,
          "description": "Bar chart showing yearly growth...",
          "dimensions": [800, 600],
          "image_path": "extracted_images/extracted_image_page1_img0.png"
        }
      ]
    }
  ]
}
```

### Content Types

1. **Paragraph**: Regular text content
   - `type`: "paragraph"
   - `text`: Extracted text content
   - `section`: Current section heading
   - `sub_section`: Current subsection heading

2. **Table**: Tabular data
   - `type`: "table"
   - `table_data`: 2D array of table cells
   - `section`: Current section heading
   - `sub_section`: Current subsection heading

3. **Chart**: Images and charts
   - `type`: "chart"
   - `dimensions`: [width, height] in pixels
   - `image_path`: Path to saved image file (if `--image-out` specified)
   - `description`: OCR-extracted text (if `--ocr` enabled)
   - `section`: Current section heading
   - `sub_section`: Current subsection heading

## How It Works

### Heading Detection

The tool uses multiple heuristics to detect section and subsection headings:

1. **Font Size Analysis**: Text with font size > 130% of median is considered a heading
2. **Numbered Sections**: Text starting with "1.", "2.", etc.
3. **Numbered Subsections**: Text starting with "1.1", "1.2", etc.
4. **ALL CAPS**: Text in all uppercase (length > 3)
5. **Colon Endings**: Text ending with ":"
6. **Title Case**: Short lines in title case

### Table Extraction

1. **Primary Method**: Uses `pdfplumber.extract_tables()` for basic table extraction
2. **Fallback Method**: Uses `camelot.read_pdf()` for complex tables if pdfplumber fails
3. **Validation**: Ensures tables have headers and data rows

### Image/Chart Extraction

1. **Detection**: Extracts images using PyMuPDF
2. **Filtering**: Only saves images above size threshold (>10,000 pixels)
3. **OCR**: Optional text extraction from images using Tesseract
4. **Storage**: Saves images to specified directory with descriptive filenames

## Examples

### Example 1: Basic Extraction

```bash
python pdf_to_json_extractor.py --input financial_report.pdf --output report.json
```

### Example 2: Full Extraction with OCR and Images

```bash
python pdf_to_json_extractor.py \
  --input technical_document.pdf \
  --output document.json \
  --ocr \
  --image-out charts_and_diagrams
```

### Example 3: Verbose Processing

```bash
python pdf_to_json_extractor.py \
  --input large_document.pdf \
  --output structured_data.json \
  --verbose
```

## Troubleshooting

### Common Issues

1. **"Ghostscript not found"**
   - Install Ghostscript system dependency
   - Ensure it's in your system PATH

2. **"Tesseract not found"**
   - Install Tesseract OCR
   - Ensure it's in your system PATH

3. **"Camelot import error"**
   - Install camelot-py: `pip install camelot-py[cv]`
   - Install OpenCV: `pip install opencv-python`

4. **"Permission denied" errors**
   - Ensure write permissions for output directory
   - Run with appropriate user permissions

5. **Empty or malformed JSON output**
   - Check if PDF is password-protected
   - Verify PDF is not corrupted
   - Try with `--verbose` flag for debugging

### Performance Tips

1. **Large PDFs**: The tool processes pages sequentially with progress bars
2. **Memory Usage**: Images are processed and freed immediately to minimize memory usage
3. **OCR Performance**: OCR can be slow; use only when necessary
4. **Table Extraction**: Camelot fallback may be slower but more accurate for complex tables

## Dependencies

### Required
- `pdfplumber`: PDF text and table extraction
- `PyMuPDF (fitz)`: Image extraction
- `pandas`: Data manipulation
- `tqdm`: Progress bars

### Optional
- `camelot-py`: Advanced table extraction
- `pytesseract`: OCR functionality
- `Pillow`: Image processing for OCR

## License

This project is open source. Feel free to modify and distribute according to your needs.

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## Version History

- **v1.0.0**: Initial release with full PDF to JSON extraction capabilities
  - Hierarchical content extraction
  - Multiple content type support
  - Advanced heading detection
  - Table extraction with fallback
  - Image/chart extraction
  - OCR support
  - Comprehensive error handling
