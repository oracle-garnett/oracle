import psutil
import time

class ResourceMonitor:
    """
    Monitors system resources (CPU, RAM) to prevent Oracle from consuming too much.
    """
    def __init__(self, cpu_limit_percent: float = 80.0, memory_limit_percent: float = 90.0):
        self.cpu_limit = cpu_limit_percent
        self.memory_limit = memory_limit_percent
        self.process = psutil.Process(os.getpid())
        print("ResourceMonitor initialized.")

    def check_resources(self):
        """Checks current resource usage and raises a warning if limits are exceeded."""
        try:
            cpu_percent = self.process.cpu_percent(interval=None)
            memory_percent = self.process.memory_percent()

            if cpu_percent > self.cpu_limit:
                print(f"WARNING: High CPU usage ({cpu_percent:.2f}%). Oracle may throttle its operations.")
                # In a full implementation, this would signal the TaskExecutor to slow down
            
            if memory_percent > self.memory_limit:
                print(f"CRITICAL: High Memory usage ({memory_percent:.2f}%). Oracle may need to clear cache.")
                # In a full implementation, this would trigger a memory cleanup routine

        except Exception as e:
            # Log the error but don't stop the main application
            print(f"Error during resource monitoring: {e}")

# Import os for process ID
import os
