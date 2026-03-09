import { useState } from "react"
import { useNavigate, Link } from "react-router-dom"
import "./auth-layout.css"

export default function Login() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const navigate = useNavigate()

  const handleLogin = async () => {
    const res = await fetch("http://127.0.0.1:5000/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    })

    const data = await res.json()

    if (data.access_token) {
      localStorage.setItem("token", data.access_token)
      navigate("/dashboard")
    } else {
      alert("Login failed")
    }
  }

  return (
    <div className="auth-shell">
      <div className="auth-card">
        <div className="auth-card-header">
          <div className="auth-pill">
            <span>●</span>
            Job Tracker
          </div>
          <h2>Welcome back</h2>
          <p>Sign in to access your dashboard and admin tools.</p>
        </div>

        <div className="auth-form">
          <div className="auth-field">
            <label className="auth-label">Email</label>
            <input
              className="auth-input"
              placeholder="you@example.com"
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
            />
          </div>

          <div className="auth-field">
            <label className="auth-label">Password</label>
            <input
              className="auth-input"
              type="password"
              placeholder="Your password"
              value={password}
              onChange={e => setPassword(e.target.value)}
            />
          </div>

          <div className="auth-actions">
            <button className="auth-primary-btn" type="button" onClick={handleLogin}>
              Log in
            </button>

            <div className="auth-secondary-text">
              No account yet? <Link to="/signup">Create one</Link>
            </div>

            <div className="auth-footer-hint">
              Tip: use an admin account to access the admin panel.
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
