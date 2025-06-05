from datetime import datetime

from openg2p_fastapi_common.models import BaseORMModel
from sqlalchemy import Column, DateTime, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Define many-to-many association table
draft_g2p_group_membership_draft_g2p_group_membership_kind_rel = Table(
    "draft_g2p_group_membership_draft_g2p_group_membership_kind_rel",
    BaseORMModel.metadata,
    Column(
        "draft_g2p_group_membership_id",
        ForeignKey("draft_g2p_group_membership.id"),
        primary_key=True,
    ),
    Column(
        "draft_g2p_group_membership_kind_id",
        ForeignKey("draft_g2p_group_membership_kind.id"),
        primary_key=True,
    ),
)


class DraftG2PGroupMembershipORM(BaseORMModel):
    __tablename__ = "draft_g2p_group_membership"

    id: Mapped[int] = mapped_column(primary_key=True)
    group: Mapped[int] = mapped_column(ForeignKey("draft_res_partner.id"))
    individual: Mapped[int] = mapped_column(ForeignKey("draft_res_partner.id"))
    create_date: Mapped[datetime] = mapped_column(DateTime(), default=datetime.utcnow)

    group_partner = relationship(
        "DraftPartnerORM", foreign_keys=[group], back_populates="group_memberships"
    )

    individual_partner = relationship(
        "DraftPartnerORM",
        foreign_keys=[individual],
        back_populates="individual_group_memberships",
    )

    # Many-to-Many Relationship with Membership Kind
    group_membership_kind = relationship(
        "DraftG2PGroupMembershipKindORM",
        secondary=draft_g2p_group_membership_draft_g2p_group_membership_kind_rel,
        back_populates="group_memberships",
    )
