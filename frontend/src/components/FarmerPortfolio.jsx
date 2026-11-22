import { useEffect, useState } from "react";

const labels = {
  en: {
    title: "My chilli inventory", login: "Sign in", register: "Create account", logout: "Sign out",
    username: "Username", password: "Password (at least 12 characters)", loading: "Loading…",
    error: "Could not complete the request. Check your details and try again.",
    invalidLogin: "Invalid username or password.", duplicate: "That username is already taken.",
    refresh: "Refresh quotes", add: "Add harvest lot", edit: "Edit", save: "Save lot", cancel: "Cancel",
    remove: "Remove", confirm: "Remove this harvest lot and its alerts?", empty: "Add your first harvest lot.",
    variety: "Chilli variety", market: "Market", location: "Village or pincode", quintals: "Quantity (quintals)",
    target_price: "Target price (₹/quintal)", storage_type: "Storage type", stored_since: "Storage start date",
    storage_rate: "Storage cost (₹/quintal/day)", days: "Days stored", cost: "Estimated storage cost",
    price: "Latest quote", value: "Estimated gross market value", stale: "Historical quote",
    noQuote: "No comparable quote available", alerts: "Target price alerts", noAlerts: "No target prices reached yet.",
    alertHint: "Alerts use observed quotes up to three calendar days old and appear here when a target is reached.",
  },
  te: {
    title: "నా మిర్చి నిల్వలు", login: "ప్రవేశించండి", register: "ఖాతా సృష్టించండి", logout: "నిష్క్రమించండి",
    username: "వినియోగదారు పేరు", password: "పాస్‌వర్డ్ (కనీసం 12 అక్షరాలు)", loading: "లోడ్ అవుతోంది…",
    error: "అభ్యర్థన పూర్తి కాలేదు. వివరాలు సరిచూసి మళ్లీ ప్రయత్నించండి.",
    invalidLogin: "వినియోగదారు పేరు లేదా పాస్‌వర్డ్ తప్పు.", duplicate: "ఈ వినియోగదారు పేరు ఇప్పటికే ఉంది.",
    refresh: "ధరలు నవీకరించండి", add: "పంట నిల్వ జోడించండి", edit: "సవరించండి", save: "దాచండి", cancel: "రద్దు",
    remove: "తొలగించండి", confirm: "ఈ నిల్వను, దాని హెచ్చరికలను తొలగించాలా?", empty: "మీ మొదటి పంట నిల్వను జోడించండి.",
    variety: "మిర్చి రకం", market: "మార్కెట్", location: "గ్రామం లేదా పిన్‌కోడ్", quintals: "పరిమాణం (క్వింటాళ్లు)",
    target_price: "లక్ష్య ధర (₹/క్వింటాల్)", storage_type: "నిల్వ రకం", stored_since: "నిల్వ ప్రారంభ తేదీ",
    storage_rate: "నిల్వ ఖర్చు (₹/క్వింటాల్/రోజు)", days: "నిల్వ రోజులు", cost: "అంచనా నిల్వ ఖర్చు",
    price: "తాజా ధర", value: "అంచనా స్థూల మార్కెట్ విలువ", stale: "పాత ధర",
    noQuote: "సరిపోలే ధర అందుబాటులో లేదు", alerts: "లక్ష్య ధర హెచ్చరికలు", noAlerts: "ఇంకా ఏ లక్ష్య ధర చేరలేదు.",
    alertHint: "గరిష్ఠంగా మూడు రోజుల నాటి నమోదైన ధర లక్ష్యాన్ని చేరితే ఇక్కడ హెచ్చరిక కనిపిస్తుంది.",
  },
};

