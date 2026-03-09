import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import "./admin.css"

export default function Admin() {
  const [users, setUsers] = useState([])
  const navigate = useNavigate()

  useEffect(() => {
    const token = localStorage.getItem("token")

    if (!token) {
      navigate("/")
      return
    }

    // Verify admin role
    fetch("http://127.0.0.1:5000/check-admin", {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => {
        // Treat 401/403 as not authorized and redirect
        if (res.status === 401 || res.status === 403) {
          throw new Error("Not authorized")
        }
        if (!res.ok) {
          throw new Error("Request failed")
        }
        return res.json()
      })
      .then(data => {
        console.log("Admin check result:", data)
        if (!data.admin) {
          alert("Admins only")
          navigate("/dashboard")
          return
        }

        // Fetch users
        fetch("http://127.0.0.1:5000/admin/users", {
          headers: { Authorization: `Bearer ${token}` }
        })
          .then(res => {
            if (!res.ok) {
              throw new Error('Not authorized')
            }
            return res.json()
          })
          .then(setUsers)
          .catch(err => {
            console.error('Error fetching users:', err)
            alert("Admins only")
            navigate("/dashboard")
          })
      })
      .catch(err => {
        console.error('Error checking admin:', err)
        alert("Admins only")
        navigate("/dashboard")
      })
  }, [navigate])

  return (
    <div className="admin-page">
      <div className="admin-card">
        <div className="admin-header">
          <div className="admin-title-group">
            <div className="admin-badge">
              <span>●</span>
              Admin Area
            </div>
            <h2>Admin Panel</h2>
            <p>Manage users and view roles in your application.</p>
          </div>

          <button
            className="admin-back-btn"
            type="button"
            onClick={() => navigate("/dashboard")}
          >
            <span>←</span>
            Back to dashboard
          </button>
        </div>

        <div className="admin-content">
          <div className="admin-section-header">
            <h3>All Users</h3>
            <small>{users.length} total</small>
          </div>

          {users.length === 0 ? (
            <div className="admin-empty">
              No users found yet. Once users sign up, they will appear here.
            </div>
          ) : (
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Role</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.id}>
                    <td data-label="Name">{u.name}</td>
                    <td data-label="Email">{u.email}</td>
                    <td data-label="Role">
                      <span
                        className={
                          "admin-role-pill " +
                          (u.role === "admin"
                            ? "admin-role-pill--admin"
                            : "admin-role-pill--user")
                        }
                      >
                        {u.role}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  )
}