// Analytics Dashboard Implementation

class AnalyticsManager {
    constructor() {
        this.charts = {};
        this.currentFilters = {};
        this.dateRange = {
            start_date: null,
            end_date: null
        };
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeDateFilters();
    }

    setupEventListeners() {
        // Filter controls
        const applyFilterBtn = document.getElementById('apply-filter-btn');
        if (applyFilterBtn) {
            applyFilterBtn.addEventListener('click', () => this.applyFilters());
        }

        // Export button
        const exportBtn = document.getElementById('export-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportData());
        }

        // Date inputs
        const dateFromInput = document.getElementById('date-from');
        const dateToInput = document.getElementById('date-to');
        
        if (dateFromInput) {
            dateFromInput.addEventListener('change', (e) => {
                this.dateRange.start_date = e.target.value;
            });
        }
        
        if (dateToInput) {
            dateToInput.addEventListener('change', (e) => {
                this.dateRange.end_date = e.target.value;
            });
        }
    }

    initializeDateFilters() {
        // Set default date range to last 30 days
        const today = new Date();
        const thirtyDaysAgo = new Date(today.getTime() - (30 * 24 * 60 * 60 * 1000));
        
        const dateFromInput = document.getElementById('date-from');
        const dateToInput = document.getElementById('date-to');
        
        if (dateFromInput) {
            dateFromInput.value = thirtyDaysAgo.toISOString().split('T')[0];
            this.dateRange.start_date = dateFromInput.value;
        }
        
        if (dateToInput) {
            dateToInput.value = today.toISOString().split('T')[0];
            this.dateRange.end_date = dateToInput.value;
        }
    }

    async loadAnalytics() {
        try {
            UIUtils.setLoading('analytics-tab', true);
            
            // Load dashboard data
            await this.loadDashboardData();
            
        } catch (error) {
            console.error('Error loading analytics:', error);
            UIUtils.showError('Failed to load analytics data');
        } finally {
            UIUtils.setLoading('analytics-tab', false);
        }
    }

