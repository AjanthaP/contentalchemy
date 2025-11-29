"""
Debug script to identify the exact issue
Run this in Railway logs to see what's happening
"""

import sys
import os

print("=" * 60)
print("DEBUGGING OPENAI PROXIES ISSUE")
print("=" * 60)

# Check Python version
print(f"\n1. Python Version: {sys.version}")
print(f"   Python executable: {sys.executable}")

# Check environment
print(f"\n2. Environment Variables:")
for key in sorted(os.environ.keys()):
    if 'PROXY' in key.upper() or 'HTTP' in key.upper():
        print(f"   {key}={os.environ[key]}")
if not any('PROXY' in key.upper() for key in os.environ.keys()):
    print("   (No proxy variables found)")

# Check installed packages
print(f"\n3. Installed Packages:")
try:
    import openai
    print(f"   openai: {openai.__version__}")
except:
    print("   openai: NOT INSTALLED")

try:
    import httpx
    print(f"   httpx: {httpx.__version__}")
except:
    print("   httpx: NOT INSTALLED")

try:
    import langchain_openai
    print(f"   langchain-openai: {langchain_openai.__version__}")
except:
    print("   langchain-openai: NOT INSTALLED")

try:
    import langchain
    print(f"   langchain: {langchain.__version__}")
except:
    print("   langchain: NOT INSTALLED")

# Try to create OpenAI client
print(f"\n4. Testing OpenAI Client Creation:")
try:
    from openai import OpenAI
    
    client = OpenAI(api_key="test-key")
    print("   ✅ OpenAI client created successfully")
except TypeError as e:
    print(f"   ❌ TypeError: {e}")
except Exception as e:
    print(f"   ❌ Other error: {type(e).__name__}: {e}")

# Try to create ChatOpenAI
print(f"\n5. Testing ChatOpenAI Creation:")
try:
    from langchain_openai import ChatOpenAI
    
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key="test-key"
    )
    print("   ✅ ChatOpenAI created successfully")
except TypeError as e:
    print(f"   ❌ TypeError: {e}")
    print(f"      This means: ChatOpenAI is passing unexpected 'proxies' parameter")
except Exception as e:
    print(f"   ❌ Other error: {type(e).__name__}: {e}")

print("\n" + "=" * 60)