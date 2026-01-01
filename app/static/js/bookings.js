// Booking Management Module

class BookingManager {
    constructor() {
        this.bookings = [];
        this.filteredBookings = [];
        this.sortColumn = null;
        this.sortDirection = 'asc';
        this.editingBooking = null;
        this.userRole = null; // Will be set by the main app
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupModal();
    }

    setupEventListeners() {
        // Add booking button
        const addBookingBtn = document.getElementById('add-booking-btn');
        if (addBookingBtn) {
            addBookingBtn.addEventListener('click', () => this.showBookingForm());
        }

        // Search input
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.handleSearch(e.target.value));
        }

        // Status filter
        const statusFilter = document.getElementById('status-filter');
        if (statusFilter) {
            statusFilter.addEventListener('change', (e) => this.handleStatusFilter(e.target.value));
        }

        // Modal close events
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeModal();
            }
        });

        // Form submission
        document.addEventListener('submit', (e) => {
            if (e.target.id === 'booking-form') {
                e.preventDefault();
                this.handleFormSubmit(e);
            }
        });
    }

    setupModal() {
        const modal = document.getElementById('booking-modal');
        if (!modal) return;

        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2 id="modal-title">Add New Booking</h2>
                    <button type="button" class="modal-close" onclick="bookingManager.closeModal()">&times;</button>
                </div>
                <div class="modal-body">
                    <div id="modal-error" class="error-message"></div>
                    <form id="booking-form">
                        <div class="form-row">
                            <div class="form-group">
                                <label for="customer_name">Customer Name *</label>
                                <input type="text" id="customer_name" name="customer_name" required>
                            </div>
                            <div class="form-group">
                                <label for="contact_number">Contact Number *</label>
                                <input type="tel" id="contact_number" name="contact_number" required>
                            </div>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label for="project_name">Project Name *</label>
                                <input type="text" id="project_name" name="project_name" required>
                            </div>
                            <div class="form-group">
                                <label for="type">Property Type *</label>
                                <select id="type" name="type" required>
                                    <option value="">Select Type</option>
                                    <option value="1BHK">1BHK</option>
                                    <option value="2BHK">2BHK</option>
                                    <option value="3BHK">3BHK</option>
                                    <option value="4BHK">4BHK</option>
                                    <option value="Villa">Villa</option>
                                    <option value="Plot">Plot</option>
                                </select>
                            </div>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label for="area">Area (sq ft) *</label>
                                <input type="number" id="area" name="area" min="1" step="0.01" required>
                            </div>
                            <div class="form-group">
                                <label for="agreement_cost">Agreement Cost *</label>
                                <input type="number" id="agreement_cost" name="agreement_cost" min="0" step="0.01" required>
                            </div>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label for="amount">Amount *</label>
                                <input type="number" id="amount" name="amount" min="0" step="0.01" required>
                            </div>
                            <div class="form-group">
                                <label for="tax_gst">Tax/GST</label>
                                <input type="number" id="tax_gst" name="tax_gst" min="0" step="0.01" value="0">
                            </div>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label for="refund_buyer">Refund Buyer</label>
                                <input type="number" id="refund_buyer" name="refund_buyer" min="0" step="0.01" value="0">
                            </div>
                            <div class="form-group">
                                <label for="refund_referral">Refund Referral</label>
                                <input type="number" id="refund_referral" name="refund_referral" min="0" step="0.01" value="0">
                            </div>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label for="onc_trust_fund">ONC Trust Fund</label>
                                <input type="number" id="onc_trust_fund" name="onc_trust_fund" min="0" step="0.01" value="0">
                            </div>
                            <div class="form-group">
                                <label for="oncct_funded">ONCCT Funded</label>
                                <input type="number" id="oncct_funded" name="oncct_funded" min="0" step="0.01" value="0">
                            </div>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label for="timeline">Timeline *</label>
                                <input type="datetime-local" id="timeline" name="timeline" required>
                            </div>
                            <div class="form-group">
                                <label for="invoice_status">Invoice Status</label>
                                <select id="invoice_status" name="invoice_status">
                                    <option value="pending">Pending</option>
                                    <option value="sent">Sent</option>
                                    <option value="paid">Paid</option>
                                    <option value="overdue">Overdue</option>
                                </select>
                            </div>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-group">
                                <label for="loan_req">Loan Required</label>
                                <select id="loan_req" name="loan_req">
                                    <option value="no">No</option>
                                    <option value="yes">Yes</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="status">Status</label>
                                <select id="status" name="status">
                                    <option value="active">Active</option>
                                    <option value="complete">Complete</option>
                                    <option value="cancelled">Cancelled</option>
                                </select>
                            </div>
                        </div>
                        
                        <div class="form-actions">
                            <button type="button" class="btn btn-secondary" onclick="bookingManager.closeModal()">Cancel</button>
                            <button type="submit" class="btn btn-primary" id="submit-booking">Save Booking</button>
                        </div>
                    </form>
                </div>
            </div>
        `;
    }

    async loadBookings() {
        try {
            UIUtils.setLoading('bookings-tab', true);
            const response = await authService.apiRequest('/bookings');
            
            if (!response || !response.ok) {
                if (response) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
                } else {
                    throw new Error('Network error or authentication failed');
                }
            }
            
            const data = await response.json();
            this.bookings = data.bookings || [];
            this.filteredBookings = [...this.bookings];
            this.renderBookingsTable();
            
        } catch (error) {
            console.error('Error loading bookings:', error);
            UIUtils.showError('Failed to load bookings');
            // Show empty state
            const tbody = document.getElementById('bookings-tbody');
            if (tbody) {
                tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 20px; color: #e74c3c;">Failed to load bookings. Please try again.</td></tr>';
            }
        } finally {
            UIUtils.setLoading('bookings-tab', false);
        }
    }

    renderBookingsTable() {
        const tbody = document.getElementById('bookings-tbody');
        if (!tbody) return;

        if (this.filteredBookings.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 20px;">No bookings found</td></tr>';
            return;
        }

        tbody.innerHTML = this.filteredBookings.map(booking => {
            const canEdit = this.canEditBooking(booking);
            const canDelete = this.canDeleteBooking(booking);
            
            return `
                <tr>
                    <td>${this.escapeHtml(booking.customer_name)}</td>
                    <td>${this.escapeHtml(booking.project_name)}</td>
                    <td>${this.escapeHtml(booking.contact_number)}</td>
                    <td>${this.escapeHtml(booking.type)}</td>
                    <td>${UIUtils.formatCurrency(booking.amount)}</td>
                    <td><span class="status-badge status-${booking.status}">${booking.status}</span></td>
                    <td>${UIUtils.formatDate(booking.timeline)}</td>
                    <td>
                        ${canEdit ? `<button class="btn btn-sm btn-edit" onclick="bookingManager.editBooking('${booking.id}')">Edit</button>` : ''}
                        ${canDelete ? `<button class="btn btn-sm btn-delete" onclick="bookingManager.confirmDeleteBooking('${booking.id}')">${this.userRole === 'admin' ? 'Delete' : 'Cancel'}</button>` : ''}
                        ${!canEdit && !canDelete ? '<span style="color: #999; font-size: 12px;">View Only</span>' : ''}
                    </td>
                </tr>
            `;
        }).join('');
    }

    showBookingForm(booking = null) {
        this.editingBooking = booking;
        const modal = document.getElementById('booking-modal');
        const modalTitle = document.getElementById('modal-title');
        const form = document.getElementById('booking-form');
        
        if (booking) {
            modalTitle.textContent = 'Edit Booking';
            this.populateForm(booking);
        } else {
            modalTitle.textContent = 'Add New Booking';
            form.reset();
            // Set default timeline to tomorrow
            const tomorrow = new Date();
            tomorrow.setDate(tomorrow.getDate() + 1);
            document.getElementById('timeline').value = tomorrow.toISOString().slice(0, 16);
        }
        
        modal.style.display = 'block';
        UIUtils.hideError('modal-error');
    }

    populateForm(booking) {
        const form = document.getElementById('booking-form');
        const formData = new FormData();
        
        // Populate form fields
        Object.keys(booking).forEach(key => {
            const input = form.querySelector(`[name="${key}"]`);
            if (input) {
                if (key === 'timeline') {
                    // Convert ISO string to datetime-local format
                    const date = new Date(booking[key]);
                    input.value = date.toISOString().slice(0, 16);
                } else {
                    input.value = booking[key];
                }
            }
        });
    }

    closeModal() {
        const modal = document.getElementById('booking-modal');
        modal.style.display = 'none';
        this.editingBooking = null;
        UIUtils.hideError('modal-error');
    }

    async handleFormSubmit(e) {
        const form = e.target;
        const formData = new FormData(form);
        const bookingData = {};
        
        // Convert form data to object
        for (let [key, value] of formData.entries()) {
            if (value.trim() === '') {
                continue; // Skip empty values for optional fields
            }
            
            // Convert numeric fields
            if (['area', 'agreement_cost', 'amount', 'tax_gst', 'refund_buyer', 
                 'refund_referral', 'onc_trust_fund', 'oncct_funded'].includes(key)) {
                bookingData[key] = parseFloat(value) || 0;
            } else if (key === 'timeline') {
                // Convert datetime-local to ISO string
                bookingData[key] = new Date(value).toISOString();
            } else {
                bookingData[key] = value.trim();
            }
        }

        // Validate required fields
        const validation = this.validateBookingData(bookingData);
        if (!validation.isValid) {
            UIUtils.showError(validation.errors.join(', '), 'modal-error');
            return;
        }

        UIUtils.hideError('modal-error');
        UIUtils.setLoading('submit-booking', true);

        try {
            let response;
            if (this.editingBooking) {
                // Update existing booking
                response = await authService.apiRequest(`/bookings/${this.editingBooking.id}`, {
                    method: 'PUT',
                    body: JSON.stringify(bookingData)
                });
            } else {
                // Create new booking
                response = await authService.apiRequest('/bookings', {
                    method: 'POST',
                    body: JSON.stringify(bookingData)
                });
            }

            if (response && response.ok) {
                const result = await response.json();
                UIUtils.showSuccess(result.message || 'Booking saved successfully');
                this.closeModal();
                await this.loadBookings(); // Reload bookings
            } else {
                const error = await response.json();
                UIUtils.showError(error.error || 'Failed to save booking', 'modal-error');
            }
        } catch (error) {
            console.error('Error saving booking:', error);
            UIUtils.showError('Network error. Please try again.', 'modal-error');
        } finally {
            UIUtils.setLoading('submit-booking', false);
        }
    }

    validateBookingData(data) {
        const errors = [];

        // Required field validation
        if (!data.customer_name) errors.push('Customer name is required');
        if (!data.contact_number) errors.push('Contact number is required');
        if (!data.project_name) errors.push('Project name is required');
        if (!data.type) errors.push('Property type is required');
        if (!data.area || data.area <= 0) errors.push('Area must be greater than 0');
        if (!data.agreement_cost || data.agreement_cost < 0) errors.push('Agreement cost cannot be negative');
        if (!data.amount || data.amount < 0) errors.push('Amount cannot be negative');
        if (!data.timeline) errors.push('Timeline is required');

        // Contact number validation
        if (data.contact_number && data.contact_number.length < 10) {
            errors.push('Contact number must be at least 10 digits');
        }

        // Timeline validation
        if (data.timeline) {
            const timelineDate = new Date(data.timeline);
            const now = new Date();
            if (timelineDate < now) {
                errors.push('Timeline cannot be in the past');
            }
        }

        return {
            isValid: errors.length === 0,
            errors
        };
    }

    async editBooking(id) {
        const booking = this.bookings.find(b => b.id == id);
        if (!booking) return;

        if (!this.canEditBooking(booking)) {
            UIUtils.showError('You do not have permission to edit this booking.');
            return;
        }

        this.showBookingForm(booking);
    }

    confirmDeleteBooking(id) {
        const booking = this.bookings.find(b => b.id == id);
        if (!booking) return;

        if (!this.canDeleteBooking(booking)) {
            UIUtils.showError('You do not have permission to delete this booking.');
            return;
        }

        const action = this.userRole === 'admin' ? 'delete' : 'cancel';
        const confirmMessage = `Are you sure you want to ${action} the booking for ${booking.customer_name} - ${booking.project_name}?\n\n${action === 'delete' ? 'This action cannot be undone.' : 'This will mark the booking as cancelled.'}`;
        
        if (confirm(confirmMessage)) {
            this.deleteBooking(id);
        }
    }

    async deleteBooking(id) {
        try {
            const response = await authService.apiRequest(`/bookings/${id}`, {
                method: 'DELETE'
            });

            if (response && response.ok) {
                const result = await response.json();
                UIUtils.showSuccess(result.message || 'Booking deleted successfully');
                await this.loadBookings(); // Reload bookings
            } else {
                const error = await response.json();
                UIUtils.showError(error.error || 'Failed to delete booking');
            }
        } catch (error) {
            console.error('Error deleting booking:', error);
            UIUtils.showError('Network error. Please try again.');
        }
    }

    handleSearch(searchTerm) {
        const term = searchTerm.toLowerCase().trim();
        
        if (!term) {
            this.filteredBookings = [...this.bookings];
        } else {
            this.filteredBookings = this.bookings.filter(booking => 
                booking.customer_name.toLowerCase().includes(term) ||
                booking.project_name.toLowerCase().includes(term) ||
                booking.contact_number.includes(term) ||
                booking.type.toLowerCase().includes(term) ||
                booking.invoice_status.toLowerCase().includes(term)
            );
        }
        
        this.renderBookingsTable();
    }

    handleStatusFilter(status) {
        if (!status) {
            this.filteredBookings = [...this.bookings];
        } else {
            this.filteredBookings = this.bookings.filter(booking => booking.status === status);
        }
        
        this.renderBookingsTable();
    }

    sortTable(column) {
        if (this.sortColumn === column) {
            this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortColumn = column;
            this.sortDirection = 'asc';
        }

        this.filteredBookings.sort((a, b) => {
            let aVal = a[column];
            let bVal = b[column];

            // Handle different data types
            if (typeof aVal === 'string') {
                aVal = aVal.toLowerCase();
                bVal = bVal.toLowerCase();
            }

            if (aVal < bVal) return this.sortDirection === 'asc' ? -1 : 1;
            if (aVal > bVal) return this.sortDirection === 'asc' ? 1 : -1;
            return 0;
        });

        this.renderBookingsTable();
        this.updateSortIndicators(column);
    }

    updateSortIndicators(column) {
        // Remove existing sort indicators
        document.querySelectorAll('.table th').forEach(th => {
            th.classList.remove('sort-asc', 'sort-desc');
        });

        // Add sort indicator to current column
        const th = document.querySelector(`th[onclick*="${column}"]`);
        if (th) {
            th.classList.add(this.sortDirection === 'asc' ? 'sort-asc' : 'sort-desc');
        }
    }

    setUserRole(role) {
        this.userRole = role;
        this.applyRoleBasedRestrictions();
        this.updateUIForRole();
        // Re-render table to apply role-based button visibility
        this.renderBookingsTable();
    }

    applyRoleBasedRestrictions() {
        if (this.userRole === 'sales_person') {
            // Sales persons have limited permissions
            this.applySalesPersonRestrictions();
        } else if (this.userRole === 'admin') {
            // Admins have full permissions
            this.applyAdminPermissions();
        }
    }

    applySalesPersonRestrictions() {
        // Sales persons can create and edit bookings but cannot hard delete
        // They can only soft delete (cancel) bookings they created
        // This will be enforced in the delete confirmation
    }

    applyAdminPermissions() {
        // Admins have full access to all operations
        // No restrictions needed
    }

    canDeleteBooking(booking) {
        if (this.userRole === 'admin') {
            return true; // Admins can delete any booking
        } else if (this.userRole === 'sales_person') {
            // Sales persons can only cancel bookings, not permanently delete
            // And only if the booking is not already completed
            return booking.status !== 'complete';
        }
        return false;
    }

    canEditBooking(booking) {
        if (this.userRole === 'admin') {
            return true; // Admins can edit any booking
        } else if (this.userRole === 'sales_person') {
            // Sales persons can edit active bookings
            return booking.status === 'active';
        }
        return false;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Role-based UI updates
    updateUIForRole() {
        const addBookingBtn = document.getElementById('add-booking-btn');
        
        if (this.userRole === 'sales_person') {
            // Sales persons can add bookings
            if (addBookingBtn) {
                addBookingBtn.style.display = 'block';
                addBookingBtn.textContent = 'Add New Booking';
            }
        } else if (this.userRole === 'admin') {
            // Admins can add bookings
            if (addBookingBtn) {
                addBookingBtn.style.display = 'block';
                addBookingBtn.textContent = 'Add New Booking';
            }
        }
    }
}

// Initialize booking manager globally
window.bookingManager = new BookingManager();