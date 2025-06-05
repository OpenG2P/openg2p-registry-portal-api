from typing import Annotated

from fastapi import Depends
from openg2p_fastapi_auth.controllers.auth_controller import AuthController
from openg2p_fastapi_common.errors.http_exceptions import UnauthorizedError
from openg2p_portal_api_common.dependencies import JwtBearerAuth
from openg2p_portal_api_common.models.credentials import AuthCredentials

from ..config import Settings
from ..models.group import GroupDetails, GroupMember
from ..services.draft_group_services import DraftGroupService

_config = Settings.get_config()


class DraftGroupController(AuthController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._draft_group_service = DraftGroupService.get_component()

        self.router.prefix = "/sr"
        self.router.tags = ["portal sr"]

        self.router.add_api_route(
            "/group",
            self.create_group,
            responses={200: {"model": GroupDetails}},
            methods=["POST"],
        )
        self.router.add_api_route(
            "/group/member/{id}",
            self.member_addition,
            responses={200: {"model": GroupMember}},
            methods=["POST"],
        )

    @property
    def draft_group_service(self):
        if not self._draft_group_service:
            self._draft_group_service = DraftGroupService.get_component()
        return self._draft_group_service

    async def create_group(
        self,
        group_details: GroupDetails,
        auth: Annotated[AuthCredentials, Depends(JwtBearerAuth())],
    ) -> GroupDetails:
        if not auth.partner_id:
            raise UnauthorizedError("Unauthorized. Partner Not Found in Registry.")

        return await self.draft_group_service.create_group(group_details)

    async def member_addition(
        self,
        id: int,
        group_member: GroupMember,
        auth: Annotated[AuthCredentials, Depends(JwtBearerAuth())],
    ):
        if not auth.partner_id:
            raise UnauthorizedError("Unauthorized. Partner Not Found in Registry.")

        return await self.draft_group_service.add_member_to_group(
            group_id=id, member=group_member
        )
