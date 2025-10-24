## ADDED Requirements
### Requirement: OCR Operation Number Extraction
The system SHALL extract operation numbers from transaction images using OCR technology.

#### Scenario: Image OCR processing
- **WHEN** transaction image (JPEG/PNG) is provided
- **THEN** system performs OCR to extract operation number
- **AND** validates extracted operation number format

#### Scenario: Unorganized image detection
- **WHEN** processing starts
- **THEN** system locates single image in "unorganized" folder
- **AND** uses it for OCR processing

### Requirement: OCR Result Validation
The system SHALL validate and handle OCR extraction results.

#### Scenario: Successful extraction
- **WHEN** OCR successfully extracts operation number
- **THEN** system formats and validates the operation number
- **AND** prepares it for CSV processing

#### Scenario: OCR failure handling
- **WHEN** OCR fails to extract operation number
- **THEN** system prompts user for manual operation number input
- **AND** allows retry with different image