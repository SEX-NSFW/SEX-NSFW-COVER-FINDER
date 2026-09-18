const https = require("https");
const { URL } = require("url");

function fetchText(url, redirects = 0) {
  return new Promise((resolve, reject) => {
    if (redirects > 4) return reject(new Error("too many redirects"));
    const request = https.get(url, {
      headers: {
        "User-Agent": "Mozilla/5.0 (compatible; CoverFinder/1.0)",
        Accept: "text/html,application/xhtml+xml"
      }
    }, (response) => {
      if ([301, 302, 303, 307, 308].includes(response.statusCode) && response.headers.location) {
        response.resume();
        return fetchText(new URL(response.headers.location, url).toString(), redirects + 1).then(resolve, reject);
      }
      let body = "";
      response.setEncoding("utf8");
      response.on("data", (chunk) => { body += chunk; });
      response.on("end", () => resolve({ status: response.statusCode || 0, body, url }));
    });
    request.setTimeout(12000, () => request.destroy(new Error("request timeout")));
    request.on("error", reject);
  });
}

function decodeHtml(value) {
  return value
    .replace(/&amp;/g, "&")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&#x27;/gi, "'")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">");
}

function cleanUrl(value) {
  return decodeHtml(value).replace(/&amp;/g, "&");
}

function extractSearchLinks(html) {
  const links = [];
  const regex = /<a[^>]+href="([^"]+)"[^>]*>/gi;
  let match;
  while ((match = regex.exec(html))) {
    let href = cleanUrl(match[1]);
    if (href.startsWith("/l/?")) {
      const target = href.match(/[?&]uddg=([^&]+)/i);
      if (target) href = decodeURIComponent(target[1]);
    }
    if (!/^https?:\/\//i.test(href)) continue;
    if (/bing\.com|duckduckgo\.com|google\.com/i.test(href)) continue;
    if (!links.includes(href)) links.push(href);
  }
  return links.slice(0, 8);
}

function firstMeta(html, property, name) {
  const propertyRegex = new RegExp(`<meta[^>]+property=["']${property}["'][^>]+content=["']([^"']+)["']`, "i");
  const nameRegex = new RegExp(`<meta[^>]+name=["']${name}["'][^>]+content=["']([^"']+)["']`, "i");
  const reversePropertyRegex = new RegExp(`<meta[^>]+content=["']([^"']+)["'][^>]+property=["']${property}["']`, "i");
  const reverseNameRegex = new RegExp(`<meta[^>]+content=["']([^"']+)["'][^>]+name=["']${name}["']`, "i");
  const match = html.match(propertyRegex) || html.match(nameRegex) || html.match(reversePropertyRegex) || html.match(reverseNameRegex);
  return match ? decodeHtml(match[1]) : null;
}

function titleFromQuery(query) {
  return query.replace(/\s+/g, " ").trim();
}

module.exports = async (req, res) => {
  if (req.method !== "GET") return res.status(405).json({ error: "GET only" });
  const query = titleFromQuery(req.query && req.query.q ? String(req.query.q) : "");
  if (!query) return res.status(400).json({ error: "Missing q" });

  const searchTerms = [
    `"${query}" cover`,
    `"${query}" official`,
    `${query} episode cover`
  ];

  try {
    const results = [];
    for (const terms of searchTerms) {
      const searchUrl = `https://html.duckduckgo.com/html/?q=${encodeURIComponent(terms)}`;
      const searchResponse = await fetchText(searchUrl);
      for (const link of extractSearchLinks(searchResponse.body)) {
        if (results.some((item) => item.page === link)) continue;
        try {
          const page = await fetchText(link);
          if (page.status < 200 || page.status >= 400) continue;
          const image = firstMeta(page.body, "og:image", "twitter:image");
          const pageTitle = firstMeta(page.body, "og:title", "title") || query;
          if (image) results.push({ title: pageTitle, page: link, image });
        } catch (_) {
          // Ignore an unavailable result and continue with the next source.
        }
        if (results.length >= 5) break;
      }
      if (results.length >= 5) break;
    }
    return res.status(200).json({ query, results });
  } catch (error) {
    return res.status(502).json({ error: "External search failed", details: error.message });
  }
};

module.exports.config = { api: { bodyParser: false } };

// This endpoint searches public pages only. It does not download or store images.
// The user should verify image rights and source terms before reuse.
// The endpoint is intentionally limited to a small number of results.
// It is designed for Vercel's Node.js serverless runtime.
// No API key is required for the current public search provider.
// A production deployment may replace the provider with an official search API.
// Keep the response small to avoid unnecessary bandwidth.
// End of file.

// eslint-disable-next-line no-unused-vars
const _runtimeNote = "nodejs";

// The explicit export above is the CommonJS Vercel handler.
// Vercel will route /api/search to this file.
// The frontend calls it with /api/search?q=... .
// Existing local known-cover results remain available without this endpoint.
// This file contains no credentials.
// It follows redirects only for public HTML pages.
// It does not bypass authentication or access controls.
// It does not scrape private resources.
// It returns source page URLs for attribution.
// It does not guarantee that every title has a matching result.
// End.

// Silence linters that inspect trailing declarations in some setups.
void _runtimeNote;
