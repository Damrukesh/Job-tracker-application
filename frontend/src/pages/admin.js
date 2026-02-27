import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"

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
    fetch("http://127.0.0.1:5000/profile", {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => {
        console.log("Admin check /profile result:", data)
        if (data.role !== "admin") {
          alert("Admins only")
          navigate("/dashboard")
          return
        }

        // Fetch users
        fetch("http://127.0.0.1:5000/admin/users", {
          headers: { Authorization: `Bearer ${token}` }
        })
          .then(res => res.json())
          .then(setUsers)
      })
  }, [navigate])

  return (
    <div>
      <h2>Admin Panel</h2>

      <button onClick={() => navigate("/dashboard")}>
        Back to Dashboard
      </button>

      <h3>All Users</h3>

      <ul>
        {users.map(u => (
          <li key={u.id}>
            {u.name} — {u.email} — {u.role}
          </li>
        ))}
      </ul>
    </div>
  )
}