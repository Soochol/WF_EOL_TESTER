"""
Results Command

Handles test results management and display commands.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

from loguru import logger

from application.interfaces.repository.test_result_repository import (
    TestResultRepository,
)
from application.services.repository_service import (
    RepositoryService,
)
from ui.cli.commands.base import Command, CommandResult


class ResultsCommand(Command):
    """Command for test results management"""

    def __init__(
        self,
        repository_service: Optional[RepositoryService] = None,
    ):
        super().__init__(
            name="results",
            description="Test results management and analysis",
        )
        self._repository_service = repository_service

    def set_repository_service(self, repository_service: RepositoryService) -> None:
        """Set the repository service for results access"""
        self._repository_service = repository_service

    async def execute(self, args: List[str]) -> CommandResult:  # pylint: disable=too-many-return-statements
        """
        Execute results command

        Args:
            args: Command arguments (subcommand and parameters)

        Returns:
            CommandResult with results operation results
        """
        if not self._repository_service:
            return CommandResult.error("Repository service not initialized")
        # Type narrowing for mypy
        assert self._repository_service is not None

        if not args:
            return await self._list_recent_results()

        subcommand = args[0].lower()

        # Route to appropriate handler
        if subcommand == "list":
            return await self._list_results(args[1:])
        if subcommand == "view":
            return await self._view_result(args[1:])
        if subcommand == "stats":
            return await self._show_statistics()
        if subcommand == "export":
            return await self._export_results(args[1:])
        if subcommand == "clean":
            return await self._clean_old_results(args[1:])
        if subcommand == "search":
            return await self._search_results(args[1:])
        if subcommand == "help":
            return CommandResult.info(self.get_help())

        return CommandResult.error(f"Unknown results subcommand: {subcommand}")

    def get_subcommands(self) -> Dict[str, str]:
        """Get available subcommands"""
        return {
            "list [count]": "List recent test results (default: 10)",
            "view <test_id>": "View detailed test result",
            "stats": "Show test statistics",
            "export [format]": "Export results (json, csv)",
            "clean [days]": "Clean old results (default: 30 days)",
            "search <query>": "Search results by DUT ID or model",
            "help": "Show results command help",
        }

    async def _list_recent_results(self, limit: int = 10) -> CommandResult:
        """List recent test results"""
        try:
            if not self._repository_service:
                return CommandResult.error("Repository service not initialized")
            # Get all test results from repository
            repo_service = self._repository_service
            test_repo = cast(
                TestResultRepository,
                repo_service.test_repository,
            )
            all_tests = await test_repo.get_all_tests()

            if not all_tests:
                return CommandResult.info("No test results found")

            # Sort by creation time (most recent first)
            sorted_tests = sorted(
                all_tests,
                key=lambda x: x.get("created_at", ""),
                reverse=True,
            )

            # Limit results
            recent_tests = sorted_tests[:limit]

            # Prepare data for rich display
            title = f"Recent Test Results (showing {len(recent_tests)} of {len(all_tests)})"

            # Return result with test data for rich display
            result_data = {
                "test_results": recent_tests,
                "title": title,
                "total_count": len(all_tests),
                "shown_count": len(recent_tests),
            }

            message = f"Showing {len(recent_tests)} of {len(all_tests)} test results"
            if len(all_tests) > limit:
                message += f". Use '/results list {len(all_tests)}' to see all results."

            return CommandResult.success(message, data=result_data)

        except Exception as e:
            logger.error(f"Failed to list results: {e}")
            return CommandResult.error(f"Failed to list results: {str(e)}")

    async def _list_results(self, args: List[str]) -> CommandResult:
        """List test results with optional limit"""
        try:
            limit = 10  # Default
            if args:
                try:
                    limit = int(args[0])
                    if limit <= 0:
                        return CommandResult.error("Limit must be a positive number")
                except ValueError:
                    return CommandResult.error("Invalid limit. Must be a number.")

            return await self._list_recent_results(limit)

        except Exception as e:
            logger.error(f"Failed to list results: {e}")
            return CommandResult.error(f"Failed to list results: {str(e)}")

    async def _view_result(self, args: List[str]) -> CommandResult:
        """View detailed test result"""
        if not args:
            return CommandResult.error("Test ID is required. Usage: /results view <test_id>")

        test_id = args[0]

        try:
            if not self._repository_service:
                return CommandResult.error("Repository service not initialized")
            # Find test by ID
            repo_service = self._repository_service
            test_repo = cast(
                TestResultRepository,
                repo_service.test_repository,
            )
            test = await test_repo.find_by_id(test_id)

            if not test:
                return CommandResult.error(f"Test result not found: {test_id}")

            # Format detailed view
            result_text = "Test Result Details:\\n"
            result_text += "=" * 60 + "\\n"
            # Convert test object to dictionary for display
            if hasattr(test, '__dict__'):
                test_dict = test.__dict__
            else:
                # Fallback: create basic dict from object attributes
                test_dict = {
                    'test_id': getattr(test, 'test_id', 'N/A'),
                    'passed': getattr(test, 'passed', False),
                    'created_at': getattr(test, 'created_at', 'N/A'),
                    'duration': getattr(test, 'duration', 'N/A'),
                    'dut': getattr(test, 'dut', {}),
                    'measurement_ids': getattr(test, 'measurement_ids', []),
                }
            dut_info = test_dict.get("dut", {})

            result_text += f"Test ID: {test_dict.get('test_id', 'N/A')}\\n"
            result_text += f"Status: {'PASS' if test_dict.get('passed', False) else 'FAIL'}\\n"
            result_text += f"DUT ID: {dut_info.get('dut_id', 'N/A')}\\n"
            result_text += f"Model: {dut_info.get('model_number', 'N/A')}\\n"
            result_text += f"Serial: {dut_info.get('serial_number', 'N/A')}\\n"
            result_text += f"Created: {test_dict.get('created_at', 'N/A')}\\n"
            result_text += f"Duration: {test_dict.get('duration', 'N/A')}\\n"
            measurement_ids = test_dict.get("measurement_ids", [])
            result_text += f"Measurements: {len(measurement_ids) if measurement_ids else 0}\\n"

            if "operator_id" in test_dict:
                result_text += f"Operator: {test_dict['operator_id']}\\n"

            # Show measurements summary
            if measurement_ids:
                result_text += "\\nMeasurement IDs:\\n"
                result_text += "-" * 40 + "\\n"

                for i, measurement_id in enumerate(measurement_ids[:5]):  # Show first 5
                    result_text += f"  {i+1}. ID: {measurement_id}\\n"

                if len(measurement_ids) > 5:
                    remaining_count = len(measurement_ids) - 5
                    result_text += f"  ... and {remaining_count} more measurement IDs\\n"

            # Show failure reasons if failed
            if not test_dict.get("passed", False) and "failure_reason" in test_dict:
                result_text += f"\\nFailure Reason: {test_dict['failure_reason']}\\n"

            return CommandResult.success(result_text)

        except Exception as e:
            logger.error(f"Failed to view result: {e}")
            return CommandResult.error(f"Failed to view result: {str(e)}")

    def _calculate_overall_stats(self, all_tests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall test statistics"""
        total_tests = len(all_tests)
        passed_tests = sum(1 for test in all_tests if test.get("passed", False))
        failed_tests = total_tests - passed_tests
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "pass_rate": pass_rate,
        }

    def _calculate_recent_stats(self, all_tests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate recent test statistics (last 7 days)"""
        week_ago = datetime.now() - timedelta(days=7)
        recent_tests = []

        for test in all_tests:
            created_at = test.get("created_at")
            if created_at:
                try:
                    test_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    if test_date >= week_ago:
                        recent_tests.append(test)
                except (ValueError, AttributeError):
                    pass

        recent_total = len(recent_tests)
        recent_passed = sum(1 for test in recent_tests if test.get("passed", False))
        recent_pass_rate = (recent_passed / recent_total * 100) if recent_total > 0 else 0

        return {
            "total_tests": recent_total,
            "passed_tests": recent_passed,
            "pass_rate": recent_pass_rate,
        }

    def _calculate_model_stats(self, all_tests: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Calculate statistics by DUT model"""
        models: Dict[str, Dict[str, int]] = {}

        for test in all_tests:
            dut_info = test.get("dut", {})
            model = dut_info.get("model_number", "Unknown")
            if model not in models:
                models[model] = {
                    "total": 0,
                    "passed": 0,
                }
            models[model]["total"] += 1
            if test.get("passed", False):
                models[model]["passed"] += 1

        model_stats = {}
        for model, data in models.items():
            model_pass_rate = (data["passed"] / data["total"] * 100) if data["total"] > 0 else 0
            model_stats[model] = {
                "total": data["total"],
                "passed": data["passed"],
                "pass_rate": model_pass_rate,
            }

        return model_stats

    async def _show_statistics(self) -> CommandResult:
        """Show test statistics"""
        try:
            if not self._repository_service:
                return CommandResult.error("Repository service not initialized")
            # Get all test results
            repo_service = self._repository_service
            test_repo = cast(
                TestResultRepository,
                repo_service.test_repository,
            )
            all_tests = await test_repo.get_all_tests()

            if not all_tests:
                return CommandResult.info("No test results available for statistics")

            # Calculate statistics using helper methods
            overall_stats = self._calculate_overall_stats(all_tests)
            recent_stats = self._calculate_recent_stats(all_tests)
            model_stats = self._calculate_model_stats(all_tests)

            # Prepare statistics data for rich display
            statistics_data = {
                "overall": overall_stats,
                "recent": recent_stats,
            }

            if model_stats:
                statistics_data["by_model"] = model_stats

            # Return result with statistics data for rich display
            result_data = {"statistics": statistics_data}
            message = f"Test statistics generated for {overall_stats['total_tests']} total tests"

            return CommandResult.success(message, data=result_data)

        except Exception as e:
            logger.error(f"Failed to generate statistics: {e}")
            return CommandResult.error(f"Failed to generate statistics: {str(e)}")

    async def _export_results(self, args: List[str]) -> CommandResult:  # pylint: disable=too-many-return-statements
        """Export test results"""
        format_type = "json"  # Default
        if args:
            format_type = args[0].lower()
            if format_type not in ["json", "csv"]:
                return CommandResult.error("Supported formats: json, csv")

        try:
            if not self._repository_service:
                return CommandResult.error("Repository service not initialized")
            # Get all test results
            repo_service = self._repository_service
            test_repo = cast(
                TestResultRepository,
                repo_service.test_repository,
            )
            all_tests = await test_repo.get_all_tests()

            if not all_tests:
                return CommandResult.info("No test results to export")

            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"eol_test_results_{timestamp}.{format_type}"

            if format_type == "json":
                # Export as JSON
                export_path = Path(filename)
                with open(export_path, "w", encoding="utf-8") as f:
                    json.dump(
                        all_tests,
                        f,
                        indent=2,
                        ensure_ascii=False,
                        default=str,
                    )

                return CommandResult.success(
                    f"Results exported to {filename} ({len(all_tests)} tests)"
                )

            if format_type == "csv":
                # Export as CSV
                import csv

                export_path = Path(filename)

                with open(
                    export_path,
                    "w",
                    newline="",
                    encoding="utf-8",
                ) as f:
                    writer = csv.writer(f)

                    # Write header
                    writer.writerow(
                        [
                            "Test ID",
                            "DUT ID",
                            "Model",
                            "Serial",
                            "Status",
                            "Created At",
                            "Duration",
                            "Measurements Count",
                        ]
                    )

                    # Write data
                    for test in all_tests:
                        dut_info = test.get("dut", {})
                        writer.writerow(
                            [
                                test.get("test_id", ""),
                                dut_info.get("dut_id", ""),
                                dut_info.get("model_number", ""),
                                dut_info.get("serial_number", ""),
                                ("PASS" if test.get("passed", False) else "FAIL"),
                                test.get("created_at", ""),
                                test.get("duration", ""),
                                len(test.get("measurements", [])),
                            ]
                        )

                return CommandResult.success(
                    f"Results exported to {filename} ({len(all_tests)} tests)"
                )

            # This should not be reached due to format validation above
            return CommandResult.error(f"Unsupported export format: {format_type}")

        except Exception as e:
            logger.error(f"Failed to export results: {e}")
            return CommandResult.error(f"Failed to export results: {str(e)}")

    async def _clean_old_results(self, args: List[str]) -> CommandResult:
        """Clean old test results"""
        days = 30  # Default
        if args:
            try:
                days = int(args[0])
                if days <= 0:
                    return CommandResult.error("Days must be a positive number")
            except ValueError:
                return CommandResult.error("Invalid days. Must be a number.")

        try:
            if not self._repository_service:
                return CommandResult.error("Repository service not initialized")
            # Use repository's cleanup method
            repo_service = self._repository_service
            test_repo = cast(
                TestResultRepository,
                repo_service.test_repository,
            )
            deleted_count = await test_repo.cleanup_old_tests(days)

            if deleted_count > 0:
                return CommandResult.success(
                    f"Cleaned up {deleted_count} test results older than {days} days"
                )
            return CommandResult.info(f"No test results older than {days} days found")

        except Exception as e:
            logger.error(f"Failed to clean results: {e}")
            return CommandResult.error(f"Failed to clean results: {str(e)}")

    async def _search_results(self, args: List[str]) -> CommandResult:
        """Search test results"""
        if not args:
            return CommandResult.error("Search query is required. Usage: /results search <query>")

        query = " ".join(args).lower()

        try:
            if not self._repository_service:
                return CommandResult.error("Repository service not initialized")
            # Get all test results
            repo_service = self._repository_service
            test_repo = cast(
                TestResultRepository,
                repo_service.test_repository,
            )
            all_tests = await test_repo.get_all_tests()

            if not all_tests:
                return CommandResult.info("No test results to search")

            # Search through results
            matching_tests = []
            for test in all_tests:
                dut_info = test.get("dut", {})

                # Search in DUT ID, model, serial number, test ID
                search_fields = [
                    test.get("test_id", "").lower(),
                    dut_info.get("dut_id", "").lower(),
                    dut_info.get("model_number", "").lower(),
                    dut_info.get("serial_number", "").lower(),
                ]

                if any(query in field for field in search_fields):
                    matching_tests.append(test)

            if not matching_tests:
                return CommandResult.info(f"No results found for: {query}")

            # Prepare search results for rich display
            displayed_results = matching_tests[:20]  # Limit to 20 results
            title = f"Search Results for '{query}' ({len(matching_tests)} found)"

            result_data = {
                "test_results": displayed_results,
                "title": title,
                "total_count": len(matching_tests),
                "shown_count": len(displayed_results),
                "search_query": query,
            }

            message = f"Found {len(matching_tests)} results for '{query}'"
            if len(matching_tests) > 20:
                message += ". Showing first 20 results."

            return CommandResult.success(message, data=result_data)

        except Exception as e:
            logger.error(f"Failed to search results: {e}")
            return CommandResult.error(f"Failed to search results: {str(e)}")
