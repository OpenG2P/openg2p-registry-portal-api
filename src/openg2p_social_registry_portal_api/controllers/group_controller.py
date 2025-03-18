from typing import Annotated, List, Optional

from fastapi import Body, Depends
from openg2p_fastapi_common.errors.http_exceptions import UnauthorizedError
from openg2p_portal_api_common.controllers.auth_controller import AuthController
from openg2p_portal_api_common.dependencies import JwtBearerAuth
from openg2p_portal_api_common.models.credentials import AuthCredentials

from ..models.group import GroupDetail
from ..services.group_services import GroupService


class GroupController(AuthController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._group_service = GroupService.get_component()

        self.router.prefix = "/portal"
        self.router.tags = ["portal"]

        self.router.add_api_route(
            "/group",
            self.create_group,
            responses={200: {"model": GroupDetail}},
            methods=["POST"],
        )
        self.router.add_api_route(
            "/groups/{id}",
            self.get_groups_by_partner_id,
            responses={200: {"model": List[GroupDetail]}},
            methods=["GET"],
        )
        self.router.add_api_route(
            "/group/{id}",
            self.get_group_by_id,
            responses={200: {"model": GroupDetail}},
            methods=["GET"],
        )
        self.router.add_api_route(
            "/group/{id}",
            self.update_group_by_id,
            responses={200: {"model": GroupDetail}},
            methods=["PUT"],
        )
        self.router.add_api_route(
            "/group/{id}",
            self.remove_group_by_id,
            responses={204: {"description": "Group deleted successfully"}},
            methods=["DELETE"],
        )

    @property
    def group_service(self):
        if not self._group_service:
            self._group_service = GroupService.get_component()
        return self._group_service

    async def get_groups_by_partner_id(
        self,
        id: int,
        auth: Annotated[AuthCredentials, Depends(JwtBearerAuth())],
    ) -> List[GroupDetail]:
        if not auth.partner_id:
            raise UnauthorizedError("Unauthorized. Partner Not Found in Registry.")

        return await self.group_service.get_groups_by_partner_id(partner_id=id)

    async def get_group_by_id(
        self,
        id: int,
        auth: Annotated[AuthCredentials, Depends(JwtBearerAuth())],
    ) -> GroupDetail:
        if not auth.partner_id:
            raise UnauthorizedError("Unauthorized. Partner Not Found in Registry.")

        group = await self.group_service.get_group_by_id(group_id=id)
        return group

    async def update_group_by_id(
        self,
        id: int,
        auth: Annotated[AuthCredentials, Depends(JwtBearerAuth())],
        updated_group_details: Optional[GroupDetail] = Body(...),
    ) -> Optional[GroupDetail]:
        if not auth.partner_id:
            raise UnauthorizedError("Unauthorized. Partner Not Found in Registry.")
        return await self.group_service.update_group(updated_group_details, group_id=id)

    async def create_group(
        self,
        group_details: GroupDetail,
        auth: Annotated[AuthCredentials, Depends(JwtBearerAuth())],
    ) -> GroupDetail:
        if not auth.partner_id:
            raise UnauthorizedError("Unauthorized. Partner Not Found in Registry.")

        return await self.group_service.create_group(group_details)

    async def remove_group_by_id(
        self,
        id: int,
        auth: Annotated[AuthCredentials, Depends(JwtBearerAuth())],
    ) -> dict:
        if not auth.partner_id:
            raise UnauthorizedError("Unauthorized. Partner Not Found in Registry.")

        return await self.group_service.remove_group_by_id(id)
