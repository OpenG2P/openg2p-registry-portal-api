from typing import Annotated

from fastapi import Depends
from openg2p_fastapi_common.errors.http_exceptions import UnauthorizedError
from openg2p_portal_api_common.controllers.auth_controller import AuthController
from openg2p_portal_api_common.dependencies import JwtBearerAuth
from openg2p_portal_api_common.models.credentials import AuthCredentials

from ..models.individual import IndividualDetails
from ..services.individual_services import IndividualService


class IndividualController(AuthController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._individual_service = IndividualService.get_component()

        self.router.prefix = "/portal"
        self.router.tags = ["portal"]

        self.router.add_api_route(
            "/individual",
            self.create_individual,
            responses={200: {"model": IndividualDetails}},
            methods=["POST"],
        )

        self.router.add_api_route(
            "/individual/{id}",
            self.get_individual_by_id,
            responses={200: {"model": IndividualDetails}},
            methods=["GET"],
        )

        self.router.add_api_route(
            "/individual/{id}",
            self.update_individual_by_id,
            responses={200: {"model": IndividualDetails}},
            methods=["PUT"],
        )

        self.router.add_api_route(
            "/individual/{id}",
            self.remove_individual_by_id,
            responses={204: {"description": "Individual deleted successfully"}},
            methods=["DELETE"],
        )

    @property
    def individual_service(self):
        if not self._individual_service:
            self._individual_service = IndividualService.get_component()
        return self._individual_service

    async def get_individual_by_id(
        self,
        id: int,
        auth: Annotated[AuthCredentials, Depends(JwtBearerAuth())],
    ):
        if not auth.partner_id:
            raise UnauthorizedError("Unauthorized. Partner Not Found in Registry.")

        return await self.individual_service.get_individual_details_by_partner_id(
            partner_id=id
        )

    async def create_individual(
        self,
        individual_details: IndividualDetails,
        auth: Annotated[AuthCredentials, Depends(JwtBearerAuth())],
    ):
        if not auth.partner_id:
            raise UnauthorizedError("Unauthorized. Partner Not Found in Registry.")

        return await self.individual_service.create_individual(individual_details)

    async def update_individual_by_id(
        self,
        individual_details: IndividualDetails,
        auth: Annotated[AuthCredentials, Depends(JwtBearerAuth())],
    ):
        if not auth.partner_id:
            raise UnauthorizedError("Unauthorized. Partner Not Found in Registry.")

        return await self.individual_service.update_individual_details_by_partner_id(
            individual_details
        )

    async def remove_individual_by_id(
        self,
        id: int,
        auth: Annotated[AuthCredentials, Depends(JwtBearerAuth())],
    ):
        if not auth.partner_id:
            raise UnauthorizedError("Unauthorized. Partner Not Found in Registry.")

        await self.individual_service.remove_individual_details_by_partner_id(
            partner_id=id
        )
        return {"message": "Individual deleted successfully"}
