from typing import List, Optional

from openg2p_fastapi_common.context import dbengine
from openg2p_fastapi_common.service import BaseService
from openg2p_portal_api_common.models.orm.reg_id_orm import RegIDORM, RegIDTypeORM
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from ..models.group import GroupDetail, GroupMember, GroupRegId
from ..models.orm.g2p_group_membership_kind_orm import G2PGroupMembershipKindORM
from ..models.orm.g2p_group_membership_orm import G2PGroupMembershipORM
from ..models.orm.partner_orm import SRPartnerORM


class GroupService(BaseService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.async_session_maker = async_sessionmaker(dbengine.get())


    async def create_group(self, group_details: GroupDetail) -> GroupDetail:
        async with self.async_session_maker() as session:
            new_group = SRPartnerORM(
                name=group_details.name,
                email=group_details.email,
                phone=group_details.phone,
                registration_date=group_details.registration_date,
                address=group_details.address,
                company_id=group_details.company_id,
                is_group=group_details.is_group,
            )
            session.add(new_group)
            # Ensure the ID is generated before committing
            await session.flush()

            # Add members to the group
            if group_details.members:
                for member in group_details.members:
                    member_record = await session.get(SRPartnerORM, member.id)
                    if member_record:
                        session.add(
                            G2PGroupMembershipORM(
                                group=new_group.id, individual=member_record.id
                            )
                        )

            # Add registration IDs to the group
            if group_details.reg_ids:
                for reg_id in group_details.reg_ids:
                    session.add(
                        RegIDORM(
                            partner_id=new_group.id,
                            id_type=reg_id.id_type,
                            value=reg_id.value,
                            expiry_date=reg_id.expiry_date,
                        )
                    )
            await session.commit()
            await session.refresh(new_group)

        return await self.get_group_by_id(new_group.id)

    async def get_groups_by_partner_id(
        self, partner_id: int
    ) -> Optional[List[GroupDetail]]:
        async with self.async_session_maker() as session:

            partner = await session.get(SRPartnerORM, partner_id)
            if not partner:
                return None

            # Fetch all group memberships for the partner
            group_membership_results = await session.execute(
                select(G2PGroupMembershipORM).where(
                    G2PGroupMembershipORM.individual == partner.id
                )
            )
            group_membership_records = group_membership_results.scalars().all()

            groups = []
            for group_membership in group_membership_records:
                # Fetch group details for each membership
                group_record = await session.get(SRPartnerORM, group_membership.group)
                if group_record:
                    groups.append(await self.get_group_by_id(group_record.id))
            return groups

    async def get_group_by_id(self, group_id: int) -> Optional[GroupDetail]:
        async with self.async_session_maker() as session:
            group = await session.get(SRPartnerORM, group_id)
            if not group:
                return None

            members = await self.get_group_members(group_id, session)
            reg_ids = await self.get_group_reg_ids(group_id, session)

            # Fetch membership kinds for each member
            # for member in members:
            #     membership_record = await session.execute(
            #         select(G2PGroupMembershipORM).where(
            #             G2PGroupMembershipORM.individual == member.id
            #         )
            #     )
            #     membership = membership_record.scalars().first()

            #     if membership:
            #         kind_records = await session.execute(
            #             select(G2PGroupMembershipKindORM).where(
            #                 G2PGroupMembershipKindORM.id.in_([kind.id for kind in membership.group_membership_kind])
            #             )
            #         )
            #         member.membership_kinds = kind_records.scalars().all()

            return GroupDetail(
                id=group.id,
                name=group.name,
                email=group.email,
                phone=group.phone,
                registration_date=group.registration_date,
                address=group.address,
                is_registrant=group.is_registrant,
                is_group=group.is_group,
                members=members,
                reg_ids=reg_ids,
            )

    async def update_group(self, update_details: GroupDetail, group_id: int)-> Optional[GroupDetail]:
        async with self.async_session_maker() as session:
            group = await session.get(SRPartnerORM, group_id)
            if not group:
                raise ValueError(f"Group with ID {group_id} not found.")

            # Update group fields
            for field in ["name", "email", "phone", "registration_date", "address", "is_group"]:
                setattr(group, field, getattr(update_details, field))


            # Remove and update members
            await session.execute(delete(G2PGroupMembershipORM).where(G2PGroupMembershipORM.group == group_id))
            if update_details.members:
                session.add_all([
                    G2PGroupMembershipORM(group=group.id, individual=member.id)
                    for member in update_details.members
                ])

            # Remove and update registration IDs
            await session.execute(delete(RegIDORM).where(RegIDORM.partner_id == group_id))
            if update_details.reg_ids:
                session.add_all([
                    RegIDORM(partner_id=group.id, id_type=reg_id.id_type, value=reg_id.value, expiry_date=reg_id.expiry_date)
                    for reg_id in update_details.reg_ids
                ])

            await session.commit()
            await session.refresh(group)

            return await self.get_group_by_id(group.id)

    async def remove_group_by_id(self, group_id: int) -> dict:
        async with self.async_session_maker() as session:

            group = await session.get(SRPartnerORM, group_id)
            if not group:
                raise ValueError(f"Group with ID {group_id} not found.")

            # Unlink the members from the group
            await session.execute(
                delete(G2PGroupMembershipORM).where(G2PGroupMembershipORM.group == group_id)
            )

            # Unlink the registration IDs from the group
            await session.execute(
                delete(RegIDORM).where(RegIDORM.partner_id == group_id)
            )

            await session.delete(group)
            await session.commit()

            return {
                "message":  f"Group with ID {group_id} removed successfully."
            }


    async def get_group_members(self, group_id: int, session) -> List[GroupMember]:
        group_members = []
        group_membership_records = await session.execute(
            select(G2PGroupMembershipORM).where(G2PGroupMembershipORM.group == group_id)
        )
        group_membership_records = group_membership_records.scalars().all()
        for membership in group_membership_records:
            individual_record = await session.get(SRPartnerORM, membership.individual)
            if individual_record:
                group_members.append(
                    GroupMember(
                        id=individual_record.id,
                        name=individual_record.name,
                        email=individual_record.email,
                        phone=individual_record.phone,
                        birthdate=individual_record.birthdate.isoformat(),
                        gender=individual_record.gender,
                        company_id=individual_record.company_id,
                        is_registrant=individual_record.is_registrant,
                        is_group=individual_record.is_group,
                    )
                )
        return group_members

    async def get_group_reg_ids(self, group_id: int, session) -> List[GroupRegId]:
        reg_ids = []
        reg_id_records = await session.execute(
            select(RegIDORM).where(RegIDORM.partner_id == group_id)
        )
        reg_id_records = reg_id_records.scalars().all()

        for record in reg_id_records:
            id_type_name = await RegIDTypeORM.get_id_type_name(record.id_type)

            reg_ids.append(
                GroupRegId(
                    id_type=record.id_type,
                    name=id_type_name.name,
                    value=record.value,
                    expiry_date=record.expiry_date,
                )
            )
        return reg_ids



