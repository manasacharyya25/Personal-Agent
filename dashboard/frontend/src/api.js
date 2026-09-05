const API = "/api";

function messageFrom(data) {
  if (typeof data?.detail === "string") return data.detail;
  if (Array.isArray(data?.detail)) return data.detail[0]?.msg || "Invalid request";
  return "Request failed";
}

async function request(path, options = {}) {
  const res = await fetch(`${API}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (res.status === 204) return null;
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(messageFrom(data));
  return data;
}

export const api = {
  categories: () => request("/categories"),
  createCategory: (body) =>
    request("/categories", { method: "POST", body: JSON.stringify(body) }),
  updateCategory: (id, body) =>
    request(`/categories/${id}`, { method: "PATCH", body: JSON.stringify(body) }),
  deleteCategory: (id) => request(`/categories/${id}`, { method: "DELETE" }),

  sources: () => request("/reddit/sources"),
  createSource: (body) =>
    request("/reddit/sources", { method: "POST", body: JSON.stringify(body) }),
  updateSource: (id, body) =>
    request(`/reddit/sources/${id}`, { method: "PATCH", body: JSON.stringify(body) }),
  deleteSource: (id) => request(`/reddit/sources/${id}`, { method: "DELETE" }),

  searches: () => request("/reddit/search-queries"),
  createSearch: (body) =>
    request("/reddit/search-queries", { method: "POST", body: JSON.stringify(body) }),
  updateSearch: (id, body) =>
    request(`/reddit/search-queries/${id}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),
  deleteSearch: (id) => request(`/reddit/search-queries/${id}`, { method: "DELETE" }),

  evaluations: (params = {}) => {
    const query = new URLSearchParams();
    if (params.category_id) query.set("category_id", String(params.category_id));
    if (params.limit) query.set("limit", String(params.limit));
    const suffix = query.toString() ? `?${query}` : "";
    return request(`/evaluations${suffix}`);
  },
};
