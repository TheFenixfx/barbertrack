class PaymentChart {
    constructor() {
        this.data = null;
        this.pixelsPerDay = 40; // Height of each day in pixels
        this.dateRange = { start: null, end: null };
        this.init();
    }

    async init() {
        try {
            await this.fetchData();
            this.calculateDateRange();
            this.renderChart();
            this.hideLoading();
        } catch (error) {
            this.showError();
            console.error('Error initializing chart:', error);
        }
    }

    async fetchData() {
        const response = await fetch('/api/chartdata');
        if (!response.ok) {
            throw new Error('Failed to fetch chart data');
        }
        this.data = await response.json();
    }

    calculateDateRange() {
        let allDates = [];
        
        Object.values(this.data.teams).forEach(team => {
            team.forEach(payment => {
                // Create dates at midnight to avoid timezone issues
                const startDate = new Date(payment.startDate + 'T00:00:00');
                const endDate = new Date(payment.endDate + 'T00:00:00');
                allDates.push(startDate);
                allDates.push(endDate);
            });
        });

        if (allDates.length === 0) {
            // Default range if no data
            this.dateRange.start = new Date('2025-08-01T00:00:00');
            this.dateRange.end = new Date('2025-08-31T00:00:00');
        } else {
            this.dateRange.start = new Date(Math.min(...allDates));
            this.dateRange.end = new Date(Math.max(...allDates));
            
            // Add some padding (1 day before and after)
            const paddedStart = new Date(this.dateRange.start);
            paddedStart.setDate(paddedStart.getDate() - 1);
            this.dateRange.start = paddedStart;
            
            const paddedEnd = new Date(this.dateRange.end);
            paddedEnd.setDate(paddedEnd.getDate() + 1);
            this.dateRange.end = paddedEnd;
        }
        
        // Ensure both dates are set to midnight
        this.dateRange.start.setHours(0, 0, 0, 0);
        this.dateRange.end.setHours(0, 0, 0, 0);
    }

    formatDateForDisplay(date) {
        const day = date.getDate().toString().padStart(2, '0');
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const year = date.getFullYear().toString().slice(-2);
        return `${day}/${month}/${year}`;
    }

    formatDateForWhatsApp(date) {
        const day = date.getDate().toString().padStart(2, '0');
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const year = date.getFullYear();
        return `${day}/${month}/${year}`;
    }

    getDaysSinceStart(date) {
        const targetDate = new Date(date);
        const startDate = new Date(this.dateRange.start);
        
        // Reset time to midnight for accurate day calculation
        targetDate.setHours(0, 0, 0, 0);
        startDate.setHours(0, 0, 0, 0);
        
        const timeDiff = targetDate.getTime() - startDate.getTime();
        return Math.floor(timeDiff / (1000 * 60 * 60 * 24));
    }

    createWhatsAppLink(teamName, startDate, endDate) {
        const start = this.formatDateForWhatsApp(new Date(startDate));
        const end = this.formatDateForWhatsApp(new Date(endDate));
        const message = `Payment details for ${teamName} - Period: ${start} to ${end}`;
        return `https://wa.me/04162069479?text=${encodeURIComponent(message)}`;
    }

    renderTimeline() {
        const timelineAxis = document.getElementById('timelineAxis');
        const totalDays = this.getDaysSinceStart(this.dateRange.end) + 1;
        const totalHeight = totalDays * this.pixelsPerDay;
        
        timelineAxis.style.height = `${totalHeight + 60}px`; // +60 for header space
        timelineAxis.innerHTML = '';

        // Add grid lines and date labels
        let currentDate = new Date(this.dateRange.start);
        while (currentDate <= this.dateRange.end) {
            const dayIndex = this.getDaysSinceStart(currentDate);
            const topPosition = dayIndex * this.pixelsPerDay + 60; // +60 for header space

            // Create date label
            const dateLabel = document.createElement('div');
            dateLabel.className = 'date-label';
            dateLabel.style.top = `${topPosition}px`;
            dateLabel.textContent = this.formatDateForDisplay(currentDate);
            timelineAxis.appendChild(dateLabel);

            // Create grid line
            const gridLine = document.createElement('div');
            gridLine.className = 'grid-line';
            gridLine.style.top = `${topPosition}px`;
            timelineAxis.appendChild(gridLine);

            currentDate.setDate(currentDate.getDate() + 1);
        }
    }

    renderTeamColumn(teamName, payments) {
        const column = document.createElement('div');
        column.className = 'team-column';
        
        const totalDays = this.getDaysSinceStart(this.dateRange.end) + 1;
        const totalHeight = totalDays * this.pixelsPerDay + 60;
        column.style.height = `${totalHeight}px`;

        // Team header
        const header = document.createElement('div');
        header.className = 'team-header';
        header.textContent = teamName;
        column.appendChild(header);

        // Payment blocks
        payments.forEach((payment, index) => {
            // Parse dates consistently with calculateDateRange
            const startDate = new Date(payment.startDate + 'T00:00:00');
            const endDate = new Date(payment.endDate + 'T00:00:00');
            const startDay = this.getDaysSinceStart(startDate);
            const endDay = this.getDaysSinceStart(endDate);
            const duration = endDay - startDay + 1;

            const block = document.createElement('a');
            block.className = 'payment-block';
            block.style.top = `${startDay * this.pixelsPerDay + 60}px`; // +60 for header
            block.style.height = `${duration * this.pixelsPerDay - 4}px`; // -4 for spacing
            
            // Create WhatsApp link instead of using the original link
            const whatsappLink = this.createWhatsAppLink(teamName, payment.startDate, payment.endDate);
            block.href = whatsappLink;
            block.target = '_blank';
            block.rel = 'noopener noreferrer';
            
            // Block content
            const startFormatted = this.formatDateForDisplay(startDate);
            const endFormatted = this.formatDateForDisplay(endDate);
            block.innerHTML = `
                <div>
                    <div style="font-size: 11px; margin-bottom: 2px;">${startFormatted}</div>
                    <div style="font-size: 10px; opacity: 0.9;">to</div>
                    <div style="font-size: 11px; margin-top: 2px;">${endFormatted}</div>
                </div>
            `;

            column.appendChild(block);
        });

        return column;
    }

    renderChart() {
        this.renderTimeline();

        const chartArea = document.getElementById('chartArea');
        chartArea.innerHTML = '';

        const teams = this.data.teams;
        Object.entries(teams).forEach(([teamName, payments]) => {
            const column = this.renderTeamColumn(teamName, payments);
            chartArea.appendChild(column);
        });

        // Synchronize scrolling between timeline and chart area
        this.synchronizeScrolling();
    }

    synchronizeScrolling() {
        const timelineAxis = document.getElementById('timelineAxis');
        const chartArea = document.getElementById('chartArea');

        const syncScroll = (source, target) => {
            source.addEventListener('scroll', () => {
                target.scrollTop = source.scrollTop;
            });
        };

        syncScroll(timelineAxis, chartArea);
        syncScroll(chartArea, timelineAxis);
    }

    hideLoading() {
        document.getElementById('loading').style.display = 'none';
        document.querySelector('.chart-container').style.display = 'flex';
    }

    showError() {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('error').style.display = 'block';
    }
}

// Initialize the chart when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PaymentChart();
});
