// Run this in browser JS context (evaluate) AFTER reading cookies from /data/workspace/credentials/twitter.env
// Do not print cookie values.

(function setXCookies(auth_token, ct0) {
  // Best effort: set for both x.com and twitter.com
  const base = "path=/; secure; samesite=lax";

  if (auth_token) {
    document.cookie = `auth_token=${auth_token}; domain=.x.com; ${base}`;
    document.cookie = `auth_token=${auth_token}; domain=.twitter.com; ${base}`;
  }

  if (ct0) {
    document.cookie = `ct0=${ct0}; domain=.x.com; ${base}`;
    document.cookie = `ct0=${ct0}; domain=.twitter.com; ${base}`;
  }

  return {
    ok: true,
    note: "Cookies set (values not returned). Reload the page."
  };
})
