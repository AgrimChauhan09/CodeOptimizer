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
        // Get the example code from the page
        const exampleCode = `
#include <stdio.h>

int fibonacci(int n) {
    if (n <= 1)
        return n;
    return fibonacci(n-1) + fibonacci(n-2);
}

int main() {
    int result = 0;
    for (int i = 0; i < 20; i++) {
        result += fibonacci(i);
    }
    printf("Result: %d\\n", result);
    return 0;
}
`;
        codeEditor.setValue(exampleCode.trim());
        hideResults();
        hideError();
    });
    
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
        
        // Display times
        document.getElementById('unoptimized-time').textContent = data.unoptimized_time;
        document.getElementById('optimized-time').textContent = data.optimized_time;
        document.getElementById('best-optimization').textContent = data.best_optimization;
        document.getElementById('time-improvement').textContent = data.time_improvement;
        
        // Display LLVM IR
        irViewer.setValue(data.llvm_ir || 'No LLVM IR available');
        
        // Populate features table
        const featuresTable = document.getElementById('features-table');
        featuresTable.innerHTML = '';
        
        const featureDescriptions = {
            'loop_count': 'Number of loops in the code',
            'func_calls': 'Number of function calls',
            'instr_count': 'Total number of instructions',
            'has_branch': 'Contains branching instructions (if/else/switch)',
            'uses_memory': 'Uses memory operations (alloca/load/store)',
            'uses_global': 'References global variables'
        };
        
        for (const [key, value] of Object.entries(data.features)) {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><strong>${key.replace('_', ' ')}</strong></td>
                <td>${value}</td>
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
        
        performanceChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Unoptimized (O0)', `Optimized (${optimizationPass})`],
                datasets: [{
                    label: 'Execution Time (seconds)',
                    data: [unoptimizedTime, optimizedTime],
                    backgroundColor: [
                        'rgba(220, 53, 69, 0.7)',
                        'rgba(40, 167, 69, 0.7)'
                    ],
                    borderColor: [
                        'rgba(220, 53, 69, 1)',
                        'rgba(40, 167, 69, 1)'
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
                                return `${context.raw} seconds`;
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
});
