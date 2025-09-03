"""
Digital I/O Controller

Provides individual digital output control with Rich UI formatting.
Allows users to read current output states and toggle individual channels.
"""

from typing import Dict, Optional

from loguru import logger

from application.interfaces.hardware.digital_io import DigitalIOService

from ...rich_formatter import RichFormatter
from ..base.hardware_controller import HardwareController, simple_interactive_menu


class DigitalIOController(HardwareController):
    """Digital I/O hardware controller with output control focus

    Provides real-time output state reading and simple toggle functionality.
    """

    name = "Digital I/O Control"

    def __init__(
        self,
        digital_io_service: DigitalIOService,
        formatter: RichFormatter,
        digital_io_config=None,
    ):
        """Initialize Digital I/O controller.

        Args:
            digital_io_service: Digital I/O service instance
            formatter: Rich formatter for output
            digital_io_config: Configuration object (optional)
        """
        super().__init__(formatter)
        self.digital_io_service = digital_io_service
        self.digital_io_config = digital_io_config

        # Internal state
        self._output_count = 0
        self._current_outputs: Dict[int, bool] = {}

    async def show_status(self) -> None:
        """Display digital I/O hardware status"""
        try:
            is_connected = await self.digital_io_service.is_connected()

            # Format status for display
            connection_status = self._format_connection_status(is_connected)

            self.formatter.print_message(
                f"Digital I/O Status: {connection_status}",
                message_type="info" if is_connected else "warning",
                title="Digital I/O Hardware Status",
            )

            if is_connected:
                # Try to get basic info
                try:
                    input_count = await self.digital_io_service.get_input_count()
                    output_count = await self.digital_io_service.get_output_count()

                    self.formatter.console.print("  Hardware Type: Digital I/O")
                    self.formatter.console.print(f"  Input Channels: {input_count}")
                    self.formatter.console.print(f"  Output Channels: {output_count}")
                except Exception as info_e:
                    logger.debug(f"Could not get detailed status: {info_e}")

        except Exception as e:
            self.formatter.print_message(
                f"Failed to get Digital I/O status: {str(e)}", message_type="error"
            )
            logger.error(f"Digital I/O status error: {e}")

    async def connect(self) -> bool:
        """Connect to digital I/O hardware"""

        async def connect_operation():
            await self.digital_io_service.connect()
            return True

        return await self._show_progress_with_message(
            "Connecting to Digital I/O hardware...",
            connect_operation,
            "Digital I/O hardware connected successfully",
            "Failed to connect to Digital I/O hardware",
        )

    async def disconnect(self) -> bool:
        """Disconnect from digital I/O hardware"""

        async def disconnect_operation():
            await self.digital_io_service.disconnect()
            return True

        return await self._show_progress_with_message(
            "Disconnecting Digital I/O hardware...",
            disconnect_operation,
            "Digital I/O hardware disconnected",
            "Failed to disconnect Digital I/O hardware",
        )

    async def show_control_menu(self) -> Optional[str]:
        """Display digital I/O control menu"""
        menu_options = {
            "1": "Connect",
            "2": "Disconnect",
            "3": "Read Single Input Channel (0-31)",
            "4": "Read All Input Channels",
            "5": "Toggle Output Channel (0-31)",
            "6": "Reset All Outputs",
            "7": "Show All Output States",
            "8": "Show Status",
            "b": "Back to Hardware Menu",
        }

        return simple_interactive_menu(
            self.formatter.console, menu_options, "Digital I/O Control", "Select action"
        )

    async def execute_command(self, command: str) -> bool:
        """Execute digital I/O control command"""
        try:
            if command == "1":
                await self.connect()
            elif command == "2":
                await self.disconnect()
            elif command == "3":
                await self._read_input_interactive()
            elif command == "4":
                await self._show_all_input_states()
            elif command == "5":
                await self._toggle_output_interactive()
            elif command == "6":
                await self._reset_all_outputs()
            elif command == "7":
                await self._show_all_output_states()
            elif command == "8":
                await self.show_status()
            elif command == "b":
                return True
            else:
                self.formatter.print_message(f"Invalid command: {command}", message_type="warning")

            return True

        except Exception as e:
            self.formatter.print_message(f"Command execution error: {str(e)}", message_type="error")
            logger.error(f"Digital I/O command error: {e}")
            return False

    async def _show_all_output_states(self) -> None:
        """Display all digital output states in a table format"""
        try:
            self.formatter.print_header("Digital Output States", "Current output channel states")

            # Read current states from hardware
            await self._read_current_output_states()

            if not self._current_outputs:
                self.formatter.print_message(
                    "No output channels available or hardware not connected", message_type="warning"
                )
                return

            # Display states in a table format
            self._display_output_states_table()

        except Exception as e:
            self.formatter.print_message(
                f"Failed to read output states: {str(e)}", message_type="error"
            )
            logger.error(f"Output state reading error: {e}")

    async def _toggle_output_interactive(self) -> None:
        """Interactive output channel toggle"""
        try:
            # First show current states
            await self._show_all_output_states()

            if not self._current_outputs:
                return

            self.formatter.console.print()
            self.formatter.print_message(
                "Enter channel number to toggle (or 'cancel' to abort):", message_type="info"
            )

            # Continuous toggle loop
            while True:
                try:
                    user_input = input("Channel number (or 'b' to back): ").strip()

                    if user_input.lower() in ["b", "back", "cancel"]:
                        break

                    channel = int(user_input)

                    if channel < 0 or channel >= self._output_count:
                        self.formatter.print_message(
                            f"Channel {channel} out of range [0, {self._output_count-1}]",
                            message_type="warning",
                        )
                        continue

                    # Toggle the channel
                    success = await self._toggle_output_channel(channel)

                    if success:
                        # Read updated state and show change
                        await self._read_current_output_states()
                        current_state = self._current_outputs.get(channel, False)
                        state_str = "HIGH" if current_state else "LOW"

                        self.formatter.print_message(
                            f"Channel {channel} toggled → {state_str}", message_type="success"
                        )

                        # Show updated states table
                        self._display_output_states_table()

                except ValueError:
                    self.formatter.print_message(
                        "Invalid channel number. Please enter a valid integer.",
                        message_type="warning",
                    )
                except (KeyboardInterrupt, EOFError):
                    break
                except Exception as e:
                    self.formatter.print_message(f"Toggle error: {str(e)}", message_type="error")

        except Exception as e:
            self.formatter.print_message(
                f"Interactive toggle error: {str(e)}", message_type="error"
            )
            logger.error(f"Interactive toggle error: {e}")

    async def _toggle_output_channel(self, channel: int) -> bool:
        """Toggle specific output channel"""
        try:
            # Read current state
            current_state = await self.digital_io_service.read_output(channel)

            # Toggle state
            new_state = not current_state

            # Write new state
            success = await self.digital_io_service.write_output(channel, new_state)

            if success:
                logger.debug(f"Toggled output channel {channel}: {current_state} → {new_state}")

            return success

        except Exception as e:
            logger.error(f"Failed to toggle output channel {channel}: {e}")
            raise

    async def _reset_all_outputs(self) -> None:
        """Reset all outputs to LOW"""
        try:
            success = await self._show_progress_with_message(
                "Resetting all outputs to LOW...",
                self.digital_io_service.reset_all_outputs,
                "All outputs reset to LOW",
                "Failed to reset outputs",
            )

            if success:
                # Update internal state
                await self._read_current_output_states()

        except Exception as e:
            self.formatter.print_message(f"Reset outputs error: {str(e)}", message_type="error")
            logger.error(f"Reset outputs error: {e}")

    async def _toggle_connection(self) -> None:
        """Toggle hardware connection"""
        try:
            is_connected = await self.digital_io_service.is_connected()

            if is_connected:
                await self.disconnect()
            else:
                await self.connect()

        except Exception as e:
            self.formatter.print_message(f"Connection toggle error: {str(e)}", message_type="error")
            logger.error(f"Connection toggle error: {e}")

    async def _read_current_output_states(self) -> None:
        """Read current output states from hardware"""
        try:
            # Get output count
            self._output_count = await self.digital_io_service.get_output_count()

            if self._output_count == 0:
                self._current_outputs = {}
                return

            # Read all output states
            output_states = await self.digital_io_service.read_all_outputs()

            # Store in internal dict
            self._current_outputs = {}
            for i, state in enumerate(output_states):
                if i < self._output_count:
                    self._current_outputs[i] = state

            logger.debug(f"Read {len(self._current_outputs)} output states")

        except Exception as e:
            logger.error(f"Failed to read output states: {e}")
            # Fallback to empty state
            self._current_outputs = {}

    def _display_output_states_table(self) -> None:
        """Display output states in a formatted table"""
        if not self._current_outputs:
            return

        self.formatter.console.print()
        self.formatter.console.print("[bold cyan]Current Output States:[/bold cyan]")

        # Display in rows of 8 channels
        channels_per_row = 8

        for start_ch in range(0, self._output_count, channels_per_row):
            end_ch = min(start_ch + channels_per_row, self._output_count)

            # Channel headers
            header_line = "  "
            state_line = "  "

            for ch in range(start_ch, end_ch):
                header_line += f"CH{ch:<3} "
                state = self._current_outputs.get(ch, False)

                if state:
                    state_line += "[green]HIGH[/green] "
                else:
                    state_line += "[dim]LOW [/dim] "

            self.formatter.console.print(header_line)
            self.formatter.console.print(state_line)
            self.formatter.console.print()

    # ========================================================================
    # Digital Input Methods
    # ========================================================================

    async def _read_input_interactive(self) -> None:
        """Interactively read a single digital input channel"""
        try:
            self.formatter.print_header("Read Input Channel", "Select channel to read (0-31)")

            # Get channel from user
            channel_input = input("Enter channel number (0-31): ").strip()

            try:
                channel = int(channel_input)
                if channel < 0 or channel > 31:
                    self.formatter.print_message(
                        "Channel must be between 0 and 31", message_type="warning"
                    )
                    return
            except ValueError:
                self.formatter.print_message(
                    "Please enter a valid number (0-31)", message_type="warning"
                )
                return

            # Read the input
            self.formatter.console.print(f"Reading input channel {channel}...")

            # Read raw state
            raw_state = await self.digital_io_service.read_input(channel)

            # Apply B-contact logic for button channels (8, 9) - inverted logic
            if channel in [8, 9]:  # Button channels with B-contact (normally closed)
                actual_state = not raw_state
                contact_type = "B-contact (NC)"
            else:
                actual_state = raw_state
                contact_type = "A-contact (NO)"

            # Display result
            self.formatter.console.print()
            self.formatter.console.print(f"[bold]Channel {channel} Status:[/bold]")
            self.formatter.console.print(
                f"  Raw State: {'[green]HIGH[/green]' if raw_state else '[dim]LOW[/dim]'}"
            )
            self.formatter.console.print(
                f"  Actual State: {'[green]HIGH[/green]' if actual_state else '[dim]LOW[/dim]'}"
            )
            self.formatter.console.print(f"  Contact Type: {contact_type}")

            if channel in [8, 9]:
                button_name = "Left" if channel == 8 else "Right"
                button_status = "PRESSED" if actual_state else "RELEASED"
                self.formatter.console.print(
                    f"  Button Status: [bold]{button_name} button {button_status}[/bold]"
                )

            self.formatter.console.print()

        except Exception as e:
            self.formatter.print_message(
                f"Failed to read input channel: {str(e)}", message_type="error"
            )
            logger.error(f"Input read error: {e}")

    async def _show_all_input_states(self) -> None:
        """Display all digital input states in a table format"""
        try:
            self.formatter.print_header("All Input States", "Current state of all input channels")

            # Get input count
            try:
                input_count = await self.digital_io_service.get_input_count()
            except Exception:
                input_count = 32  # Default to 32 channels

            # Read all input states
            self.formatter.console.print("Reading all input channels...")
            input_states = await self.digital_io_service.read_all_inputs()

            # Ensure we have exactly input_count states
            if len(input_states) < input_count:
                input_states.extend([False] * (input_count - len(input_states)))
            elif len(input_states) > input_count:
                input_states = input_states[:input_count]

            # Display in rows of 8 channels
            self.formatter.console.print()
            self.formatter.console.print("[bold cyan]Current Input States:[/bold cyan]")

            channels_per_row = 8

            for start_ch in range(0, input_count, channels_per_row):
                end_ch = min(start_ch + channels_per_row, input_count)

                # Channel headers
                header_line = "  "
                raw_line = "  "
                actual_line = "  "

                for ch in range(start_ch, end_ch):
                    header_line += f"CH{ch:<3} "
                    raw_state = input_states[ch]

                    # Apply B-contact logic for button channels
                    if ch in [8, 9]:  # B-contact channels
                        actual_state = not raw_state
                    else:
                        actual_state = raw_state

                    # Raw state display
                    if raw_state:
                        raw_line += "[green]HIGH[/green] "
                    else:
                        raw_line += "[dim]LOW [/dim] "

                    # Actual state display
                    if actual_state:
                        actual_line += "[green]HIGH[/green] "
                    else:
                        actual_line += "[dim]LOW [/dim] "

                self.formatter.console.print(header_line)
                self.formatter.console.print(f"Raw:    {raw_line}")
                self.formatter.console.print(f"Actual: {actual_line}")
                self.formatter.console.print()

            # Special status for button channels
            self.formatter.console.print("[bold yellow]Button Status:[/bold yellow]")
            left_raw = input_states[8]
            right_raw = input_states[9]
            left_pressed = not left_raw  # B-contact inversion
            right_pressed = not right_raw

            self.formatter.console.print(
                f"  Left Button (CH8):  {'[bold green]PRESSED[/bold green]' if left_pressed else '[dim]RELEASED[/dim]'}"
            )
            self.formatter.console.print(
                f"  Right Button (CH9): {'[bold green]PRESSED[/bold green]' if right_pressed else '[dim]RELEASED[/dim]'}"
            )
            self.formatter.console.print()

        except Exception as e:
            self.formatter.print_message(
                f"Failed to read input states: {str(e)}", message_type="error"
            )
            logger.error(f"Input states read error: {e}")
