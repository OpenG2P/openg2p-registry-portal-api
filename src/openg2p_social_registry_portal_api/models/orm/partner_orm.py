from openg2p_portal_api_common.models.orm.partner_orm import PartnerORM as BaseORM
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..orm.g2p_group_membership_orm import G2PGroupMembershipORM


class SRPartnerORM(BaseORM):

    # Many-to-one relationship with G2PGroupKindORM
    # kind: Mapped[int] = mapped_column(ForeignKey("g2p_group_kind.id"), nullable=True)
    # group_kind = relationship("G2PGroupKindORM", back_populates="partners")


    # Define relationships with groups and individuals
    group_memberships: Mapped[list["G2PGroupMembershipORM"]] = relationship(
        "G2PGroupMembershipORM",
        foreign_keys=[G2PGroupMembershipORM.group],
        back_populates="group_partner",
        cascade="all, delete-orphan",
    )

    individual_group_memberships: Mapped[list["G2PGroupMembershipORM"]] = relationship(
        "G2PGroupMembershipORM",
        foreign_keys=[G2PGroupMembershipORM.individual],
        back_populates="individual_partner",
        cascade="all, delete-orphan",
    )
