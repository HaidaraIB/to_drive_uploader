# to_drive_uploader

A Telegram bot that lets admins upload files from Telegram to Google Drive folders. It supports admin and folder management, uses OAuth (credentials + refresh token) for Google Drive, and optionally uses Telethon to download files larger than 20MB. The bot interface is in Arabic.

## Key Features

* **Upload to Google Drive**: Choose a folder from your configured list, then send a file (documents, video, audio, or photos). The bot downloads it temporarily, uploads it to Drive, returns a clickable link, and removes the temporary file.
* **Admin Management**: Add or remove admins via commands. Adding uses "Select User" (Telegram's Users Shared) and callback lists for removal.
* **Folder Management**: Add a Google Drive folder by providing a display name and its Drive folder ID; remove folders from the list when no longer needed.
* **Large File Support**: For files over 20MB, the bot uses Telethon to download from Telegram (via a dedicated media channel), then uploads to Drive.
* **Local Storage**: SQLite stores the list of admins and folders. The `data/` and `media/` directories are created automatically on first run.
* **Security**: All bot commands work only in private chats with the bot and only for users registered as admins.

## Technology Stack & Architecture

* **Language**: Python 3.x
* **Telegram Bot**: `python-telegram-bot` for handlers, ConversationHandlers, and InlineKeyboard flows.
* **Google Drive**: `google-api-python-client`, `google-auth-httplib2`, and `google-auth-oauthlib` for OAuth with refresh token.
* **Large File Downloads**: `telethon` (TelegramClient) when file size exceeds 20MB; messages are forwarded to a media channel and downloaded via Telethon.
* **Database**: SQLite via `sqlite3` with two tables: `admins` and `folders`. Access is wrapped in a thread-safe singleton in `database.py`.
* **Configuration**: `python-dotenv` and a `.env` file for all secrets and paths.

Uploads are handled by **DriveServiceSingleton** (Google Drive API, token refresh). Large-file downloads use **TeleClientSingleton**. Configuration and permissions are centralized in **Config** and **Database**.

## Project Structure

```
to_drive_uploader/
├── bot.py                  # Entry point: handler registration and ConversationHandlers
├── Config.py               # Loads .env, exposes DB access (admins, folders), credentials paths
├── database.py             # Singleton for SQLite (admins, folders)
├── DriveServiceSingleton.py # Google Drive service (upload, OAuth refresh)
├── TeleClientSingleton.py  # Telethon client for large file downloads
├── admin_settings.py       # Add/remove admin commands and handlers
├── folder_settings.py      # Add/remove folder commands and handlers
├── upload_settings.py      # Upload flow: choose folder → receive file → download → upload
├── generate_refresh_token.py # One-time script to generate refresh token from credentials
├── requirements.txt
├── .env                    # Not committed; required environment variables
└── credentials/            # Optional; credentials.json and refresh_token.txt (or paths in .env)
```

The `data/` (database, persistence) and `media/` (temporary uploads) directories are created automatically when the bot starts.

## Setup and Installation

### Prerequisites

* Python 3.x
* A [Google Cloud](https://console.cloud.google.com/) project with the Google Drive API enabled
* A Telegram bot token from [BotFather](https://t.me/BotFather)
* For large files (>20MB): a Telegram API app from [my.telegram.org](https://my.telegram.org/) (API_ID, API_HASH) and a dedicated channel for media (see `MEDIA_CHANNEL_ID` below)

### 1. Clone the repository

```sh
git clone <repository_url>
cd to_drive_uploader
```

### 2. Install dependencies

```sh
pip install -r requirements.txt
```

### 3. Google Drive OAuth setup

1. In [Google Cloud Console](https://console.cloud.google.com/), create or select a project and enable the **Google Drive API**.
2. Go to **APIs & Services** > **Credentials**, click **Create Credentials** > **OAuth client ID**.
3. Choose **Desktop app**, name it, and create. Download the JSON file.
4. Place the file as `credentials/credentials.json` (or set `CREDENTIALS_FILE` in `.env` to your path).
5. Run the refresh token script (a browser window will open for sign-in):

   ```sh
   python generate_refresh_token.py
   ```

6. Save the generated refresh token as `credentials/refresh_token.txt` (or set `REFRESH_TOKEN_FILE` in `.env`).

### 4. Environment variables (`.env`)

Create a `.env` file in the project root with at least:

| Variable | Description |
|----------|-------------|
| `BOT_TOKEN` | Bot token from BotFather |
| `OWNER_ID` | Your Telegram user ID (added as first admin on startup) |
| `CREDENTIALS_FILE` | Path to OAuth client JSON (e.g. `credentials/credentials.json`) |
| `REFRESH_TOKEN_FILE` | Path to the refresh token file (e.g. `credentials/refresh_token.txt`) |
| `API_ID` | Telegram API ID from my.telegram.org (for Telethon) |
| `API_HASH` | Telegram API hash from my.telegram.org (for Telethon) |
| `PHONE` | Your phone number for Telethon login (e.g. `+1234567890`) |
| `SESSION` | Session name for Telethon (e.g. `uploader_session`) |
| `MEDIA_CHANNEL_ID` | Telegram channel ID used when downloading large files (>20MB) via Telethon |

Folders and the database are initialized automatically on first run (`Config.create_folders()` and `Database`).

### 5. Run the bot

```sh
python bot.py
```

## Run with systemd on Ubuntu VPS (instead of screen)

This project includes ready-to-use files for `systemd`:

- `systemd/to-drive-uploader.service` (service template)
- `deploy/ubuntu/setup_systemd.sh` (setup script)

### 1) Prepare server dependencies

```sh
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
```

### 2) Upload/clone the project on VPS

Example path:

```sh
/opt/to_drive_uploader
```

Make sure these exist in project root:

- `.env`
- `credentials/credentials.json`
- `credentials/refresh_token.txt`

### 3) Create a dedicated Linux user (recommended)

```sh
sudo useradd -r -m -d /opt/to_drive_uploader -s /usr/sbin/nologin botuser || true
sudo chown -R botuser:botuser /opt/to_drive_uploader
```

### 4) Install and start the service

```sh
cd /opt/to_drive_uploader
sudo bash deploy/ubuntu/setup_systemd.sh \
  --project-dir /opt/to_drive_uploader \
  --user botuser \
  --group botuser \
  --service-name to-drive-uploader
```

### 5) Check health and logs

```sh
sudo systemctl status to-drive-uploader.service
sudo journalctl -u to-drive-uploader.service -f
```

### 6) Useful service commands

```sh
sudo systemctl restart to-drive-uploader.service
sudo systemctl stop to-drive-uploader.service
sudo systemctl disable to-drive-uploader.service
```

If you update dependencies or code, restart service:

```sh
cd /opt/to_drive_uploader
sudo -u botuser ./.venv/bin/pip install -r requirements.txt
sudo systemctl restart to-drive-uploader.service
```

## Obtaining Google Drive Folder IDs

To use a folder with the bot, you need its Drive folder ID:

1. Open [Google Drive](https://drive.google.com/) in a browser.
2. Go to the folder you want to use.
3. The folder ID is the long string in the URL between `/folders/` and the next `/` or `?`.

Example URL:

```
https://drive.google.com/drive/folders/1AbCdEfGhIjKlMnOpQrStUvWxYz
```

The folder ID here is: `1AbCdEfGhIjKlMnOpQrStUvWxYz`

## Bot Usage Guide

### Uploading files

1. In a **private chat** with the bot, send `/upload` (or start the flow as configured).
2. The bot shows your configured folders as buttons; choose one.
3. Send the file (document, video, audio, or photo). The bot downloads it, uploads to Drive, and replies with a link. Files over 20MB are handled via Telethon and the media channel.

### Admin management

* **Add admin**: `/addadmin` → use "Select User" to pick a contact. The bot confirms if the user was added.
* **Remove admin**: `/removeadmin` → the bot lists current admins; choose one to remove. The owner cannot be removed.

### Folder management

* **Add folder**: `/addfolder`, then send a **single message** in this format (name on first line, folder ID on second):

  ```
  Folder Name
  GoogleDriveFolderID
  ```

  Example:

  ```
  My Documents
  1AbCdEfGhIjKlMnOpQrStUvWxYz
  ```

* **Remove folder**: `/removefolder` → select a folder from the list to remove it.

### Other

* **Cancel**: `/cancel` (or `/stop`, `/exit`) to cancel the current conversation step.

All of the above commands work only in private chat and only for users who are admins.

## Troubleshooting

* **Uploads fail**
  * Check that the Google Drive API is enabled and within quota.
  * Verify folder IDs are correct and the OAuth account has access to those folders.
  * Ensure `CREDENTIALS_FILE` and `REFRESH_TOKEN_FILE` are correct and the token is valid (re-run `generate_refresh_token.py` if needed).

* **Admin commands do nothing**
  * Confirm your user ID is in the admins list (e.g. set `OWNER_ID` and restart so you are added as owner).
  * Use the bot only in **private** chats.

* **Large file downloads fail**
  * Ensure `API_ID`, `API_HASH`, `PHONE`, and `SESSION` are set and Telethon can log in.
  * Ensure `MEDIA_CHANNEL_ID` is a channel the bot and the Telethon client can access; the bot forwards the message there and Telethon downloads from it.

## Security and Important Notes

* Do **not** commit `.env`, `credentials/`, or `*.session` files. They give access to your bot and Google Drive.
* Keep `credentials.json` and `refresh_token.txt` secure; anyone with them can access the linked Drive account.
* Only add trusted users as admins.
* The first time you run `generate_refresh_token.py`, you must sign in in the browser. The refresh token then allows the app to obtain new access tokens without user interaction. If you see auth errors, you may need to delete the refresh token file and regenerate it.
