from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework import permissions, status, serializers
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
import smtplib
from email.mime.text import MIMEText

class EmailSenderView(APIView):

    permission_classes = []

    def post(self, request, *args, **kwargs):
        try:
            # SES SMTP Configuration
            smtp_host = "email-smtp.eu-north-1.amazonaws.com"
            smtp_port = 587
            smtp_username = "AKIAYMLXUUV6TIDS4FOS"
            smtp_password = "BEjUZnrpBljEk3URxUmeh6JyegRMnI5XIzWG6HfqLh9F"

            # # Get data from request
            from_email = "xoftify.global@gmail.com"
            sender = request.data.get('sender')
            inquiry_type = request.data.get('enquiryType')
            frontend = request.data.get('frontend')
            subject = request.data.get('subject')
            recipient = "xoftify.global@gmail.com"

            ### customize email body based on frontend
            if frontend == "etoolsbuddy":
                body = f"""Sender: {sender}
                    Inquiry Type: {inquiry_type}
    
                    Message:
                    {request.data.get('message')}
                    """
            else:
                body = f"""Sender: {sender}
    
                    Message:
                    {request.data.get('message')}
                    """


            # Create MIMEText object
            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = from_email
            msg["To"] = recipient

            # Connect to SES SMTP Server
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                # Start TLS for security
                server.starttls()

                # Login with SES SMTP credentials
                server.login(smtp_username, smtp_password)

                # Send the email
                server.sendmail(from_email, recipient, msg.as_string())

            return JsonResponse({"message": "Email sent successfully."}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
