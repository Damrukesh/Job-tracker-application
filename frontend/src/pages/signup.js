import { useState } from "react"
import { useNavigate, Link } from "react-router-dom"
import "./auth-layout.css"

export default function Signup() {
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const navigate = useNavigate()

  const handleSignup = async () => {
    const res = await fetch("http://127.0.0.1:5000/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, password })
    })

    if (res.status === 201) {
      alert("User created")
      navigate("/")
    } else {
      alert("Signup failed")
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
          <h2>Create an account</h2>
          <p>Sign up to start using the job tracker.</p>
        </div>

        <div className="auth-form">
          <div className="auth-field">
            <label className="auth-label">Name</label>
            <input
              className="auth-input"
              placeholder="Jane Doe"
              value={name}
              onChange={e => setName(e.target.value)}
            />
          </div>

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
              placeholder="Create a password"
              value={password}
              onChange={e => setPassword(e.target.value)}
            />
          </div>

          <div className="auth-actions">
            <button className="auth-primary-btn" type="button" onClick={handleSignup}>
              Sign up
            </button>

            <div className="auth-secondary-text">
              Already have an account? <Link to="/">Log in</Link>
            </div>

            <div className="auth-footer-hint">
              Default signups use the <strong>candidate</strong> role.
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
