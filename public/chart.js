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

    /**
     * Get daily rate for a barber based on year.
     * 2025: $7 for barbers, $5 for Genesis
     * 2026: $8 for barbers, $6 for Genesis
     */
    getDailyRateForBarberAndYear(barberName, year) {
        const isGenesis = barberName.toLowerCase() === 'genesis';
        if (year === 2025) {
            return isGenesis ? 5 : 7;
        }
        return isGenesis ? 6 : 8;
    }

    /**
     * Calculate how many working days a payment covers based on its amount.
     * A payment of $48 at $8/day covers exactly 6 working days.
     * Sundays are NOT charge days and don't consume from balance.
     * Post-payment: payment on April 11 covers April 11, 10, 9, 8 (skip Sun 7), 6, 5.
     */
    calculatePaymentDays(payment, barberName) {
        const amount = parseFloat(payment.Amount) || 0;
        if (amount <= 0) {
            return 1; // Zero/negative amounts show as single day (debt day)
        }

        const date = new Date(payment.startDate + 'T00:00:00');
        const year = date.getFullYear();
        const dailyRate = this.getDailyRateForBarberAndYear(barberName, year);

        // Number of working days covered = amount / dailyRate (rounded down)
        // Sundays are free - they don't count as covered days
        const workingDaysCovered = Math.floor(amount / dailyRate);

        return Math.max(1, workingDaysCovered);
    }

    /**
     * Get the effective payment date (if Sunday, move to Saturday).
     * Sunday payments are treated as if made on Saturday.
     */
    getEffectivePaymentDate(payment) {
        const paymentDate = new Date(payment.startDate + 'T00:00:00');
        
        // If payment is on Sunday, treat it as Saturday
        if (paymentDate.getDay() === 0) {
            paymentDate.setDate(paymentDate.getDate() - 1);
        }
        
        return paymentDate;
    }

    /**
     * Calculate the START date for a payment based on its amount.
     * Post-payment: payment on April 11 with $48 at $8/day
     * covers 6 working days BACKWARD: Apr 11, 10, 9, 8 (skip Sun 7), 6, 5.
     * We count working days only, skipping Sundays.
     * 
     * If payment is on Sunday, treat it as Saturday payment.
     */
    calculatePaymentStartDate(payment, barberName) {
        const amount = parseFloat(payment.Amount) || 0;
        if (amount <= 0) {
            return payment.startDate; // Single day for debt
        }

        // Get effective date (Sunday -> Saturday)
        const endDate = this.getEffectivePaymentDate(payment);
        const year = endDate.getFullYear();
        const dailyRate = this.getDailyRateForBarberAndYear(barberName, year);

        // Number of working days to go backward
        const workingDaysToCover = Math.floor(amount / dailyRate);
        
        let currentDate = new Date(endDate);
        let daysCounted = 0;

        // Go backward, counting only working days (skip Sundays)
        while (daysCounted < workingDaysToCover - 1) {
            // Move backward one day
            currentDate.setDate(currentDate.getDate() - 1);
            
            // Only count if it's NOT Sunday (Sunday is free)
            if (currentDate.getDay() !== 0) {
                daysCounted++;
            }
        }

        return currentDate.toISOString().split('T')[0];
    }

    calculateDateRange() {
        let allDates = []; // all payment dates
        let allVisualStarts = []; // earliest covered dates (backward expansion)
        
        Object.entries(this.data.teams).forEach(([teamName, payments]) => {
            payments.forEach(payment => {
                const paymentDate = new Date(payment.startDate + 'T00:00:00');
                allDates.push(paymentDate);
                
                // Calculate visual start (backward expansion)
                const visualStartDateStr = this.calculatePaymentStartDate(payment, teamName);
                const visualStartDate = new Date(visualStartDateStr + 'T00:00:00');
                allVisualStarts.push(visualStartDate);
            });
        });

        if (allDates.length === 0) {
            this.dateRange.start = new Date('2025-08-01T00:00:00');
            this.dateRange.end = new Date('2025-08-31T00:00:00');
        } else {
            // Start = earliest visual start (backward expanded)
            // End = latest payment date
            this.dateRange.start = new Date(Math.min(...allVisualStarts));
            this.dateRange.end = new Date(Math.max(...allDates));
            
            // Add padding
            const paddedStart = new Date(this.dateRange.start);
            paddedStart.setDate(paddedStart.getDate() - 1);
            this.dateRange.start = paddedStart;
            
            const paddedEnd = new Date(this.dateRange.end);
            paddedEnd.setDate(paddedEnd.getDate() + 1);
            this.dateRange.end = paddedEnd;
        }
        
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
        
        targetDate.setHours(0, 0, 0, 0);
        startDate.setHours(0, 0, 0, 0);
        
        const timeDiff = targetDate.getTime() - startDate.getTime();
        return Math.floor(timeDiff / (1000 * 60 * 60 * 24));
    }

    getPositionFromBottom(date, totalDays) {
        const daysSinceStart = this.getDaysSinceStart(date);
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
        
        timelineAxis.style.height = `${totalHeight + 60}px`;
        timelineAxis.innerHTML = '';

        let currentDate = new Date(this.dateRange.start);
        while (currentDate <= this.dateRange.end) {
            const bottomPosition = this.getPositionFromBottom(currentDate, totalDays) + 60;

            // Sunday styling (lighter color)
            const isSunday = currentDate.getDay() === 0;

            const dateLabel = document.createElement('div');
            dateLabel.className = 'date-label';
            if (isSunday) {
                dateLabel.classList.add('sunday');
            }
            dateLabel.style.top = `${bottomPosition}px`;
            dateLabel.textContent = this.formatDateForDisplay(currentDate);
            timelineAxis.appendChild(dateLabel);

            const gridLine = document.createElement('div');
            gridLine.className = 'grid-line';
            if (isSunday) {
                gridLine.classList.add('sunday');
            }
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

        // Payment blocks - use expanded visualization
        payments.forEach((payment, index) => {
            const paymentDate = new Date(payment.startDate + 'T00:00:00');
            // Get effective date (Sunday -> Saturday)
            const effectiveEndDate = this.getEffectivePaymentDate(payment);
            // For post-payment: visual block extends BACKWARD from effective payment date
            // Block START = earliest covered day, Block END = effective payment date
            const visualStartDateStr = this.calculatePaymentStartDate(payment, teamName);
            
            // Calculate visual duration based on payment amount
            const visualDays = this.calculatePaymentDays(payment, teamName);

            const block = document.createElement('a');
            block.className = 'payment-block';
            
            // Color coding based on amount
            const amount = parseFloat(payment.Amount) || 0;
            if (amount > 40) {
                block.classList.add('large-payment');
            } else if (amount > 20) {
                block.classList.add('medium-payment');
            } else if (amount <= 0) {
                block.classList.add('debt-day');
            }
            
            // Check if this is the most recent payment for this team
            const teamMostRecent = mostRecent[teamName];
            const isTheMostRecent = teamMostRecent && teamMostRecent.index === index;
            
            if (isTheMostRecent) {
                block.classList.add('most-recent');
            }
            
            // Position: block BOTTOM is at the effective END date
            // Block extends UPWARD to cover the previous working days
            const blockBottomPosition = this.getPositionFromBottom(effectiveEndDate, totalDays) + 60;
            block.style.top = `${blockBottomPosition}px`;
            
            // Height based on visual days covered
            block.style.height = `${visualDays * this.pixelsPerDay - 4}px`;
            
            const whatsappLink = this.createWhatsAppLink(teamName, visualStartDateStr, payment.startDate);
            block.href = whatsappLink;
            block.target = '_blank';
            block.rel = 'noopener noreferrer';
            
            // Block content - show amount and date range
            const visualStart = this.formatDateForDisplay(new Date(visualStartDateStr));
            const paymentEnd = this.formatDateForDisplay(paymentDate);
            const effectiveEnd = this.formatDateForDisplay(effectiveEndDate);
            const amountDisplay = amount > 0 ? `$${amount.toFixed(0)}` : 'Debt';
            
            // Show effective date if payment was on Sunday
            const dateToShow = paymentDate.getDay() === 0 ? effectiveEnd : paymentEnd;
            
            block.innerHTML = `
                <div class="payment-content">
                    <div class="payment-date">${dateToShow}</div>
                    <div class="payment-amount">${amountDisplay}</div>
                    ${visualDays > 1 ? `<div class="payment-days">${visualDays}d</div>` : ''}
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

        const mostRecentPerTeam = this.findMostRecentPaymentPerTeam();

        const teams = this.data.teams;
        Object.entries(teams).forEach(([teamName, payments]) => {
            const column = this.renderTeamColumn(teamName, payments, mostRecentPerTeam);
            chartArea.appendChild(column);
        });

        this.synchronizeScrolling();
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
        const timelineAxis = document.getElementById('timelineAxis');
        const chartArea = document.getElementById('chartArea');
        
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
        try {
            const response = await fetch('/api/debts');
            if (!response.ok) {
                throw new Error('Failed to fetch debt data');
            }

            const payload = await response.json();
            const storedDebts = payload.debts || [];
            
            // Add source label to indicate these are from the debt calculation script
            return storedDebts.map(debt => ({
                ...debt,
                source: 'stored'
            }));
        } catch (error) {
            console.warn('Debt API unavailable.', error);
            return [];
        }
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2
        }).format(amount);
    }

    parseDateAtMidnight(dateString) {
        if (!dateString) {
            return null;
        }

        const parsed = new Date(`${dateString}T00:00:00`);
        if (Number.isNaN(parsed.getTime())) {
            return null;
        }

        parsed.setHours(0, 0, 0, 0);
        return parsed;
    }

    getLastPaymentDate(payments) {
        if (!Array.isArray(payments) || !payments.length) {
            return null;
        }

        return payments.reduce((latest, payment) => {
            const candidate = this.parseDateAtMidnight(payment?.endDate || payment?.startDate);
            if (!candidate) {
                return latest;
            }

            if (!latest || candidate > latest) {
                return candidate;
            }

            return latest;
        }, null);
    }

    getDailyRateForBarber(barberName) {
        if (!barberName) {
            return 7;
        }

        return barberName.toLowerCase() === 'genesis' ? 5 : 7;
    }

    countChargeableDays(startDate, endDate) {
        if (!(startDate instanceof Date) || !(endDate instanceof Date)) {
            return 0;
        }

        if (startDate > endDate) {
            return 0;
        }

        const cursor = new Date(startDate);
        let chargeableDays = 0;

        while (cursor <= endDate) {
            if (cursor.getDay() !== 0) {
                chargeableDays += 1;
            }
            cursor.setDate(cursor.getDate() + 1);
        }

        return chargeableDays;
    }

    calculateDefaultDebts(referenceDate = new Date()) {
        if (!this.data || !this.data.teams) {
            return [];
        }

        const today = new Date(referenceDate);
        today.setHours(0, 0, 0, 0);

        const defaults = Object.entries(this.data.teams)
            .map(([barberName, payments]) => {
                const lastPaymentDate = this.getLastPaymentDate(payments);
                if (!lastPaymentDate) {
                    return null;
                }

                const dailyRate = this.getDailyRateForBarber(barberName);
                const firstPendingDate = new Date(lastPaymentDate);
                firstPendingDate.setDate(firstPendingDate.getDate() + 1);
                firstPendingDate.setHours(0, 0, 0, 0);

                let days = 0;
                if (firstPendingDate <= today) {
                    days = this.countChargeableDays(firstPendingDate, today);
                }

                return {
                    name: barberName,
                    days,
                    amount: days * dailyRate,
                    lastPaymentDate,
                    dailyRate,
                    source: 'calculated'
                };
            })
            .filter((entry) => entry !== null);

        return defaults.sort((a, b) => b.amount - a.amount);
    }

    mergeDebtSummaries(calculatedDebts, storedDebts) {
        const merged = [];
        const storedByName = new Map();

        if (Array.isArray(storedDebts)) {
            storedDebts.forEach((entry) => {
                if (entry && entry.name) {
                    storedByName.set(entry.name, entry);
                }
            });
        }

        const calculatedNames = new Set();

        calculatedDebts.forEach((calculated) => {
            calculatedNames.add(calculated.name);
            const storedMatch = storedByName.get(calculated.name);
            merged.push({
                ...calculated,
                storedAmount: storedMatch ? storedMatch.amount : null,
                storedDays: storedMatch ? storedMatch.days : null
            });
        });

        if (Array.isArray(storedDebts)) {
            storedDebts.forEach((entry) => {
                if (!entry || calculatedNames.has(entry.name)) {
                    return;
                }

                const dailyRate = this.getDailyRateForBarber(entry.name);
                merged.push({
                    name: entry.name,
                    amount: entry.amount,
                    days: entry.days,
                    lastPaymentDate: null,
                    dailyRate,
                    source: 'stored',
                    storedAmount: entry.amount,
                    storedDays: entry.days
                });
            });
        }

        return merged.sort((a, b) => b.amount - a.amount);
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
                    const sourceLabel = debt.source === 'calculated'
                        ? ' <span class="debt-source">estimado</span>'
                        : debt.source === 'stored'
                            ? ' <span class="debt-source">registro</span>'
                            : '';
                    const dayLabel = debt.days === 1 ? 'día' : 'días';
                    return `
                        <li>
                            <span class="debt-name">${debt.name}</span>
                            <span class="debt-amount">${amount}${sourceLabel}</span>
                            <span class="debt-days">${debt.days} ${dayLabel}</span>
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
            modalBody.innerHTML = '<p>Cargando deudas...</p>';
            try {
                this.debtData = await this.fetchDebtData();
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