document.addEventListener('DOMContentLoaded', function() {
    // Custom printing functions using Print.js
    window.printBill = function(billId) {
        // First we get the bill data from the server if needed
        
        // Then use print.js to print the element
        printJS({
            printable: 'bill-' + billId,
            type: 'html',
            css: [
                'https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css',
                '/static/css/style.css'
            ],
            scanStyles: false,
            style: `
                @page { size: A4; margin: 10mm; }
                body { color: #000; }
                .card { border: 1px solid #dee2e6 !important; }
                .card-body { padding: 1.25rem; }
                .table { color: #000 !important; }
                .badge-success { background-color: #28a745 !important; color: #fff !important; }
                .badge-danger { background-color: #dc3545 !important; color: #fff !important; }
                .footer-note { margin-top: 30px; text-align: center; font-size: 12px; color: #6c757d; }
            `
        });
    };
    
    // Function to print reports
    window.printReport = function(reportId) {
        printJS({
            printable: reportId,
            type: 'html',
            css: [
                'https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css',
                'https://cdn.jsdelivr.net/npm/chart.js/dist/chart.min.css',
                '/static/css/style.css'
            ],
            scanStyles: false,
            style: `
                @page { size: landscape; margin: 10mm; }
                body { color: #000; }
                .card { border: 1px solid #dee2e6 !important; }
                .table { color: #000 !important; }
                .progress { border: 1px solid #dee2e6; }
                .progress-bar { color: #fff !important; }
            `
        });
    };
    
    // Function to print student list
    window.printStudentList = function() {
        printJS({
            printable: 'student-list',
            type: 'html',
            css: [
                'https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css',
                '/static/css/style.css'
            ],
            scanStyles: false,
            style: `
                @page { size: A4 landscape; margin: 10mm; }
                body { color: #000; }
                .table { color: #000 !important; }
                .header { text-align: center; margin-bottom: 20px; }
                .footer { text-align: center; margin-top: 20px; font-size: 12px; color: #6c757d; }
            `
        });
    };
});
