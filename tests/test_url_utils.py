import pytest

from plugin.commands.open_git_repo_on_web import remote_uri_to_web_url


@pytest.mark.parametrize(
    ("uri", "expected"),
    [
        # SSH GitHub
        (
            "git@github.com:jfcherng-sublime/ST-CommandAndMenu.git",
            "https://github.com/jfcherng-sublime/ST-CommandAndMenu",
        ),
        # SSH GitLab
        (
            "git@gitlab.com:user/project.git",
            "https://gitlab.com/user/project",
        ),
        # SSH Bitbucket
        (
            "git@bitbucket.org:user/repo.git",
            "https://bitbucket.org/user/repo",
        ),
        # Already HTTPS — returned unchanged
        (
            "https://github.com/user/repo",
            "https://github.com/user/repo",
        ),
        # Already HTTP — returned unchanged
        (
            "http://internal.git/repo",
            "http://internal.git/repo",
        ),
        # No .git suffix — still works
        (
            "git@github.com:user/repo",
            "https://github.com/user/repo",
        ),
        # Unknown scheme — returns None
        ("svn+ssh://example.com/repo", None),
        ("file:///local/repo", None),
    ],
)
def test_remote_uri_to_web_url(uri: str, expected: str | None) -> None:
    assert remote_uri_to_web_url(uri, rules=[]) == expected


def test_remote_uri_to_web_url_user_rule() -> None:
    rules = [{"search": r"^git@internal\.corp:(.+)\.git$", "replace": r"https://internal.corp/\1"}]
    result = remote_uri_to_web_url("git@internal.corp:team/project.git", rules=rules)
    assert result == "https://internal.corp/team/project"
