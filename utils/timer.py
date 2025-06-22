import subprocess
import time
import logging
import statistics

logger = logging.getLogger(__name__)

def measure_execution_time(executable_path, runs=7):
    """
    Measure the execution time of a compiled program by running it multiple times
    and returning a stable, consistent average time.
    
    Args:
        executable_path: Path to the executable file
        runs: Number of times to run the program for averaging
        
    Returns:
        Stable average execution time in seconds
    """
    if not executable_path:
        logger.error("No executable path provided")
        return 0
        
    execution_times = []
    
    try:
        # Warmup run to stabilize system
        subprocess.run([executable_path], capture_output=True, timeout=5)
        time.sleep(0.1)
        
        for i in range(runs):
            # Ensure consistent system state between runs
            if i > 0:
                time.sleep(0.02)  # Smaller delay for consistency
                
            # Use high-precision timing
            start_time = time.perf_counter_ns()
            
            # Run the executable
            process = subprocess.run([executable_path], 
                                    capture_output=True, 
                                    text=True, 
                                    timeout=8)
            
            end_time = time.perf_counter_ns()
            
            if process.returncode == 0:
                execution_time = (end_time - start_time) / 1_000_000_000  # Convert to seconds
                execution_times.append(execution_time)
            else:
                logger.warning(f"Execution failed for {executable_path}: {process.stderr}")
            
        # Calculate stable average execution time
        if execution_times and len(execution_times) >= 3:
            # Remove outliers more aggressively for stability
            execution_times.sort()
            # Remove top and bottom 20% of results
            trim_count = max(1, len(execution_times) // 5)
            trimmed_times = execution_times[trim_count:-trim_count] if trim_count > 0 else execution_times
            
            if trimmed_times:
                # Use median of trimmed results for maximum stability
                average_time = statistics.median(trimmed_times)
                logger.debug(f"Measured stable execution time for {executable_path}: {average_time:.6f}s")
                return round(average_time, 6)  # Round to microsecond precision
        
        # Fallback for insufficient data
        if execution_times:
            average_time = statistics.median(execution_times)
            return round(average_time, 6)
        else:
            logger.warning(f"No successful executions for {executable_path}")
            return 0
            
    except subprocess.TimeoutExpired:
        logger.warning(f"Execution of {executable_path} timed out")
        return 10.0  # Return maximum time on timeout
    except Exception as e:
        logger.exception(f"Error measuring execution time: {str(e)}")
        return 0
