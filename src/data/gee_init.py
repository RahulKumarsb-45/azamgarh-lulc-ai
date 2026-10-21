"""Earth Engine initialization module.

Uses the local Google Earth Engine user token and the project ID defined in
the EE_PROJECT environment variable.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Add project root to sys.path
_project_root = Path(__file__).resolve().parents[2]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import ee
from dotenv import load_dotenv


class EarthEngineConfigError(Exception):
    """Raised when .env or EE_PROJECT is not properly configured."""
    pass


class EarthEngineAuthError(Exception):
    """Raised when Earth Engine authentication credentials are missing or invalid."""
    pass


def check_env_file() -> tuple[bool, Path]:
    """Check if .env exists in the workspace root."""
    root = Path(__file__).resolve().parents[2]
    env_path = root / ".env"
    return env_path.is_file(), env_path


def is_authenticated() -> bool:
    """Check if local Google Earth Engine credentials file exists."""
    home = Path.home()
    candidates = [
        home / ".config" / "earthengine" / "credentials",
        home / ".earthengine" / "credentials",
    ]
    return any(p.is_file() for p in candidates)


def init_ee(force_auth: bool = False, raise_exit: bool = False) -> str:
    """Initialize Earth Engine with informative diagnostic errors.

    Args:
        force_auth: Force launching interactive browser authentication.
        raise_exit: If True, calls sys.exit(1) on failure for CLI friendliness.
                    If False, raises EarthEngineConfigError or EarthEngineAuthError.
    """
    load_dotenv()
    project = os.environ.get("EE_PROJECT")

    env_exists, env_path = check_env_file()
    if not env_exists:
        err_msg = (
            "[ERROR] .env file not found in repository root!\n"
            "Please create it by running:\n"
            "  Copy-Item .env.example .env  (Windows PowerShell)\n"
            "  cp .env.example .env        (Linux/macOS)\n"
            "Then set EE_PROJECT=<your-gcp-project-id> inside .env."
        )
        if raise_exit:
            sys.stderr.write(f"\n{err_msg}\n\n")
            raise SystemExit(1)
        raise EarthEngineConfigError(err_msg)

    if not project or project.strip() in ("", "your-gcp-project-id", "YOUR_GCP_PROJECT_ID"):
        err_msg = (
            f"[ERROR] EE_PROJECT is not configured in {env_path.name}!\n"
            "Please open .env and set EE_PROJECT to your actual Google Cloud Project ID.\n"
            "Example: EE_PROJECT=azamgarh-lulc-2026"
        )
        if raise_exit:
            sys.stderr.write(f"\n{err_msg}\n\n")
            raise SystemExit(1)
        raise EarthEngineConfigError(err_msg)

    project = project.strip()

    if force_auth or not is_authenticated():
        if not force_auth and not is_authenticated():
            print("[*] No stored Earth Engine credentials found. Launching authentication...")
        try:
            ee.Authenticate()
        except Exception as e:
            err_msg = (
                f"[ERROR] Interactive authentication failed: {e}\n"
                "Please run the following command directly in PowerShell:\n"
                "  earthengine authenticate\n"
                "Then re-run your script."
            )
            if raise_exit:
                sys.stderr.write(f"\n{err_msg}\n\n")
                raise SystemExit(1)
            raise EarthEngineAuthError(err_msg)

    try:
        ee.Initialize(project=project)
    except Exception as exc:
        msg = str(exc)
        err_msg = (
            f"[ERROR] ee.Initialize(project='{project}') failed:\n{msg}\n\n"
            "Common causes and solutions:\n"
            "1. Earth Engine API not enabled:\n"
            f"   Go to https://console.cloud.google.com/apis/library/earthengine.googleapis.com\n"
            f"   Select project '{project}' and click 'ENABLE'.\n"
            "2. Project ID typo or mismatch:\n"
            "   Ensure you are using the Project ID (e.g. 'my-project-12345'), NOT the project name.\n"
            "3. Non-commercial registration pending:\n"
            "   Register at https://code.earthengine.google.com/register for academic/research access.\n"
            "4. Token expired:\n"
            "   Run: earthengine authenticate --force"
        )
        if raise_exit:
            sys.stderr.write(f"\n{err_msg}\n\n")
            raise SystemExit(1)
        raise EarthEngineAuthError(err_msg)

    return project


def main() -> None:
    parser = argparse.ArgumentParser(description="Check or initialize Earth Engine.")
    parser.add_argument("--force-auth", action="store_true", help="Force re-authentication")
    args = parser.parse_args()

    print("Checking Earth Engine environment...")
    has_creds = is_authenticated()
    print(f"  Local credentials found: {has_creds}")
    env_exists, env_path = check_env_file()
    print(f"  .env file present: {env_exists}")
    project = os.environ.get("EE_PROJECT")
    print(f"  EE_PROJECT: {project if project else '(not set)'}")

    if not env_exists or not project or project in ("your-gcp-project-id", "YOUR_GCP_PROJECT_ID"):
        print("\nSetup required: Please copy .env.example -> .env and add your Google Cloud project ID.")
        return

    if not has_creds:
        print("\nAuthentication required: Please run 'earthengine authenticate' in your browser.")
        return

    try:
        p = init_ee(force_auth=args.force_auth, raise_exit=True)
        print(f"\n[SUCCESS] Successfully initialized Earth Engine with project: {p}")
        print(f"earthengine-api version: {ee.__version__}")
    except Exception as e:
        print(f"\n[FAILED] {e}")


if __name__ == "__main__":
    main()
