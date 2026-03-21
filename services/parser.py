import re

class EmailParser:
    @staticmethod
    def categorize(email):
        subject = email.get('subject', '').lower()
        body = email.get('body', '').lower()
        
        if 'deadline' in subject or 'submit' in body or 'due' in body:
            return 'Deadlines'
        elif 'meeting' in subject or 'call' in subject or 'zoom' in body:
            return 'Meetings'
        elif 'reminder' in subject or 'don\'t forget' in body:
            return 'Reminders'
        elif 'important' in subject:
            return 'Important'
        else:
            return 'Updates'

    @staticmethod
    def extract_info(email):
        # Very basic regex-based extraction
        body = email.get('body', '')
        
        # Look for dates (e.g., 20 March)
        date_match = re.search(r'(\d{1,2}\s+[A-Za-z]+)', body)
        deadline = date_match.group(1) if date_match else "No deadline"
        
        # Look for time (e.g., 5 PM)
        time_match = re.search(r'(\d{1,2}\s*(?:AM|PM|am|pm))', body)
        time = time_match.group(1) if time_match else ""
        
        return {
            'deadline': f"{deadline} {time}".strip(),
            'title': email.get('subject', 'No Title')
        }
