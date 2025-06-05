from openg2p_fastapi_common.models import BaseORMModel
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..orm.draft_g2p_group_membership_orm import (
    draft_g2p_group_membership_draft_g2p_group_membership_kind_rel,
)


class DraftG2PGroupMembershipKindORM(BaseORMModel):
    __tablename__ = "draft_g2p_group_membership_kind"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()

    # Many-to-Many Relationship with Group Membership
    group_memberships = relationship(
        "DraftG2PGroupMembershipORM",
        secondary=draft_g2p_group_membership_draft_g2p_group_membership_kind_rel,
        back_populates="group_membership_kind",
    )
