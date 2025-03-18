# Import the base class
from openg2p_fastapi_common.context import dbengine
from openg2p_portal_api_common.services.partner_service import PartnerService
from sqlalchemy import (
    text,
)
from sqlalchemy.ext.asyncio import async_sessionmaker

from ..models.orm.partner_orm import PartnerORM


class SocialRegistryPartnerService(PartnerService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def update_household_member_info(self, member_id, data, session=None):
        # Update partner_info with fields from program_registrant_info
        is_create_session = False
        if not session:
            session = async_sessionmaker(dbengine.get())()
            is_create_session = True
        updated_fields = {}
        partner_fields = await self.get_partner_fields()
        for key, value in data.items():
            # if hasattr(partner_info, key) and getattr(partner_info, key) != value:
            # TODO: handle deleted values

            if key in partner_fields and data.get(key, None):
                updated_fields[key] = value
            # TODO: handle the name change
            # name=self.create_partner_process_name(data["family_name"],data["given_name"],data["addl_name"])
        if updated_fields:
            set_clause = ", ".join(
                [f"{key} = '{value}'" for key, value in updated_fields.items()]
            )
            await session.execute(
                text(
                    f"UPDATE {PartnerORM.__tablename__} SET {set_clause} WHERE id='{member_id}'"
                )
            )
            await session.commit()
        if is_create_session:
            await session.close()
        return updated_fields
