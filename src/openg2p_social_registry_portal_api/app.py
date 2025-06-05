# ruff: noqa: E402
from .config import Settings

_config = Settings.get_config()

from openg2p_portal_api_common.app import Initializer
from .controllers.draft_group_controller import DraftGroupController
from .services.draft_group_services import DraftGroupService


class Initializer(Initializer):
    def initialize(self, **kwargs):
        super().initialize()

        DraftGroupService()

        DraftGroupController().post_init()

    def migrate_database(self, args):
        super().migrate_database(args)
