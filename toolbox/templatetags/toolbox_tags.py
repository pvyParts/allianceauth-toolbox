from django.utils.safestring import mark_safe
from django.template.defaulttags import register


@register.simple_tag()
def evename_img(id, name, cat, size):
    if cat == "character":
        return mark_safe("<img class=\"img-circle\" src=\"https://imageserver.eveonline.com/Character/%s_%s.jpg\" style=\"height: %spx; width: %spx;\" title=\"%s\">" % (id, size, size, size, name))

    elif cat == "corporation":
        return mark_safe("<img class=\"img-circle\" src=\"https://imageserver.eveonline.com/Corporation/%s_%s.png\" style=\"height: %spx; width: %spx;\" title=\"%s\">" % (id, size, size, size, name))

    elif cat == "alliance":
        return mark_safe("<img class=\"img-circle\" src=\"https://imageserver.eveonline.com/Alliance/%s_%s.png\" style=\"height: %spx; width: %spx;\" title=\"%s\">" % (id, size, size, size, name))

    else:
        return ""


@register.filter(name='addclass')
def addclass(value, arg):
    return value.as_widget(attrs={'class': arg})
