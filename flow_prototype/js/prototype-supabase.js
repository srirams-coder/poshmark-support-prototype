/**
 * Minimal Supabase REST client for static GitHub Pages demos.
 * GitHub Pages cannot run a database server; the browser calls Supabase HTTPS APIs (CORS-enabled).
 */
(function (global) {
  function cfg() {
    return global.PROTOTYPE_SUPABASE || {};
  }

  function isEnabled() {
    var c = cfg();
    if (!c.enabled) return false;
    var url = String(c.url || '').trim();
    var key = String(c.anonKey || '').trim();
    if (!url || !key) return false;
    if (/YOUR_PROJECT|YOUR_ANON|placeholder/i.test(url + key)) return false;
    return true;
  }

  function authHeaders() {
    var c = cfg();
    var key = String(c.anonKey || '').trim();
    return {
      apikey: key,
      Authorization: 'Bearer ' + key
    };
  }

  function upsertHeaders() {
    var h = authHeaders();
    h['Content-Type'] = 'application/json';
    h.Prefer = 'return=minimal,resolution=merge-duplicates';
    return h;
  }

  function baseUrl() {
    return String(cfg().url || '').replace(/\/$/, '');
  }

  /**
   * @returns {Promise<Array<object>>} Case objects (from JSON payload column)
   */
  function loadCases() {
    var u = baseUrl() + '/rest/v1/prototype_cases?select=id,payload,created_at&order=created_at.desc';
    return fetch(u, { method: 'GET', headers: authHeaders(), mode: 'cors' }).then(function (r) {
      if (!r.ok) return r.text().then(function (t) { throw new Error(t || r.status); });
      return r.json();
    }).then(function (rows) {
      return (rows || []).map(function (row) {
        var p = row.payload;
        if (p == null) return null;
        if (typeof p === 'string') {
          try {
            p = JSON.parse(p);
          } catch (e) {
            return null;
          }
        }
        return p;
      }).filter(Boolean);
    });
  }

  /**
   * Upsert one case (id + full case JSON in payload).
   */
  function upsertCase(caseObj) {
    if (!caseObj || !caseObj.id) return Promise.resolve();
    var row = { id: caseObj.id, payload: caseObj };
    var u = baseUrl() + '/rest/v1/prototype_cases';
    return fetch(u, {
      method: 'POST',
      headers: upsertHeaders(),
      mode: 'cors',
      body: JSON.stringify(row)
    }).then(function (r) {
      if (r.ok || r.status === 201 || r.status === 204) return;
      return r.text().then(function (t) { throw new Error(t || String(r.status)); });
    });
  }

  global.PrototypeSupabase = {
    isEnabled: isEnabled,
    loadCases: loadCases,
    upsertCase: upsertCase
  };
})(typeof window !== 'undefined' ? window : this);
