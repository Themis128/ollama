#!/usr/bin/env python3
"""Live Ollama monitoring with verbose debugging."""

import time
import httpx
import json
from datetime import datetime
from pathlib import Path

def get_debug_info():
    """Get detailed Ollama debugging information."""
    info = {}
    
    try:
        # Server status
        response = httpx.get("http://localhost:11434/api/tags", timeout=2)
        info["server"] = "✅ Running" if response.status_code == 200 else "❌ Error"
        
        # Models
        data = response.json()
        models = data.get("models", [])
        info["model_count"] = len(models)
        info["models"] = [{"name": m["name"], "size_gb": round(m["size"]/(1024**3), 2)} for m in models]
        
        # Version
        version_resp = httpx.get("http://localhost:11434/api/version", timeout=2)
        if version_resp.status_code == 200:
            info["version"] = version_resp.json().get("version", "unknown")
            
    except Exception as e:
        info["server"] = f"❌ Down: {str(e)}"
        info["model_count"] = 0
    
    # Integration status
    skill_path = Path("/home/tbaltzakis/cloudless.gr/.deepagents/skills/ollama-infrastructure")
    info["integration"] = "✅ Active" if skill_path.exists() else "❌ Missing"
    
    return info

def main():
    print("📡 Live Ollama Debug Monitor (Ctrl+C to stop)")
    print("=" * 60)
    
    try:
        while True:
            info = get_debug_info()
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            print(f"\n[{timestamp}]")
            print(f"  Server: {info['server']}")
            print(f"  Models: {info['model_count']}")
            print(f"  Integration: {info['integration']}")
            if info.get("version"):
                print(f"  Version: {info['version']}")
            if info.get("models"):
                for m in info["models"]:
                    print(f"    - {m['name']} ({m['size_gb']} GB)")
                    
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n✅ Monitoring stopped")

if __name__ == "__main__":
    main()