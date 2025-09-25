"""
emailtool.py

This MCP tool server sends an email to a specified recipient using Gmail SMTP.
It is exposed as a callable tool via FastMCP.

Author: Anjum Zahid  
Date: June 2025
"""

# Import FastMCP to create an MCP-compatible tool server
from fastmcp import FastMCP

# Import smtplib to send emails using the SMTP protocol
import smtplib

# EmailMessage helps construct well-formatted email content
from email.message import EmailMessage

# os module is used to access environment variables
import os

# load_dotenv loads sensitive credentials from a .env file into environment
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Initialize the MCP server and name it "Email"
mcp = FastMCP("Email")

# Define a tool function to send an email
@mcp.tool()
def send_email(to: str, subject: str, body: str) -> str:
    """
    Send an email using Gmail SMTP.

    Args:
        to (str): Recipient email address (not used here – hardcoded instead).
        subject (str): Email subject.
        body (str): Email message body.

    Returns:
        str: Success or failure message.
    """
    try:
        # Sender email credentials
        sender_email = "sender_email@gmail.com" # add sender email address
        sender_password = os.getenv("EMAIL_APP_PASSWORD")  # Loaded securely from .env

        # Construct the email message
        msg = EmailMessage()
        msg["From"] = sender_email
        msg["To"] = "recipient_email@gmail.com"  # addd recipient email
        msg["Subject"] = subject
        msg.set_content(body)

        # Connect to Gmail SMTP server securely over SSL
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender_email, sender_password)  # Authenticate
            smtp.send_message(msg)  # Send the email

        return "Email sent successfully."
    
    # Handle any errors during email sending
    except Exception as e:
        return f"Failed to send email: {str(e)}"

# Run the MCP tool server on localhost:8001 with a custom path
if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8001, path="/mcp")
