"""Example plugin: Automatic filename cleaner for Silo."""

import os
import re
import logging
from utils.plugin_system import SiloPlugin, PluginAPI

logger = logging.getLogger(__name__)


class FilenameCleanerPlugin(SiloPlugin):
    """Plugin to automatically clean and standardize audiobook filenames."""

    @property
    def name(self) -> str:
        return "Filename Cleaner"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Automatically clean and standardize audiobook filenames based on metadata"

    def initialize(self, app) -> bool:
        """Initialize the plugin."""
        self.api = PluginAPI(app)

        # Register hook for after file load
        # This would be called by the main application
        logger.info(f"{self.name} plugin initialized")

        # Example: Register menu item
        self.api.register_menu_item(
            "Plugins",
            "Clean All Filenames",
            self.clean_all_filenames
        )

        return True

    def shutdown(self) -> None:
        """Cleanup."""
        logger.info(f"{self.name} shut down")

    def clean_all_filenames(self) -> int:
        """Clean all loaded filenames based on metadata.

        Returns:
            Number of files renamed
        """
        renamed_count = 0

        for file_path in self.api.get_files():
            try:
                # Get metadata
                metadata = self.api.get_metadata(file_path)
                if not metadata:
                    continue

                # Generate new filename
                new_filename = self.generate_filename(metadata)

                # Rename file
                old_dir = os.path.dirname(file_path)
                new_path = os.path.join(old_dir, new_filename)

                if file_path != new_path:
                    # Note: Actual renaming would require careful handling
                    # This is a simplified example
                    logger.info(f"Would rename: {os.path.basename(file_path)} -> {new_filename}")
                    renamed_count += 1

            except Exception as e:
                logger.error(f"Failed to clean {file_path}: {e}")

        logger.info(f"Cleaned {renamed_count} filenames")
        return renamed_count

    def generate_filename(self, metadata: dict) -> str:
        """Generate clean filename from metadata.

        Args:
            metadata: Metadata dictionary

        Returns:
            Clean filename with extension
        """
        # Get title and author
        title = metadata.get('title', 'Unknown')
        author = metadata.get('author', 'Unknown')

        # Clean title: remove invalid characters
        title = self.clean_string(title)
        author = self.clean_string(author)

        # Generate filename
        # Format: Author - Title.ext
        filename = f"{author} - {title}"

        # Get file extension
        # This would come from the actual file path
        return f"{filename}.m4b"

    def clean_string(self, text: str) -> str:
        """Clean string for use in filename.

        Args:
            text: String to clean

        Returns:
            Cleaned string
        """
        # Remove invalid filename characters
        text = re.sub(r'[<>:"/\\|?*]', '', text)

        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)

        # Remove leading/trailing spaces
        text = text.strip()

        # Limit length
        if len(text) > 100:
            text = text[:100]

        return text if text else "Unknown"


# Plugin factory function
def create_plugin():
    """Create plugin instance."""
    return FilenameCleanerPlugin()
