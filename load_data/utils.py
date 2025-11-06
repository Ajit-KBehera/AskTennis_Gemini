"""
Utility classes and functions for data loading.

This module contains utility classes like ProgressTracker for tracking
loading progress with time estimates.
"""

import time
from datetime import timedelta


class ProgressTracker:
    """Track and display loading progress with time estimates."""
    
    def __init__(self, total_steps, step_name="Loading"):
        self.total_steps = total_steps
        self.current_step = 0
        self.step_name = step_name
        self.start_time = time.time()
        self.last_update = time.time()
        
    def update(self, step_increment=1, message=""):
        """Update progress and display status."""
        self.current_step += step_increment
        percentage = (self.current_step / self.total_steps) * 100
        
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        
        if self.current_step > 0:
            # Calculate estimated total time
            estimated_total_time = elapsed_time * (self.total_steps / self.current_step)
            remaining_time = estimated_total_time - elapsed_time
            
            # Format time strings
            elapsed_str = str(timedelta(seconds=int(elapsed_time)))
            remaining_str = str(timedelta(seconds=int(remaining_time)))
            
            # Update display every 2 seconds or on completion
            if current_time - self.last_update >= 2 or self.current_step == self.total_steps:
                print(f"\r{self.step_name}: {self.current_step}/{self.total_steps} ({percentage:.1f}%) | "
                      f"Elapsed: {elapsed_str} | ETA: {remaining_str} | {message}", end="", flush=True)
                self.last_update = current_time
        
        if self.current_step == self.total_steps:
            print()  # New line when complete
    
    def complete(self, message=""):
        """Mark as complete and show final stats."""
        total_time = time.time() - self.start_time
        print(f"\n✅ {self.step_name} completed in {str(timedelta(seconds=int(total_time)))} | {message}")

