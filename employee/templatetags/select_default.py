from employee.models import StudentStudyRecord

from django.utils.safestring import mark_safe

from django.template import Library

register=Library()


@register.filter
def select_default(val):
    choices_list = StudentStudyRecord.record_choices
    html = ''
    for i in choices_list:
        if val == i[0]:
            html+='<option value=%s checked="checked">%s</option>'%(i[0],i[1])
        else:
            html+='<option value=%s>%s</option>' % (i[0], i[1])

    return mark_safe(html)
