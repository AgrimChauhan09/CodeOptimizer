document.addEventListener('DOMContentLoaded', function() {
    // Initialize Feather icons
    feather.replace();
    
    // Initialize CodeMirror for C code
    const codeEditor = CodeMirror.fromTextArea(document.getElementById('code-editor'), {
        lineNumbers: true,
        mode: 'text/x-csrc',
        theme: 'dracula',
        indentUnit: 4,
        smartIndent: true,
        tabSize: 4,
        indentWithTabs: false,
        lineWrapping: true,
        gutters: ["CodeMirror-linenumbers"],
        extraKeys: {"Ctrl-Space": "autocomplete"}
    });
    
    // Initialize CodeMirror for LLVM IR viewer
    const irViewer = CodeMirror.fromTextArea(document.getElementById('ir-viewer'), {
        lineNumbers: true,
        mode: 'text/x-csrc', // Using C-like syntax for now
        theme: 'dracula',
        readOnly: true,
        lineWrapping: true
    });
    
    // Initialize performance chart
    let performanceChart = null;
    
    // Handle run button click
    document.getElementById('run-btn').addEventListener('click', function() {
        const code = codeEditor.getValue();
        if (!code.trim()) {
            showError('Please enter some C code to optimize');
            return;
        }
        
        optimizeCode(code);
    });
    
    // Handle reset button click
    document.getElementById('reset-btn').addEventListener('click', function() {
        // Get the example code from the initial page load
        // Use the matrix multiplication example that's now set in app.py
        const exampleCodeElement = document.getElementById('code-editor');
        const exampleCode = exampleCodeElement.value || exampleCodeElement.textContent;
        
        codeEditor.setValue(exampleCode.trim());
        hideResults();
        hideError();
    });
    
    // Handle add to dataset button click
    document.getElementById('add-to-dataset-btn').addEventListener('click', function() {
        const code = codeEditor.getValue();
        if (!code.trim()) {
            showError('Please enter some C code before adding to dataset');
            return;
        }
        
        // Show the modal
        const modal = new bootstrap.Modal(document.getElementById('addToDatasetModal'));
        modal.show();
    });
    
    // Handle confirm add to dataset
    document.getElementById('confirm-add-to-dataset').addEventListener('click', function() {
        const code = codeEditor.getValue();
        const codeName = document.getElementById('code-name-input').value.trim();
        
        if (!codeName) {
            alert('Please enter a code name');
            return;
        }
        
        addToDataset(code, codeName);
    });
    
    // Dataset statistics section removed per user request
    
    // Toggle LLVM IR code visibility
    document.getElementById('toggle-ir-btn').addEventListener('click', function() {
        const irCard = document.getElementById('llvm-ir-card');
        const button = document.getElementById('toggle-ir-btn');
        
        if (irCard.classList.contains('d-none')) {
            irCard.classList.remove('d-none');
            button.textContent = 'Hide LLVM IR';
        } else {
            irCard.classList.add('d-none');
            button.textContent = 'Show LLVM IR';
        }
    });
    
    // Function to optimize code
    function optimizeCode(code) {
        // Show loading spinner
        showLoading();
        hideResults();
        hideError();
        
        // Send code to server for optimization
        fetch('/optimize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ code: code })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Server error during optimization');
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                showError(data.error);
                return;
            }
            
            displayResults(data);
        })
        .catch(error => {
            console.error('Error:', error);
            showError(error.message || 'An error occurred during optimization');
        })
        .finally(() => {
            hideLoading();
        });
    }
    
    // Function to display optimization results
    function displayResults(data) {
        // Show results container
        document.getElementById('results-content').classList.remove('d-none');
        
        // Display times and optimization info
        document.getElementById('unoptimized-time').textContent = data.unoptimized_time;
        document.getElementById('optimized-time').textContent = data.optimized_time;
        document.getElementById('best-optimization').textContent = data.best_optimization;
        document.getElementById('time-improvement').textContent = data.time_improvement;
        
        // Add optimization message if available
        if (data.optimization_message) {
            // Check if we need to add the message element
            let messageElement = document.getElementById('optimization-message');
            if (!messageElement) {
                // Create a message element if it doesn't exist
                const messageContainer = document.createElement('div');
                messageContainer.classList.add('alert', 'mt-3');
                messageContainer.id = 'optimization-message';
                
                // Find where to insert the message
                const timeImprovementCard = document.querySelector('.card-header.bg-info').closest('.card');
                timeImprovementCard.parentNode.appendChild(messageContainer);
                
                messageElement = messageContainer;
            }
            
            // Set message and style based on whether there was improvement
            if (data.time_improvement && parseFloat(data.time_improvement) > 0) {
                messageElement.textContent = data.optimization_message;
                messageElement.classList.remove('alert-warning');
                messageElement.classList.add('alert-success');
            } else {
                messageElement.textContent = data.optimization_message;
                messageElement.classList.remove('alert-success');
                messageElement.classList.add('alert-warning');
            }
        }
        
        // Display LLVM IR
        irViewer.setValue(data.llvm_ir || 'No LLVM IR available');
        
        // Display optimization details if available (only for non-cached results)
        if (data.optimization_details && data.optimization_details.length > 0 && !data.cached) {
            // Remove any existing optimization details section first
            const existingDetailsSection = document.getElementById('optimization-details-section');
            if (existingDetailsSection) {
                existingDetailsSection.remove();
            }
            
            // Create the container
            const detailsContainer = document.createElement('div');
            detailsContainer.classList.add('card', 'mb-4');
            detailsContainer.id = 'optimization-details-section';
            detailsContainer.innerHTML = `
                <div class="card-header bg-gradient text-white" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                    <h5 class="mb-0">
                        <i data-feather="zap"></i> Optimization Techniques Applied
                    </h5>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead class="table-dark">
                                <tr>
                                    <th>Technique</th>
                                    <th>Benefit</th>
                                    <th>Potential Impact</th>
                                </tr>
                            </thead>
                            <tbody id="optimization-details-body"></tbody>
                        </table>
                    </div>
                </div>
            `;
            
            // Find where to insert - before the features card
            const featuresCard = document.querySelector('#features-table').closest('.card');
            if (featuresCard && featuresCard.parentNode) {
                featuresCard.parentNode.insertBefore(detailsContainer, featuresCard);
            } else {
                // Fallback - add to the results content area
                document.getElementById('results-content').appendChild(detailsContainer);
            }
            
            // Populate the optimization details
            const detailsBody = document.getElementById('optimization-details-body');
            
            data.optimization_details.forEach(detail => {
                const row = document.createElement('tr');
                const potentialColor = detail.potential >= 8 ? 'success' : detail.potential >= 5 ? 'warning' : 'info';
                row.innerHTML = `
                    <td><strong><i data-feather="cpu"></i> ${detail.name}</strong></td>
                    <td><span class="text-muted">${detail.benefit}</span></td>
                    <td>
                        <div class="progress" style="height: 20px;">
                            <div class="progress-bar bg-${potentialColor} progress-bar-striped progress-bar-animated" 
                                 role="progressbar" 
                                 style="width: ${Math.min(detail.potential * 10, 100)}%" 
                                 aria-valuenow="${detail.potential}" aria-valuemin="0" aria-valuemax="10">
                                ${detail.potential}/10
                            </div>
                        </div>
                    </td>
                `;
                detailsBody.appendChild(row);
            });
            
            // Re-initialize feather icons
            feather.replace();
        }
        
        // Populate features table
        const featuresTable = document.getElementById('features-table');
        featuresTable.innerHTML = '';
        
        const featureDescriptions = {
            'loop_count': 'Number of loops in the code',
            'func_calls': 'Number of function calls (including recursive calls)',
            'instr_count': 'Total number of LLVM IR instructions',
            'has_branch': 'Contains branching instructions (if/else/switch)',
            'uses_memory': 'Uses memory operations (alloca/load/store)',
            'uses_global': 'References global variables'
        };
        
        for (const [key, value] of Object.entries(data.features)) {
            const row = document.createElement('tr');
            let displayValue = value;
            
            // Format boolean values
            if (value === 0 || value === 1) {
                if (key === 'has_branch' || key === 'uses_memory' || key === 'uses_global') {
                    displayValue = value === 1 ? '✅ Yes' : '❌ No';
                }
            }
            
            row.innerHTML = `
                <td><strong>${key.replace(/_/g, ' ')}</strong></td>
                <td>${displayValue}</td>
                <td>${featureDescriptions[key] || ''}</td>
            `;
            featuresTable.appendChild(row);
        }
        
        // Update performance chart
        updatePerformanceChart(
            parseFloat(data.unoptimized_time), 
            parseFloat(data.optimized_time),
            data.best_optimization
        );
    }
    
    // Function to update performance chart
    function updatePerformanceChart(unoptimizedTime, optimizedTime, optimizationPass) {
        const ctx = document.getElementById('performance-chart').getContext('2d');
        
        // Destroy existing chart if it exists
        if (performanceChart) {
            performanceChart.destroy();
        }
        
        // Calculate percentage improvement for display
        const improvement = unoptimizedTime > 0 ? 
            ((unoptimizedTime - optimizedTime) / unoptimizedTime * 100).toFixed(2) : 0;
        
        // Determine colors based on improvement
        const optimizedColor = optimizedTime < unoptimizedTime ? 
            'rgba(40, 167, 69, 0.7)' : 'rgba(255, 193, 7, 0.7)';
        const optimizedBorder = optimizedTime < unoptimizedTime ? 
            'rgba(40, 167, 69, 1)' : 'rgba(255, 193, 7, 1)';
        
        performanceChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Unoptimized (O0)', `Optimized (${optimizationPass})`],
                datasets: [{
                    label: 'Execution Time (seconds)',
                    data: [unoptimizedTime, optimizedTime],
                    backgroundColor: [
                        'rgba(220, 53, 69, 0.7)',
                        optimizedColor
                    ],
                    borderColor: [
                        'rgba(220, 53, 69, 1)',
                        optimizedBorder
                    ],
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
                            text: 'Execution Time (seconds)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = context.raw;
                                if (context.dataIndex === 1) {
                                    const diff = optimizedTime < unoptimizedTime ? 
                                        `${improvement}% faster` : 
                                        (optimizedTime > unoptimizedTime ? 
                                            `${Math.abs(improvement)}% slower` : 'no change');
                                    return `${value} seconds (${diff})`;
                                }
                                return `${value} seconds`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Helper functions
    function showLoading() {
        document.getElementById('loading-spinner').classList.remove('d-none');
    }
    
    function hideLoading() {
        document.getElementById('loading-spinner').classList.add('d-none');
    }
    
    function showResults() {
        document.getElementById('results-content').classList.remove('d-none');
    }
    
    function hideResults() {
        document.getElementById('results-content').classList.add('d-none');
    }
    
    function showError(message) {
        const errorElement = document.getElementById('error-message');
        errorElement.textContent = message;
        errorElement.classList.remove('d-none');
    }
    
    function hideError() {
        document.getElementById('error-message').classList.add('d-none');
    }
    
    // Function to add code to dataset
    function addToDataset(code, codeName) {
        // Show loading state
        const confirmBtn = document.getElementById('confirm-add-to-dataset');
        const originalText = confirmBtn.innerHTML;
        confirmBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Adding...';
        confirmBtn.disabled = true;
        
        fetch('/contribute', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                code: code,
                name: codeName
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('addToDatasetModal'));
                modal.hide();
                
                // Clear input
                document.getElementById('code-name-input').value = '';
                
                // Show success message
                showSuccess(`✅ Code "${codeName}" successfully added to training dataset! This helps improve optimization accuracy for everyone.`);
                
                // Dataset statistics functionality removed
            } else {
                showError(data.error || 'Failed to add code to dataset');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('Network error while adding code to dataset');
        })
        .finally(() => {
            // Restore button
            confirmBtn.innerHTML = originalText;
            confirmBtn.disabled = false;
        });
    }
    
    // Dataset statistics functionality removed per user request
    
    // Function to show success message
    function showSuccess(message) {
        // Remove existing success messages
        const existingSuccess = document.querySelector('.alert-success');
        if (existingSuccess) {
            existingSuccess.remove();
        }
        
        const successDiv = document.createElement('div');
        successDiv.className = 'alert alert-success alert-dismissible fade show';
        successDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert at top of main container
        const container = document.querySelector('.container-fluid');
        container.insertBefore(successDiv, container.firstChild);
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (successDiv.parentNode) {
                successDiv.remove();
            }
        }, 5000);
    }
});
