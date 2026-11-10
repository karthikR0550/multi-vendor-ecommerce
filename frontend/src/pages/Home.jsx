
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import API from "../api/axios";

function Home() {
    const [user, setUser] = useState(null);
    const [error, setError] = useState("");

    const navigate = useNavigate();

    useEffect(() => {
        const fetchUser = async () => {
            try {
                const response = await API.get("auth/me/");
                setUser(response.data);
            } catch (err) {
                console.error(
                    "User fetch error:",
                    err.response?.data || err.message
                );
                setError("Unable to load user information.");
            }
        };

        fetchUser();
    }, []);

    const handleLogout = () => {
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        navigate("/");
    };

    return (
        <div>
            <nav className="navbar">
                <div className="logo">ShopSmart</div>

                <div className="nav-links">
                    <Link to="/home">Home</Link>
                    <Link to="/products">Products</Link>
                    <Link to="/cart">Cart</Link>
                    <Link to="/orders">My Orders</Link>

                    <button onClick={handleLogout}>
                        Logout
                    </button>
                </div>
            </nav>

            <div className="page-container">
                <div className="card">
                    <h1>
                        Welcome {user
                            ? user.first_name || user.username
                            : "to ShopSmart"}!
                    </h1>

                    {user && (
                        <p>
                            Logged in as: {user.username}
                        </p>
                    )}

                    {error && (
                        <p style={{ color: "red" }}>{error}</p>
                    )}

                    <p>
                        Discover amazing products from different vendors
                        all in one place.
                    </p>

                    <Link to="/products">
                        <button>Explore Products</button>
                    </Link>
                </div>

                <h2 style={{ marginTop: "35px" }}>
                    Why Shop With Us?
                </h2>

                <div className="dashboard-grid">
                    <div className="card">
                        <h2>Quality Products</h2>
                        <p>
                            Explore products from different categories.
                        </p>
                    </div>

                    <div className="card">
                        <h2>Multiple Vendors</h2>
                        <p>
                            Shop from different sellers in one platform.
                        </p>
                    </div>

                    <div className="card">
                        <h2>Secure Payments</h2>
                        <p>
                            Enjoy a convenient checkout experience.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Home;
