#!/usr/bin/env python
"""
Startup validation script for the chatbot application.
Validates environment, dependencies, and system requirements before starting the server.
"""

import os
import sys
import logging
import subprocess
from pathlib import Path
import sqlite3
from django.core.management import execute_from_command_line

# Configure basic logging for startup validation
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",  # Use utf-8 encoding for file handlers if added, though console might still issue
)
# Force console encoding to be safe
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

logger = logging.getLogger(__name__)


class StartupValidator:
    """Validates system requirements and configuration before startup."""

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.errors = []
        self.warnings = []

    def validate_python_version(self):
        """Check if Python version meets requirements."""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            self.errors.append(
                f"Python 3.8+ required. Current version: {version.major}.{version.minor}.{version.micro}"
            )
            return False
        logger.info(
            f"[OK] Python version: {version.major}.{version.minor}.{version.micro}"
        )
        return True

    def validate_environment_file(self):
        """Check if .env file exists and contains required variables."""
        env_file = self.base_dir / ".env"
        if not env_file.exists():
            self.errors.append(
                ".env file not found. Please create it with required environment variables."
            )
            return False

        # Load and check required environment variables
        with open(env_file, "r") as f:
            env_content = f.read()

        required_vars = ["GROQ_API_KEY"]
        missing_vars = []

        for var in required_vars:
            if f"{var}=" not in env_content:
                missing_vars.append(var)

        if missing_vars:
            self.errors.append(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )
            return False

        logger.info("[OK] Environment file validation passed")
        return True

    def validate_dependencies(self):
        """Check if required packages are installed."""
        requirements_file = self.base_dir / "requirements.txt"

        if not requirements_file.exists():
            self.errors.append("requirements.txt not found")
            return False

        try:
            # Check if Django is installed
            import django

            logger.info(f"[OK] Django version: {django.get_version()}")
        except ImportError:
            self.errors.append("Django is not installed")
            return False

        # Check other critical dependencies
        # Map package name to import name
        critical_deps = {
            "google-genai": "google.genai",
            "python-dotenv": "dotenv",
            "whitenoise": "whitenoise",
        }
        missing_deps = []

        for pkg, module in critical_deps.items():
            try:
                # specific check for google-genai which might be a namespace package
                if pkg == "google-genai":
                    import google.genai
                else:
                    __import__(module)
            except ImportError:
                # Fallback for google-genai old versions or if it's installed differently
                if pkg == "google-genai":
                    try:
                        import google_genai
                    except ImportError:
                        missing_deps.append(pkg)
                else:
                    missing_deps.append(pkg)

        if missing_deps:
            self.errors.append(
                f"Missing critical dependencies: {', '.join(missing_deps)}"
            )
            return False

        logger.info("✓ Dependencies validation passed")
        return True

    def validate_database(self):
        """Check if database is accessible and properly configured."""
        db_path = self.base_dir / "db.sqlite3"

        try:
            # Test database connection
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            conn.close()

            logger.info(f"[OK] Database accessible. Found {len(tables)} tables")
            return True

        except sqlite3.Error as e:
            self.errors.append(f"Database validation failed: {str(e)}")
            return False

    def validate_static_files(self):
        """Check if static files directory exists."""
        staticfiles_dir = self.base_dir / "staticfiles"

        if not staticfiles_dir.exists():
            self.warnings.append(
                "staticfiles directory not found. Run 'python manage.py collectstatic' first."
            )
            return False

        logger.info("[OK] Static files directory exists")
        return True

    def run_django_checks(self):
        """Run Django's built-in system checks."""
        try:
            os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chatbot_project.settings")

            # Import Django after setting up environment
            import django
            from django.core.management import call_command
            from django.conf import settings

            django.setup()

            # Run system checks
            call_command("check", verbosity=0)
            logger.info("[OK] Django system checks passed")
            return True

        except Exception as e:
            self.errors.append(f"Django system checks failed: {str(e)}")
            return False

    def validate_port_availability(self, port=8000):
        """Check if the specified port is available."""
        import socket

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", port))
            logger.info(f"[OK] Port {port} is available")
            return True
        except socket.error:
            self.warnings.append(f"Port {port} appears to be in use by another process")
            return False

    def run_all_validations(self):
        """Run all validation checks."""
        logger.info("Starting startup validation...")

        validations = [
            self.validate_python_version(),
            self.validate_environment_file(),
            self.validate_dependencies(),
            self.validate_database(),
            self.validate_static_files(),
            self.run_django_checks(),
            self.validate_port_availability(),
        ]

        all_passed = all(validations)

        if self.errors:
            logger.error("Validation errors found:")
            for error in self.errors:
                logger.error(f"  [ERROR] {error}")

        if self.warnings:
            logger.warning("Validation warnings:")
            for warning in self.warnings:
                logger.warning(f"  [WARNING]  {warning}")

        if all_passed and not self.errors:
            logger.info("[SUCCESS] All validations passed! Ready to start the server.")
            return True
        else:
            logger.error(
                "[ERROR] Validation failed. Please address the issues above before starting the server."
            )
            return False


def main():
    """Main validation function."""
    validator = StartupValidator()

    if validator.run_all_validations():
        logger.info("Starting Django development server...")
        # Start the server if validation passes
        execute_from_command_line(["manage.py", "runserver", "127.0.0.1:8000"])
    else:
        logger.error("Startup validation failed. Server not started.")
        sys.exit(1)


if __name__ == "__main__":
    main()
