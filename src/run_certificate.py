import json
import sys

from certificate_service import WorkOrder, generate_certificate


def main() -> None:
    order = WorkOrder(
        work_order_id=sys.argv[1] if len(sys.argv) > 1 else "WO-1042",
        participant="Northside Facilities",
        technician="Mina Chen",
        dispatch_status="completed",
        photo_count=3,
        follow_up="Send inspection summary to site manager",
    )
    print(json.dumps(generate_certificate(order), indent=2))


if __name__ == "__main__":
    main()

