import { useState } from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { Header } from './components/Header';
import { MobileNavigation } from './components/MobileNavigation';
import { HomePage } from './pages/HomePage';
import { ParentCallPage } from './pages/ParentCallPage';
import { ResponsePage } from './pages/ResponsePage';
import { PrivacyPage } from './pages/PrivacyPage';
import { NotFoundPage } from './pages/NotFoundPage';
import { Shield } from 'lucide-react';

export default function App() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col bg-background text-slate-100">

        {/* Navigation */}
        <Header onMenuToggle={() => setMobileMenuOpen(true)} />
        <MobileNavigation isOpen={mobileMenuOpen} onClose={() => setMobileMenuOpen(false)} />

        {/* Main Content Area */}
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/parent-call" element={<ParentCallPage />} />
            <Route path="/response" element={<ResponsePage />} />
            <Route path="/privacy" element={<PrivacyPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </main>

        {/* Global Footer */}
        <footer className="border-t border-surface-border bg-surface/80 py-8 px-4 sm:px-6 lg:px-8 mt-12">
          <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-6 text-xs text-slate-400">

            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-cyan-950 border border-cyan-800 flex items-center justify-center text-cyan-400">
                <Shield className="w-4 h-4 text-cyan-accent" />
              </div>
              <div>
                <div className="font-bold text-white text-sm">SentryMesh Guardian</div>
                <div className="text-slate-400">Pause. Verify. Protect.</div>
              </div>
            </div>

            <div className="flex flex-wrap items-center justify-center gap-6">
              <Link to="/parent-call" className="hover:text-cyan-300 transition-colors">
                ParentCall Guardian
              </Link>
              <Link to="/response" className="hover:text-cyan-300 transition-colors">
                Emergency Guide
              </Link>
              <Link to="/privacy" className="hover:text-cyan-300 transition-colors">
                Privacy Promises
              </Link>
              <a
                href="https://cybercrime.gov.in"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-cyan-300 transition-colors text-cyan-400"
              >
                cybercrime.gov.in (Helpline 1930)
              </a>
            </div>

            <div className="text-center sm:text-right text-slate-400 text-[11px]">
              <div>In-memory analysis only. No call recording.</div>
              <div className="text-slate-500 mt-0.5">Powered by local SentryMesh V4 TF-IDF Model</div>
            </div>

          </div>
        </footer>

      </div>
    </BrowserRouter>
  );
}
