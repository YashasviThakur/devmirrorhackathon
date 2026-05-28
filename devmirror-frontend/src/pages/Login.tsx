import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, ArrowRight, Shield } from 'lucide-react'
import clsx from 'clsx'

type Tier = 'personal' | 'institution' | null

const API_BASE = import.meta.env.VITE_API_URL ?? ''

export default function Login() {
  const navigate            = useNavigate()
  const [tier, setTier]     = useState<Tier>(null)
  const [instName, setInstName] = useState('')
  const [instError, setInstError] = useState('')

  function handleGoogleLogin() {
    if (tier === 'institution') {
      if (!instName.trim()) { setInstError('Institution name is required.'); return }
      window.location.href = `${API_BASE}/api/auth/google/login?account_type=institution&institution_name=${encodeURIComponent(instName.trim())}`
      return
    }
    window.location.href = `${API_BASE}/api/auth/google/login?account_type=personal`
  }

  return (
    <div className="min-h-screen bg-white flex flex-col">

      {/* Nav */}
      <nav className="border-b border-dm-border px-8 h-16 flex items-center justify-between">
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-2 text-sm text-dm-muted hover:text-dm-text transition-colors"
        >
          <ArrowLeft size={14} /> DevMirror
        </button>
        <span className="font-black text-xl tracking-tighter">DevMirror</span>
        <div className="w-24" />
      </nav>

      {/* Content */}
      <div className="flex-1 flex">

        {/* Left ?" dark panel */}
        <div className="hidden lg:flex lg:w-1/2 bg-[#1A1A14] flex-col justify-between p-16">
          <div>
            <p className="dm-label text-dm-dim mb-10">Developer Intelligence Platform</p>
            <h1 className="text-display text-white mb-8">
              Your entire<br />dev life.<br />Reflected.
            </h1>
            <p className="text-white/50 text-lg font-light leading-relaxed max-w-sm">
              Connect GitHub, LeetCode, Codeforces, Gmail, Calendar, and YouTube. Get daily AI coaching from Cohere.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-px border border-white/10">
            {[
              { val: '6',  label: 'Live data sources'  },
              { val: '3',  label: 'Personal goals'      },
              { val: 'AI', label: 'Cohere'             },
              { val: '2+', label: 'Account tiers'       },
            ].map(({ val, label }) => (
              <div key={label} className="bg-white/5 p-6">
                <div className="font-black text-3xl text-white tracking-tighter mb-1">{val}</div>
                <div className="text-xs text-white/40 font-mono uppercase tracking-wider">{label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Right ?" form panel */}
        <div className="flex-1 flex items-center justify-center px-8 py-16">
          <div className="w-full max-w-md">

            {!tier ? (
              /* Tier selection */
              <>
                <p className="dm-label mb-4">Choose your account type</p>
                <h2 className="font-black text-3xl tracking-tighter mb-10">Sign in to DevMirror</h2>

                <div className="flex flex-col gap-4">
                  <button
                    onClick={() => setTier('personal')}
                    className="border border-dm-border p-6 text-left hover:border-dm-text transition-colors group"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <span className="font-bold text-base">Personal</span>
                      <ArrowRight size={14} className="text-dm-muted group-hover:text-dm-text transition-colors" />
                    </div>
                    <p className="text-sm text-dm-muted font-light leading-relaxed">
                      Track your individual progress. Connect all six data sources and get a daily
                      AI coaching session tailored to your journey.
                    </p>
                    <div className="flex gap-2 mt-4 flex-wrap">
                      {['GitHub', 'LeetCode', 'Gmail', 'AI Coach'].map(t => (
                        <span key={t} className="text-[10px] font-mono px-2 py-0.5 border border-dm-border text-dm-muted">{t}</span>
                      ))}
                    </div>
                  </button>

                  <button
                    onClick={() => setTier('institution')}
                    className="border border-dm-border p-6 text-left hover:border-dm-text transition-colors group"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <span className="font-bold text-base">Institutional</span>
                      <ArrowRight size={14} className="text-dm-muted group-hover:text-dm-text transition-colors" />
                    </div>
                    <p className="text-sm text-dm-muted font-light leading-relaxed">
                      For colleges, bootcamps, and cohorts. Register under your institution name.
                      Each student's OAuth tokens remain isolated and encrypted.
                    </p>
                    <div className="flex gap-2 mt-4 flex-wrap">
                      {['Multi-user', 'Encrypted', 'Cohort', 'Analytics'].map(t => (
                        <span key={t} className="text-[10px] font-mono px-2 py-0.5 border border-dm-border text-dm-muted">{t}</span>
                      ))}
                    </div>
                  </button>
                </div>
              </>
            ) : (
              /* Sign-in panel */
              <>
                <button
                  onClick={() => { setTier(null); setInstName(''); setInstError('') }}
                  className="flex items-center gap-2 text-sm text-dm-muted hover:text-dm-text transition-colors mb-8"
                >
                  <ArrowLeft size={13} /> Change account type
                </button>

                <p className="dm-label mb-4">
                  {tier === 'personal' ? 'Personal account' : 'Institutional account'}
                </p>
                <h2 className="font-black text-3xl tracking-tighter mb-10">
                  Sign in with Google
                </h2>

                {/* Institution name */}
                {tier === 'institution' && (
                  <div className="mb-6">
                    <label className="dm-label mb-2 block">Institution Name</label>
                    <input
                      type="text"
                      value={instName}
                      onChange={e => { setInstName(e.target.value); setInstError('') }}
                      placeholder="e.g. IIT Delhi, Lambda School, BITS Pilani"
                      className="dm-input"
                      onKeyDown={e => e.key === 'Enter' && handleGoogleLogin()}
                      autoFocus
                    />
                    {instError && (
                      <p className="text-xs text-dm-red mt-2">{instError}</p>
                    )}
                  </div>
                )}

                {/* Google button */}
                <button
                  onClick={handleGoogleLogin}
                  className={clsx(
                    'w-full flex items-center justify-center gap-3 py-4 text-sm font-semibold transition-colors mb-6',
                    tier === 'personal'
                      ? 'bg-[#1A1A14] text-white hover:opacity-80'
                      : 'bg-[#1A1A14] text-white hover:opacity-80',
                  )}
                >
                  <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                    <path d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.874 2.684-6.615z" fill="#4285F4" />
                    <path d="M9 18c2.43 0 4.467-.806 5.956-2.18l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 009 18z" fill="#34A853" />
                    <path d="M3.964 10.71A5.41 5.41 0 013.682 9c0-.593.102-1.17.282-1.71V4.958H.957A8.996 8.996 0 000 9c0 1.452.348 2.827.957 4.042l3.007-2.332z" fill="#FBBC05" />
                    <path d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 00.957 4.958L3.964 7.29C4.672 5.163 6.656 3.58 9 3.58z" fill="#EA4335" />
                  </svg>
                  Continue with Google
                </button>

                {/* Security note */}
                <div className="flex items-start gap-3 p-4 bg-[#F5F0E8] border border-dm-border">
                  <Shield size={13} className="text-dm-green mt-0.5 shrink-0" />
                  <p className="text-[11px] text-dm-muted font-light leading-relaxed">
                    OAuth tokens are encrypted with Fernet symmetric encryption before storage.
                    DevMirror only requests read-only scopes for Gmail and YouTube.
                  </p>
                </div>

                {/* Scopes */}
                <div className="mt-6">
                  <p className="dm-label mb-3">Permissions requested</p>
                  <div className="flex flex-wrap gap-2">
                    {['Gmail readonly', 'Calendar events', 'YouTube readonly', 'User email'].map(s => (
                      <span key={s} className="text-[10px] font-mono px-2 py-0.5 border border-dm-border text-dm-muted">{s}</span>
                    ))}
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

