import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export async function fetchProducts({ skip=0, limit=100, search=null } = {}) {
  const params = { skip, limit };
  if (search) params.search = search;
  const res = await axios.get(`${API_BASE}/products`, { params });
  return res.data;
}

export async function addProduct(urun_kodu, urun_adi) {
  const res = await axios.post(`${API_BASE}/products`, null, { params: { urun_kodu, urun_adi } });
  return res.data;
}

export async function uploadFile(file) {
  const form = new FormData();
  form.append("file", file);
  const res = await axios.post(`${API_BASE}/upload`, form, {
    headers: { "Content-Type": "multipart/form-data" }
  });
  return res.data;
}

export async function deleteProduct(id) {
  const res = await axios.delete(`${API_BASE}/products/${id}`);
  return res.data;
}
