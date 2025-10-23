## ADDED Requirements

### Requirement: CSV Date Processing
The system SHALL read barber CSV files and extract the most recent payment date from the endDate column.

#### Scenario: Read barber CSV file
- **WHEN** a CSV file is provided for processing
- **THEN** the system SHALL parse the CSV and identify the latest date in the endDate column
- **AND** the system SHALL extract the barber name from the filename

#### Scenario: Handle empty or invalid CSV files
- **WHEN** a CSV file is empty or contains no valid dates
- **THEN** the system SHALL report an error and skip processing that file

### Requirement: Day Count Calculation
The system SHALL calculate the number of days from the last payment date to the current date, excluding Sundays.

#### Scenario: Calculate working days between dates
- **WHEN** calculating days from last payment to current date
- **THEN** the system SHALL count all days except Sundays
- **AND** the system SHALL handle timezone differences correctly

#### Scenario: Handle same-day calculation
- **WHEN** the last payment date is the same as the current date
- **THEN** the system SHALL return 0 days passed

### Requirement: Debt Amount Calculation
The system SHALL calculate the total debt amount based on $7 per day for the calculated working days.

#### Scenario: Calculate debt from days
- **WHEN** the system has calculated the number of working days
- **THEN** the system SHALL multiply days by $7 to get the total debt amount
- **AND** the system SHALL format the amount as a decimal number

#### Scenario: Handle zero debt
- **WHEN** no days have passed since last payment
- **THEN** the system SHALL return $0.00 as the debt amount

### Requirement: Debt CSV Output Generation
The system SHALL generate a new CSV file with the calculated debt information.

#### Scenario: Generate debt report file
- **WHEN** debt calculation is complete for a barber
- **THEN** the system SHALL create a CSV file named "[barber_name]_debt.csv"
- **AND** the file SHALL contain columns for "days_passed" and "debt_amount"
- **AND** the file SHALL be saved in the same directory as the input files

#### Scenario: Format debt report content
- **WHEN** creating the debt CSV file
- **THEN** the system SHALL include a header row
- **AND** the system SHALL write the calculated values in the appropriate columns

### Requirement: Batch Processing
The system SHALL process multiple barber CSV files in a directory.

#### Scenario: Process all barber files
- **WHEN** the script is run with a directory path
- **THEN** the system SHALL process all CSV files in the barbers directory
- **AND** the system SHALL generate a debt report for each barber
- **AND** the system SHALL report the processing summary to the user

#### Scenario: Handle missing directory
- **WHEN** the specified directory does not exist
- **THEN** the system SHALL display an error message and exit gracefully