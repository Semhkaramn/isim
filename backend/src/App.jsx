import React, { useEffect, useState } from "react";
import { fetchProducts, addProduct, uploadFile, deleteProduct } from "./api";

function App(){
  const [products, setProducts] = useState([]);
  const [search, setSearch] = useState("");
  const [urunKodu, setUrunKodu] = useState("");
  const [urunAdi, setUrunAdi] = useState("");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const data = await fetchProducts({ skip: 0, limit: 200, search: search || null });
      setProducts(data);
    } catch (e) {
      alert("Ürünler yüklenemedi: " + e);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function handleAdd(e){
    e.preventDefault();
    try {
      await addProduct(urunKodu, urunAdi);
      setUrunKodu(""); setUrunAdi("");
      await load();
    } catch (e) { alert("Ekleme hatası: " + e); }
  }

  async function handleUpload(e){
    e.preventDefault();
    if(!file){ alert("Dosya seçin"); return; }
    setLoading(true);
    try {
      const res = await uploadFile(file);
      alert(`Eklendi: ${res.added}. Hatalar: ${res.errors?.length || 0}`);
      await load();
    } catch (e) { alert("Yükleme hatası: " + e); }
    finally { setLoading(false); }
  }

  async function handleDelete(id){
    if(!confirm("Silinsin mi?")) return;
    await deleteProduct(id);
    await load();
  }

  return (
    <div className="container mx-auto p-4">
      <header className="mb-6">
        <h1 className="text-2xl font-bold">Ürün Yönetimi</h1>
        <p className="text-sm text-gray-600">Hızlı arama, ekleme, toplu yükleme</p>
      </header>

      <section className="mb-6">
        <div className="flex gap-2">
          <input value={search} onChange={(e)=>setSearch(e.target.value)} placeholder="Ara..." className="border p-2 rounded w-full" />
          <button onClick={load} className="bg-blue-600 text-white px-4 py-2 rounded">Ara / Yenile</button>
        </div>
      </section>

      <section className="mb-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        <form onSubmit={handleAdd} className="p-4 border rounded bg-white">
          <h2 className="font-semibold mb-2">Yeni Ürün Ekle</h2>
          <input required placeholder="Ürün Kodu" value={urunKodu} onChange={(e)=>setUrunKodu(e.target.value)} className="border p-2 rounded w-full mb-2" />
          <input required placeholder="Orijinal Ürün Adı" value={urunAdi} onChange={(e)=>setUrunAdi(e.target.value)} className="border p-2 rounded w-full mb-2" />
          <button className="bg-green-600 text-white px-4 py-2 rounded">Ekle</button>
        </form>

        <form onSubmit={handleUpload} className="p-4 border rounded bg-white">
          <h2 className="font-semibold mb-2">Excel/CSV Yükle</h2>
          <input type="file" accept=".csv,.xls,.xlsx" onChange={(e)=>setFile(e.target.files[0])} className="mb-2" />
          <button className="bg-indigo-600 text-white px-4 py-2 rounded">Yükle</button>
        </form>
      </section>

      <section>
        <div className="bg-white border rounded p-2">
          <h2 className="font-semibold mb-2">Ürünler {loading ? "(yükleniyor...)" : ""}</h2>
          <table className="w-full table-auto">
            <thead>
              <tr className="text-left">
                <th className="p-2">ID</th>
                <th className="p-2">Ürün Kodu</th>
                <th className="p-2">Ürün Adı (SEO)</th>
                <th className="p-2">Model Kodu</th>
                <th className="p-2">İşlemler</th>
              </tr>
            </thead>
            <tbody>
              {products.map(p => (
                <tr key={p.id} className="border-t">
                  <td className="p-2">{p.id}</td>
                  <td className="p-2">{p.urun_kodu}</td>
                  <td className="p-2">{p.urun_adi}</td>
                  <td className="p-2">{p.model_kodu}</td>
                  <td className="p-2">
                    <button onClick={()=>handleDelete(p.id)} className="text-red-600 hover:underline">Sil</button>
                  </td>
                </tr>
              ))}
              {products.length === 0 && (
                <tr><td colSpan="5" className="p-4 text-center text-gray-500">Hiç ürün yok</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

export default App;
