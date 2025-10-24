## ADDED Requirements
### Requirement: CSV Payment Record Processing
The system SHALL automatically process CSV payment records with operation numbers, links, and calculated amounts.

#### Scenario: Single date processing
- **WHEN** user provides CSV file and transaction image with operation number
- **THEN** system updates CSV with operation number, image link, and calculated amount

#### Scenario: Date range processing with Sunday exclusion
- **WHEN** user provides start and end dates for payment period
- **THEN** system creates rows for each date excluding Sundays
- **AND** each row has progressively discounted amounts ($7 decrement)

#### Scenario: Final row calculation
- **WHEN** processing completes all payment dates
- **THEN** system adds final row with next date, empty link/operation, and final amount minus $7

### Requirement: CSV Data Validation
The system SHALL validate CSV data integrity and format before processing.

#### Scenario: Required fields validation
- **WHEN** CSV file is loaded
- **THEN** system validates presence of startDate, endDate, link, Operation, Amount columns

#### Scenario: Barber identification
- **WHEN** processing CSV files
- **THEN** system identifies target barber (Alejandro, Andres V, David, Genesis) from filename or user input