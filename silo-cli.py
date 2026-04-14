#!/usr/bin/env python3
"""
Silo CLI - Command-line interface for batch audiobook metadata operations

This tool allows you to process audiobook files without the GUI,
perfect for automation, scripting, and batch processing.
"""

import sys
import os
import json
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SiloCLI:
    """Command-line interface for Silo operations."""

    def __init__(self):
        """Initialize CLI."""
        self.files = []

    def load_directory(self, directory: str) -> int:
        """Load all audiobook files from directory.

        Args:
            directory: Path to directory

        Returns:
            Number of files loaded
        """
        extensions = ['.m4b', '.m4a', '.mp3', '.flac']

        try:
            for filename in os.listdir(directory):
                ext = os.path.splitext(filename)[1].lower()
                if ext in extensions:
                    file_path = os.path.join(directory, filename)
                    self.files.append(file_path)

            logger.info(f"Loaded {len(self.files)} files from {directory}")
            return len(self.files)

        except Exception as e:
            logger.error(f"Failed to load directory: {e}")
            return 0

    def export_metadata(self, output_file: str) -> bool:
        """Export metadata for all loaded files to JSON.

        Args:
            output_file: Path to output JSON file

        Returns:
            True if successful
        """
        try:
            from core.metadata_handler import read_metadata

            export_data = {}

            for file_path in self.files:
                try:
                    metadata = read_metadata(file_path)
                    export_data[os.path.basename(file_path)] = {
                        'metadata': {k: v for k, v in metadata.items() if not k.startswith('_')},
                        'duration': metadata.get('length', 'Unknown'),
                        'has_cover_art': metadata.get('_cover_art') is not None,
                        'chapter_count': len(metadata.get('_chapters', []))
                    }
                except Exception as e:
                    logger.warning(f"Failed to read {file_path}: {e}")
                    export_data[os.path.basename(file_path)] = {'error': str(e)}

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Exported metadata for {len(self.files)} files to {output_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to export metadata: {e}")
            return False

    def import_metadata(self, input_file: str, dry_run: bool = False) -> int:
        """Import metadata from JSON and apply to matching files.

        Args:
            input_file: Path to input JSON file
            dry_run: If True, show changes without applying

        Returns:
            Number of files processed
        """
        try:
            from core.metadata_handler import apply_metadata

            with open(input_file, 'r', encoding='utf-8') as f:
                import_data = json.load(f)

            processed_count = 0

            for file_path in self.files:
                filename = os.path.basename(file_path)

                if filename in import_data:
                    data = import_data[filename]

                    if 'error' in data:
                        logger.warning(f"Skipping {filename}: {data['error']}")
                        continue

                    metadata = data.get('metadata', {})

                    if dry_run:
                        logger.info(f"Would update {filename}:")
                        for key, value in metadata.items():
                            logger.info(f"  {key}: {value}")
                    else:
                        try:
                            apply_metadata(file_path, metadata, None)
                            logger.info(f"Updated {filename}")
                            processed_count += 1
                        except Exception as e:
                            logger.error(f"Failed to update {filename}: {e}")

            logger.info(f"Processed {processed_count} files")
            return processed_count

        except Exception as e:
            logger.error(f"Failed to import metadata: {e}")
            return 0

    def batch_update(self, updates: Dict[str, str], dry_run: bool = False) -> int:
        """Apply metadata updates to all loaded files.

        Args:
            updates: Dictionary of field-value pairs to update
            dry_run: If True, show changes without applying

        Returns:
            Number of files updated
        """
        try:
            from core.metadata_handler import apply_metadata

            updated_count = 0

            for file_path in self.files:
                if dry_run:
                    logger.info(f"Would update {os.path.basename(file_path)}:")
                    for key, value in updates.items():
                        logger.info(f"  {key}: {value}")
                else:
                    try:
                        apply_metadata(file_path, updates, None)
                        logger.info(f"Updated {os.path.basename(file_path)}")
                        updated_count += 1
                    except Exception as e:
                        logger.error(f"Failed to update {os.path.basename(file_path)}: {e}")

            logger.info(f"Batch updated {updated_count} files")
            return updated_count

        except Exception as e:
            logger.error(f"Failed to batch update: {e}")
            return 0

    def list_files(self):
        """List all loaded files with basic info."""
        try:
            from core.metadata_handler import read_metadata

            print(f"\nLoaded {len(self.files)} files:")
            print("-" * 80)

            for file_path in self.files:
                try:
                    metadata = read_metadata(file_path)
                    title = metadata.get('title', 'Unknown')
                    author = metadata.get('author', 'Unknown')
                    duration = metadata.get('length', 'Unknown')

                    print(f"📖 {title}")
                    print(f"   Author: {author}")
                    print(f"   Duration: {duration}")
                    print(f"   File: {os.path.basename(file_path)}")
                    print("-" * 80)

                except Exception as e:
                    print(f"❌ {os.path.basename(file_path)}: {e}")
                    print("-" * 80)

        except Exception as e:
            logger.error(f"Failed to list files: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Silo CLI - Audiobook metadata batch processor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export metadata from all audiobooks in a directory
  silo-cli.py load -d ./audiobooks export -o metadata.json

  # Import metadata and apply to files (dry run)
  silo-cli.py load -d ./audiobooks import -i metadata.json --dry-run

  # Batch update all files with new author
  silo-cli.py load -d ./audiobooks update --author "New Author" --dry-run

  # List all files with metadata
  silo-cli.py load -d ./audiobooks list
        """
    )

    parser.add_argument('--version', action='version', version='Silo CLI 2.0')

    # Load files
    parser.add_argument('load', nargs='?', help='Load files from directory')
    parser.add_argument('-d', '--directory', help='Directory containing audiobooks')

    # Operations
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Export command
    export_parser = subparsers.add_parser('export', help='Export metadata to JSON')
    export_parser.add_argument('-o', '--output', required=True, help='Output JSON file')

    # Import command
    import_parser = subparsers.add_parser('import', help='Import metadata from JSON')
    import_parser.add_argument('-i', '--input', required=True, help='Input JSON file')
    import_parser.add_argument('--dry-run', action='store_true', help='Show changes without applying')

    # Update command
    update_parser = subparsers.add_parser('update', help='Batch update metadata')
    update_parser.add_argument('--title', help='Set book title')
    update_parser.add_argument('--author', help='Set author')
    update_parser.add_argument('--narrator', help='Set narrator')
    update_parser.add_argument('--genre', help='Set genre')
    update_parser.add_argument('--year', help='Set year')
    update_parser.add_argument('--dry-run', action='store_true', help='Show changes without applying')

    # List command
    list_parser = subparsers.add_parser('list', help='List all loaded files')

    args = parser.parse_args()

    # Create CLI instance
    cli = SiloCLI()

    # Load files if directory specified
    if args.load == 'load' or args.load is None:
        if not args.directory:
            parser.error("Directory required for load command")

        if not os.path.isdir(args.directory):
            parser.error(f"Directory not found: {args.directory}")

        count = cli.load_directory(args.directory)
        if count == 0:
            logger.error("No audiobook files found in directory")
            return 1

    # Execute command
    if args.command == 'export':
        success = cli.export_metadata(args.output)
        return 0 if success else 1

    elif args.command == 'import':
        count = cli.import_metadata(args.input, args.dry_run)
        return 0 if count > 0 else 1

    elif args.command == 'update':
        updates = {}
        if args.title:
            updates['title'] = args.title
        if args.author:
            updates['author'] = args.author
        if args.narrator:
            updates['narrator'] = args.narrator
        if args.genre:
            updates['genre'] = args.genre
        if args.year:
            updates['year'] = args.year

        if not updates:
            parser.error("At least one field must be specified for update")

        count = cli.batch_update(updates, args.dry_run)
        return 0 if count > 0 else 1

    elif args.command == 'list':
        cli.list_files()
        return 0

    elif args.command is None:
        # No command specified, just load and list
        cli.list_files()
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
