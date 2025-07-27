"""
Results Command

Handles test results management and display commands.
"""

import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path
from loguru import logger

from ui.cli.commands.base import Command, CommandResult
from application.services.repository_service import RepositoryService
from domain.entities.eol_test import EOLTest


class ResultsCommand(Command):
    """Command for test results management"""
    
    def __init__(self, repository_service: Optional[RepositoryService] = None):
        super().__init__(
            name="results",
            description="Test results management and analysis"
        )
        self._repository_service = repository_service
    
    def set_repository_service(self, repository_service: RepositoryService) -> None:
        """Set the repository service for results access"""
        self._repository_service = repository_service
    
    async def execute(self, args: List[str]) -> CommandResult:
        """
        Execute results command
        
        Args:
            args: Command arguments (subcommand and parameters)
            
        Returns:
            CommandResult with results operation results
        """
        if not self._repository_service:
            return CommandResult.error("Repository service not initialized")
        
        if not args:
            return await self._list_recent_results()
        
        subcommand = args[0].lower()
        
        if subcommand == "list":
            return await self._list_results(args[1:])
        elif subcommand == "view":
            return await self._view_result(args[1:])
        elif subcommand == "stats":
            return await self._show_statistics()
        elif subcommand == "export":
            return await self._export_results(args[1:])
        elif subcommand == "clean":
            return await self._clean_old_results(args[1:])
        elif subcommand == "search":
            return await self._search_results(args[1:])
        elif subcommand == "help":
            return CommandResult.info(self.get_help())
        else:
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
            "help": "Show results command help"
        }
    
    async def _list_recent_results(self, limit: int = 10) -> CommandResult:
        """List recent test results"""
        try:
            # Get all test results from repository
            all_tests = await self._repository_service.test_repository.get_all_tests()
            
            if not all_tests:
                return CommandResult.info("No test results found")
            
            # Sort by creation time (most recent first)
            sorted_tests = sorted(
                all_tests, 
                key=lambda x: x.get('created_at', ''), 
                reverse=True
            )
            
            # Limit results
            recent_tests = sorted_tests[:limit]
            
            # Prepare data for rich display
            title = f"Recent Test Results (showing {len(recent_tests)} of {len(all_tests)})"
            
            # Return result with test data for rich display
            result_data = {
                'test_results': recent_tests,
                'title': title,
                'total_count': len(all_tests),
                'shown_count': len(recent_tests)
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
            # Find test by ID
            test = await self._repository_service.test_repository.find_by_id(test_id)
            
            if not test:
                return CommandResult.error(f"Test result not found: {test_id}")
            
            # Format detailed view
            result_text = f"Test Result Details:\\n"
            result_text += "=" * 60 + "\\n"
            result_text += f"Test ID: {test.test_id}\\n"
            result_text += f"Status: {'PASS' if test.is_passed() else 'FAIL'}\\n"
            result_text += f"DUT ID: {test.dut.dut_id}\\n"
            result_text += f"Model: {test.dut.model_number}\\n"
            result_text += f"Serial: {test.dut.serial_number}\\n"
            result_text += f"Created: {test.created_at}\\n"
            result_text += f"Duration: {test.get_duration() or 'N/A'}\\n"
            result_text += f"Measurements: {len(test.measurement_ids)}\\n"
            
            if hasattr(test, 'operator_id'):
                result_text += f"Operator: {test.operator_id}\\n"
            
            # Show measurements summary
            if test.measurement_ids:
                result_text += "\\nMeasurement IDs:\\n"
                result_text += "-" * 40 + "\\n"
                
                for i, measurement_id in enumerate(test.measurement_ids[:5]):  # Show first 5
                    result_text += f"  {i+1}. ID: {measurement_id}\\n"
                
                if len(test.measurement_ids) > 5:
                    result_text += f"  ... and {len(test.measurement_ids) - 5} more measurement IDs\\n"
            
            # Show failure reasons if failed
            if not test.is_passed() and hasattr(test, 'failure_reason'):
                result_text += f"\\nFailure Reason: {test.failure_reason}\\n"
            
            return CommandResult.success(result_text)
            
        except Exception as e:
            logger.error(f"Failed to view result: {e}")
            return CommandResult.error(f"Failed to view result: {str(e)}")
    
    async def _show_statistics(self) -> CommandResult:
        """Show test statistics"""
        try:
            # Get all test results
            all_tests = await self._repository_service.test_repository.get_all_tests()
            
            if not all_tests:
                return CommandResult.info("No test results available for statistics")
            
            # Calculate statistics
            total_tests = len(all_tests)
            passed_tests = sum(1 for test in all_tests if test.get('passed', False))
            failed_tests = total_tests - passed_tests
            pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
            
            # Calculate recent statistics (last 7 days)
            week_ago = datetime.now() - timedelta(days=7)
            recent_tests = []
            
            for test in all_tests:
                created_at = test.get('created_at')
                if created_at:
                    try:
                        test_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        if test_date >= week_ago:
                            recent_tests.append(test)
                    except:
                        pass
            
            recent_total = len(recent_tests)
            recent_passed = sum(1 for test in recent_tests if test.get('passed', False))
            recent_pass_rate = (recent_passed / recent_total * 100) if recent_total > 0 else 0
            
            # Prepare statistics data for rich display
            statistics_data = {
                'overall': {
                    'total_tests': total_tests,
                    'passed_tests': passed_tests,
                    'failed_tests': failed_tests,
                    'pass_rate': pass_rate
                },
                'recent': {
                    'total_tests': recent_total,
                    'passed_tests': recent_passed,
                    'pass_rate': recent_pass_rate
                }
            }
            
            # DUT Model statistics
            models = {}
            for test in all_tests:
                dut_info = test.get('dut', {})
                model = dut_info.get('model_number', 'Unknown')
                if model not in models:
                    models[model] = {'total': 0, 'passed': 0}
                models[model]['total'] += 1
                if test.get('passed', False):
                    models[model]['passed'] += 1
            
            if models:
                statistics_data['by_model'] = {}
                for model, data in models.items():
                    model_pass_rate = (data['passed'] / data['total'] * 100) if data['total'] > 0 else 0
                    statistics_data['by_model'][model] = {
                        'total': data['total'],
                        'passed': data['passed'],
                        'pass_rate': model_pass_rate
                    }
            
            # Return result with statistics data for rich display
            result_data = {'statistics': statistics_data}
            message = f"Test statistics generated for {total_tests} total tests"
            
            return CommandResult.success(message, data=result_data)
            
        except Exception as e:
            logger.error(f"Failed to generate statistics: {e}")
            return CommandResult.error(f"Failed to generate statistics: {str(e)}")
    
    async def _export_results(self, args: List[str]) -> CommandResult:
        """Export test results"""
        format_type = "json"  # Default
        if args:
            format_type = args[0].lower()
            if format_type not in ["json", "csv"]:
                return CommandResult.error("Supported formats: json, csv")
        
        try:
            # Get all test results
            all_tests = await self._repository_service.test_repository.get_all_tests()
            
            if not all_tests:
                return CommandResult.info("No test results to export")
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"eol_test_results_{timestamp}.{format_type}"
            
            if format_type == "json":
                # Export as JSON
                export_path = Path(filename)
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(all_tests, f, indent=2, ensure_ascii=False, default=str)
                
                return CommandResult.success(f"Results exported to {filename} ({len(all_tests)} tests)")
            
            elif format_type == "csv":
                # Export as CSV
                import csv
                export_path = Path(filename)
                
                with open(export_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    
                    # Write header
                    writer.writerow([
                        'Test ID', 'DUT ID', 'Model', 'Serial', 'Status', 
                        'Created At', 'Duration', 'Measurements Count'
                    ])
                    
                    # Write data
                    for test in all_tests:
                        dut_info = test.get('dut', {})
                        writer.writerow([
                            test.get('test_id', ''),
                            dut_info.get('dut_id', ''),
                            dut_info.get('model_number', ''),
                            dut_info.get('serial_number', ''),
                            'PASS' if test.get('passed', False) else 'FAIL',
                            test.get('created_at', ''),
                            test.get('duration', ''),
                            len(test.get('measurements', []))
                        ])
                
                return CommandResult.success(f"Results exported to {filename} ({len(all_tests)} tests)")
            
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
            # Use repository's cleanup method if available
            if hasattr(self._repository_service.test_repository, 'cleanup_old_tests'):
                deleted_count = await self._repository_service.test_repository.cleanup_old_tests(days)
                
                if deleted_count > 0:
                    return CommandResult.success(f"Cleaned up {deleted_count} test results older than {days} days")
                else:
                    return CommandResult.info(f"No test results older than {days} days found")
            else:
                return CommandResult.info("Cleanup functionality not available for current repository")
            
        except Exception as e:
            logger.error(f"Failed to clean results: {e}")
            return CommandResult.error(f"Failed to clean results: {str(e)}")
    
    async def _search_results(self, args: List[str]) -> CommandResult:
        """Search test results"""
        if not args:
            return CommandResult.error("Search query is required. Usage: /results search <query>")
        
        query = " ".join(args).lower()
        
        try:
            # Get all test results
            all_tests = await self._repository_service.test_repository.get_all_tests()
            
            if not all_tests:
                return CommandResult.info("No test results to search")
            
            # Search through results
            matching_tests = []
            for test in all_tests:
                dut_info = test.get('dut', {})
                
                # Search in DUT ID, model, serial number, test ID
                search_fields = [
                    test.get('test_id', '').lower(),
                    dut_info.get('dut_id', '').lower(),
                    dut_info.get('model_number', '').lower(),
                    dut_info.get('serial_number', '').lower()
                ]
                
                if any(query in field for field in search_fields):
                    matching_tests.append(test)
            
            if not matching_tests:
                return CommandResult.info(f"No results found for: {query}")
            
            # Prepare search results for rich display
            displayed_results = matching_tests[:20]  # Limit to 20 results
            title = f"Search Results for '{query}' ({len(matching_tests)} found)"
            
            result_data = {
                'test_results': displayed_results,
                'title': title,
                'total_count': len(matching_tests),
                'shown_count': len(displayed_results),
                'search_query': query
            }
            
            message = f"Found {len(matching_tests)} results for '{query}'"
            if len(matching_tests) > 20:
                message += f". Showing first 20 results."
            
            return CommandResult.success(message, data=result_data)
            
        except Exception as e:
            logger.error(f"Failed to search results: {e}")
            return CommandResult.error(f"Failed to search results: {str(e)}")