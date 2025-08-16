from google_auth_oauthlib.flow import InstalledAppFlow
from Config import Config

flow = InstalledAppFlow.from_client_secrets_file(
    Config.CREDENTIALS_FILE, scopes=Config.SCOPES
)

credentials = flow.run_local_server(port=0)

with open("credentials/refresh_token.txt", "w") as f:
    f.write(credentials.refresh_token)

print("Refresh token saved to refresh_token.txt")
