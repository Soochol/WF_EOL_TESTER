# Temporary file with methods to append to search_widget.py

def _on_delete_clicked(self) -> None:
    """Handle Delete Selected button click"""
    if not self.results_table:
        return

    selected_ids = self.results_table.get_selected_test_ids()
    logger.info(f"Delete clicked: {len(selected_ids)} test IDs selected")

    if not selected_ids:
        logger.warning("No tests selected for deletion")
        return

    # Third-party imports
    from PySide6.QtWidgets import QMessageBox

    # Confirmation dialog
    reply = QMessageBox.question(
        self,
        "Confirm Deletion",
        f"Are you sure you want to delete {len(selected_ids)} test(s) and all associated measurements?\n\n"
        f"This action cannot be undone.",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No,  # Default to No
    )

    if reply == QMessageBox.StandardButton.Yes:
        logger.info(f"User confirmed deletion of {len(selected_ids)} tests")
        # Run async deletion using QTimer for proper Qt-asyncio integration
        from PySide6.QtCore import QTimer

        QTimer.singleShot(0, lambda: self._run_delete_async(selected_ids))
    else:
        logger.info("User cancelled deletion")


def _run_delete_async(self, test_ids: List[str]) -> None:
    """Run async deletion using new event loop"""
    # Third-party imports
    import asyncio

    try:
        # Create new event loop for this operation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._delete_tests(test_ids))
        loop.close()
    except Exception as e:
        logger.error(f"Delete execution failed: {e}")
        # Standard library imports
        import traceback

        traceback.print_exc()


async def _delete_tests(self, test_ids: List[str]) -> None:
    """Perform database deletion"""
    try:
        logger.info(f"Deleting {len(test_ids)} tests from database...")

        # Call repository delete method
        result = await self.db_repo.delete_measurements_by_test_ids(test_ids)

        # Show result dialog
        from PySide6.QtWidgets import QMessageBox

        deleted_count = result.get("deleted_count", 0)
        deleted_tests = result.get("deleted_tests", [])
        failed = result.get("failed", [])
        errors = result.get("errors", {})

        if failed:
            # Some deletions failed
            error_details = "\n".join([f"- {tid}: {errors.get(tid, 'Unknown error')}" for tid in failed])
            QMessageBox.warning(
                self,
                "Partial Deletion",
                f"Deleted {deleted_count} measurements from {len(deleted_tests)} test(s).\n\n"
                f"Failed to delete {len(failed)} test(s):\n{error_details}",
            )
            logger.warning(
                f"Partial deletion: {len(deleted_tests)} succeeded, {len(failed)} failed"
            )
        else:
            # All deletions succeeded
            QMessageBox.information(
                self,
                "Deletion Complete",
                f"Successfully deleted {deleted_count} measurements from {len(deleted_tests)} test(s).",
            )
            logger.info(f"Deletion complete: {deleted_count} measurements deleted")

        # Refresh search results
        self._refresh_search()

    except Exception as e:
        logger.error(f"Delete failed: {e}")
        # Standard library imports
        import traceback

        traceback.print_exc()

        # Show error dialog
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.critical(
            self,
            "Deletion Error",
            f"Failed to delete tests:\n{str(e)}",
        )


def _refresh_search(self) -> None:
    """Refresh search results after deletion"""
    logger.info("Refreshing search results after deletion...")

    if not self.filters_panel:
        return

    # Get current filters
    filters = self.filters_panel.get_filters()

    # Run search again
    # Third-party imports
    from PySide6.QtCore import QTimer

    QTimer.singleShot(0, lambda: self._run_search_async(filters))


def _get_delete_button_style(self) -> str:
    """Get delete button stylesheet (red/warning style)"""
    # Local application imports
    from ui.gui.styles.common_styles import (
        BACKGROUND_MEDIUM,
        BORDER_DEFAULT,
        TEXT_PRIMARY,
        TEXT_SECONDARY,
    )

    return f"""
        QPushButton {{
            background-color: #8B0000;  /* Dark red */
            color: {TEXT_PRIMARY};
            border: 1px solid #A52A2A;  /* Brown-red border */
            border-radius: 4px;
            padding: 8px 16px;
            font-size: 14px;
            font-weight: 500;
            min-width: 120px;
            min-height: 32px;
        }}
        QPushButton:hover {{
            background-color: #A52A2A;  /* Lighter red on hover */
            border-color: #CD5C5C;
        }}
        QPushButton:pressed {{
            background-color: #660000;  /* Darker red when pressed */
        }}
        QPushButton:disabled {{
            background-color: {BACKGROUND_MEDIUM};
            color: {TEXT_SECONDARY};
            border-color: {BORDER_DEFAULT};
        }}
    """
