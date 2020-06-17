from django import template

from reversion.models import Version

from archival.models import Collection, File, Item, Series
from authority.models import Entity


register = template.Library()


@register.simple_tag()
def get_last_modifier(model_name, obj_id):
    """Returns the user of the most recent Revision for the object specified
    by `model_name` and `obj_id`."""
    models = {
        'collection': Collection,
        'entity': Entity,
        'file': File,
        'item': Item,
        'series': Series,
    }
    model = models[model_name]
    version = Version.objects.get_for_object_reference(model, obj_id)[0]
    return version.revision.user


@register.inclusion_tag('editor/includes/form_facet.html')
def render_facet(facet):
    """Renders the facet `facet`.

    `facet` is a Haystack facet, consisting of four items: the string
    display value, the integer count,.the string link to apply/unapply
    the facet, and a Boolean indicating whether the facet is selected.

    """
    context = {
        'count': facet[1],
        'label': facet[0],
        'link': facet[2],
        'selected': facet[3],
    }
    return context


@register.inclusion_tag('editor/includes/form_field.html')
def render_field(form_field, form_id=None):
    """Renders the form field `form_field`, including label, widget, and
    error messages.

    Due to polymorphism of the AuthorityRecord-based models,
    `form_field` may be an empty string, when the model subclass does
    not have that field. In such cases, do not render anything.

    """
    if form_field == '':
        return {'render': False}
    attrs = {
        'aria-label': 'input field'
    }
    if form_id:
        attrs['form'] = form_id
    if form_field.errors:
        attrs['class'] = ' '.join((form_field.css_classes(), 'error'))
    widget = form_field.as_widget(attrs=attrs)
    return {
        'errors': form_field.errors,
        'form_id': form_id,
        'help_text': form_field.help_text,
        'is_hidden': form_field.is_hidden,
        'label': form_field.label,
        'render': True,
        'required': form_field.field.required,
        'widget': widget,
    }


@register.simple_tag()
def render_field_option(form_field, default):
    """Render a choice form field's selected option, or `default` if none
    match."""
    key = form_field.value()
    for k, v in form_field.field.choices:
        if k == key:
            return v
    return default


@register.inclusion_tag('editor/includes/delete_form_field.html')
def render_form_delete_widget(field):
    """Renders the widget for a form's DELETE `field`."""
    context = {}
    context['widget'] = field.as_widget(
        attrs={'aria-label': 'delete field checkbox'})
    return context
