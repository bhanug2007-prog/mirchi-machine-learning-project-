import { useState } from "react";

const copy = {
  en: {
    title: "Agricultural guidance", intro: "Search official guidance on eNAM registration, payments, and handling dried chilli.",
    label: "Your question", ask: "Find guidance", loading: "Searching official sources…",
    documents: "What documents do I need to register at Guntur mandi?",
    storage: "How should I store dried Teja S17 chilli?",
    missing: "The available sources don’t answer this question. Try asking about eNAM registration, eNAM payments, or dried chilli handling.",
    failed: "The guidance service couldn’t respond. Please try again.", published: "Published", reviewed: "Source reviewed",
    source: "Open official source",
  },
  te: {
    title: "వ్యవసాయ మార్గదర్శకాలు", intro: "eNAM నమోదు, చెల్లింపులు, ఎండు మిర్చి నిర్వహణపై అధికారిక సూచనలు వెతకండి.",
    label: "మీ ప్రశ్న", ask: "సూచనలు వెతకండి", loading: "అధికారిక మూలాలను వెతుకుతున్నాము…",
    documents: "గుంటూరు మండీలో నమోదు కోసం ఏ పత్రాలు అవసరం?",
    storage: "ఎండు తేజ S17 మిర్చిని ఎలా నిల్వ చేయాలి?",
    missing: "అందుబాటులో ఉన్న మూలాల్లో ఈ ప్రశ్నకు సమాధానం లేదు. eNAM నమోదు, చెల్లింపులు లేదా ఎండు మిర్చి నిర్వహణ గురించి అడగండి.",
    failed: "సూచనల సేవ స్పందించలేదు. మళ్లీ ప్రయత్నించండి.", published: "ప్రచురణ", reviewed: "మూలం పరిశీలించిన తేదీ",
    source: "అధికారిక మూలాన్ని తెరవండి",
  },
};

export default function AgriculturalKnowledge({ api, lang }) {
  const t = copy[lang] || copy.en;
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [failed, setFailed] = useState(false);

  async function ask(event) {
    event.preventDefault();
    if (question.trim().length < 3 || busy) return;
    setBusy(true);
    setFailed(false);
    setResult(null);
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 75000);
    try {
      const response = await fetch(`${api}/api/knowledge/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: question.trim(), language: lang }),
        signal: controller.signal,
      });
      if (!response.ok) throw new Error("Guidance request failed");
      setResult(await response.json());
    } catch {
      setFailed(true);
    } finally {
      clearTimeout(timeout);
      setBusy(false);
    }
  }

  return (
    <section className="mx-auto max-w-4xl space-y-4" aria-busy={busy}>
      <div className="rounded-2xl border border-slate-800 bg-[#0F1322] p-5 sm:p-7">
        <h2 className="text-2xl font-bold text-white">{t.title}</h2>
        <p className="mt-2 text-sm text-slate-300">{t.intro}</p>
        <div className="mt-4 flex flex-wrap gap-2">
          {[t.documents, t.storage].map((example) => <button key={example} type="button" disabled={busy}
            className="rounded-xl border border-slate-700 px-3 py-2 text-left text-xs text-emerald-300 hover:bg-slate-800"
            onClick={() => setQuestion(example)}>{example}</button>)}
        </div>
        <form className="mt-4 flex flex-col items-start gap-3" onSubmit={ask}>
          <label className="w-full text-sm text-slate-200">{t.label}
            <textarea rows={2} value={question} onChange={(event) => setQuestion(event.target.value)}
              maxLength={400} required disabled={busy}
              className="mt-1 block w-full rounded-xl border border-slate-700 bg-slate-950 p-3 text-white" />
          </label>
          <button disabled={busy || question.trim().length < 3} className="rounded-xl bg-emerald-400 px-4 py-2 font-semibold text-slate-950 disabled:opacity-50">{t.ask}</button>
        </form>
      </div>
      <div aria-live="polite" className="space-y-3">
        {busy && <p role="status" className="text-sm text-slate-300">{t.loading}</p>}
        {failed && <p role="alert" className="text-sm text-red-300">{t.failed}</p>}
        {result?.status === "no_support" && <p className="text-sm text-slate-300">{t.missing}</p>}
        {result?.notes?.map((note) => <p key={note} className="rounded-lg border border-amber-400/20 px-3 py-2 text-sm text-amber-200">{note}</p>)}
        {result?.passages?.map((passage) => (
          <article key={passage.id} className="rounded-xl border border-slate-800 bg-[#0F1322] p-4">
            <h3 className="text-xs font-semibold text-emerald-300">{passage.scope}</h3>
            <p className="mt-2 text-sm leading-relaxed text-white">{passage.answer}</p>
            <p className="mt-3 text-xs text-slate-300">{passage.publisher} · {passage.title} · {passage.section}</p>
            <p className="mt-1 text-xs text-slate-400">{passage.published_on && `${t.published} ${passage.published_on} · `}{t.reviewed} {passage.reviewed_on}</p>
            <a className="mt-2 inline-block text-xs font-semibold text-emerald-300 underline" href={passage.url} target="_blank" rel="noreferrer">{t.source}</a>
          </article>
        ))}
      </div>
    </section>
  );
}
