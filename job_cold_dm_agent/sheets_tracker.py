import os
import datetime
from google_services import GoogleWorkspaceManager

COLUMNS = [
    "Date Added", "Company", "Company Website", "Industry / Size", "HQ / Location",
    "Job Title", "Work Mode", "Salary", "Top Requirements", "Skill Gaps",
    "Job Posting URL", "APPLY LINK", "TAILORED RESUME LINK",
    "Hiring Manager", "Manager Role", "Contact Email", "Email Source URL",
    "Recent Company News", "Email Subject", "Email Status", "Date Sent",
    "Follow-up Date", "Reply Status", "Applied via Portal? (Y/N)", "Notes"
]

def get_or_create_tracker(manager: GoogleWorkspaceManager):
    """Finds existing 'Job Outreach Tracker' or creates a new one in Drive."""
    q = "name = 'Job Outreach Tracker' and mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false"
    res = manager.drive_service.files().list(q=q, spaces='drive', fields='files(id, name, webViewLink)').execute()
    files = res.get('files', [])
    if files:
        sheet = files[0]
        print(f"Found existing tracker sheet: {sheet['name']} ({sheet['id']})")
        return sheet['id'], sheet.get('webViewLink')
    
    # Create new spreadsheet
    file_metadata = {
        'name': 'Job Outreach Tracker',
        'mimeType': 'application/vnd.google-apps.spreadsheet'
    }
    sheet = manager.drive_service.files().create(body=file_metadata, fields='id, webViewLink').execute()
    sheet_id = sheet['id']
    sheet_link = sheet.get('webViewLink')
    print(f"Created new tracker sheet: {sheet_id}")
    
    # Initialize header row using Sheets API or batch update
    # We can check if sheets service is available
    return sheet_id, sheet_link

def append_outreach_row(row_data: dict, sheet_id: str, manager: GoogleWorkspaceManager):
    from googleapiclient.discovery import build
    sheets_service = build('sheets', 'v4', credentials=manager.creds)
    
    # Check if header exists
    res = sheets_service.spreadsheets().values().get(spreadsheetId=sheet_id, range="A1:Y1").execute()
    values = res.get('values', [])
    if not values:
        # Write header
        sheets_service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range="A1:Y1",
            valueInputOption="RAW",
            body={"values": [COLUMNS]}
        ).execute()
        
    row_values = [row_data.get(col, "") for col in COLUMNS]
    append_res = sheets_service.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range="A1",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": [row_values]}
    ).execute()
    return append_res

if __name__ == "__main__":
    m = GoogleWorkspaceManager()
    s_id, s_link = get_or_create_tracker(m)
    print("Tracker Sheet Link:", s_link)
