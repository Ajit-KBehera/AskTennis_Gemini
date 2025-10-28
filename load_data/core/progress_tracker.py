"""
Progress tracking utilities for AskTennis data loading.
Provides progress tracking with time estimates and status updates.
"""

import time
from datetime import timedelta
from config.settings import PROGRESS_DISPLAY_INTERVAL


class ProgressTracker:
    """
    Track and display loading progress with time estimates.
    
    Provides real-time progress tracking with:
    - Percentage completion
    - Elapsed time
    - Estimated time remaining
    - Custom status messages
    """
    
    def __init__(self, total_steps, step_name="Loading"):
        """
        Initialize the progress tracker.
        
        Args:
            total_steps (int): Total number of steps to complete
            step_name (str): Name of the process being tracked
        """
        self.total_steps = total_steps
        self.current_step = 0
        self.step_name = step_name
        self.start_time = time.time()
        self.last_update = time.time()
        
    def update(self, step_increment=1, message=""):
        """
        Update progress and display status.
        
        Args:
            step_increment (int): Number of steps completed
            message (str): Optional status message to display
        """
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
            
            # Update display every PROGRESS_DISPLAY_INTERVAL seconds or on completion
            if (current_time - self.last_update >= PROGRESS_DISPLAY_INTERVAL or 
                self.current_step == self.total_steps):
                print(f"\r{self.step_name}: {self.current_step}/{self.total_steps} ({percentage:.1f}%) | "
                      f"Elapsed: {elapsed_str} | ETA: {remaining_str} | {message}", end="", flush=True)
                self.last_update = current_time
        
        if self.current_step == self.total_steps:
            print()  # New line when complete
    
    def complete(self, message=""):
        """
        Mark as complete and show final stats.
        
        Args:
            message (str): Optional completion message
        """
        total_time = time.time() - self.start_time
        print(f"\n✅ {self.step_name} completed in {str(timedelta(seconds=int(total_time)))} | {message}")
    
    def reset(self, total_steps=None, step_name=None):
        """
        Reset the progress tracker for reuse.
        
        Args:
            total_steps (int): New total steps (optional)
            step_name (str): New step name (optional)
        """
        if total_steps is not None:
            self.total_steps = total_steps
        if step_name is not None:
            self.step_name = step_name
        
        self.current_step = 0
        self.start_time = time.time()
        self.last_update = time.time()
    
    @property
    def percentage(self):
        """Get current completion percentage."""
        if self.total_steps == 0:
            return 0
        return (self.current_step / self.total_steps) * 100
    
    @property
    def elapsed_time(self):
        """Get elapsed time in seconds."""
        return time.time() - self.start_time
    
    @property
    def estimated_remaining_time(self):
        """Get estimated remaining time in seconds."""
        if self.current_step == 0:
            return 0
        
        elapsed_time = self.elapsed_time
        estimated_total_time = elapsed_time * (self.total_steps / self.current_step)
        return max(0, estimated_total_time - elapsed_time)
    
    def __str__(self):
        """String representation of progress."""
        return f"{self.step_name}: {self.current_step}/{self.total_steps} ({self.percentage:.1f}%)"
    
    def __repr__(self):
        """Detailed string representation."""
        return (f"ProgressTracker(total_steps={self.total_steps}, "
                f"current_step={self.current_step}, "
                f"step_name='{self.step_name}')")
