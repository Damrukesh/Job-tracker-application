import { useState } from "react"
import { useNavigate } from "react-router-dom"

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
    <div>
      <h2>Signup</h2>

      <input placeholder="Name" onChange={e => setName(e.target.value)} />
      <br />

      <input placeholder="Email" onChange={e => setEmail(e.target.value)} />
      <br />

      <input
        type="password"
        placeholder="Password"
        onChange={e => setPassword(e.target.value)}
      />
      <br />

      <button onClick={handleSignup}>Signup</button>
    </div>
  )
}