"""Progress Indicators and Spinners for CLI Rich UI Components

Specialized formatter class focused on progress displays, spinners, and
long-running operation indicators. This module provides methods for creating
progress bars, status spinners, and other progress-related UI elements with
consistent styling and cross-platform compatibility.

This formatter handles both deterministic progress (with known total steps)
and indeterminate progress (unknown duration) with appropriate visual feedback.
"""

from typing import Optional, Union

from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.status import Status

from .base_formatter import BaseFormatter


class ProgressFormatter(BaseFormatter):
    """Specialized formatter for progress indicators and long-running operations.

    This class extends BaseFormatter to provide specialized methods for creating
    progress displays, spinners, and status indicators for long-running operations.
    It handles both deterministic and indeterminate progress with appropriate
    visual feedback and cross-platform compatibility.

    Key Features:
    - Progress bars for deterministic operations (known total steps)
    - Spinner status for indeterminate operations (unknown duration)
    - Cross-platform spinner compatibility (Windows, Linux, macOS)
    - Consistent styling with theme integration
    - Time elapsed tracking for performance monitoring
    """

    def create_progress_display(
        self,
        task_name: str,
        total_steps: Optional[int] = None,
        current_step: Optional[int] = None,
        show_spinner: bool = True,
    ) -> Union[Progress, Status]:
        """Create a progress display for long-running operations.

        Generates an appropriate progress indicator based on whether the total
        number of steps is known. Creates a progress bar for deterministic
        operations or a spinner for indeterminate operations.

        Args:
            task_name: Descriptive name of the task being performed
            total_steps: Total number of steps (enables progress bar if provided)
            current_step: Current step number for initial progress position
            show_spinner: Whether to show a spinner animation in progress displays

        Returns:
            Rich Progress bar for deterministic operations or Status spinner
            for indeterminate operations
        """
        if total_steps is not None:
            return self._create_progress_bar(task_name, total_steps, current_step, show_spinner)
        else:
            return self._create_spinner_status(task_name)

    def create_spinner_status(
        self,
        task_name: str,
        spinner_type: Optional[str] = None,
    ) -> Status:
        """Create a spinner status for indeterminate operations.

        Creates a spinner status display with automatic platform-specific
        spinner selection for optimal compatibility and visual appeal.

        Args:
            task_name: Descriptive name of the task being performed
            spinner_type: Optional spinner type override (auto-detected if None)

        Returns:
            Rich Status spinner with platform-optimized animation
        """
        if not spinner_type:
            spinner_type = self._get_optimal_spinner()

        return Status(
            f"{self.icons.get_icon('running')} {task_name}",
            console=self.console,
            spinner=spinner_type,
            spinner_style=self.colors.get_color("primary"),
            speed=1.0,  # Normal spinner speed
        )

    def _create_progress_bar(
        self,
        task_name: str,
        total_steps: int,
        current_step: Optional[int],
        show_spinner: bool,
    ) -> Progress:
        """Create a progress bar for deterministic operations.

        Args:
            task_name: Descriptive name of the task
            total_steps: Total number of steps in the operation
            current_step: Current step number for initial position
            show_spinner: Whether to show spinner animation

        Returns:
            Configured Rich Progress bar with appropriate columns
        """
        # Configure progress bar columns based on options
        columns = []

        # Add spinner column if requested
        if show_spinner:
            columns.append(SpinnerColumn())
        else:
            columns.append(TextColumn("[progress.description]{task.description}"))

        # Add core progress bar components
        columns.extend(
            [
                TextColumn("[progress.description]{task.description}"),
                BarColumn(
                    style=self.colors.get_color("primary"),
                    complete_style=self.colors.get_color("success"),
                ),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
            ]
        )

        progress = Progress(*columns, console=self.console)

        # Add the task with initial progress if specified
        task_id = progress.add_task(task_name, total=total_steps)
        if current_step is not None:
            progress.update(task_id, completed=current_step)

        return progress

    def _create_spinner_status(self, task_name: str) -> Status:
        """Create a spinner status with platform-optimized settings.

        Args:
            task_name: Descriptive name of the task

        Returns:
            Platform-optimized Status spinner
        """
        spinner_type = self._get_optimal_spinner()

        return Status(
            f"{self.icons.get_icon('running')} {task_name}",
            console=self.console,
            spinner=spinner_type,
            spinner_style=self.colors.get_color("primary"),
            speed=1.0,
        )

    def _get_optimal_spinner(self) -> str:
        """Get optimal spinner type based on platform and terminal capabilities.

        Selects the best spinner animation for the current platform and terminal
        to ensure maximum compatibility and visual appeal.

        Returns:
            Spinner type string optimized for current platform
        """
        # Default spinner options ordered by preference
        spinner_options = ["dots2", "dots", "line", "arc", "arrow3"]
        selected_spinner = "dots2"  # Default preference

        # Use simpler spinner for Windows/basic terminals for better compatibility
        try:
            import os

            if os.name == "nt":  # Windows
                selected_spinner = "line"
        except ImportError:
            # Fallback to simple dots if os module unavailable
            selected_spinner = "dots"

        return selected_spinner

    def update_progress(
        self,
        progress: Progress,
        task_id,  # TaskID type from Rich
        advance: Optional[int] = None,
        completed: Optional[int] = None,
        description: Optional[str] = None,
    ) -> None:
        """Update progress bar with new values.

        Provides a convenient method for updating progress bar state with
        optional parameters for different update scenarios.

        Args:
            progress: Progress bar instance to update
            task_id: Task identifier returned from add_task()
            advance: Number of steps to advance (incremental update)
            completed: Absolute completed step count (absolute update)
            description: Optional new task description
        """
        update_kwargs = {}

        if advance is not None:
            update_kwargs["advance"] = advance
        if completed is not None:
            update_kwargs["completed"] = completed
        if description is not None:
            update_kwargs["description"] = description

        if update_kwargs:
            progress.update(task_id, **update_kwargs)

    def finish_progress(
        self, progress: Progress, task_id, final_message: Optional[str] = None
    ) -> None:
        """Complete a progress bar with optional final message.

        Marks a progress task as complete and optionally updates the description
        with a final completion message.

        Args:
            progress: Progress bar instance to complete
            task_id: Task identifier to mark as complete
            final_message: Optional final message to display
        """
        if final_message:
            progress.update(task_id, description=final_message)

        # Complete the task by setting completed to total
        task = progress.tasks[task_id]
        progress.update(task_id, completed=task.total)

    # Convenience methods for common progress scenarios
    def create_simple_progress(self, task_name: str, total_steps: int):
        """Create a simple progress bar without spinner.

        Args:
            task_name: Descriptive name of the task
            total_steps: Total number of steps

        Returns:
            Simple progress bar without spinner animation
        """
        return self.create_progress_display(
            task_name=task_name, total_steps=total_steps, show_spinner=False
        )

    def create_animated_progress(self, task_name: str, total_steps: int):
        """Create an animated progress bar with spinner.

        Args:
            task_name: Descriptive name of the task
            total_steps: Total number of steps

        Returns:
            Animated progress bar with spinner
        """
        return self.create_progress_display(
            task_name=task_name, total_steps=total_steps, show_spinner=True
        )
