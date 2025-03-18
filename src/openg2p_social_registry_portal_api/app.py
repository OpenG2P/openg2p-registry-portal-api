# ruff: noqa: E402


from .config import Settings

_config = Settings.get_config()

from openg2p_portal_api_common.app import Initializer
from openg2p_portal_api_common.controllers.auth_controller import AuthController
from openg2p_portal_api_common.controllers.form_controller import FormController
from openg2p_portal_api_common.controllers.oauth_controller import OAuthController
from openg2p_portal_api_common.services.form_service import FormService
from openg2p_portal_api_common.services.partner_service import PartnerService

from .controllers.group_controller import GroupController
from .controllers.individual_controller import IndividualController
from .services.group_services import GroupService
from .services.individual_services import IndividualService


class Initializer(Initializer):
    def initialize(self, **kwargs):
        super().initialize()
        # Initialize all Services, Controllers, any utils here.
        PartnerService()
        FormService()
        GroupService()
        IndividualService()

        GroupController().post_init()
        IndividualController().post_init()
        FormController().post_init()
        AuthController().post_init()
        OAuthController().post_init()

    def migrate_database(self, args):
        super().migrate_database(args)
