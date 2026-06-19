"""
File: email_sender.py

Purpose:
Provides SMTP-based email notification services to distribute test reports,
summaries, and failure logs. Integrates with config/config.json configurations,
and can be run programmatically or as a post-test command-line script.

Author: <Your Name>

Created: 2026-06-19
"""

import logging
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from utils.config_loader import ConfigLoader

# Initialize logger
logger = logging.getLogger(__name__)


class EmailSender:
    """
    Constructs and sends test reports via SMTP email.
    """

    def __init__(self):
        self.config = ConfigLoader()
        self.email_settings = self.config.email_config

    def send_report_email(self, force: bool = False) -> bool:
        """
        Gathers summary.md content, hooks up report.html as attachment,
        and transmits it via configured SMTP server settings.

        Args:
            force: Override config enable check.

        Returns:
            bool: True if mail sent successfully, False otherwise.
        """
        # Return early if feature is not enabled
        if not self.email_settings.get("enabled", False) and not force:
            logger.info("Email distribution is disabled in configuration. Skipping.")
            return False

        smtp_server = self.email_settings.get("smtp_server")
        smtp_port = self.email_settings.get("smtp_port")
        sender_email = self.email_settings.get("sender_email")
        sender_password = self.email_settings.get("sender_password")
        receiver_email = self.email_settings.get("receiver_email")

        # Validate SMTP configuration settings
        if not all([smtp_server, smtp_port, sender_email, receiver_email]):
            logger.error("Missing mandatory SMTP email settings. Cannot send notification.")
            return False

        logger.info(f"Preparing test report email for transmission to: '{receiver_email}'")

        # Initialize multipart container
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = (
            f"QA Test Run Report - {self.config.environment.upper()} - Demo Web Shop"
        )

        # 1. Load summary metrics from reports/execution_summary.md if available
        summary_path = self.config.reports_dir / "execution_summary.md"
        email_body = "The automation test suite run has completed.\n\n"
        if summary_path.exists():
            try:
                with open(summary_path, "r", encoding="utf-8") as summary_file:
                    email_body += summary_file.read()
            except Exception as read_error:
                logger.warning(f"Could not load execution summary file: {str(read_error)}")
        else:
            email_body += "Detailed report is attached."

        message.attach(MIMEText(email_body, "plain"))

        # 2. Attach html test report if available
        report_path = self.config.reports_dir / "report.html"
        if report_path.exists():
            try:
                with open(report_path, "rb") as report_file:
                    attachment = MIMEBase("application", "octet-stream")
                    attachment.set_payload(report_file.read())
                    encoders.encode_base64(attachment)
                    attachment.add_header(
                        "Content-Disposition",
                        f"attachment; filename={report_path.name}",
                    )
                    message.attach(attachment)
                logger.info(f"Attached HTML report file successfully: {report_path.name}")
            except Exception as attach_error:
                logger.error(f"Failed to attach report.html: {str(attach_error)}")
        else:
            logger.warning(
                f"HTML report file missing at {report_path}. Sending without attachment."
            )

        # 3. Transmit email via SMTP
        try:
            # We connect to standard SMTP and secure with STARTTLS
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            if sender_password:
                # Login only if password is provided
                server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            server.quit()
            logger.info("Test execution email report sent successfully.")
            return True
        except Exception as smtp_error:
            logger.error(f"SMTP transmission failed: {str(smtp_error)}")
            return False


if __name__ == "__main__":
    # Allows executing directly to trigger post-run distribution
    logging.basicConfig(level=logging.INFO)
    sender = EmailSender()
    sender.send_report_email(force=True)
