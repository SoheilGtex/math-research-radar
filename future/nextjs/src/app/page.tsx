import React from 'react';

// Type definition for our FastAPI response
interface Paper {
  id: string;
  title: string;
  published: string;
  summary: string | null;
  link: string;
  category: string;
  source: string;
}

async function getPapers(): Promise<Paper[]> {
  // SERVER-SIDE FETCH: Talk directly to the FastAPI container using Docker DNS!
  // No CORS issues exist here because this runs inside the Node.js container, not the browser.
  const apiUrl = process.env.API_URL || 'http://127.0.0.1:8000/api';
  
  const res = await fetch(`${apiUrl}/papers?limit=12`, { cache: 'no-store' });
  
  if (!res.ok) {
    throw new Error(`Failed to fetch papers: ${res.status}`);
  }
  return res.json();
}

export default async function Dashboard() {
  const papers = await getPapers();

  return (
    <main className="min-h-screen bg-gray-50 text-slate-800 p-8 font-sans">
      <div className="max-w-6xl mx-auto">
        
        <header className="mb-10 text-center">
          <h1 className="text-4xl font-extrabold text-blue-600 tracking-tight">🔭 Math Research Radar</h1>
          <p className="text-gray-500 mt-2 text-lg">Real-time Intelligence Dashboard powered by FastAPI & PostgreSQL</p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {papers.length === 0 ? (
            <div className="col-span-full text-center text-gray-400 py-10">
              No papers found in the database.
            </div>
          ) : (
            papers.map((paper) => (
              <a 
                key={paper.id} 
                href={paper.link} 
                target="_blank" 
                rel="noopener noreferrer"
                className="block bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-md transition-shadow p-6 group"
              >
                <div className="flex justify-between items-start mb-4">
                  <span className="bg-blue-100 text-blue-800 text-xs font-semibold px-2.5 py-0.5 rounded">
                    {paper.category}
                  </span>
                  <span className="bg-yellow-100 text-yellow-800 text-xs font-semibold px-2.5 py-0.5 rounded">
                    {paper.source}
                  </span>
                </div>
                <h2 className="text-lg font-bold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors line-clamp-2">
                  {paper.title}
                </h2>
                <p className="text-sm text-gray-500 line-clamp-3 mb-4">
                  {paper.summary || "No abstract provided."}
                </p>
                <div className="text-xs text-gray-400 mt-auto pt-4 border-t border-gray-100">
                  Published: {paper.published.substring(0, 10)}
                </div>
              </a>
            ))
          )}
        </div>

      </div>
    </main>
  );
}