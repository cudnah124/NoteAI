#!/usr/bin/env python3
"""
Check environment variables before starting the app
Use this to diagnose deployment issues on Render
"""
import os
import sys

required_vars = {
    "DATABASE_URL": "PostgreSQL connection string",
    "SECRET_KEY": "JWT secret key",
    "NCP_CLOVASTUDIO_API_KEY": "Naver Cloud API key",
    "NCP_CLOVASTUDIO_API_KEY_PRIMARY_VAL": "Naver Cloud primary key",
    "NCP_CLOVASTUDIO_REQUEST_ID": "Naver Cloud request ID",
    "QDRANT_URL": "Qdrant vector database URL",
    "QDRANT_API_KEY": "Qdrant API key",
}

optional_vars = {
    "MOCK_MODE": "AI mock mode (default: false)",
    "ALLOWED_ORIGINS": "CORS allowed origins",
    "PORT": "Server port (default: 8000)",
}

def mask_value(value: str) -> str:
    """Mask sensitive values for display"""
    if not value:
        return "NOT SET"
    if len(value) <= 8:
        return "****"
    return f"{value[:4]}...{value[-4:]}"

def check_env():
    print("=" * 60)
    print("ENVIRONMENT VARIABLES CHECK")
    print("=" * 60)
    
    missing = []
    
    print("\n📋 Required Variables:")
    print("-" * 60)
    for var, description in required_vars.items():
        value = os.getenv(var)
        status = "✅" if value else "❌"
        display_value = mask_value(value) if value else "NOT SET"
        print(f"{status} {var:40} {display_value}")
        if not value:
            missing.append(var)
    
    print("\n📋 Optional Variables:")
    print("-" * 60)
    for var, description in optional_vars.items():
        value = os.getenv(var)
        status = "✅" if value else "⚠️"
        display_value = value if value else "NOT SET (using default)"
        print(f"{status} {var:40} {display_value}")
    
    print("\n" + "=" * 60)
    
    if missing:
        print("\n❌ MISSING REQUIRED VARIABLES:")
        for var in missing:
            print(f"   - {var}: {required_vars[var]}")
        print("\n⚠️  Application will fail to start!")
        print("\n📖 Set these in Render Dashboard:")
        print("   Go to: Web Service → Environment → Add Environment Variable")
        print("\n" + "=" * 60)
        sys.exit(1)
    else:
        print("✅ All required environment variables are set!")
        print("=" * 60)
        sys.exit(0)

if __name__ == "__main__":
    check_env()
