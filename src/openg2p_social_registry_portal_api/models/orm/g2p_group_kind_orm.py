from typing import List

from openg2p_fastapi_common.models import BaseORMModel
from sqlalchemy.orm import Mapped, mapped_column, relationship

# from ..orm.partner_orm import SRPartnerORM


class G2PGroupKindORM(BaseORMModel):
    __tablename__ = "g2p_group_kind"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()

    # One-to-Many Relationship: A kind has multiple partners
    # partners = relationship("SRPartnerORM", back_populates="group_kind")