const inputClass = "w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-white";
const panel = "rounded-2xl border border-slate-800 bg-[#0F1322] p-5";
const button = "rounded-lg border border-slate-700 px-3 py-2 text-sm font-semibold hover:bg-slate-800 disabled:opacity-50";
const fields = {
  variety: "text", market: "text", location: "text", quintals: "number", target_price: "number",
  storage_type: "text", stored_since: "date", storage_rate: "number",
};
const defaultLot = { variety: "", market: "Guntur APMC", location: "", quintals: "", target_price: "",
  storage_type: "", stored_since: "", storage_rate: "" };
const rupees = (value) => new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 2 }).format(value);

export default function FarmerPortfolio({ api, lang, varieties }) {
  const t = labels[lang] || labels.en;
  const [token, setToken] = useState(() => sessionStorage.getItem("mm_portfolio_token"));
  const [registering, setRegistering] = useState(false);
  const [data, setData] = useState({ lots: [], alerts: [] });
  const [draft, setDraft] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  async function request(path, { method = "GET", body } = {}) {
    const response = await fetch(`${api}/api/portfolio${path}`, {
      method,
      headers: { ...(token && { Authorization: `Bearer ${token}` }), ...(body && { "Content-Type": "application/json" }) },
      body: body ? JSON.stringify(body) : undefined,
      cache: "no-store",
    });
    if (!response.ok) {
      if (response.status === 401 && token) clearSession();
      throw new Error(response.status === 409 ? "duplicate" : (response.status === 401 && !token ? "invalidLogin" : "error"));
    }
    return response.json();
  }

  function clearSession() {
    sessionStorage.removeItem("mm_portfolio_token");
    setToken(null);
    setData({ lots: [], alerts: [] });
    setDraft(null);
  }

  async function run(action) {
    setBusy(true);
    setError(null);
    try { await action(); }
    catch (failure) { setError(failure.message); }
    finally { setBusy(false); }
  }

  async function refresh() { setData(await request("")); }

  useEffect(() => {
    if (token) run(refresh);
  }, [token]);

  function authenticate(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const credentials = Object.fromEntries(new FormData(form));
    run(async () => {
      if (registering) await request("/register", { method: "POST", body: credentials });
      const result = await request("/login", { method: "POST", body: credentials });
      form.reset();
      sessionStorage.setItem("mm_portfolio_token", result.token);
      setToken(result.token);
    });
  }

  function edit(lot) {
    setDraft({ id: lot.id, ...Object.fromEntries(Object.keys(fields).map((key) => [key, lot[key]])) });
  }

  function save(event) {
    event.preventDefault();
    const { id, ...body } = draft;
    for (const key of ["quintals", "target_price", "storage_rate"]) body[key] = Number(body[key]);
    run(async () => {
      await request(id ? `/lots/${id}` : "/lots", { method: id ? "PUT" : "POST", body });
      setDraft(null);
      await refresh();
    });
  }

  return (
    <section className="space-y-4" aria-busy={busy}>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-2xl font-bold text-white">{t.title}</h2>
        {token && <div className="flex flex-wrap gap-2">
          <button className={button} disabled={busy} onClick={() => run(refresh)}>{t.refresh}</button>
          <button className={button} disabled={busy} onClick={() => setDraft({ ...defaultLot })}>{t.add}</button>
          <button className={button} disabled={busy} onClick={() => run(async () => {
            await request("/logout", { method: "POST" });
            clearSession();
          })}>{t.logout}</button>
        </div>}
      </div>
      {busy && <p role="status" className="text-sm text-slate-300">{t.loading}</p>}
      {error && <p role="alert" className="text-sm text-red-300">{t[error] || t.error}</p>}
      {!token && <form onSubmit={authenticate} className={`${panel} max-w-md space-y-3`}>
        <label className="block">{t.username}<input className={inputClass} name="username" autoComplete="username" required pattern="[A-Za-z0-9_]{3,32}" /></label>
        <label className="block">{t.password}<input className={inputClass} type="password" name="password" autoComplete={registering ? "new-password" : "current-password"} required minLength={12} maxLength={128} /></label>
        <div className="flex flex-wrap gap-2">
          <button className={`${button} text-emerald-300`} disabled={busy}>{registering ? t.register : t.login}</button>
          <button className={button} type="button" disabled={busy} onClick={() => { setRegistering(!registering); setError(null); }}>{registering ? t.login : t.register}</button>
        </div>
      </form>}
      {token && <>
        {draft && <form onSubmit={save} className={`${panel} space-y-4`}>
          <div className="grid gap-3 sm:grid-cols-2">
            {Object.entries(fields).map(([key, type]) => (
              <label key={key} className="block text-sm">{t[key]}
                <input className={inputClass} type={type} value={draft[key]} required maxLength={100}
                  list={key === "variety" ? "portfolio-varieties" : undefined}
                  min={type === "number" ? (key === "storage_rate" ? 0 : 0.01) : undefined}
                  step={type === "number" ? "0.01" : undefined}
                  onChange={(event) => setDraft({ ...draft, [key]: event.target.value })} />
              </label>
            ))}
            <datalist id="portfolio-varieties">{varieties.map((value) => <option key={value} value={value} />)}</datalist>
          </div>
          <div className="flex gap-2">
            <button className={`${button} text-emerald-300`} disabled={busy}>{t.save}</button>
            <button type="button" className={button} onClick={() => setDraft(null)}>{t.cancel}</button>
          </div>
        </form>}
        {!data.lots.length && !busy && <p className="text-slate-400">{t.empty}</p>}
        <div className="grid gap-4 md:grid-cols-2">
          {data.lots.map((lot) => <article key={lot.id} className={panel}>
            <h3 className="font-bold text-white">{lot.variety} · {lot.quintals} qtl</h3>
            <p className="text-sm text-slate-300">{lot.location} · {lot.market} · {lot.storage_type}</p>
            <dl className="mt-3 space-y-1 text-sm text-slate-300">
              <div><dt className="inline font-medium">{t.target_price} </dt><dd className="inline">{rupees(lot.target_price)}</dd></div>
              <div><dt className="inline font-medium">{t.days} </dt><dd className="inline">{lot.storage_days}</dd></div>
              <div><dt className="inline font-medium">{t.cost} </dt><dd className="inline">{rupees(lot.storage_cost)}</dd></div>
              {lot.quote_price != null && <>
                <div><dt className="inline font-medium">{lot.quote_fresh ? t.price : t.stale} </dt><dd className="inline">{rupees(lot.quote_price)}/qtl · {lot.quote_date}</dd></div>
                <div><dt className="inline font-medium">{t.value} </dt><dd className="inline">{rupees(lot.market_value)}</dd></div>
              </>}
            </dl>
            {lot.quote_price == null && <p className="mt-2 text-sm text-slate-400">{t.noQuote}</p>}
            <div className="mt-3 flex gap-2">
              <button className={button} disabled={busy} onClick={() => edit(lot)}>{t.edit}</button>
              <button className={`${button} text-red-300`} disabled={busy} onClick={() => {
                if (window.confirm(t.confirm)) run(async () => {
                  await request(`/lots/${lot.id}`, { method: "DELETE" });
                  if (draft?.id === lot.id) setDraft(null);
                  await refresh();
                });
              }}>{t.remove}</button>
            </div>
          </article>)}
        </div>
        <div className={panel}>
          <h3 className="font-bold text-white">{t.alerts}</h3>
          <p className="mt-1 text-sm text-slate-400">{t.alertHint}</p>
          {!data.alerts.length ? <p className="mt-2 text-sm text-slate-300">{t.noAlerts}</p> : <ul className="mt-2 space-y-2 text-sm">
            {data.alerts.map((alert) => <li key={alert.id} className="text-emerald-300">
              {alert.variety} · {alert.market} · {alert.quote_date} · {rupees(alert.price)} ≥ {rupees(alert.target_price)}/qtl
            </li>)}
          </ul>}
        </div>
      </>}
    </section>
  );
}
