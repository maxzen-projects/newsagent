"use client";

import { useEffect, useState } from "react";

type Article = {
title: string;
description?: string;
source?: string;
url?: string;
score?: number;
category?: string;
};

export default function NewsDashboard() {
const [articles, setArticles] = useState<Article[]>([]);
const [search, setSearch] = useState("");
const [activeTab, setActiveTab] = useState("articles");
const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

useEffect(() => {
  setLastUpdated(new Date());
}, []);

const [stats, setStats] = useState({
raw: 0,
locality: 0,
semantic: 0,
final: 0,
});

const tabs = [
{ key: "articles", label: "Raw Articles" },
{ key: "locality", label: "Locality Filter" },
{ key: "semantic", label: "Semantic Deduped" },
{ key: "final", label: "Final Digest" },
];

const loadData = async (tab: string) => {
const res = await fetch(`http://127.0.0.1:8000/${tab}`);
const data = await res.json();
setArticles(data);
setLastUpdated(new Date());
};

const loadStats = async () => {
const [raw, locality, semantic, final] = await Promise.all([
fetch("http://127.0.0.1:8000/articles").then((r) => r.json()),
fetch("http://127.0.0.1:8000/locality").then((r) => r.json()),
fetch("http://127.0.0.1:8000/semantic").then((r) => r.json()),
fetch("http://127.0.0.1:8000/final").then((r) => r.json()),
]);


setStats({
  raw: raw.length,
  locality: locality.length,
  semantic: semantic.length,
  final: final.length,
});


};

useEffect(() => {
loadData(activeTab);
loadStats();


const interval = setInterval(() => {
  loadData(activeTab);
  loadStats();
}, 30000);

return () => clearInterval(interval);


}, [activeTab]);

const filtered = articles.filter((article) =>
article.title.toLowerCase().includes(search.toLowerCase())
);

return ( <main className="dashboard-bg p-8">


  <div className="max-w-7xl mx-auto">

    <div className="mb-10">

      <h1 className="dashboard-title">
        Newsroom Analytics Platform
      </h1>

     <p className="dashboard-subtitle mt-3">
  AI-Powered News Intelligence Pipeline
</p>
<div className="flex items-center gap-3 mt-4">
  <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse"></div>

  <span className="text-sm text-slate-300">
    Live • Auto Refresh Every 30s
    {lastUpdated && (
      <> • Last Updated {lastUpdated.toLocaleTimeString()}</>
    )}
  </span>
</div>  

    </div>

    {/* STATS */}

    <div className="grid md:grid-cols-4 gap-5 mb-10">

      <StatCard title="Raw Articles" value={stats.raw} />
      <StatCard title="Locality Filtered" value={stats.locality} />
      <StatCard title="Semantic Deduped" value={stats.semantic} />
      <StatCard title="Final Digest" value={stats.final} />

    </div>

    {/* PIPELINE */}

    <div className="glass-card p-6 mb-8">

      <h2 className="text-xl font-bold mb-5">
        Pipeline Flow
      </h2>

      <div className="flex flex-wrap gap-3 items-center">

        <FlowBox text={`Raw (${stats.raw})`} />

        <span className="text-slate-400">→</span>

        <FlowBox text={`Local (${stats.locality})`} />

        <span className="text-slate-400">→</span>

        <FlowBox text={`Semantic (${stats.semantic})`} />

        <span className="text-slate-400">→</span>

        <FlowBox text={`Digest (${stats.final})`} />

      </div>

    </div>

    {/* SEARCH */}

    <input
      placeholder="Search articles..."
      value={search}
      onChange={(e) => setSearch(e.target.value)}
      className="search-box mb-8"
    />

    {/* TABS */}

    <div className="flex gap-3 flex-wrap mb-8">

      {tabs.map((tab) => (
        <button
          key={tab.key}
          onClick={() => setActiveTab(tab.key)}
          className={`pipeline-tab ${
            activeTab === tab.key ? "active" : ""
          }`}
        >
          {tab.label}
        </button>
      ))}

    </div>

    {/* ARTICLES */}

    <div className="grid gap-5">

      {filtered.map((article, index) => (
        <div key={index} className="news-card">

          <h2 className="news-title">
            {article.title}
          </h2>

          <p className="news-description">
            {article.description}
          </p>

          <div className="flex flex-wrap gap-3 mt-4">

            {article.category && (
              <span className={`badge badge-${article.category.toLowerCase()}`}>
                {article.category}
              </span>
            )}

            {article.score !== undefined && (
              <span className="badge badge-cricket">
                Score {article.score}
              </span>
            )}

            {article.source && (
              <span className="badge badge-politics">
                {article.source}
              </span>
            )}

          </div>

          {article.url && (
            <a
              href={article.url}
              target="_blank"
              rel="noreferrer"
              className="news-link inline-block mt-4"
            >
              Read Full Story →
            </a>
          )}

        </div>
      ))}

    </div>

  </div>

</main>


);
}

function StatCard({
title,
value,
}: {
title: string;
value: number;
}) {
return ( <div className="glass-card stat-card p-6">


  <div className="stat-number">
    {value}
  </div>

  <div className="stat-label">
    {title}
  </div>

</div>

);
}

function FlowBox({
text,
}: {
text: string;
}) {
return ( <div className="glass-card px-5 py-3 font-semibold">
{text} </div>
);
}

