import re
import os
import pypdf
from google_services import GoogleWorkspaceManager

def get_next_resume_number(manager: GoogleWorkspaceManager) -> int:
    """Finds the highest number used in existing 'Farzaan's Resume X' files in Drive."""
    q = "name contains \"Farzaan's Resume\" and trashed = false"
    res = manager.drive_service.files().list(q=q, spaces='drive', fields='files(name)').execute()
    files = res.get('files', [])
    
    max_num = 0
    pattern = re.compile(r"^Farzaan's Resume (\d+)")
    for f in files:
        name = f.get('name', '')
        m = pattern.match(name)
        if m:
            num = int(m.group(1))
            if num > max_num:
                max_num = num
                
    return max_num + 1

def set_pdf_metadata(pdf_path: str, title: str, author: str = "Farzaan Khan"):
    """Sets clean PDF metadata: Title and Author only, no AI/tool traces."""
    reader = pypdf.PdfReader(pdf_path)
    writer = pypdf.PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
        
    metadata = {
        '/Title': title,
        '/Author': author,
        '/Producer': '',
        '/Creator': ''
    }
    writer.add_metadata(metadata)
    with open(pdf_path, 'wb') as f:
        writer.write(f)
    print(f"PDF metadata set cleanly: Title='{title}', Author='{author}'")

if __name__ == '__main__':
    m = GoogleWorkspaceManager()
    next_num = get_next_resume_number(m)
    print(f"Next resume name will be: Farzaan's Resume {next_num}")
