#!/usr/bin/env python3
"""CLI for Anthropic API Proxy."""

import argparse
import os
import sys
import subprocess
from pathlib import Path


def find_server_py():
    """Find the server.py file in the package directory."""
    # Get the directory where this CLI module is located
    cli_dir = Path(__file__).parent
    
    # Look for server.py in the parent directory (project root)
    server_path = cli_dir.parent / "server.py"
    
    if server_path.exists():
        return str(server_path)
    
    # Fallback: look in the same directory as the CLI
    server_path = cli_dir / "server.py"
    if server_path.exists():
        return str(server_path)
    
    raise FileNotFoundError("Could not find server.py")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Anthropic API Proxy - Run Claude Code on OpenAI/Gemini models"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8082,
        help="Port to bind to (default: 8082)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Environment file to load (default: .env)"
    )
    
    args = parser.parse_args()
    
    # Check if .env file exists and warn if not
    env_file_path = Path(args.env_file)
    if not env_file_path.exists():
        print(f"⚠️  Warning: Environment file '{args.env_file}' not found.")
        print("   Make sure to set your API keys via environment variables.")
        print("   See README.md for configuration details.")
        print()
    
    # Find the server.py file
    try:
        server_path = find_server_py()
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    # Prepare the uvicorn command
    cmd = [
        "uvicorn",
        "--host", args.host,
        "--port", str(args.port)
    ]
    
    if args.reload:
        cmd.append("--reload")
    
    # Add the server module (convert path to module notation)
    server_dir = Path(server_path).parent
    server_name = Path(server_path).stem
    
    # Change to the server directory so imports work correctly
    os.chdir(server_dir)
    
    # Add the app specification
    cmd.append(f"{server_name}:app")
    
    print(f"🚀 Starting Anthropic API Proxy on {args.host}:{args.port}")
    print(f"📁 Server: {server_path}")
    print(f"🔧 Command: {' '.join(cmd)}")
    print()
    print("Use this with Claude Code:")
    print(f"   ANTHROPIC_BASE_URL=http://localhost:{args.port} claude")
    print()
    print("Press Ctrl+C to stop the server")
    print()
    
    try:
        # Run uvicorn
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Error: uvicorn not found. Make sure it's installed:")
        print("   uv add uvicorn")
        sys.exit(1)


if __name__ == "__main__":
    main() 