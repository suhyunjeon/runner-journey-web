import argparse

from app.bootstrap import init_db
from app.collectors.marathongo import MarathonGoCollector
from app.database import SessionLocal
from app.services.sync_service import SyncService


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync marathon races from external sources.")
    parser.add_argument("--source", choices=["marathongo"], default="marathongo")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    init_db()

    with SessionLocal() as session:
        service = SyncService(session)
        if args.source == "marathongo":
            collector = MarathonGoCollector()
        else:
            raise ValueError(f"Unsupported source: {args.source}")

        result = service.sync_races(collector=collector, limit=args.limit)
        print(result)


if __name__ == "__main__":
    main()
