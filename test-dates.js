// Simple test to verify date calculations work correctly
// This file is just for testing - not part of the main application

function testDateCalculations() {
    console.log('Testing date calculations across month boundaries...\n');
    
    // Test data similar to what's causing issues
    const testData = {
        teams: {
            "Test Team": [
                { "startDate": "2025-07-31", "endDate": "2025-08-02", "link": "test" }
            ]
        }
    };
    
    // Simulate the calculateDateRange logic
    let allDates = [];
    
    Object.values(testData.teams).forEach(team => {
        team.forEach(payment => {
            const startDate = new Date(payment.startDate + 'T00:00:00');
            const endDate = new Date(payment.endDate + 'T00:00:00');
            console.log(`Original dates: ${payment.startDate} to ${payment.endDate}`);
            console.log(`Parsed start: ${startDate.toISOString()}`);
            console.log(`Parsed end: ${endDate.toISOString()}`);
            allDates.push(startDate);
            allDates.push(endDate);
        });
    });
    
    const dateRange = {
        start: new Date(Math.min(...allDates)),
        end: new Date(Math.max(...allDates))
    };
    
    // Add padding
    const paddedStart = new Date(dateRange.start);
    paddedStart.setDate(paddedStart.getDate() - 1);
    dateRange.start = paddedStart;
    
    const paddedEnd = new Date(dateRange.end);
    paddedEnd.setDate(paddedEnd.getDate() + 1);
    dateRange.end = paddedEnd;
    
    // Ensure midnight
    dateRange.start.setHours(0, 0, 0, 0);
    dateRange.end.setHours(0, 0, 0, 0);
    
    console.log(`\nCalculated range: ${dateRange.start.toISOString()} to ${dateRange.end.toISOString()}`);
    
    // Test getDaysSinceStart function
    function getDaysSinceStart(date, startDate) {
        const targetDate = new Date(date);
        const start = new Date(startDate);
        
        targetDate.setHours(0, 0, 0, 0);
        start.setHours(0, 0, 0, 0);
        
        const timeDiff = targetDate.getTime() - start.getTime();
        return Math.floor(timeDiff / (1000 * 60 * 60 * 24));
    }
    
    // Test specific dates
    const testStartDate = new Date('2025-07-31T00:00:00');
    const testEndDate = new Date('2025-08-02T00:00:00');
    
    const startDay = getDaysSinceStart(testStartDate, dateRange.start);
    const endDay = getDaysSinceStart(testEndDate, dateRange.start);
    const duration = endDay - startDay + 1;
    
    console.log(`\nTest payment block:`);
    console.log(`Start day index: ${startDay}`);
    console.log(`End day index: ${endDay}`);
    console.log(`Duration: ${duration} days`);
    
    // Format dates for display
    function formatDateForDisplay(date) {
        const day = date.getDate().toString().padStart(2, '0');
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const year = date.getFullYear().toString().slice(-2);
        return `${day}/${month}/${year}`;
    }
    
    console.log(`Display format: ${formatDateForDisplay(testStartDate)} to ${formatDateForDisplay(testEndDate)}`);
    
    console.log('\n✓ Date calculations completed successfully!');
}

// Run the test
testDateCalculations();
