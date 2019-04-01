from . import urls
from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook


class AllianceMenu(MenuItemHook):
    def __init__(self):
        MenuItemHook.__init__(self, 'Pilot Log',
                              'fa fa-address-book fa-fw',
                              'toolbox:eve_note_board',
                              navactive=['toolbox:eve_note_board'])

    def render(self, request):
        if request.user.has_perm('toolbox.view_eve_notes'):
            return MenuItemHook.render(self, request)
        return ''


class BlacklistMenu(MenuItemHook):
    def __init__(self):
        MenuItemHook.__init__(self, 'Blacklist',
                              'fa fa-ban fa-fw',
                              'toolbox:blacklist',
                              navactive=['toolbox:blacklist'])

    def render(self, request):
        if request.user.has_perm('toolbox.view_eve_blacklist'):
            return MenuItemHook.render(self, request)
        return ''


@hooks.register('menu_item_hook')
def register_menu():
    return AllianceMenu()


@hooks.register('menu_item_hook')
def register_menu():
    return BlacklistMenu()


@hooks.register('url_hook')
def register_url():
    return UrlHook(urls, 'toolbox', r'^toolbox/')