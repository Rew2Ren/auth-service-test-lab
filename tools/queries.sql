-- name: failed_logins_per_user
-- Who is failing to log in, and how often? Spikes can mean brute forcing or a broken client.
SELECT user, COUNT(*) AS failures
FROM events
WHERE event = 'login_failed'
GROUP BY user
ORDER BY failures DESC;

-- name: server_errors
-- Any 5xx response is a defect: the service should never crash on client input.
SELECT line_no, ts, path
FROM events
WHERE status >= 500
ORDER BY line_no;

-- name: session_used_after_logout
-- A session that keeps working after logout means tokens are not being revoked.
SELECT later.line_no, later.user, later.session, later.event
FROM events AS logout_event
JOIN events AS later
  ON later.session = logout_event.session
 AND later.line_no > logout_event.line_no
WHERE logout_event.event = 'logout'
  AND later.status = 200
ORDER BY later.line_no;
