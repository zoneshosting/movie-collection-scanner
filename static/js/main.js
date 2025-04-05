// Main JavaScript for Movie Collection Site

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });

    // Auto-dismiss alerts
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
});

// Function to preview image before upload
function previewImage(input, previewId) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        
        reader.onload = function(e) {
            document.getElementById(previewId).src = e.target.result;
            document.getElementById(previewId).style.display = 'block';
        }
        
        reader.readAsDataURL(input.files[0]);
    }
}

// Function to toggle watch status
function toggleWatchStatus(movieId, element) {
    fetch('/api/movie/' + movieId + '/toggle-watch-status', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (data.watch_status) {
                element.classList.remove('bg-secondary');
                element.classList.add('bg-success');
                element.textContent = 'Watched';
            } else {
                element.classList.remove('bg-success');
                element.classList.add('bg-secondary');
                element.textContent = 'Unwatched';
            }
        }
    })
    .catch(error => console.error('Error:', error));
}

// Function to handle CSV file validation
function validateCsvFile(input) {
    const fileSize = input.files[0].size / 1024 / 1024; // in MB
    const fileType = input.files[0].name.split('.').pop().toLowerCase();
    
    if (fileType !== 'csv') {
        alert('Please select a CSV file');
        input.value = '';
        return false;
    }
    
    if (fileSize > 10) {
        alert('File size exceeds 10MB. Please choose a smaller file.');
        input.value = '';
        return false;
    }
    
    document.getElementById('file-name').textContent = input.files[0].name;
    return true;
}
