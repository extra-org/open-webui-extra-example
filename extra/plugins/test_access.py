"""Self-check: only a caller whose token carries the admin role gets through.

Run: python -m plugins.test_access
"""

from plugins.access import AccessResolver


def main():
    resolver = AccessResolver()

    assert resolver.can_access({"auth": {"roles": ("admin",)}}, "admin_management")
    assert not resolver.can_access({"auth": {"roles": ("user",)}}, "admin_management")
    assert not resolver.can_access({"auth": {"roles": ()}}, "admin_management")
    # No auth key at all, or no roles key inside it — same as no role: denied.
    assert not resolver.can_access({}, "admin_management")
    assert not resolver.can_access({"auth": {}}, "admin_management")

    print("ok")


if __name__ == "__main__":
    main()
