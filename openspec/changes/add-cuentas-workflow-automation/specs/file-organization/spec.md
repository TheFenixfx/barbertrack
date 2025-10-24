## ADDED Requirements
### Requirement: Image File Organization
The system SHALL organize transaction images from unorganized folder to structured barber directories.

#### Scenario: Image file moving
- **WHEN** operation number is extracted from image
- **THEN** system moves image using PowerShell command: `Move-Item -LiteralPath "unorganized\*" -Destination "barber\<OPERATION NUMBER>.jpg"`
- **AND** uses the new path for CSV link column

#### Scenario: Path generation
- **WHEN** image is moved to organized location
- **THEN** system generates correct path format: `E:\Projects\Barberia\payment-chart-app\<barber-name>\<OPERATION NUMBER>.jpg`
- **AND** populates link column for each date row

### Requirement: File System Validation
The system SHALL validate file operations and handle errors gracefully.

#### Scenario: Source file validation
- **WHEN** processing begins
- **THEN** system verifies image exists in unorganized folder
- **AND** confirms file accessibility

#### Scenario: Destination directory creation
- **WHEN** moving image to barber folder
- **THEN** system creates destination directory if it doesn't exist
- **AND** ensures proper permissions for file operations