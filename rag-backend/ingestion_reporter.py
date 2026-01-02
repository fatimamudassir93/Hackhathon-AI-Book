"""
Ingestion comparison reporter
Creates reports showing before/after stats for ingestion operations
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from pathlib import Path


class IngestionReporter:
    """
    Generates reports comparing ingestion states before and after operations.
    """

    def __init__(self, report_dir: str = "reports"):
        """
        Initialize the ingestion reporter.

        Args:
            report_dir: Directory to store reports
        """
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(exist_ok=True)

    def generate_comparison_report(
        self,
        before_stats: Dict[str, Any],
        after_stats: Dict[str, Any],
        operation: str = "ingestion",
        sources_before: Optional[Dict[str, int]] = None,
        sources_after: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """
        Generate a comparison report between before and after states.

        Args:
            before_stats: Statistics before the operation
            after_stats: Statistics after the operation
            operation: Type of operation (ingestion, update, deletion, etc.)
            sources_before: Source counts before the operation
            sources_after: Source counts after the operation

        Returns:
            Dictionary with comparison report
        """
        # Calculate differences
        differences = {}
        all_keys = set(before_stats.keys()) | set(after_stats.keys())

        for key in all_keys:
            before_val = before_stats.get(key, 0)
            after_val = after_stats.get(key, 0)

            if isinstance(before_val, (int, float)) and isinstance(after_val, (int, float)):
                diff = after_val - before_val
                differences[key] = {
                    'before': before_val,
                    'after': after_val,
                    'difference': diff,
                    'change_percent': round(((after_val - before_val) / max(before_val, 1)) * 100, 2) if before_val != 0 else float('inf')
                }
            else:
                differences[key] = {
                    'before': before_val,
                    'after': after_val,
                    'difference': 'N/A'
                }

        # Calculate source changes if provided
        source_changes = {}
        if sources_before is not None and sources_after is not None:
            all_sources = set(sources_before.keys()) | set(sources_after.keys())

            added_sources = set(sources_after.keys()) - set(sources_before.keys())
            removed_sources = set(sources_before.keys()) - set(sources_after.keys())
            changed_sources = {}

            for source in all_sources:
                before_count = sources_before.get(source, 0)
                after_count = sources_after.get(source, 0)
                if source not in added_sources and source not in removed_sources:
                    if before_count != after_count:
                        changed_sources[source] = {
                            'before': before_count,
                            'after': after_count,
                            'difference': after_count - before_count
                        }

            source_changes = {
                'added_sources': list(added_sources),
                'removed_sources': list(removed_sources),
                'changed_sources': changed_sources,
                'added_count': len(added_sources),
                'removed_count': len(removed_sources),
                'changed_count': len(changed_sources)
            }

        report = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'comparison': differences,
            'source_changes': source_changes,
            'summary': {
                'operation': operation,
                'started_at': before_stats.get('started_at', 'N/A'),
                'completed_at': after_stats.get('completed_at', 'N/A'),
                'duration_seconds': after_stats.get('duration_seconds', 'N/A')
            }
        }

        return report

    def save_report(self, report: Dict[str, Any], filename: str = None) -> str:
        """
        Save the report to a file.

        Args:
            report: The report dictionary to save
            filename: Optional filename (auto-generated if not provided)

        Returns:
            Path to saved report file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ingestion_report_{timestamp}.json"

        filepath = self.report_dir / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return str(filepath)

    def generate_ingestion_summary(
        self,
        stats: Dict[str, Any],
        operation: str = "ingestion"
    ) -> str:
        """
        Generate a human-readable summary of ingestion statistics.

        Args:
            stats: Statistics dictionary
            operation: Type of operation

        Returns:
            Formatted summary string
        """
        summary_lines = [
            f"Ingestion {operation.title()} Summary",
            "=" * 50
        ]

        # Add key metrics
        if 'files_processed' in stats:
            summary_lines.append(f"Files processed:     {stats.get('files_processed', 0)}")
        if 'files_skipped' in stats:
            summary_lines.append(f"Files skipped:       {stats.get('files_skipped', 0)}")
        if 'chunks_created' in stats:
            summary_lines.append(f"Chunks created:      {stats.get('chunks_created', 0)}")
        if 'embeddings_generated' in stats:
            summary_lines.append(f"Embeddings generated: {stats.get('embeddings_generated', 0)}")
        if 'vectors_uploaded' in stats:
            summary_lines.append(f"Vectors uploaded:    {stats.get('vectors_uploaded', 0)}")
        if 'errors' in stats:
            summary_lines.append(f"Errors:              {stats.get('errors', 0)}")

        # Add timing if available
        if 'duration_seconds' in stats:
            summary_lines.append(f"Duration:            {stats['duration_seconds']:.2f}s")

        summary_lines.append("=" * 50)
        return "\n".join(summary_lines)

    def generate_detailed_report(
        self,
        before_stats: Dict[str, Any],
        after_stats: Dict[str, Any],
        operation: str = "ingestion",
        sources_before: Optional[Dict[str, int]] = None,
        sources_after: Optional[Dict[str, int]] = None,
        filename: str = None
    ) -> str:
        """
        Generate and save a detailed comparison report.

        Args:
            before_stats: Statistics before the operation
            after_stats: Statistics after the operation
            operation: Type of operation
            sources_before: Source counts before the operation
            sources_after: Source counts after the operation
            filename: Optional filename for the report

        Returns:
            Path to saved report file
        """
        # Generate comparison report
        report = self.generate_comparison_report(
            before_stats, after_stats, operation, sources_before, sources_after
        )

        # Add summary to report
        report['summary_text'] = self.generate_ingestion_summary(after_stats, operation)

        # Save the report
        filepath = self.save_report(report, filename)

        return filepath


