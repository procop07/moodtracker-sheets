"""
Notification System Module

Provides notification functionality for mood tracking reminders and alerts.
"""

import smtplib
import schedule
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional


class NotificationSystem:
    """Class for managing notifications and reminders."""
    
    def __init__(self, email_config: Dict[str, str] = None):
        """
        Initialize notification system.
        
        Args:
            email_config: Dictionary containing email settings
                - smtp_server: SMTP server address
                - smtp_port: SMTP server port
                - sender_email: Sender email address
                - sender_password: Sender email password
        """
        self.email_config = email_config or {}
        self.scheduled_notifications = []
    
    def send_email_notification(self, recipient: str, subject: str, message: str) -> bool:
        """
        Send email notification.
        
        Args:
            recipient: Recipient email address
            subject: Email subject
            message: Email message body
        
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.email_config:
            print("Email configuration not provided")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config.get('sender_email')
            msg['To'] = recipient
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(
                self.email_config.get('smtp_server'),
                int(self.email_config.get('smtp_port', 587))
            )
            server.starttls()
            server.login(
                self.email_config.get('sender_email'),
                self.email_config.get('sender_password')
            )
            
            text = msg.as_string()
            server.sendmail(
                self.email_config.get('sender_email'),
                recipient,
                text
            )
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def schedule_daily_reminder(self, time_str: str, recipient: str) -> None:
        """
        Schedule daily mood tracking reminder.
        
        Args:
            time_str: Time in format 'HH:MM'
            recipient: Email address to send reminder
        """
        schedule.every().day.at(time_str).do(
            self.send_mood_reminder,
            recipient=recipient
        )
    
    def send_mood_reminder(self, recipient: str) -> bool:
        """
        Send mood tracking reminder.
        
        Args:
            recipient: Email address to send reminder
        
        Returns:
            bool: True if reminder sent successfully
        """
        subject = "Daily Mood Tracking Reminder"
        message = """
Hi there!

This is your daily reminder to track your mood. 

Taking a few minutes to reflect on your mental state can help you:
- Identify patterns in your mood
- Track your progress over time
- Better understand what affects your wellbeing

Please visit your mood tracker to log today's entry.

Take care,
Your Mood Tracker Team
        """
        
        return self.send_email_notification(recipient, subject, message)
    
    def send_weekly_summary(self, recipient: str, mood_data: Dict) -> bool:
        """
        Send weekly mood summary.
        
        Args:
            recipient: Email address to send summary
            mood_data: Dictionary containing mood statistics
        
        Returns:
            bool: True if summary sent successfully
        """
        subject = "Your Weekly Mood Summary"
        
        # Calculate basic statistics
        avg_mood = mood_data.get('average_mood', 'N/A')
        entries_count = mood_data.get('entries_count', 0)
        dominant_mood = mood_data.get('dominant_mood', 'N/A')
        
        message = f"""
Hi there!

Here's your weekly mood summary:

📊 This Week's Statistics:
- Total mood entries: {entries_count}
- Average mood rating: {avg_mood}
- Most common mood: {dominant_mood}

💡 Insights:
- You logged {entries_count} mood entries this week
- Your average mood was {avg_mood} out of 10

Keep up the great work tracking your mental health!

Best regards,
Your Mood Tracker Team
        """
        
        return self.send_email_notification(recipient, subject, message)
    
    def send_alert_notification(self, recipient: str, alert_type: str, data: Dict) -> bool:
        """
        Send alert notification for concerning patterns.
        
        Args:
            recipient: Email address to send alert
            alert_type: Type of alert ('low_mood', 'missing_entries', etc.)
            data: Additional data for the alert
        
        Returns:
            bool: True if alert sent successfully
        """
        if alert_type == 'low_mood':
            subject = "Mood Tracker - Wellness Check"
            message = f"""
Hi,

We noticed your mood has been lower than usual over the past few days.

Average mood: {data.get('avg_mood', 'N/A')}
Duration: {data.get('duration', 'N/A')} days

Remember:
- It's normal to have ups and downs
- Consider reaching out to friends, family, or a mental health professional
- Take care of your basic needs: sleep, nutrition, exercise

You're not alone. Take care of yourself.

Best regards,
Your Mood Tracker Team
            """
            
        elif alert_type == 'missing_entries':
            subject = "Mood Tracker - Missing Entries Reminder"
            message = f"""
Hi,

We noticed you haven't logged your mood in {data.get('days_missing', 'several')} days.

Consistent tracking helps you:
- Identify patterns and triggers
- Monitor your mental health progress
- Make informed decisions about your wellbeing

We're here when you're ready to continue your journey.

Best regards,
Your Mood Tracker Team
            """
        else:
            subject = "Mood Tracker - Notification"
            message = "You have a new notification from your mood tracker."
        
        return self.send_email_notification(recipient, subject, message)
    
    def run_scheduler(self) -> None:
        """
        Run the notification scheduler.
        Call this method to start processing scheduled notifications.
        """
        print("Starting notification scheduler...")
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def clear_scheduled_notifications(self) -> None:
        """
        Clear all scheduled notifications.
        """
        schedule.clear()
        self.scheduled_notifications = []
        print("All scheduled notifications cleared")
    
    def get_scheduled_jobs(self) -> List:
        """
        Get list of scheduled notification jobs.
        
        Returns:
            List of scheduled jobs
        """
        return schedule.jobs
