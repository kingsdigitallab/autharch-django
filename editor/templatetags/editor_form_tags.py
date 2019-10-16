from django import template


register = template.Library()


@register.inclusion_tag('editor/includes/form_field.html')
def render_field(form_field):
    """Renders the form field `form_field`, including label, widget, and
    error messages.

    Due to polymorphism, `form_field` may be an empty string, when the
    model subclass does not have that field. In such cases, do not
    render anything.

    """
    if form_field == '':
        return {'render': False}
    if form_field.errors:
        widget = form_field.as_widget(attrs={
            'class': ' '.join((form_field.css_classes(), 'error'))
        })
    else:
        widget = form_field.as_widget()
    return {
        'errors': form_field.errors,
        'help_text': form_field.help_text,
        'is_hidden': form_field.is_hidden,
        'label': form_field.label,
        'render': True,
        'required': form_field.field.required,
        'widget': widget,
    }
