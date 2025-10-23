# Project Context

## Purpose
Payment Chart Application is a web-based visualization tool for tracking payment periods across different teams/individuals. The application displays payment status as interactive timeline blocks, with each team having its own column showing payment periods. Users can click on payment blocks to open WhatsApp messages with payment details. The system is designed for small business payment tracking, particularly for service-based businesses like barber shops.

## Tech Stack
- **Backend**: Node.js with Express.js framework
- **Frontend**: Vanilla JavaScript (ES6+), HTML5, CSS3
- **Data Storage**: JSON file-based storage (data.json)
- **Deployment**: Static file serving with Express
- **External Integration**: WhatsApp API for payment notifications
- **Package Manager**: npm

## Project Conventions

### Code Style
- **JavaScript**: ES6+ class-based syntax, camelCase naming, async/await for asynchronous operations
- **File Structure**: Flat structure with clear separation (server.js, public/, data.json)
- **Naming Conventions**:
  - Classes: PascalCase (PaymentChart)
  - Functions/Variables: camelCase
  - Constants: UPPER_SNAKE_CASE
- **Comments**: JSDoc-style comments for complex methods
- **Error Handling**: Try-catch blocks with user-friendly error messages

### Architecture Patterns
- **MVC-like Separation**: Server handles data and routing, frontend handles presentation
- **Component-based Frontend**: PaymentChart class encapsulates all chart functionality
- **RESTful API**: Single GET endpoint for data retrieval
- **Event-driven**: DOM event listeners for user interactions
- **Data Flow**: Unidirectional data flow from JSON file → API → Frontend → DOM

### Testing Strategy
- No automated testing currently implemented
- Manual testing through browser interaction
- Error handling tested through invalid data scenarios
- Cross-browser compatibility testing required

### Git Workflow
- **Current Branch**: `montos` feature branch
- **Commit Convention**: Simple descriptive messages (e.g., "calculo", "saving")
- **No CI/CD**: Manual deployment and testing
- **File-based Version Control**: Changes tracked through git, data updates through data.json

## Domain Context
- **Business Type**: Service-based payment tracking (barber shop context)
- **Payment Periods**: Daily payment tracking with backup image references
- **Teams**: Individual service providers (e.g., Alejandro, other barbers)
- **Data Structure**: Each payment has startDate, endDate, backup image link, and optional operation/amount fields
- **WhatsApp Integration**: Venezuelan phone number (+58 416 206 9479) for payment notifications
- **Date Format**: International format (YYYY-MM-DD) for data, display format (dd/mm/yy) for users

## Important Constraints
- **File-based Storage**: All data stored in single JSON file, requiring server restart for updates
- **No Database**: Limited scalability due to file-based approach
- **Single User**: Designed for single business owner use
- **Manual Data Updates**: Payment data must be manually edited in JSON file
- **WhatsApp Dependency**: Relies on WhatsApp being installed on user's device
- **Timezone Handling**: Uses midnight timestamp normalization to avoid timezone issues
- **Static Design**: No user authentication or role-based access

## External Dependencies
- **Express.js**: Web server framework (v4.18.2)
- **Node.js**: Runtime environment
- **WhatsApp Web**: External service for payment notifications
- **File System**: Local file system for data.json storage
- **Browser APIs**: Fetch API, DOM manipulation, CSS Grid/Flexbox
