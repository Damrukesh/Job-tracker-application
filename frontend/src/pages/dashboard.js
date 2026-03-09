import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import "./dashboard.css"

export default function Dashboard() {
  const [role, setRole] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    const token = localStorage.getItem("token")

    if (!token) {
      navigate("/")
      return
    }

    fetch("http://127.0.0.1:5000/profile", {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => setRole(data.role))
      .catch(() => navigate("/"))
  }, [navigate])

  const logout = () => {
    localStorage.removeItem("token")
    navigate("/")
  }

  return (
    <div className="dashboard-page">
      <div className="dashboard-shell">
        <div className="dashboard-card">
          <div className="dashboard-header">
            <div className="dashboard-title">
              <h2>Dashboard</h2>
              <p>You are signed in to the job tracker.</p>
            </div>
            {role && (
              <div
                className={
                  "dashboard-role-pill " +
                  (role === "admin"
                    ? "dashboard-role-pill--admin"
                    : "dashboard-role-pill--user")
                }
              >
                {role}
              </div>
            )}
          </div>

          <div className="dashboard-main-actions">
            <button className="dashboard-btn" type="button" onClick={logout}>
              Logout
            </button>

            {role === "admin" && (
              <button
                className="dashboard-btn"
                type="button"
                onClick={() => navigate("/admin")}
              >
                Admin panel
              </button>
            )}
          </div>

          <p className="dashboard-secondary">
            <strong>RBAC tip:</strong> only accounts with the <code>admin</code> role can
            access admin tools.
          </p>
        </div>

        <div className="dashboard-card">
          <h3 className="dashboard-side-card-title">About this app</h3>
          <div className="dashboard-side-card-body">
            <p>
              This dashboard is protected by JWT authentication. Use it as a starting
              point for your own job tracking workflow.
            </p>
            <p>
              You can extend it with more pages and connect real job data while keeping
              the same access control rules.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}