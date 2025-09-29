import os
# Access credentials stored in environment variables
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

# Check if any required config is missing
missing_configs = [key for key in ['ACCESS_TOKEN', 'REFRESH_TOKEN', 'GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET'] if not globals().get(key)]
if missing_configs:
    raise Exception(f"Missing config values for: {', '.join(missing_configs)}")
