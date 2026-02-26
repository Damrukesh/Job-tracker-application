import axios from "axios";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function Dashboard() {
  const navigate = useNavigate();
  const [message, setMessage] = useState("");
  const [role, setRole] = useState("");

  // 🔐 Logout function (OUTSIDE useEffect)
  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/");
  };

  useEffect(() => {
    const token = localStorage.getItem("token");

    if (!token) {
      navigate("/");
      return;
    }

    const fetchProfile = async () => {
      try {
        const res = await axios.get(
          "http://127.0.0.1:5000/profile",
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        setMessage(`Welcome ${res.data.name}`);
        setRole(res.data.role);
      } catch (err) {
        localStorage.removeItem("token");
        navigate("/");
      }
    };

    fetchProfile();
  }, [navigate]);

  return (
    <div>
      <h2>Dashboard (Protected)</h2>
      <p>{message}</p>

      {role === "admin" && <h3>Admin Controls</h3>}
      {role === "manager" && <h3>Manager Panel</h3>}
      {role === "user" && <h3>User Dashboard</h3>}

      <button onClick={handleLogout}>
        Logout
      </button>
    </div>
  );
}

export default Dashboard;