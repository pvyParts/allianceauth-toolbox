from . import urls
from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook


class AllianceMenu(MenuItemHook):
    def __init__(self):
        MenuItemHook.__init__(self, 'Pilot Log',
                              'fas fa-address-book fa-fw',
                              'toolbox:eve_note_board',
                              navactive=['toolbox:eve_note_board'])

    def render(self, request):
        if request.user.has_perm('toolbox.view_eve_notes') or request.user.has_perm('toolbox.view_basic_eve_notes'):
            return MenuItemHook.render(self, request)
        return ''


class BlacklistMenu(MenuItemHook):
    def __init__(self):
        MenuItemHook.__init__(self, 'Blacklist',
                              'fas fa-ban fa-fw',
                              'toolbox:blacklist',
                              navactive=['toolbox:blacklist'])

    def render(self, request):
        if request.user.has_perm('toolbox.view_eve_blacklist'):
            return MenuItemHook.render(self, request)
        return ''


class TaxMenu(MenuItemHook):
    def __init__(self):
        MenuItemHook.__init__(self, 'Moon Taxes',
                              'fas fa-moon fa-fw',
                              'toolbox:view_character_mining',
                              navactive=['toolbox:view_character_mining'])

    def render(self, request):
        if request.user.has_perm('toolbox.view_own_character_mining'):
            return MenuItemHook.render(self, request)
        return ''

class TaxAdminMenu(MenuItemHook):
    def __init__(self):
        MenuItemHook.__init__(self, 'Moon Tax Admin',
                              'fas fa-moon fa-fw',
                              'toolbox:admin_character_mining',
                              navactive=['toolbox:admin_character_mining'])

    def render(self, request):
        if request.user.has_perm('toolbox.admin_alliance_mining') or request.user.has_perm('toolbox.admin_corporation_mining'):
            return MenuItemHook.render(self, request)
        return ''


@hooks.register('menu_item_hook')
def register_menu():
    return TaxMenu()

@hooks.register('menu_item_hook')
def register_menu():
    return TaxAdminMenu()

@hooks.register('menu_item_hook')
def register_menu():
    return AllianceMenu()


@hooks.register('menu_item_hook')
def register_menu():
    return BlacklistMenu()


@hooks.register('url_hook')
def register_url():
    return UrlHook(urls, 'toolbox', r'^toolbox/')
