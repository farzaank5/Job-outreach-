import sys
from google_services import GoogleWorkspaceManager

def test_draft():
    try:
        manager = GoogleWorkspaceManager()
        result = manager.create_referral_email_draft(
            to_email="test.hiring.manager@example.com",
            subject="Test Referral Request - Senior Software Engineer",
            body_text=(
                "Hi Alex,\n\n"
                "I noticed the open Senior Engineer role on your team. Given my experience scaling "
                "distributed backend systems and real-time agents, I'd love to learn more and see if "
                "there's a strong fit.\n\n"
                "Best regards,\nFarzaan"
            )
        )
        print("Success! Draft created in Gmail:", result)
    except Exception as e:
        print("Error creating draft:", str(e))
        sys.exit(1)

if __name__ == '__main__':
    test_draft()
