from datetime import date, datetime
from typing import List, Optional

from openg2p_fastapi_common.models import BaseORMModel, BaseORMModelWithId
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..orm.draft_g2p_group_kind_orm import DraftG2PGroupKindORM
from ..orm.draft_g2p_group_membership_orm import DraftG2PGroupMembershipORM
from .draft_reg_id_orm import DraftRegIDORM


class DraftPartnerORM(BaseORMModelWithId):
    __tablename__ = "draft_res_partner"

    name: Mapped[str] = mapped_column()
    family_name: Mapped[str] = mapped_column()
    given_name: Mapped[str] = mapped_column()
    addl_name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column()
    gender: Mapped[str] = mapped_column()
    address: Mapped[str] = mapped_column()
    birthdate: Mapped[date] = mapped_column(Date())
    birth_place: Mapped[str] = mapped_column()
    phone: Mapped[str] = mapped_column()
    company_id: Mapped[Optional[int]] = mapped_column()
    registration_date: Mapped[date] = mapped_column(Date(), default=date.today)
    status: Mapped[str] = mapped_column(String, default="draft")

    create_date: Mapped[datetime] = mapped_column(DateTime(), default=datetime.utcnow)
    write_date: Mapped[datetime] = mapped_column(DateTime(), default=datetime.utcnow)
    type: Mapped[str] = mapped_column(String(), default="contact")
    is_registrant: Mapped[bool] = mapped_column(Boolean(), default=True)
    is_group: Mapped[bool] = mapped_column(Boolean(), default=False)
    active: Mapped[bool] = mapped_column(Boolean(), default=True)

    # Relationship with other table
    reg_ids: Mapped[Optional[List[DraftRegIDORM]]] = relationship(
        back_populates="partner"
    )
    kind: Mapped[int] = mapped_column(
        ForeignKey("draft_g2p_group_kind.id"), nullable=True
    )
    group_kind: Mapped[list["DraftG2PGroupKindORM"]] = relationship(
        "DraftG2PGroupKindORM", back_populates="partners"
    )

    group_memberships: Mapped[list["DraftG2PGroupMembershipORM"]] = relationship(
        "DraftG2PGroupMembershipORM",
        foreign_keys=[DraftG2PGroupMembershipORM.group],
        back_populates="group_partner",
        cascade="all, delete-orphan",
    )

    individual_group_memberships: Mapped[
        list["DraftG2PGroupMembershipORM"]
    ] = relationship(
        "DraftG2PGroupMembershipORM",
        foreign_keys=[DraftG2PGroupMembershipORM.individual],
        back_populates="individual_partner",
        cascade="all, delete-orphan",
    )


class DraftPartnerPhoneNoORM(BaseORMModel):
    __tablename__ = "draft_g2p_phone_number"

    id: Mapped[int] = mapped_column(primary_key=True)
    phone_no: Mapped[str] = mapped_column()
    partner_id: Mapped[int] = mapped_column(ForeignKey("draft_res_partner.id"))
    date_collected: Mapped[date] = mapped_column()

    partner: Mapped[DraftPartnerORM] = relationship()
