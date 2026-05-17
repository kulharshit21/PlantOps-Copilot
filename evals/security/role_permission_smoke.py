from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    api_root = Path(__file__).resolve().parents[2] / "apps" / "api"
    sys.path.insert(0, str(api_root))

    from fastapi import HTTPException
    from app.core.security import CurrentUser, UserRole
    from app.schemas.work_orders import WorkOrderCreate
    from app.services.work_orders import WorkOrderService

    technician = CurrentUser(
        user_id="tech",
        email="tech@example.com",
        role=UserRole.technician,
        organization_id="demo-org",
        plant_id="chennai-plant-a",
    )
    try:
        WorkOrderService().create(
            WorkOrderCreate(
                asset_id="asset-line-2-spindle",
                title="Unauthorized draft",
                priority="high",
                recommended_action="Should not be allowed.",
            ),
            technician,
        )
    except HTTPException as exc:
        if exc.status_code == 403:
            print("PASS: technician cannot create work-order drafts")
            return 0
    print("FAIL: technician was allowed to create a work-order draft")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
