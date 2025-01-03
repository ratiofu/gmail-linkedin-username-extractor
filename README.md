# Gmail LinkedIn Username Extractor

## What
This script extracts LinkedIn usernames from email messages in a Gmail account.

## Why

Every week, my employer is sending a "Welcome" email to everyone, introducing new team members, including a link to their LinkedIn profile. I had not followed up for a while, so I decided to automate the extraction of LinkedIn usernames from all such email messags. I update a Google Sheet with the resulting usernames and link directly to the profiles from there. This enables efficient tracking of which invites I have already sent.

Secondary goal: As a learning exercise to get familiar with it, I used the [Cursor IDE](https://www.cursor.com/) to help me build this.

## How

Use the Gmail API and its Python SDK to find messages from a particular sender with a specific subject and extract the LinkedIn usernames from the body of the message via [BeautifulSoup 4](https://pypi.org/project/beautifulsoup4/).

# Usage

## Gmail Client Application

Before you can use this script, you have to provide the credentials for a Gmail OAuth client application:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/) and create a new project (or reuse an existing one).
2. Ensure that the Gmail API is enabled for the project.
3. Create a new OAuth client ID and secret.
4. Download the `credentials.json` file and put it in the root of this repository.

## Running the script

Optionally, create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate
```

Install the required dependencies:
```bash
pip install -r requirements.txt
```

Run the script:
```bash
python gmail_parser.py -s some_sender@example.com -q "Some Subject"
```

### ⚠️ Note

_The filters for sender and subject are required to limit the scope of the search and extraction._
