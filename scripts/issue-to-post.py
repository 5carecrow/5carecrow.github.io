#!/usr/bin/env python3
"""Turn a GitHub issue into a Hugo post.

Driven by .github/workflows/issue-to-post.yml. Only issues opened by
ALLOWED_AUTHORS are converted, so random visitors cannot write to the repo.

Label conventions (case-insensitive for status labels):
  draft / 草稿                -> post is saved as draft (hidden on the site)
  category:xxx / 分类:xxx     -> goes into `categories`
  published / 已发布 / blog   -> status label, ignored as a tag
  any other label             -> goes into `tags`

Environment:
  GITHUB_EVENT_PATH   issue webhook payload (provided by Actions)
  GITHUB_TOKEN        token used to write a status comment back to the issue
  GITHUB_REPOSITORY   owner/repo
  ALLOWED_AUTHORS     comma separated GitHub logins (default: 5carecrow)
  SITE_BASE_URL       public blog URL
  DRY_RUN=1           generate the file but skip git push / API calls
"""

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

ROOT = os.environ.get("GITHUB_WORKSPACE") or os.getcwd()
POSTS_DIR = os.path.join(ROOT, "content", "posts")
REPO = os.environ.get("GITHUB_REPOSITORY", "5carecrow/5carecrow.github.io")
BASE_URL = os.environ.get("SITE_BASE_URL", "https://5carecrow.github.io").rstrip("/")
ALLOWED_AUTHORS = {
    name.strip().lower()
    for name in os.environ.get("ALLOWED_AUTHORS", "5carecrow").split(",")
    if name.strip()
}
STATUS_LABELS = {"draft", "草稿", "published", "已发布", "blog", "博客", "ghzone"}
BOT_MARKER = "<!-- ghzone-issue-bot -->"
CN_TZ = timezone(timedelta(hours=8))
DRY_RUN = os.environ.get("DRY_RUN") == "1"
HANDLED_ACTIONS = {"opened", "edited", "labeled", "unlabeled", "reopened", "deleted"}


def log(message):
    print("[issue-to-post] " + str(message), flush=True)


def yaml_string(value):
    # JSON strings are valid YAML strings, and this escapes quotes/newlines safely.
    return json.dumps(value, ensure_ascii=False)


def format_date(value):
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return dt.astimezone(CN_TZ).isoformat(timespec="seconds")
    except (TypeError, ValueError):
        return datetime.now(CN_TZ).isoformat(timespec="seconds")


def now_cn():
    return datetime.now(CN_TZ).isoformat(timespec="seconds")


def parse_front_matter(text):
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not match:
        return {}
    result = {}
    for line in match.group(1).splitlines():
        field = re.match(r"^([\w-]+):\s*(.*)$", line)
        if not field:
            continue
        key, value = field.group(1), field.group(2).strip()
        if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
            value = value[1:-1]
        result[key] = value
    return result


def find_post(number):
    if not os.path.isdir(POSTS_DIR):
        return None
    for name in sorted(os.listdir(POSTS_DIR)):
        if not name.endswith(".md"):
            continue
        path = os.path.join(POSTS_DIR, name)
        try:
            with open(path, encoding="utf-8") as handle:
                front = parse_front_matter(handle.read())
        except OSError:
            continue
        if str(front.get("issue", "")).strip() == str(number):
            return path
    return None


def parse_labels(labels):
    tags, categories, draft = [], [], False
    for label in labels or []:
        name = (label.get("name") or "").strip()
        if not name:
            continue
        lowered = name.lower()
        if lowered in STATUS_LABELS:
            if lowered in {"draft", "草稿"}:
                draft = True
            continue
        category = re.match(r"^(?:category|分类)\s*[:：]\s*(.+)$", name, re.I)
        if category:
            value = category.group(1).strip()
            if value and value not in categories:
                categories.append(value)
        elif name not in tags:
            tags.append(name)
    return tags, categories, draft


def build_post(title, body, date, lastmod, draft, tags, categories, number, old_front):
    lines = [
        "---",
        "title: " + yaml_string(title),
        # A stable slug keeps the URL unchanged when the issue title is edited.
        "slug: " + yaml_string("issue-" + str(number)),
        "date: " + date,
        "lastmod: " + lastmod,
        "draft: " + ("true" if draft else "false"),
        "issue: " + str(number),
    ]
    description = old_front.get("description", "")
    if description:
        lines.append("description: " + yaml_string(description))
    if tags:
        lines.append("tags: [" + ", ".join(yaml_string(tag) for tag in tags) + "]")
    if categories:
        lines.append(
            "categories: [" + ", ".join(yaml_string(cat) for cat in categories) + "]"
        )
    lines.extend(["---", "", body.rstrip(), ""])
    return "\n".join(lines)


