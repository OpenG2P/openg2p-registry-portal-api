from typing import List, Optional

from openg2p_fastapi_common.context import dbengine
from openg2p_fastapi_common.service import BaseService
from openg2p_portal_api_common.models.orm.reg_id_orm import RegIDORM, RegIDTypeORM
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from ..models.group import GroupDetail, GroupMember, GroupRegId
from ..models.orm.g2p_group_kind_orm import G2PGroupKindORM
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
                kind=group_details.kind,
                company_id=group_details.company_id,
                is_group=group_details.is_group,
            )
            session.add(new_group)
            await session.flush()

            # Dict to track membership records per individual
            membership_map = {}

            # Add members and their membership kinds
            if group_details.members:
                for member in group_details.members:
                    member_record = await session.get(SRPartnerORM, member.id)
                    if member_record:
                        membership = G2PGroupMembershipORM(
                            group=new_group.id, individual=member_record.id
                        )
                        session.add(membership)
                        await session.flush()

                        # Store membership for later use
                        membership_map[member_record.id] = membership

            # Add membership kinds for members
            if group_details.members:
                for member in group_details.members:
                    if member.id in membership_map and member.membership_kinds:
                        kind_records = await session.execute(
                            select(G2PGroupMembershipKindORM).where(
                                G2PGroupMembershipKindORM.name.in_(
                                    member.membership_kinds
                                )
                            )
                        )
                        kind_objects = kind_records.scalars().all()
                        if kind_objects:
                            membership = membership_map[member.id]
                            # Use session.sync_mode() to update relationship
                            await session.run_sync(
                                lambda s, m=membership, k=kind_objects: m.group_membership_kind.extend(
                                    k
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
            group_kind = await G2PGroupKindORM.get_group_kind_name(group.kind)

            # Fetch membership kinds for each member
            for member in members:
                member.membership_kinds = await self.get_member_membership_kinds(
                    member.id
                )

            return GroupDetail(
                id=group.id,
                name=group.name,
                email=group.email,
                phone=group.phone,
                registration_date=group.registration_date,
                address=group.address,
                kind=group.kind,
                group_kind=group_kind,
                is_registrant=group.is_registrant,
                is_group=group.is_group,
                members=members,
                reg_ids=reg_ids,
            )

    async def update_group(
        self, update_details: GroupDetail, group_id: int
    ) -> Optional[GroupDetail]:
        async with self.async_session_maker() as session:
            group = await session.get(SRPartnerORM, group_id)
            if not group:
                raise ValueError(f"Group with ID {group_id} not found.")

            # Update group fields
            for field in [
                "name",
                "email",
                "phone",
                "registration_date",
                "address",
                "kind",
                "is_group",
            ]:
                setattr(group, field, getattr(update_details, field))

            # Remove and update members
            await session.execute(
                delete(G2PGroupMembershipORM).where(
                    G2PGroupMembershipORM.group == group_id
                )
            )
            if update_details.members:
                for member in update_details.members:
                    membership_entry = G2PGroupMembershipORM(
                        group=group.id, individual=member.id
                    )
                    session.add(membership_entry)

                    # Handle membership kinds
                    if hasattr(member, "membership_kinds") and member.membership_kinds:
                        kind_records = await session.execute(
                            select(G2PGroupMembershipKindORM).where(
                                G2PGroupMembershipKindORM.name.in_(
                                    member.membership_kinds
                                )
                            )
                        )
                        kind_objects = list(kind_records.scalars())

                        # Use session.sync_mode() to update relationship safely
                        await session.flush()
                        await session.run_sync(
                            lambda s, m=membership_entry, k=kind_objects: m.group_membership_kind.extend(
                                k
                            )
                        )

            # Remove and update registration IDs
            await session.execute(
                delete(RegIDORM).where(RegIDORM.partner_id == group_id)
            )
            if update_details.reg_ids:
                session.add_all(
                    [
                        RegIDORM(
                            partner_id=group.id,
                            id_type=reg_id.id_type,
                            value=reg_id.value,
                            expiry_date=reg_id.expiry_date,
                        )
                        for reg_id in update_details.reg_ids
                    ]
                )

            await session.commit()
            await session.refresh(group)

            return await self.get_group_by_id(group.id)

    async def remove_group_by_id(self, group_id: int) -> dict:
        async with self.async_session_maker() as session:
            group = await session.get(SRPartnerORM, group_id)
            if not group:
                raise ValueError(f"Group with ID {group_id} not found.")

            # Unlink membership kinds before removing group memberships
            await session.execute(
                delete(G2PGroupMembershipKindORM).where(
                    G2PGroupMembershipKindORM.id.in_(
                        select(G2PGroupMembershipORM.id).where(
                            G2PGroupMembershipORM.group == group_id
                        )
                    )
                )
            )
            # Unlink the members from the group
            await session.execute(
                delete(G2PGroupMembershipORM).where(
                    G2PGroupMembershipORM.group == group_id
                )
            )

            # Unlink the registration IDs from the group
            await session.execute(
                delete(RegIDORM).where(RegIDORM.partner_id == group_id)
            )

            await session.delete(group)
            await session.commit()

            return {"message": f"Group with ID {group_id} removed successfully."}

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

    async def get_member_membership_kinds(self, member_id: int) -> list[str]:
        async with self.async_session_maker() as session:
            membership_record = await session.execute(
                select(G2PGroupMembershipORM).where(
                    G2PGroupMembershipORM.individual == member_id
                )
            )
            membership = membership_record.scalars().first()

            membership_kinds = []
            if membership:
                # Ensure group_membership_kind is loaded
                await session.refresh(membership, ["group_membership_kind"])

                if membership.group_membership_kind:
                    kind_ids = [kind.id for kind in membership.group_membership_kind]

                    if kind_ids:
                        kind_records = await session.execute(
                            select(G2PGroupMembershipKindORM).where(
                                G2PGroupMembershipKindORM.id.in_(kind_ids)
                            )
                        )
                        membership_kinds = [
                            kind.name for kind in kind_records.scalars()
                        ]

            return membership_kinds

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
