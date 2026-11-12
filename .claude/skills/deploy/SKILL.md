---
# .claude/skills/deploy/SKILL.md
name: deploy
description: Test, commit and push trip-signup to main so Railway deploys it. Only runs when the user types /deploy.
disable-model-invocation: true
---

Ship the trip-signup app to production. Notes from the user: $ARGUMENTS

Pushing to main deploys the app to Railway automatically, so treat the push as a production release. Follow these steps in order and stop at the first problem.

1. Check the branch with `git branch --show-current`. If it isn't `main`, stop and tell me.
2. Run the tests with `pipenv run pytest -q`. If any test fails, stop, show me the failures, and don't commit or push.
3. Run `git status`. Never stage `.env`, `signups.db`, or any file that holds a password, key or token. If one of them is staged, stop and tell me.
4. If there are changes, stage the changed files by name and commit them with a short message based on my notes above and the diff. If there is nothing to commit, say so and continue.
5. Show me what will ship: run `git log --oneline origin/main..HEAD` and `git diff --stat origin/main..HEAD`. Then ask "Push these commits to main and deploy?" and wait for me to say yes. If I say anything else, stop.
6. Push with `git push origin main`. If GitHub asks me to sign in, wait while I do it.
7. Report the commits you pushed. Remind me to watch the new deploy in the Railway dashboard and then check the live URL. If the deploy fails, I'll paste the log for you to explain.