    async loadDashboardData() {
        try {
            const params = new URLSearchParams();
            
            // Add date range
            if (this.dateRange.start_date) {
                params.append('start_date', this.dateRange.start_date + 'T00:00:00');
            }
            if (this.dateRange.end_date) {
                params.append('end_date', this.dateRange.end_date + 'T23:59:59');
            }
            
            // Add filters
            Object.keys(this.currentFilters).forEach(key => {
                if (this.currentFilters[key]) {
                    params.append(key, this.currentFilters[key]);
                }
            });

            const response = await authService.apiRequest(`/analytics/dashboard?${params.toString()}`);

            if (!response || !response.ok) {
                if (response && response.status === 403) {
                    throw new Error('Access denied: You do not have permission to view analytics.');
                } else if (response) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
                } else {
                    throw new Error('Network error or authentication failed');
                }
            }

            const data = await response.json();
            
            // Update KPIs
            this.updateKPIs(data.kpis);
            
            // Update charts
            this.updateCharts(data.charts);
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            throw error;
        }
    }

    updateKPIs(kpis) {
        // Update KPI values
        const totalBookingsEl = document.getElementById('total-bookings');
        const totalRevenueEl = document.getElementById('total-revenue');
        const completionRateEl = document.getElementById('completion-rate');
        const activeBookingsEl = document.getElementById('active-bookings');

        if (totalBookingsEl) {
            totalBookingsEl.textContent = kpis.total_bookings || 0;
        }
        
        if (totalRevenueEl) {
            totalRevenueEl.textContent = this.formatCurrency(kpis.total_revenue || 0);
        }
        
        if (completionRateEl) {
            completionRateEl.textContent = `${(kpis.completion_rate || 0).toFixed(1)}%`;
        }
        
        if (activeBookingsEl) {
            activeBookingsEl.textContent = kpis.active_bookings || 0;
        }
    }

    updateCharts(chartsData) {
        // Update trends chart
        this.updateTrendsChart(chartsData.monthly_trends);
        
        // Update project distribution chart
        this.updateProjectChart(chartsData.project_distribution);
        
        // Update revenue by type chart
        this.updateRevenueChart(chartsData.property_types);
    }

    updateTrendsChart(trendsData) {
        const ctx = document.getElementById('trends-chart');
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (this.charts.trends) {
            this.charts.trends.destroy();
        }

        // Prepare data from Chart.js format
        const labels = trendsData.labels || [];
        const datasets = trendsData.datasets || [];
        
        // Find booking and revenue datasets
        const bookingDataset = datasets.find(d => d.label === 'Bookings');
        const revenueDataset = datasets.find(d => d.label === 'Revenue');

        this.charts.trends = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Bookings',
                    data: bookingDataset ? bookingDataset.data : [],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    yAxisID: 'y'
                }, {
                    label: 'Revenue (₹)',
                    data: revenueDataset ? revenueDataset.data : [],
                    borderColor: '#764ba2',
                    backgroundColor: 'rgba(118, 75, 162, 0.1)',
                    tension: 0.4,
                    yAxisID: 'y1'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Time Period'
                        }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Number of Bookings'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Revenue (₹)'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Booking Trends Over Time'
                    },
                    legend: {
                        display: true,
                        position: 'top'
                    }
                }
            }
        });
    }

    updateProjectChart(projectData) {
        const ctx = document.getElementById('project-chart');
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (this.charts.projects) {
            this.charts.projects.destroy();
        }

        // Prepare data from Chart.js format
        const labels = projectData.labels || [];
        const datasets = projectData.datasets || [];
        const dataset = datasets[0] || { data: [], backgroundColor: [] };

        this.charts.projects = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: dataset.data,
                    backgroundColor: dataset.backgroundColor || this.generateColors(labels.length),
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Bookings by Project'
                    },
                    legend: {
                        display: true,
                        position: 'bottom'
                    }
                }
            }
        });
    }

    updateRevenueChart(propertyTypeData) {
        const ctx = document.getElementById('revenue-chart');
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (this.charts.revenue) {
            this.charts.revenue.destroy();
        }

        // Prepare data from Chart.js format
        const labels = propertyTypeData.labels || [];
        const datasets = propertyTypeData.datasets || [];
        const dataset = datasets[0] || { data: [], backgroundColor: [] };

        this.charts.revenue = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Revenue (₹)',
                    data: dataset.data,
                    backgroundColor: dataset.backgroundColor || this.generateColors(labels.length),
                    borderColor: (dataset.backgroundColor || this.generateColors(labels.length)).map(color => color.replace('0.8', '1')),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Revenue (₹)'
                        },
                        ticks: {
                            callback: function(value) {
                                return '₹' + value.toLocaleString();
                            }
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Property Type'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Revenue by Property Type'
                    },
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    generateColors(count) {
        const baseColors = [
            'rgba(102, 126, 234, 0.8)',
            'rgba(118, 75, 162, 0.8)',
            'rgba(255, 99, 132, 0.8)',
            'rgba(54, 162, 235, 0.8)',
            'rgba(255, 205, 86, 0.8)',
            'rgba(75, 192, 192, 0.8)',
            'rgba(153, 102, 255, 0.8)',
            'rgba(255, 159, 64, 0.8)'
        ];

        const colors = [];
        for (let i = 0; i < count; i++) {
            colors.push(baseColors[i % baseColors.length]);
        }
        return colors;
    }

    async applyFilters() {
        try {
            UIUtils.setLoading('apply-filter-btn', true);
            
            // Reload dashboard data with current filters
            await this.loadDashboardData();
            
            UIUtils.showSuccess('Filters applied successfully');
            
        } catch (error) {
            console.error('Error applying filters:', error);
            UIUtils.showError('Failed to apply filters');
        } finally {
            UIUtils.setLoading('apply-filter-btn', false);
        }
    }

    async exportData() {
        try {
            UIUtils.setLoading('export-btn', true);
            
            const params = new URLSearchParams();
            params.append('type', 'kpis');
            params.append('format', 'json');
            
            // Add date range
            if (this.dateRange.start_date) {
                params.append('start_date', this.dateRange.start_date + 'T00:00:00');
            }
            if (this.dateRange.end_date) {
                params.append('end_date', this.dateRange.end_date + 'T23:59:59');
            }
            
            // Add filters
            Object.keys(this.currentFilters).forEach(key => {
                if (this.currentFilters[key]) {
                    params.append(key, this.currentFilters[key]);
                }
            });

            const response = await authService.apiRequest(`/analytics/export?${params.toString()}`);

            if (!response || !response.ok) {
                if (response) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
                } else {
                    throw new Error('Network error or authentication failed');
                }
            }

            const data = await response.json();
            
            // Create and download file
            this.downloadJSON(data, 'analytics_export');
            
            UIUtils.showSuccess('Data exported successfully');
            
        } catch (error) {
            console.error('Error exporting data:', error);
            UIUtils.showError('Failed to export data');
        } finally {
            UIUtils.setLoading('export-btn', false);
        }
    }

    downloadJSON(data, filename) {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `${filename}_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        URL.revokeObjectURL(url);
    }

    formatCurrency(amount) {
        return '₹' + amount.toLocaleString('en-IN');
    }

    // Cleanup method to destroy charts when switching tabs
    cleanup() {
        Object.keys(this.charts).forEach(key => {
            if (this.charts[key]) {
                this.charts[key].destroy();
                delete this.charts[key];
            }
        });
    }
}

// Initialize analytics manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.analyticsManager = new AnalyticsManager();
});