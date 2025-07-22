#!/usr/bin/env python3
"""Helper script to start proxy and Claude with proper startup timing."""

import argparse
import subprocess
import time
import requests
import sys
import os
from pathlib import Path


def wait_for_server(url, max_wait=30):
    """Wait for the server to be ready."""
    print(f"⏳ Waiting for server at {url}...")
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f"{url}/", timeout=1)
            if response.status_code == 200:
                print("✅ Server is ready!")
                return True
        except requests.RequestException:
            pass
        
        time.sleep(0.5)
    
    print("❌ Server failed to start within timeout")
    return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Start Anthropic proxy and Claude with proper timing"
    )
    parser.add_argument(
        "--provider",
        choices=["openai", "google"],
        default="openai",
        help="Preferred provider (default: openai)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8082,
        help="Port for the proxy server (default: 8082)"
    )
    parser.add_argument(
        "--big-model",
        help="Big model to use (e.g., gpt-4o, gemini-2.5-pro-preview-03-25)"
    )
    parser.add_argument(
        "--small-model", 
        help="Small model to use (e.g., gpt-4o-mini, gemini-2.0-flash)"
    )
    parser.add_argument(
        "--no-wait",
        action="store_true",
        help="Don't wait for server to be ready (use fixed delay)"
    )
    
    args = parser.parse_args()
    
    # Build environment variables
    env_vars = {
        "PREFERRED_PROVIDER": args.provider
    }
    
    if args.big_model:
        env_vars["BIG_MODEL"] = args.big_model
    
    if args.small_model:
        env_vars["SMALL_MODEL"] = args.small_model
    
    # Check for required API keys
    if args.provider == "openai" and not os.environ.get("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set")
    elif args.provider == "google" and not os.environ.get("GEMINI_API_KEY"):
        print("⚠️  Warning: GEMINI_API_KEY not set")
    
    # Start the proxy server
    print(f"🚀 Starting Anthropic proxy with {args.provider} provider...")
    
    proxy_cmd = ["anthropic-proxy", "--port", str(args.port)]
    
    try:
        # Start proxy in background
        proxy_process = subprocess.Popen(
            proxy_cmd,
            env={**os.environ, **env_vars},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to be ready
        server_url = f"http://localhost:{args.port}"
        
        if args.no_wait:
            print("⏳ Waiting 2 seconds for server startup...")
            time.sleep(2)
        else:
            if not wait_for_server(server_url):
                proxy_process.terminate()
                sys.exit(1)
        
        # Set environment for Claude
        claude_env = {**os.environ, "ANTHROPIC_BASE_URL": server_url}
        
        print("🎯 Starting Claude...")
        
        # Start Claude
        claude_process = subprocess.run(
            ["claude"],
            env=claude_env,
            check=True
        )
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        # Clean up proxy process
        if 'proxy_process' in locals():
            proxy_process.terminate()
            try:
                proxy_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proxy_process.kill()


if __name__ == "__main__":
    main() 