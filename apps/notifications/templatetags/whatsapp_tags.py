from django import template
from apps.notifications.services import build_whatsapp_link, format_fee_reminder_message, format_test_result_message

register = template.Library()

@register.inclusion_tag('notifications/whatsapp_button.html')
def whatsapp_fee_button(fee_structure):
    phone = fee_structure.student.parent_phone_number
    if not phone:
        return {'enabled': False, 'link': ''}
    
    message = format_fee_reminder_message(fee_structure)
    link = build_whatsapp_link(phone, message)
    return {'enabled': True, 'link': link}

@register.inclusion_tag('notifications/whatsapp_button.html')
def whatsapp_result_button(test_result, rank):
    phone = test_result.student.parent_phone_number
    if not phone:
        return {'enabled': False, 'link': ''}
        
    message = format_test_result_message(test_result, rank)
    link = build_whatsapp_link(phone, message)
    return {'enabled': True, 'link': link}
