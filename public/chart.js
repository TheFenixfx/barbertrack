class PaymentChart {
    constructor() {
        this.data = null;
        this.debtData = null;
        this.pixelsPerDay = 40; // Height of each day in pixels
        this.dateRange = { start: null, end: null };
        this.modalKeyHandler = null;
        this.downloadableBarbers = new Set(['Alejandro', 'Andres', 'David', 'Genesis']);
        this.init();
    }

    async init() {
        try {
            await this.fetchData();
            this.calculateDateRange();
            this.renderChart();
            this.hideLoading();
            this.setupDebtModal();
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

    // Calculate position from bottom (inverted Y-axis)
    getPositionFromBottom(date, totalDays) {
        const daysSinceStart = this.getDaysSinceStart(date);
        // Invert the position: latest dates at bottom (position 0), oldest at top
        return (totalDays - 1 - daysSinceStart) * this.pixelsPerDay;
    }

    createWhatsAppLink(teamName, startDate, endDate) {
        const start = this.formatDateForWhatsApp(new Date(startDate));
        const end = this.formatDateForWhatsApp(new Date(endDate));
        const message = `Payment details for ${teamName} - Period: ${start} to ${end}`;
        return `https://wa.me/04162069479?text=${encodeURIComponent(message)}`;
    }

    getDownloadUrl(teamName) {
        if (!this.downloadableBarbers.has(teamName)) {
            return null;
        }
        return `/downloads/${encodeURIComponent(teamName)}`;
    }

    renderTimeline() {
        const timelineAxis = document.getElementById('timelineAxis');
        const totalDays = this.getDaysSinceStart(this.dateRange.end) + 1;
        const totalHeight = totalDays * this.pixelsPerDay;
        
        timelineAxis.style.height = `${totalHeight + 60}px`; // +60 for header space
        timelineAxis.innerHTML = '';

        // Add grid lines and date labels (from bottom to top)
        let currentDate = new Date(this.dateRange.start);
        while (currentDate <= this.dateRange.end) {
            // Use inverted positioning: most recent dates at bottom
            const bottomPosition = this.getPositionFromBottom(currentDate, totalDays) + 60; // +60 for header space

            // Create date label
            const dateLabel = document.createElement('div');
            dateLabel.className = 'date-label';
            dateLabel.style.top = `${bottomPosition}px`;
            dateLabel.textContent = this.formatDateForDisplay(currentDate);
            timelineAxis.appendChild(dateLabel);

            // Create grid line
            const gridLine = document.createElement('div');
            gridLine.className = 'grid-line';
            gridLine.style.top = `${bottomPosition}px`;
            timelineAxis.appendChild(gridLine);

            currentDate.setDate(currentDate.getDate() + 1);
        }
    }

    renderTeamColumn(teamName, payments, mostRecent) {
        const column = document.createElement('div');
        column.className = 'team-column';
        
        const totalDays = this.getDaysSinceStart(this.dateRange.end) + 1;
        const totalHeight = totalDays * this.pixelsPerDay + 60;
        column.style.height = `${totalHeight}px`;

        // Team header
        const header = document.createElement('div');
        header.className = 'team-header';

        const downloadUrl = this.getDownloadUrl(teamName);
        const titleElement = document.createElement(downloadUrl ? 'a' : 'span');
        titleElement.className = 'team-name';
        titleElement.textContent = teamName;

        if (downloadUrl) {
            titleElement.href = downloadUrl;
            titleElement.setAttribute('download', `${teamName}.csv`);
        }

        header.appendChild(titleElement);
        column.appendChild(header);

        // Payment blocks
        payments.forEach((payment, index) => {
            // Parse dates consistently with calculateDateRange
            const startDate = new Date(payment.startDate + 'T00:00:00');
            const endDate = new Date(payment.endDate + 'T00:00:00');
            const duration = this.getDaysSinceStart(endDate) - this.getDaysSinceStart(startDate) + 1;

            const block = document.createElement('a');
            block.className = 'payment-block';
            
            // Check if this is the most recent payment for this team
            const teamMostRecent = mostRecent[teamName];
            const isTheMostRecent = teamMostRecent && teamMostRecent.index === index;
            
            if (isTheMostRecent) {
                block.classList.add('most-recent');
            }
            
            // Use inverted positioning: calculate from bottom
            const blockBottomPosition = this.getPositionFromBottom(endDate, totalDays) + 60; // +60 for header
            block.style.top = `${blockBottomPosition}px`;
            block.style.height = `${duration * this.pixelsPerDay - 4}px`; // -4 for spacing
            
            // Create WhatsApp link instead of using the original link
            const whatsappLink = this.createWhatsAppLink(teamName, payment.startDate, payment.endDate);
            block.href = whatsappLink;
            block.target = '_blank';
            block.rel = 'noopener noreferrer';
            
            // Block content
            const startFormatted = this.formatDateForDisplay(startDate);
            const endFormatted = this.formatDateForDisplay(endDate);
            
            //<div style="font-size: 10px; opacity: 0.9;">to</div>
            //<div style="font-size: 11px; margin-top: 2px;">${endFormatted}</div>
            block.innerHTML = `
                <div>
                    <div style="font-size: 11px; margin-bottom: 2px;">${startFormatted}</div>
                    
                </div>
            `;

            column.appendChild(block);
        });

        return column;
    }

    findMostRecentPaymentPerTeam() {
        const mostRecentPerTeam = {};

        Object.entries(this.data.teams).forEach(([teamName, payments]) => {
            if (payments.length === 0) return;
            
            let teamMostRecent = null;
            let teamMostRecentDate = null;
            let teamMostRecentIndex = -1;

            payments.forEach((payment, index) => {
                const endDate = new Date(payment.endDate + 'T00:00:00');
                if (!teamMostRecentDate || endDate > teamMostRecentDate) {
                    teamMostRecentDate = endDate;
                    teamMostRecent = payment;
                    teamMostRecentIndex = index;
                }
            });

            mostRecentPerTeam[teamName] = {
                payment: teamMostRecent,
                index: teamMostRecentIndex,
                date: teamMostRecentDate
            };
        });

        return mostRecentPerTeam;
    }

    renderChart() {
        this.renderTimeline();

        const chartArea = document.getElementById('chartArea');
        chartArea.innerHTML = '';

        // Find the most recent payment for each team individually
        const mostRecentPerTeam = this.findMostRecentPaymentPerTeam();

        const teams = this.data.teams;
        Object.entries(teams).forEach(([teamName, payments]) => {
            const column = this.renderTeamColumn(teamName, payments, mostRecentPerTeam);
            chartArea.appendChild(column);
        });

        // Synchronize scrolling between timeline and chart area
        this.synchronizeScrolling();
        
        // Scroll to bottom to show most recent items by default
        this.scrollToBottom();
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

    scrollToBottom() {
        // Scroll to bottom to show most recent items (they are positioned at the bottom)
        const timelineAxis = document.getElementById('timelineAxis');
        const chartArea = document.getElementById('chartArea');
        
        // Use setTimeout to ensure DOM is fully rendered
        setTimeout(() => {
            timelineAxis.scrollTop = timelineAxis.scrollHeight;
            chartArea.scrollTop = chartArea.scrollHeight;
        }, 100);
    }

    hideLoading() {
        document.getElementById('loading').style.display = 'none';
        document.querySelector('.chart-container').style.display = 'flex';
    }

    showError() {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('error').style.display = 'block';
    }

    async fetchDebtData() {
        const response = await fetch('/api/debts');
        if (!response.ok) {
            throw new Error('Failed to fetch debt data');
        }
        const payload = await response.json();
        return payload.debts || [];
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2
        }).format(amount);
    }

    setupDebtModal() {
        const button = document.getElementById('debtSummaryButton');
        const modal = document.getElementById('debtModal');
        const modalBody = document.getElementById('debtModalBody');
        const closeTargets = modal.querySelectorAll('[data-modal-close]');

        if (!button || !modal || !modalBody) {
            return;
        }

        const openModal = () => {
            modal.classList.add('active');
            modal.setAttribute('aria-hidden', 'false');

            this.modalKeyHandler = (event) => {
                if (event.key === 'Escape') {
                    closeModal();
                }
            };

            document.addEventListener('keydown', this.modalKeyHandler);
        };

        const closeModal = () => {
            modal.classList.remove('active');
            modal.setAttribute('aria-hidden', 'true');

            if (this.modalKeyHandler) {
                document.removeEventListener('keydown', this.modalKeyHandler);
                this.modalKeyHandler = null;
            }
        };

        const renderModalContent = (debts) => {
            if (!debts.length) {
                modalBody.innerHTML = '<p>No hay datos de deudas disponibles.</p>';
                return;
            }

            const listItems = debts
                .map((debt) => {
                    const amount = this.formatCurrency(debt.amount);
                    return `
                        <li>
                            <span class="debt-name">${debt.name}</span>
                            <span class="debt-amount">${amount}</span>
                            <span class="debt-days">${debt.days} días</span>
                        </li>
                    `;
                })
                .join('');

            modalBody.innerHTML = `
                <ul class="debt-list">
                    ${listItems}
                </ul>
            `;
        };

        button.addEventListener('click', async () => {
            try {
                if (!this.debtData) {
                    modalBody.innerHTML = '<p>Cargando deudas...</p>';
                    this.debtData = await this.fetchDebtData();
                }

                renderModalContent(this.debtData);
                openModal();
            } catch (error) {
                console.error('Error loading debt data:', error);
                modalBody.innerHTML = '<p>Error al cargar las deudas. Inténtalo nuevamente.</p>';
                openModal();
            }
        });

        closeTargets.forEach((target) => {
            target.addEventListener('click', closeModal);
        });
    }
}

// Initialize the chart when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PaymentChart();
});