def git(args, check=True):
    return subprocess.run(
        ["git"] + args,
        cwd=ROOT,
        check=check,
        text=True,
        capture_output=True,
    )


def commit_and_push(message):
    if DRY_RUN:
        log("DRY_RUN: skipping commit/push: " + message)
        return
    git(["add", "--", "content/posts"])
    staged = git(["diff", "--cached", "--quiet"], check=False)
    if staged.returncode == 0:
        log("no file changes to commit")
        return
    git(["commit", "-m", message])
    pushed = git(["push"], check=False)
    if pushed.returncode != 0:
        log("git push failed: " + pushed.stderr[-500:])
        raise SystemExit(1)
    log("pushed: " + message)


def github_api(method, path, data=None):
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN is not set")
    headers = {
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "ghzone-issue-to-post",
    }
    payload = None
    if data is not None:
        payload = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(
        "https://api.github.com/repos/" + REPO + "/" + path,
        data=payload,
        headers=headers,
        method=method,
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read()
        return json.loads(raw) if raw else None


def upsert_comment(number, text):
    if DRY_RUN:
        log("DRY_RUN: skipping issue comment")
        return
    try:
        comments = github_api("GET", "issues/%s/comments?per_page=100" % number) or []
        existing = next(
            (item for item in comments if BOT_MARKER in (item.get("body") or "")),
            None,
        )
        body = BOT_MARKER + "\n" + text
        if existing:
            github_api(
                "PATCH", "issues/comments/%s" % existing["id"], {"body": body}
            )
        else:
            github_api("POST", "issues/%s/comments" % number, {"body": body})
        log("issue status comment updated")
    except (urllib.error.URLError, RuntimeError, KeyError, ValueError) as error:
        log("WARN: could not write issue comment: " + str(error))


def main():
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path or not os.path.isfile(event_path):
        log("no webhook payload found, nothing to do")
        return 0
    with open(event_path, encoding="utf-8") as handle:
        payload = json.load(handle)

    issue = payload.get("issue") or {}
    if not issue or "pull_request" in issue:
        log("event is not a plain issue, skipping")
        return 0

    action = payload.get("action")
    if action not in HANDLED_ACTIONS:
        log("action %s not handled, skipping" % action)
        return 0

    number = issue["number"]
    author = (issue.get("user") or {}).get("login", "").lower()
    if author not in ALLOWED_AUTHORS:
        log("author %s is not allowed" % author)
        upsert_comment(number, "⚠️ 只有仓库所有者可以通过 Issue 发文。")
        return 0

    if action == "deleted":
        path = find_post(number)
        if path:
            os.remove(path)
            commit_and_push("remove post from issue #%s" % number)
            log("removed " + path)
        else:
            log("deleted issue has no matching post")
        return 0

    title = (issue.get("title") or "").strip() or "Issue #%s" % number
    body = issue.get("body") or "_（无正文）_"
    created = format_date(issue.get("created_at"))
    # Hugo skips posts dated in the future; a phone with a wrong clock must
    # not silently hide the article.
    if created > now_cn():
        created = now_cn()
    tags, categories, draft = parse_labels(issue.get("labels"))

    path = find_post(number)
    old_front = {}
    if path:
        with open(path, encoding="utf-8") as handle:
            old_front = parse_front_matter(handle.read())
        date = old_front.get("date") or created
        lastmod = now_cn()
        verb = "update"
    else:
        os.makedirs(POSTS_DIR, exist_ok=True)
        path = os.path.join(POSTS_DIR, "%s-issue-%s.md" % (created[:10], number))
        date = created
        lastmod = created
        verb = "add"

    content = build_post(
        title, body, date, lastmod, draft, tags, categories, number, old_front
    )
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)

    url = "%s/posts/issue-%s/" % (BASE_URL, number)
    commit_and_push("%s post from issue #%s: %s" % (verb, number, title))

    if draft:
        note = (
            "📝 已存为草稿（含 `draft` 标签），暂不发布。\n\n"
            "去掉 `draft` 标签即可上线：%s\n\n文件：`content/posts/%s`"
            % (url, os.path.basename(path))
        )
    else:
        note = "✅ 文章已发布：[%s](%s)\n\n约 1 分钟后生效。" % (title, url)
    if DRY_RUN:
        note += "\n\n（本地测试模式，未提交、未触发部署）"
    upsert_comment(number, note)
    log("wrote " + path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
