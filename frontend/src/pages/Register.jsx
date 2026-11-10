
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import API from "../api/axios";

function Register() {
    const [form, setForm] = useState({
        username: "",
        email: "",
        password: "",
        first_name: "",
        last_name: "",
        phone: "",
    });

    const [accountType, setAccountType] = useState("CUSTOMER");

    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");
    const [loading, setLoading] = useState(false);

    const navigate = useNavigate();

    const handleChange = (e) => {
        setForm({
            ...form,
            [e.target.name]: e.target.value,
        });
    };

    const handleRegister = async (e) => {
        e.preventDefault();
        setError("");
        setSuccess("");
        setLoading(true);

        try {
            await API.post("auth/register/", form);

            // Remember the selected account type for the login step
            if (accountType === "SHOP_OWNER") {
                localStorage.setItem(
                    "pendingSellerApplicationUsername",
                    form.username.trim()
                );
            } else {
                localStorage.removeItem("pendingSellerApplicationUsername");
            }

            setSuccess("Registration successful! Redirecting to login...");

            setTimeout(() => {
                navigate("/login");
            }, 1500);

        } catch (err) {
            console.error(
                "Registration error:",
                err.response?.data || err.message
            );

            setError(
                JSON.stringify(err.response?.data || err.message)
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="form-container">
            <h1>Create Account</h1>
            <p>Join ShopSmart today.</p>

            <form onSubmit={handleRegister}>

                <label>Account Type</label>

                <select
                    value={accountType}
                    onChange={(e) => setAccountType(e.target.value)}
                    required
                >
                    <option value="CUSTOMER">
                        Customer
                    </option>

                    <option value="SHOP_OWNER">
                        Shop Owner
                    </option>
                </select>

                <label>First Name</label>
                <input
                    name="first_name"
                    value={form.first_name}
                    onChange={handleChange}
                    placeholder="Enter first name"
                    required
                />

                <label>Last Name</label>
                <input
                    name="last_name"
                    value={form.last_name}
                    onChange={handleChange}
                    placeholder="Enter last name"
                />

                <label>Username</label>
                <input
                    name="username"
                    value={form.username}
                    onChange={handleChange}
                    placeholder="Enter username"
                    required
                />

                <label>Email</label>
                <input
                    name="email"
                    type="email"
                    value={form.email}
                    onChange={handleChange}
                    placeholder="Enter email"
                    required
                />

                <label>Phone</label>
                <input
                    name="phone"
                    value={form.phone}
                    onChange={handleChange}
                    placeholder="Enter phone number"
                />

                <label>Password</label>
                <input
                    name="password"
                    type="password"
                    value={form.password}
                    onChange={handleChange}
                    placeholder="Create password (minimum 8 characters)"
                    minLength={8}
                    required
                />

                {accountType === "SHOP_OWNER" && (
                    <p style={{ color: "#555" }}>
                        After registration and login, you will
                        complete your shop application. Your shop
                        requires admin approval.
                    </p>
                )}

                {error && (
                    <p style={{ color: "red" }}>{error}</p>
                )}

                {success && (
                    <p style={{ color: "green" }}>{success}</p>
                )}

                <button type="submit" disabled={loading}>
                    {loading ? "Registering..." : "Register"}
                </button>
            </form>

            <p style={{ marginTop: "20px" }}>
                Already have an account? <Link to="/login">Login</Link>
            </p>
        </div>
    );
}

export default Register;
