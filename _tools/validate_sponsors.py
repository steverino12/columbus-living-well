#!/usr/bin/env python3
"""Validate sponsors.json. Exit 1 on any problem.

  python3 _tools/validate_sponsors.py              # validate current file
  python3 _tools/validate_sponsors.py --can-add founding "property management"
        # pre-check before sending a Founding Partner payment link
"""
import sys
import sponsors_lib as L


def main(argv):
    data = L.load()
    if len(argv) >= 2 and argv[0] == "--can-add":
        tier = argv[1]
        cat = argv[2].strip().lower() if len(argv) > 2 else ""
        taken = L.founding_categories(data)
        if tier == "founding":
            if len(taken) >= L.MAX_FOUNDING:
                print(f"NO: all {L.MAX_FOUNDING} Founding Partner spots are filled ({', '.join(taken.values())})")
                return 1
            if cat in taken:
                print(f"NO: Founding Partner category '{cat}' is held by {taken[cat]}")
                return 1
        elif tier not in L.TIERS:
            print(f"NO: unknown tier {tier}")
            return 1
        print(f"OK: {tier} available" + (f" in '{cat}'" if cat else "")
              + f" ({L.MAX_FOUNDING - len(taken)} Founding spot(s) open)")
        return 0
    errors = L.validate(data)
    if errors:
        print("sponsors.json INVALID:")
        for e in errors:
            print("  -", e)
        return 1
    a = L.active(data)
    print(f"sponsors.json OK: {len(a)} active sponsor(s), "
          f"{sum(1 for s in a if s['tier'] == 'founding')}/{L.MAX_FOUNDING} Founding Partners")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
