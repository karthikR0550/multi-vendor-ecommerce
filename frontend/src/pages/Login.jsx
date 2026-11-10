
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import API from "../api/axios";

function Login() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        setError("");
        setLoading(true);

        try {
            const response = await API.post("token/", {
                username,
                password,
            });

            localStorage.setItem("access", response.data.access);
            localStorage.setItem("refresh", response.data.refresh);

            const userResponse = await API.get("auth/me/");
            const role = userResponse.data.role;

            const pendingSellerUsername = localStorage.getItem(
                "pendingSellerApplicationUsername"
            );

            const isPendingSeller =
                pendingSellerUsername === username.trim();

            if (role === "ADMIN") {
                navigate("/admin");

            } else if (role === "SHOP_OWNER") {
                if (isPendingSeller) {
                    localStorage.removeItem(
                        "pendingSellerApplicationUsername"
                    );
                }

                navigate("/vendor");

            }
            else if (role === "DELIVERY") {
                navigate("/delivery");
            } else if (role === "CUSTOMER") {

                if (isPendingSeller) {
                    localStorage.removeItem(
                        "pendingSellerApplicationUsername"
                    );

                    navigate("/become-seller");
                } else {
                    navigate("/home");
                }

            } else {
                localStorage.removeItem("access");
                localStorage.removeItem("refresh");
                setError("Your account has an invalid role.");
            }

        } catch (err) {
            localStorage.removeItem("access");
            localStorage.removeItem("refresh");

            setError(
                err.response?.data?.detail ||
                "Login failed. Please check your username and password."
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="form-container">
            <h1>Welcome Back!</h1>
            <p>Login to your ShopSmart account.</p>

            <form onSubmit={handleLogin}>
                <label>Username</label>
                <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="Enter username"
                    required
                />

                <label>Password</label>
                <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter password"
                    required
                />

                {error && (
                    <p style={{ color: "red" }}>{error}</p>
                )}

                <button type="submit" disabled={loading}>
                    {loading ? "Logging in..." : "Login"}
                </button>
            </form>

            <p style={{ marginTop: "20px" }}>
                Don't have an account?{" "}
                <Link to="/register">Register</Link>
            </p>
        </div>
    );
}

export default Login;
