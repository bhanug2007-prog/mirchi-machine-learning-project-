import { useEffect, useState } from "react";

const labels = {
  en: {
    title: "Weather and market arrivals", experiment: "Historical experiment", variety: "Chilli variety",
    loading: "Loading market signals…", unavailable: "The historical report is unavailable.",
    arrivals: "Reported arrivals (tonnes)", weather: "Archive weather near Guntur", date: "Date", rain: "Rain (mm)", temperature: "Max (°C)",
    noWeather: "Weather could not be evaluated from the available archive.",
    mae: "Mean absolute error (₹/quintal)", day: "Day", count: "Scored", persistence: "Last price",
    price: "Price only", weatherModel: "Price + weather", arrivalModel: "Price + arrivals", combined: "Price + both",
    notes: "Lower error is better. All columns use the same dates at each horizon. This experiment does not affect the live forecast.",
    started: "Evaluation start", source: "Open-Meteo ERA5 archive", lag: "Weather lag (days)",
  },
  te: {
    title: "వాతావరణం, మార్కెట్ రాకలు", experiment: "చారిత్రక ప్రయోగం", variety: "మిర్చి రకం",
    loading: "మార్కెట్ సమాచారం లోడ్ అవుతోంది…", unavailable: "చారిత్రక నివేదిక అందుబాటులో లేదు.",
    arrivals: "నమోదైన రాకలు (టన్నులు)", weather: "గుంటూరు సమీప చారిత్రక వాతావరణం", date: "తేదీ", rain: "వర్షం (మి.మీ.)", temperature: "గరిష్ఠం (°C)",
    noWeather: "అందుబాటులో ఉన్న ఆర్కైవ్‌తో వాతావరణాన్ని మూల్యాంకనం చేయలేకపోయాము.",
    mae: "సగటు సంపూర్ణ అంచనా లోపం (₹/క్వింటాల్)", day: "రోజు", count: "పరిశీలించినవి", persistence: "చివరి ధర",
    price: "ధర మాత్రమే", weatherModel: "ధర + వాతావరణం", arrivalModel: "ధర + రాకలు", combined: "ధర + రెండూ",
    notes: "లోపం తక్కువగా ఉంటే మంచిది. ప్రతి రోజు పరిధిలో అన్ని మోడళ్లను ఒకే తేదీలపై పోల్చాము. ఈ ప్రయోగం ప్రత్యక్ష అంచనాను ప్రభావితం చేయదు.",
    started: "మూల్యాంకనం ప్రారంభం", source: "Open-Meteo ERA5 ఆర్కైవ్", lag: "వాతావరణ డేటా ఆలస్యం (రోజులు)",
  },
};

const number = (value) => value == null ? "—" : value.toLocaleString("en-IN", { maximumFractionDigits: 2 });

export default function MarketSignals({ api, lang }) {
  const t = labels[lang] || labels.en;
  const [variety, setVariety] = useState("Red New");
  const [report, setReport] = useState(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    fetch(`${api}/api/analysis/market-signals?variety=${encodeURIComponent(variety)}`, { signal: controller.signal })
      .then((response) => {
        if (!response.ok) throw new Error("Report unavailable");
        return response.json();
      })
      .then(setReport)
      .catch((failure) => { if (failure.name !== "AbortError") setError(true); });
    return () => controller.abort();
  }, [api, variety]);

  const columns = [["persistence", t.persistence], ["price", t.price], ["arrivals", t.arrivalModel]];
  if (report?.weather_evaluated) columns.push(["weather", t.weatherModel], ["combined", t.combined]);

  return <section className="rounded-2xl border border-slate-800 bg-[#0F1322] p-5 text-slate-200">
    <div className="flex flex-wrap items-end justify-between gap-3">
      <div>
        <h2 className="text-xl font-bold text-white">{t.title}</h2>
        <p className="mt-1 text-sm text-slate-400">{t.experiment}</p>
      </div>
      <label className="text-sm">{t.variety}
        <select className="ml-2 rounded-lg border border-slate-700 bg-slate-950 px-2 py-1" value={variety} onChange={(event) => {
          setReport(null);
          setError(false);
          setVariety(event.target.value);
        }}>
          <option>Red New</option><option>Red</option>
        </select>
      </label>
    </div>
    {error && <p role="alert" className="mt-3 text-sm text-red-300">{t.unavailable}</p>}
    {!error && !report && <p role="status" className="mt-3 text-sm">{t.loading}</p>}
    {report && <>
      <p className="mt-3 text-sm text-slate-400">{report.market} · {report.variety} · {report.grade} · {report.data_start} – {report.data_end} · {t.started} {report.evaluation_start}</p>
      <div className="mt-4 overflow-x-auto">
        <table className="w-full whitespace-nowrap text-left text-sm">
          <caption className="mb-2 text-left font-semibold">{t.mae}</caption>
          <thead><tr className="border-b border-slate-700">
            <th className="pr-3">{t.day}</th><th className="pr-3">{t.count}</th>
            {columns.map(([key, label]) => <th key={key} className="px-2 py-1 text-right">{label}</th>)}
          </tr></thead>
          <tbody>{report.horizons.map((row) => <tr className="border-b border-slate-800" key={row.day}>
            <th className="pr-3" scope="row">{row.day}</th><td className="pr-3">{row.scored}</td>
            {columns.map(([key]) => <td className="px-2 py-1 text-right tabular-nums" key={key}>{number(row.metrics[key]?.mae)}</td>)}
          </tr>)}</tbody>
        </table>
      </div>
      <p className="mt-2 text-xs text-slate-400">{t.notes}</p>
      <div className="mt-5 grid gap-5 sm:grid-cols-2">
        <div>
          <h3 className="text-sm font-semibold">{t.arrivals}</h3>
          <ul className="mt-2 space-y-1 text-sm text-slate-300">{report.arrival_history.slice(-5).map((row) => (
            <li className="flex justify-between gap-3" key={row.date}><span>{row.date}</span><span>{number(row.tonnes)} t</span></li>
          ))}</ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold">{t.weather}</h3>
          {report.weather_history?.length ? <>
            <p className="mt-1 text-xs text-slate-400">
              <a className="underline" href="https://open-meteo.com/en/docs/historical-weather-api" target="_blank" rel="noreferrer">{t.source}</a> · {t.lag} {report.weather_lag_days}
            </p>
            <table className="mt-2 w-full text-left text-sm text-slate-300">
              <thead><tr><th>{t.date}</th><th>{t.rain}</th><th>{t.temperature}</th></tr></thead>
              <tbody>{report.weather_history.slice(-5).map((row) => <tr key={row.date}><td>{row.date}</td><td>{number(row.rain_mm)}</td><td>{number(row.max_temp_c)}</td></tr>)}</tbody>
            </table>
          </> : <p className="mt-2 text-sm text-slate-400">{t.noWeather}</p>}
        </div>
      </div>
    </>}
  </section>;
}
