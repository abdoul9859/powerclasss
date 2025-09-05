// Lightweight fetch-based HTTP client to replace Axios
(function(){
  const baseURL = (() => {
    try { return window.location.origin || ''; } catch { return ''; }
  })();

  function buildURL(url, params) {
    const hasProto = /^https?:\/\//i.test(url);
    const u = new URL(hasProto ? url : (baseURL + url), baseURL);
    if (params && typeof params === 'object') {
      Object.entries(params).forEach(([k, v]) => {
        if (v === undefined || v === null) return;
        if (Array.isArray(v)) {
          v.forEach(val => u.searchParams.append(k, String(val)));
        } else {
          u.searchParams.set(k, String(v));
        }
      });
    }
    return u.toString();
  }

  function toHeadersObject(headers) {
    const obj = {};
    try {
      for (const [k, v] of headers.entries()) {
        obj[k.toLowerCase()] = v;
      }
    } catch {}
    return obj;
  }

  async function request(config) {
    const { url, method = 'GET', params, data, body, headers = {}, ...rest } = config || {};
    if (!url) throw new Error('http: url is required');

    const fullUrl = buildURL(url, params);
    const isFormData = (typeof FormData !== 'undefined') && (data instanceof FormData || body instanceof FormData);

    const fetchOpts = {
      method,
      credentials: 'include',
      headers: Object.assign({}, headers, isFormData ? {} : { 'Content-Type': 'application/json' }),
      body: undefined,
      ...rest,
    };

    const payload = data !== undefined ? data : body;
    if (payload !== undefined && method.toUpperCase() !== 'GET' && method.toUpperCase() !== 'HEAD') {
      fetchOpts.body = isFormData ? payload : JSON.stringify(payload);
    }

    const resp = await fetch(fullUrl, fetchOpts);

    let respData;
    const ct = resp.headers.get('content-type') || '';
    try {
      if (ct.includes('application/json')) respData = await resp.json();
      else respData = await resp.text();
    } catch { respData = null; }

    const responseLike = {
      data: respData,
      status: resp.status,
      statusText: resp.statusText,
      headers: toHeadersObject(resp.headers),
      config,
      url: fullUrl,
    };

    if (!resp.ok) {
      if (resp.status === 401) {
        // Ne pas appeler logout automatiquement pour éviter d'effacer le cookie
        // sur des 401 transitoires; redirection simple vers /login
        try { window.location.href = '/login'; } catch {}
      }
      const err = new Error('HTTP error ' + resp.status);
      err.response = responseLike;
      throw err;
    }

    return responseLike;
  }

  // Convenience methods
  request.get = (url, config = {}) => request({ ...(config || {}), url, method: 'GET' });
  request.delete = (url, config = {}) => request({ ...(config || {}), url, method: 'DELETE' });
  request.post = (url, data, config = {}) => request({ ...(config || {}), url, method: 'POST', data });
  request.put = (url, data, config = {}) => request({ ...(config || {}), url, method: 'PUT', data });
  request.patch = (url, data, config = {}) => request({ ...(config || {}), url, method: 'PATCH', data });

  // Expose as api and as axios shim
  window.api = request;
  window.axios = request;
})();
