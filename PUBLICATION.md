# Publication checklist

The working tree has been cleaned, but the existing Git history still contains
a GitHub access token and a Telegram bot token. Revoke the GitHub token in
GitHub settings and the Telegram token using BotFather before publication.

Do not make the existing remote public or push its old branches/tags to a public
repository until all affected history has been cleaned. Existing remote copies,
pull requests, forks and caches may retain previously committed secrets.

A history-free source archive is available in `public-release.zip` (ignored by
Git). Extract it into a new directory, initialize a new Git repository there,
and publish that repository after reviewing the included source and assets.
The archive excludes local credentials, measurement configurations, recordings,
and files already missing from the working tree. Original local files remain
on disk. The archive is a snapshot; rebuild it after further source changes.
