"""Google Workspace Integration Tools (Docs, Drive, Gmail) for Job Cold DM Agent.

Handles:
- Reading base resume templates from Google Docs
- Duplicating and tailoring resume text
- Exporting ATS-friendly PDF resumes via Google Drive
- Creating personalized cold outreach email drafts with attachments via Gmail API
"""

import os
import io
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import Dict, Any, List, Optional

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES = [
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive'
]

class GoogleWorkspaceManager:
    """Manages authenticated Google Docs, Drive, and Gmail service instances."""

    def __init__(self, token_path: Optional[str] = None):
        if not token_path:
            token_path = os.path.join(os.path.dirname(__file__), 'token.json')
        self.token_path = token_path
        self.creds = self._load_credentials()
        self.docs_service = build('docs', 'v1', credentials=self.creds)
        self.drive_service = build('drive', 'v3', credentials=self.creds)
        self.gmail_service = build('gmail', 'v1', credentials=self.creds)

    def _load_credentials(self) -> Credentials:
        if not os.path.exists(self.token_path):
            raise FileNotFoundError(
                f"Token file not found at {self.token_path}. Run auth_setup.py first."
            )
        creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        return creds

    # -------------------------------------------------------------
    # GOOGLE DOCS & RESUME MANAGEMENT
    # -------------------------------------------------------------
    def get_document_text(self, document_id: str) -> str:
        """Extracts all text content from a Google Doc."""
        doc = self.docs_service.documents().get(documentId=document_id).execute()
        text_parts = []

        def extract_text(element):
            if 'textRun' in element:
                text_parts.append(element['textRun']['content'])
            elif 'paragraph' in element:
                for el in element['paragraph'].get('elements', []):
                    extract_text(el)
            elif 'table' in element:
                for row in element['table'].get('tableRows', []):
                    for cell in row.get('tableCells', []):
                        for el in cell.get('content', []):
                            extract_text(el)

        for content_element in doc.get('body', {}).get('content', []):
            extract_text(content_element)

        return "".join(text_parts)

    def create_numbered_tailored_resume(
        self,
        base_document_id: str,
        resume_number: int,
        replacements: Dict[str, str],
        bold_phrases: Optional[List[str]] = None,
        output_pdf_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """Creates a tailored resume following strict naming, bolding, and formatting rules.

        Naming: Farzaan's Resume [number]
        PDF: Farzaan's Resume [number].pdf (with Title & Author metadata only)
        """
        import pypdf

        resume_name = f"Farzaan's Resume {resume_number}"
        pdf_filename = f"{resume_name}.pdf"

        # 1. Duplicate master document in Google Drive
        copied_file = self.drive_service.files().copy(
            fileId=base_document_id,
            body={'name': resume_name}
        ).execute()
        new_doc_id = copied_file['id']

        # 2. Batch text replacements (human wording, simple verbs, no buzzwords, no em dashes)
        requests = []
        for target, replacement in replacements.items():
            requests.append({
                'replaceAllText': {
                    'containsText': {
                        'text': target,
                        'matchCase': True
                    },
                    'replaceText': replacement
                }
            })

        if requests:
            self.docs_service.documents().batchUpdate(
                documentId=new_doc_id,
                body={'requests': requests}
            ).execute()

        # 3. Apply strategic bolding (numbers, JD matching skills, key outcomes)
        if bold_phrases:
            doc = self.docs_service.documents().get(documentId=new_doc_id).execute()
            # Extract text elements and their exact start/end indices
            bold_requests = []
            
            def scan_and_bold(elements):
                for el in elements:
                    if 'textRun' in el:
                        text = el['textRun'].get('content', '')
                        start = el.get('startIndex', 0)
                        for phrase in bold_phrases:
                            pos = 0
                            while True:
                                idx = text.find(phrase, pos)
                                if idx == -1:
                                    break
                                p_start = start + idx
                                p_end = p_start + len(phrase)
                                bold_requests.append({
                                    'updateTextStyle': {
                                        'range': {
                                            'startIndex': p_start,
                                            'endIndex': p_end
                                        },
                                        'textStyle': {'bold': True},
                                        'fields': 'bold'
                                    }
                                })
                                pos = idx + len(phrase)

            for content_el in doc.get('body', {}).get('content', []):
                if 'paragraph' in content_el:
                    scan_and_bold(content_el['paragraph'].get('elements', []))
                elif 'table' in content_el:
                    for row in content_el['table'].get('tableRows', []):
                        for cell in row.get('tableCells', []):
                            for sub_el in cell.get('content', []):
                                if 'paragraph' in sub_el:
                                    scan_and_bold(sub_el['paragraph'].get('elements', []))

            if bold_requests:
                # Apply in batches
                self.docs_service.documents().batchUpdate(
                    documentId=new_doc_id,
                    body={'requests': bold_requests}
                ).execute()

        # 4. Export as PDF
        if not output_pdf_dir:
            output_pdf_dir = os.path.join(os.path.dirname(__file__), 'generated_resumes')
        os.makedirs(output_pdf_dir, exist_ok=True)

        local_pdf_path = os.path.join(output_pdf_dir, pdf_filename)
        request = self.drive_service.files().export_media(
            fileId=new_doc_id,
            mimeType='application/pdf'
        )

        with open(local_pdf_path, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()

        # 5. Set PDF Document Properties (Title & Author only, no tool or AI names)
        reader = pypdf.PdfReader(local_pdf_path)
        writer = pypdf.PdfWriter()
        for page in reader.pages:
            writer.add_page(page)

        writer.add_metadata({
            '/Title': resume_name,
            '/Author': "Farzaan Khan",
            '/Producer': '',
            '/Creator': ''
        })
        with open(local_pdf_path, 'wb') as f:
            writer.write(f)

        return {
            "status": "success",
            "resume_name": resume_name,
            "tailored_doc_id": new_doc_id,
            "tailored_doc_url": f"https://docs.google.com/document/d/{new_doc_id}/edit",
            "pdf_path": local_pdf_path,
            "filename": pdf_filename,
            "page_count": len(reader.pages)
        }

    # -------------------------------------------------------------
    # GMAIL DRAFT & COLD EMAIL OUTREACH
    # -------------------------------------------------------------
    def create_referral_email_draft(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        attachment_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Creates a drafted referral email in Gmail with fluid mobile-responsive paragraphs."""
        from email.message import EmailMessage

        msg = EmailMessage()
        msg['To'] = to_email
        msg['Subject'] = subject
        msg['From'] = 'me'

        # Build clean HTML equivalent for fluid mobile reflow
        paragraphs = body_text.split('\n\n')
        html_paras = []
        for p in paragraphs:
            # Check if this paragraph contains the sign-off with internal newline
            p_html = p.replace('\n', '<br>')
            html_paras.append(f'<p style="margin: 0 0 16px 0; line-height: 1.5; font-size: 14px; color: #222;">{p_html}</p>')
        html_body = f'<div dir="ltr">{"".join(html_paras)}</div>'

        msg.set_content(body_text, cte='8bit')
        msg.add_alternative(html_body, subtype='html', cte='8bit')

        # Attach PDF if supplied
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, 'rb') as f:
                pdf_data = f.read()
                filename = os.path.basename(attachment_path)
                msg.add_attachment(pdf_data, maintype='application', subtype='pdf', filename=filename)

        encoded_message = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
        draft_body = {'message': {'raw': encoded_message}}

        draft = self.gmail_service.users().drafts().create(
            userId='me',
            body=draft_body
        ).execute()

        return {
            "status": "success",
            "draft_id": draft['id'],
            "to": to_email,
            "subject": subject,
            "attached_file": attachment_path if (attachment_path and os.path.exists(attachment_path)) else None
        }

    def send_referral_email(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        attachment_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Directly sends a referral email via Gmail with fluid mobile-responsive paragraphs."""
        from email.message import EmailMessage

        msg = EmailMessage()
        msg['To'] = to_email
        msg['Subject'] = subject
        msg['From'] = 'me'

        # Build clean HTML equivalent for fluid mobile reflow
        paragraphs = body_text.split('\n\n')
        html_paras = []
        for p in paragraphs:
            p_html = p.replace('\n', '<br>')
            html_paras.append(f'<p style="margin: 0 0 16px 0; line-height: 1.5; font-size: 14px; color: #222;">{p_html}</p>')
        html_body = f'<div dir="ltr">{"".join(html_paras)}</div>'

        msg.set_content(body_text, cte='8bit')
        msg.add_alternative(html_body, subtype='html', cte='8bit')

        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, 'rb') as f:
                pdf_data = f.read()
                filename = os.path.basename(attachment_path)
                msg.add_attachment(pdf_data, maintype='application', subtype='pdf', filename=filename)

        encoded_message = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
        send_body = {'raw': encoded_message}

        sent = self.gmail_service.users().messages().send(
            userId='me',
            body=send_body
        ).execute()

        return {
            "status": "success",
            "message_id": sent['id'],
            "to": to_email,
            "subject": subject
        }
