import argparse
import base64
import os
import pickle
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_gmail_service():
    """Sets up and returns the Gmail service object."""
    creds = None

    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build("gmail", "v1", credentials=creds)


def search_emails(service, sender_email, subject_query):
    """Search for emails from specific sender with specific subject."""
    query = f"from:{sender_email} subject:{subject_query}"  # noqa: E231
    results = service.users().messages().list(userId="me", q=query).execute()
    messages = results.get("messages", [])
    print(f"\nFound {len(messages)} messages matching search criteria")
    return messages


def extract_linkedin_links(html_content):
    """Extract LinkedIn URLs from HTML content."""
    soup = BeautifulSoup(html_content, "html.parser")
    linkedin_links = []

    for link in soup.find_all("a"):
        href = link.get("href")
        if href and "linkedin.com" in href.lower():
            clean_url = clean_linkedin_username(href)
            if clean_url:
                linkedin_links.append(clean_url)

    return linkedin_links


def get_html_content(part):
    """Recursively search for and return HTML content from message parts."""
    if part.get("mimeType") == "text/html":
        return part["body"].get("data")

    if part.get("mimeType", "").startswith("multipart/"):
        for subpart in part.get("parts", []):
            content = get_html_content(subpart)
            if content:
                return content
    return None


def clean_linkedin_username(href):
    """
    Get a clean LinkedIn profile username.
    """
    parsed = urlparse(href)
    path = parsed.path.lower()
    if "/in/" in path:
        # Extract just the profile name after /in/, removing any trailing slash
        profile_name = path[path.find("/in/") + 4 :].rstrip("/").strip()
        return profile_name
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Extract LinkedIn usernames from Gmail messages"
    )
    parser.add_argument(
        "--sender", "-s", required=True, help="Email address of the sender"
    )
    parser.add_argument(
        "--subject",
        "-q",
        required=True,
        help="Subject line query to search for",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="linkedin_usernames.txt",
        help="Output file path (default: linkedin_usernames.txt)",
    )

    args = parser.parse_args()

    SENDER_EMAIL = args.sender
    SUBJECT_QUERY = args.subject
    OUTPUT_FILE = args.output

    print(
        f"Searching for emails from {SENDER_EMAIL} "
        f"with subject containing '{SUBJECT_QUERY}'..."
    )
    service = get_gmail_service()

    # Search for messages
    messages = search_emails(service, SENDER_EMAIL, SUBJECT_QUERY)

    # Extract LinkedIn links
    all_linkedin_links = set()
    for i, message in enumerate(messages, 1):
        msg = (
            service.users()
            .messages()
            .get(userId="me", id=message["id"], format="full")
            .execute()
        )

        # Get subject from headers
        subject = next(
            (
                header["value"]
                for header in msg["payload"]["headers"]
                if header["name"].lower() == "subject"
            ),
            "No Subject",
        )
        print(f"\nProcessing message {i}/{len(messages)}: {subject}")

        # Get the email body
        html_content = get_html_content(msg["payload"])
        if html_content:
            html_content = base64.urlsafe_b64decode(html_content).decode(
                "utf-8"
            )
            links = extract_linkedin_links(html_content)
            if links:
                print(f"  Found {len(links)} LinkedIn links in this message")
            all_linkedin_links.update(links)

    # Write links to file
    with open(OUTPUT_FILE, "w") as f:
        for link in sorted(all_linkedin_links):
            f.write(f"{link}\n")

    print("\nSummary:")
    print(f"- Processed {len(messages)} messages")
    print(f"- Found {len(all_linkedin_links)} unique LinkedIn links")
    print(f"- Saved results to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
