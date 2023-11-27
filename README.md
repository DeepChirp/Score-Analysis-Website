# A website for score analysis

---

Deployed to: https://groupwork.xiran.xyz

Pushing to main branch will trigger a redeploy of the server using github actions and webhook, so changes can be seen in "realtime" (Although **queued** github actions may impose a large delay).

You can manually trigger redeploy by visiting: http://groupwork.xiran.xyz:9000/hooks/75c04a03-a33a-4468-a44a-4f406cd5ca78

- backend: backend code (python + flask)
- frontend:
  - js/
    - main.js (for common js code using in every page.)
    - index.js (for dedicate js code using in a given page.)
    - xxx.js
  - css/
    - main.css (for common css style using in every page.)
    - index.css
    - xxx.css
  - index.html
  - xxx.html
