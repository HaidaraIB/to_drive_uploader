# Google Drive OAuth Credentials Setup

This guide will walk you through setting up OAuth credentials for uploading files to Google Drive using Python, obtaining folder IDs, and generating a refresh token.

## Prerequisites

- Google Cloud Platform account
- Python 3.x installed
- Google API Client Library for Python (`pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib`)

## Setup Instructions

### 1. Create OAuth Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to "APIs & Services" > "Credentials"
4. Click "Create Credentials" and select "OAuth client ID"
5. Select "Desktop app" as the application type
6. Give it a name and click "Create"
7. Download the JSON file by clicking the download button (⭳) next to your new OAuth 2.0 Client ID

### 2. Folder Structure Setup

Create the following folder structure in your project:

```
your_project/
├── credentials/
│   ├── credentials.json (the downloaded OAuth file)
│   └── refresh_token.txt (will be generated)
└── generate_refresh_token.py
```

### 3. Generate Refresh Token

1. Place your downloaded credentials JSON file in the `credentials` folder and rename it to `credentials.json`
2. Run the `generate_refresh_token.py` script:
   ```bash
   python generate_refresh_token.py
   ```
3. This will open a browser window asking you to authenticate with Google
4. After authentication, a `refresh_token.txt` file will be created in the `credentials` folder

## Obtaining Google Drive Folder IDs

To get the ID of a Google Drive folder:

1. Open Google Drive in your web browser
2. Navigate to the folder you want to use
3. Look at the URL in your address bar - the ID is the long string between `/folders/` and the next `/` or `?`

Example URL:

```
https://drive.google.com/drive/folders/1AbCdEfGhIjKlMnOpQrStUvWxYz
```

The folder ID in this case is: `1AbCdEfGhIjKlMnOpQrStUvWxYz`

## Important Notes

- Keep your `credentials.json` and `refresh_token.txt` files secure - they provide access to your Google Drive
- The first time you run the script, you'll need to authenticate via the browser
- The refresh token will allow your application to get new access tokens without user interaction
- If you get authentication errors, you may need to delete `refresh_token.txt` and regenerate it

Remember to enable the Google Drive API for your project in the Google Cloud Console before proceeding.

# Telegram Bot Usage Guide

This bot allows admins to manage Google Drive uploads, folders, and admin permissions. Here's how to use it:

## Prerequisites

1. A running instance of this bot
2. Admin privileges (or owner access to set up initially)

## Main Features

### 1. Uploading Files to Google Drive

**Command Flow:**

1. Send any message to start (or use `/upload` if configured)
2. Bot will show available folders
3. Select a folder
4. Send the file you want to upload

**What Happens:**

- Bot downloads the file temporarily
- Uploads it to your selected Google Drive folder
- Provides a clickable link to the uploaded file
- Deletes the temporary file

### 2. Admin Management

#### Adding Admins

1. Use `/addadmin` command
2. Click "Select User" button
3. Choose a user from your contacts
4. Bot will confirm if added successfully

#### Removing Admins

1. Use `/removeadmin` command
2. Bot shows list of current admins
3. Select admin to remove
4. Bot confirms removal (can't remove owner)

### 3. Folder Management

#### Adding a Folder

1. Use `/addfolder` command
2. Send message in this format:
   ```
   Folder Name
   GoogleDriveFolderID
   ```
   Example:
   ```
   My Documents
   1AbCdEfGhIjKlMnOpQrStUvWxYz
   ```

#### Removing a Folder

1. Use `/removefolder` command
2. Bot shows list of current folders
3. Select folder to remove
4. Bot confirms removal

## Important Notes

1. **Admin Requirements**:

   - All commands only work in private chats with the bot
   - Only admins can use these features

2. **Google Drive Setup**:

   - You must first set up Google Drive API credentials
   - Folder IDs must be valid and accessible to your service account

3. **File Types Supported**:

   - Documents
   - Videos
   - Audio files
   - Photos

4. **Security**:
   - Keep your bot token and Google credentials secure
   - Only trusted users should be made admins

## Troubleshooting

- If uploads fail:

  - Check Google Drive API quota
  - Verify folder IDs are correct
  - Ensure service account has edit permissions

- If admin commands don't work:
  - Verify your user ID is in admin list
  - Check bot privacy settings

## Configuration

The bot uses these key components:

- `Config.py` - Stores admin IDs, folder configurations
- `DriveServiceSingleton.py` - Manages Google Drive connections
- Conversation handlers manage multi-step commands
