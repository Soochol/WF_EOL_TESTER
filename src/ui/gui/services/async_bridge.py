"""
Async Bridge Service

Utility for bridging asyncio operations with Qt GUI thread.
"""

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Awaitable, Callable, Optional

from loguru import logger
from PySide6.QtCore import QObject, QTimer, Signal


class AsyncBridge(QObject):
    """
    Bridge for executing async operations from GUI thread

    Provides safe way to run asyncio coroutines from Qt GUI
    without blocking the main thread.
    """

    # Signals for async operation results
    operation_completed = Signal(object)  # result
    operation_failed = Signal(str)  # error_message

    def __init__(self, parent: Optional[QObject] = None):
        """
        Initialize async bridge

        Args:
            parent: Parent QObject
        """
        super().__init__(parent)

        # Thread pool for async operations
        self.thread_pool = ThreadPoolExecutor(max_workers=4)

        # Timer for processing asyncio events
        self.asyncio_timer = QTimer()
        self.asyncio_timer.timeout.connect(self._process_asyncio_events)
        self.asyncio_timer.start(10)  # Process every 10ms

        logger.debug("AsyncBridge initialized")

    def run_async(
        self,
        coroutine: Awaitable[Any],
        success_callback: Optional[Callable[[Any], None]] = None,
        error_callback: Optional[Callable[[str], None]] = None,
    ) -> None:
        """
        Run async coroutine in background thread

        Args:
            coroutine: Async coroutine to run
            success_callback: Callback for successful completion
            error_callback: Callback for errors
        """

        def run_in_thread():
            try:
                # Create new event loop for thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                try:
                    # Run coroutine
                    result = loop.run_until_complete(coroutine)

                    # Emit success signal
                    self.operation_completed.emit(result)

                    # Call success callback if provided
                    if success_callback:
                        success_callback(result)

                finally:
                    loop.close()

            except Exception as e:
                error_msg = str(e)
                logger.error(f"Async operation failed: {error_msg}")

                # Emit error signal
                self.operation_failed.emit(error_msg)

                # Call error callback if provided
                if error_callback:
                    error_callback(error_msg)

        # Submit to thread pool
        self.thread_pool.submit(run_in_thread)

    def run_sync_in_thread(
        self,
        func: Callable[[], Any],
        success_callback: Optional[Callable[[Any], None]] = None,
        error_callback: Optional[Callable[[str], None]] = None,
    ) -> None:
        """
        Run synchronous function in background thread

        Args:
            func: Synchronous function to run
            success_callback: Callback for successful completion
            error_callback: Callback for errors
        """

        def run_in_thread():
            try:
                result = func()

                # Emit success signal
                self.operation_completed.emit(result)

                # Call success callback if provided
                if success_callback:
                    success_callback(result)

            except Exception as e:
                error_msg = str(e)
                logger.error(f"Sync operation failed: {error_msg}")

                # Emit error signal
                self.operation_failed.emit(error_msg)

                # Call error callback if provided
                if error_callback:
                    error_callback(error_msg)

        # Submit to thread pool
        self.thread_pool.submit(run_in_thread)

    def _process_asyncio_events(self) -> None:
        """Process pending asyncio events (called by timer)"""
        try:
            # Try to get current event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Process some pending callbacks
                # This is a simplified approach
                pass
        except RuntimeError:
            # No event loop in current thread
            pass
        except Exception as e:
            # Ignore errors in event processing
            pass

    def shutdown(self) -> None:
        """Shutdown async bridge"""
        try:
            # Stop timer
            if self.asyncio_timer:
                self.asyncio_timer.stop()

            # Shutdown thread pool
            if self.thread_pool:
                self.thread_pool.shutdown(wait=True)

            logger.debug("AsyncBridge shutdown")

        except Exception as e:
            logger.error(f"AsyncBridge shutdown error: {e}")


# Global async bridge instance
_async_bridge: Optional[AsyncBridge] = None


def get_async_bridge() -> AsyncBridge:
    """
    Get global async bridge instance

    Returns:
        Global AsyncBridge instance
    """
    global _async_bridge
    if _async_bridge is None:
        _async_bridge = AsyncBridge()
    return _async_bridge


def run_async_operation(
    coroutine: Awaitable[Any],
    success_callback: Optional[Callable[[Any], None]] = None,
    error_callback: Optional[Callable[[str], None]] = None,
) -> None:
    """
    Convenience function to run async operation

    Args:
        coroutine: Async coroutine to run
        success_callback: Callback for successful completion
        error_callback: Callback for errors
    """
    bridge = get_async_bridge()
    bridge.run_async(coroutine, success_callback, error_callback)


def run_sync_operation(
    func: Callable[[], Any],
    success_callback: Optional[Callable[[Any], None]] = None,
    error_callback: Optional[Callable[[str], None]] = None,
) -> None:
    """
    Convenience function to run sync operation in background

    Args:
        func: Synchronous function to run
        success_callback: Callback for successful completion
        error_callback: Callback for errors
    """
    bridge = get_async_bridge()
    bridge.run_sync_in_thread(func, success_callback, error_callback)
