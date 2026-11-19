import pytest

from shop import symphony

repo = symphony.checkout()


@pytest.mark.skipif(repo is None, reason="no symphony checkout (set SYMPHONY_DIR)")
def test_every_symphony_link_resolves():
    have = symphony.tracked_paths(repo)
    dead = [f"{md.relative_to(symphony.build.ROOT)}: {p}" for md, p in symphony.links() if p not in have]
    assert not dead, "symphony paths gone from main (git -C $SYMPHONY_DIR fetch, then fix the link):\n" + "\n".join(dead)


def test_every_symphony_line_links_or_says_none_yet():
    bare = [slug for slug, line in symphony.index() if not symphony.LINK.search(line) and line.strip() != "none yet"]
    assert not bare, f"Symphony: line with no symphony link: {bare}"
