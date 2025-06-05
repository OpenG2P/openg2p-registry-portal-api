from datetime import datetime
from typing import Optional

from openg2p_fastapi_common.models import BaseORMModel
from openg2p_portal_api_common.models.orm.reg_id_orm import RegIDTypeORM
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class DraftRegIDORM(BaseORMModel):
    __tablename__ = "draft_g2p_reg_id"

    id: Mapped[int] = mapped_column(primary_key=True)
    partner_id: Mapped[int] = mapped_column(ForeignKey("draft_res_partner.id"))
    id_type: Mapped[Optional[int]] = mapped_column()
    value: Mapped[str] = mapped_column()
    expiry_date: Mapped[Optional[datetime]] = mapped_column(DateTime())

    partner = relationship("DraftPartnerORM", back_populates="reg_ids")


class DraftRegIDTypeORM(RegIDTypeORM):
    __tablename__ = RegIDTypeORM.__tablename__
    pass
