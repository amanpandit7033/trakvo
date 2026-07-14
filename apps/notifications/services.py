import urllib.parse
import re

def build_whatsapp_link(phone_number, message):
    """
    Cleans phone number, defaults to +91 for 10 digits, URL-encodes message.
    """
    if not phone_number:
        return ""
    
    # Strip spaces, dashes, parentheses
    cleaned = re.sub(r'[\s\-\(\)]', '', str(phone_number))
    
    # Check if it looks like a 10-digit Indian number without country code
    if len(cleaned) == 10 and cleaned.isdigit():
        cleaned = f"91{cleaned}"
    elif cleaned.startswith('+'):
        cleaned = cleaned[1:] # wa.me prefers number without the +
        
    encoded_message = urllib.parse.quote(message)
    return f"https://wa.me/{cleaned}?text={encoded_message}"

def format_fee_reminder_message(fee_structure):
    institute_name = fee_structure.student.institute.name
    student_name = fee_structure.student.full_name
    amount = fee_structure.total_amount
    paid = fee_structure.total_paid
    balance = fee_structure.balance_due
    due_date = fee_structure.due_date.strftime("%d %b, %Y")
    
    message = (
        f"Dear Parent, this is a reminder from {institute_name} regarding {student_name}'s fee.\n"
        f"Total due: ₹{amount}, Paid: ₹{paid}, Balance: ₹{balance}.\n"
        f"Due date: {due_date}. Please clear the balance at your earliest convenience."
    )
    return message

def format_test_result_message(test_result, rank=None):
    institute_name = test_result.test.batch.institute.name
    student_name = test_result.student.full_name
    test_name = test_result.test.name
    marks = test_result.marks_obtained
    max_marks = test_result.test.max_marks
    
    rank_str = f"{rank}" if rank else "N/A"
    
    message = (
        f"Dear Parent, {student_name}'s result for {test_name} ({institute_name}):\n"
        f"Marks: {marks}/{max_marks}\n"
        f"Rank in batch: {rank_str}\n"
        f"Regards, {institute_name}"
    )
    return message
