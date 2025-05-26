import subprocess
import time
import logging
import statistics

logger = logging.getLogger(__name__)

def measure_execution_time(executable_path, runs=5):
    """
    Measure the execution time of a compiled program by running it multiple times
    and returning the average time.
    
    Args:
        executable_path: Path to the executable file
        runs: Number of times to run the program for averaging
        
    Returns:
        Average execution time in seconds
    """
    if not executable_path:
        logger.error("No executable path provided")
        return 0
        
    execution_times = []
    
    try:
        for i in range(runs):
            # Add small delay between runs for consistency
            if i > 0:
                time.sleep(0.05)
                
            start_time = time.perf_counter()  # More precise timing
            
            # Run the executable
            process = subprocess.run([executable_path], 
                                    capture_output=True, 
                                    text=True, 
                                    timeout=10)  # 10 second timeout
            
            end_time = time.perf_counter()
            
            if process.returncode == 0:
                execution_time = end_time - start_time
                execution_times.append(execution_time)
            else:
                logger.warning(f"Execution failed for {executable_path}: {process.stderr}")
            
        # Calculate average execution time
        if execution_times:
            # Remove outliers if we have enough samples
            if len(execution_times) >= 3:
                execution_times.remove(max(execution_times))
                execution_times.remove(min(execution_times))
                
            average_time = statistics.mean(execution_times)
            logger.debug(f"Measured execution time for {executable_path}: {average_time:.6f}s")
            return average_time
        else:
            logger.warning(f"No successful executions for {executable_path}")
            return 0
            
    except subprocess.TimeoutExpired:
        logger.warning(f"Execution of {executable_path} timed out")
        return 10.0  # Return maximum time on timeout
    except Exception as e:
        logger.exception(f"Error measuring execution time: {str(e)}")
        return 0
