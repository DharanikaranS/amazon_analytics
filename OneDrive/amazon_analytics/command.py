from abc import ABC, abstractmethod
import smtplib
from email.mime.text import MIMEText

class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

class SendThankYouEmailCommand(Command):
    def __init__(self, recipient_email, feedback_content):
        self.recipient_email = recipient_email
        self.feedback_content = feedback_content

    def execute(self):
        try:
            # Create email content
            message = MIMEText(f"Thank you for your feedback!\n\nYour feedback: {self.feedback_content}")
            message["Subject"] = "Thank You for Your Feedback!"
            message["From"] = "ecommerceanalytics117@gmail.com"  # Replace with your sender email
            message["To"] = self.recipient_email

            # SMTP configuration
            with smtplib.SMTP("smtp.gmail.com", 587) as server:  # Replace with your SMTP server
                server.starttls()
                server.login("ecommerceanalytics117@gmail.com", "fedw rten uotw tykx")  # Replace with your login details
                server.sendmail(message["From"], message["To"], message.as_string())
            print("Thank you email sent successfully!")
        except Exception as e:
            print("Failed to send email:", e)

