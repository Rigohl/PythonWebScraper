# Export Capabilities Documentation

This document outlines the export functionality available in the Web Scraper PRO system.

## Overview

The system provides two distinct export implementations:

1. **Core Data Export** (database.py)
   - Focused on raw data export from the database
   - Supports CSV, JSON, and Markdown formats
   - Uses dataset package for data access
   - Handles field serialization and data flattening

2. **Search Results Export** (intelligent_search.py)
   - Specialized for exporting intelligent search results
   - Rich formatting with detailed sections
   - Supports Markdown, Text, JSON, and HTML formats
   - Includes styling and structured presentation

## Export Formats

### Core Data Export

- **CSV Format**
  - Comma-separated values
  - Handles field serialization
  - Suitable for spreadsheet imports
  - Uses Python's built-in csv module

- **JSON Format**
  - Complete data serialization
  - Preserves nested structures
  - Suitable for API integration
  - Uses Python's json module with proper encoding

- **Markdown Format**
  - Basic table formatting
  - Readable plain text output
  - Suitable for documentation
  - Headers and cell alignment

### Search Results Export

- **Markdown Format**
  - Rich section formatting
  - Executive summary
  - Key points listing
  - Source details and quality metrics
  - Recommended actions

- **Text Format**
  - Simple plain text
  - Section headers
  - Basic formatting
  - Summary and key points

- **JSON Format**
  - Complete data structure
  - All search session details
  - Raw and processed results
  - Analysis and metrics

- **HTML Format**
  - Styled presentation
  - CSS formatting
  - Interactive elements
  - Mobile-friendly layout

## Usage Examples

### Core Data Export

```python
# Export database table to CSV
db.export_to_csv('scraped_data', 'exports/data.csv')

# Export to JSON with custom filters
db.export_to_json('scraped_data', 'exports/filtered.json',
                 filters={'status': 'completed'})

# Export to Markdown table
db.export_to_markdown('scraped_data', 'exports/table.md')
```

### Search Results Export

```python
exporter = SearchResultsExporter()

# Export search results with default markdown format
path = exporter.export_search_results(search_session)

# Export as HTML report
path = exporter.export_search_results(search_session,
                                    format_type='html',
                                    output_path='exports/report.html')
```

## Directory Structure

Exports are organized in the following structure:

```
exports/
  ├── scrape_results_[DATE].csv      # Database exports
  ├── scrape_results_[DATE].json
  ├── search_[TOPIC]_[TIMESTAMP].md  # Search results
  ├── reports/                       # Generated reports
  │   ├── daily/
  │   └── weekly/
  └── test_exports/                  # Test outputs
```

## Output File Naming

- **Database Exports**
  - Format: `scrape_results_YYYY-MM-DD.{format}`
  - Example: `scrape_results_2025-09-02.csv`

- **Search Results**
  - Format: `search_[topic]_YYYYMMDD_HHMMSS.{format}`
  - Example: `search_python_scraping_20250902_143022.md`

## Data Format Specifications

### CSV Format
- UTF-8 encoding
- Comma delimiter
- Double quote escaping
- Headers included
- Newline: \n (Unix style)

### JSON Format
- UTF-8 encoding
- Pretty printed (indented)
- ensure_ascii=False
- Date format: ISO 8601

### Markdown Format
- GitHub Flavored Markdown
- Table alignment support
- Proper escaping of special characters
- Consistent header levels

### HTML Format
- HTML5 doctype
- Responsive CSS
- UTF-8 meta tag
- Basic styling included

## Integration

When exporting search results that reference database content:

1. Use the database export functions to export the raw data
2. Use the search exporter to create the report
3. Link the exports in the metadata section

Example integration:

```python
# Export referenced data
data_export = db.export_to_json('search_results', 'exports/raw_data.json')

# Create search report with reference
search_session['data_export'] = data_export
report = exporter.export_search_results(search_session, 'md')
```

## Error Handling

Both exporters include comprehensive error handling:

1. Directory creation errors
2. File permission issues
3. Data serialization errors
4. Format validation
5. Resource cleanup

Errors are logged and raised with descriptive messages to aid debugging.

## Best Practices

1. Always use absolute paths or Path objects for output locations
2. Create parent directories before export
3. Validate export format before processing
4. Log export operations for auditing
5. Clean up temporary files
6. Use context managers for file operations
7. Handle large datasets in chunks when needed
8. Validate output after export
