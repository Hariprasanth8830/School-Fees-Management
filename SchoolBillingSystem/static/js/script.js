document.addEventListener('DOMContentLoaded', function() {
    // Handle search functionality
    const searchForm = document.getElementById('searchForm');
    const searchInput = document.getElementById('searchInput');
    const searchResultsModal = new bootstrap.Modal(document.getElementById('searchResultsModal'), {});
    const searchResults = document.getElementById('searchResults');
    
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const query = searchInput.value.trim();
            
            if (query.length < 2) {
                alert('Please enter at least 2 characters for search');
                return;
            }
            
            // Show loading indicator
            searchResults.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div><p class="mt-2">Searching...</p></div>';
            searchResultsModal.show();
            
            // Fetch search results
            fetch(`/search?query=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    let resultsHTML = '';
                    
                    // Display student results
                    if (data.students && data.students.length > 0) {
                        resultsHTML += '<h5 class="mt-3">Students</h5>';
                        resultsHTML += '<div class="list-group mb-4">';
                        
                        data.students.forEach(student => {
                            resultsHTML += `
                                <a href="/students/edit/${student.id}" class="list-group-item list-group-item-action">
                                    <div class="d-flex w-100 justify-content-between">
                                        <h6 class="mb-1">${student.name}</h6>
                                        <small>Class ${student.class_name}${student.section ? '-' + student.section : ''}</small>
                                    </div>
                                    <p class="mb-1">Admission No: ${student.admission_number}</p>
                                    <small>Parent: ${student.parent_name}</small>
                                </a>
                            `;
                        });
                        
                        resultsHTML += '</div>';
                    }
                    
                    // Display bill results
                    if (data.bills && data.bills.length > 0) {
                        resultsHTML += '<h5 class="mt-3">Bills</h5>';
                        resultsHTML += '<div class="list-group">';
                        
                        data.bills.forEach(bill => {
                            resultsHTML += `
                                <a href="/bills/view/${bill.id}" class="list-group-item list-group-item-action">
                                    <div class="d-flex w-100 justify-content-between">
                                        <h6 class="mb-1">${bill.bill_number}</h6>
                                        <small class="badge ${bill.status === 'Paid' ? 'bg-success' : 'bg-danger'}">${bill.status}</small>
                                    </div>
                                    <p class="mb-1">Student: ${bill.student_name}</p>
                                    <small>Amount: ₹${parseFloat(bill.total_amount).toFixed(2)}</small>
                                </a>
                            `;
                        });
                        
                        resultsHTML += '</div>';
                    }
                    
                    // No results
                    if ((!data.students || data.students.length === 0) && (!data.bills || data.bills.length === 0)) {
                        resultsHTML = `
                            <div class="text-center py-4">
                                <i class="fas fa-search fa-3x mb-3 text-muted"></i>
                                <h5>No results found</h5>
                                <p>No students or bills match your search for "${query}"</p>
                            </div>
                        `;
                    }
                    
                    searchResults.innerHTML = resultsHTML;
                })
                .catch(error => {
                    console.error('Search error:', error);
                    searchResults.innerHTML = `
                        <div class="alert alert-danger">
                            <i class="fas fa-exclamation-circle me-2"></i>
                            An error occurred while searching. Please try again.
                        </div>
                    `;
                });
        });
    }

    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Auto close alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
});