def create_reporter(report_dir: str = "reports") -> IngestionReporter:
    """
    Factory function to create an IngestionReporter instance.

    Args:
        report_dir: Directory to store reports

    Returns:
        IngestionReporter instance
    """
    return IngestionReporter(report_dir=report_dir)


if __name__ == "__main__":
    # Example usage and test
    print("Ingestion Reporter Module")
    print("=" * 50)

    # Example before/after stats
    before = {
        'files_found': 10,
        'files_processed': 8,
        'files_skipped': 2,
        'chunks_created': 120,
        'embeddings_generated': 120,
        'vectors_uploaded': 120,
        'errors': 0,
        'started_at': '2024-01-01T10:00:00',
        'duration_seconds': 0
    }

    after = {
        'files_found': 12,  # 2 new files
        'files_processed': 10,  # 2 more processed
        'files_skipped': 2,  # same
        'chunks_created': 180,  # 60 more chunks
        'embeddings_generated': 180,  # 60 more embeddings
        'vectors_uploaded': 180,  # 60 more vectors
        'errors': 1,  # 1 new error
        'started_at': '2024-01-01T10:00:00',
        'completed_at': '2024-01-01T10:05:30',
        'duration_seconds': 330
    }

    # Example source counts
    sources_before = {
        'docs/chapter1.md': 15,
        'docs/chapter2.md': 20,
        'docs/chapter3.md': 10
    }

    sources_after = {
        'docs/chapter1.md': 15,  # unchanged
        'docs/chapter2.md': 25,  # 5 more chunks
        'docs/chapter3.md': 10,  # unchanged
        'docs/chapter4.md': 30,  # new file
        'docs/chapter5.md': 100  # new file
    }

    # Create reporter and generate comparison
    reporter = IngestionReporter()
    report = reporter.generate_comparison_report(
        before, after, "update", sources_before, sources_after
    )

    # Print summary
    print(reporter.generate_ingestion_summary(after, "update"))

    # Print key differences
    print("\nKey Changes:")
    for key, diff_info in report['comparison'].items():
        if isinstance(diff_info['difference'], (int, float)) and diff_info['difference'] != 0:
            print(f"  {key}: {diff_info['before']} → {diff_info['after']} ({diff_info['difference']:+d})")

    print(f"\nSource changes: {report['source_changes']['added_count']} added, {report['source_changes']['removed_count']} removed, {report['source_changes']['changed_count']} changed")

    # Save report
    filepath = reporter.save_report(report, "test_report.json")
    print(f"\nReport saved to: {filepath}")