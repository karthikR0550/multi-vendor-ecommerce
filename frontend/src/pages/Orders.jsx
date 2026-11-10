
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import API from "../api/axios";

function Orders() {
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const navigate = useNavigate();

    useEffect(() => {
        const fetchOrders = async () => {
            try {
                const token = localStorage.getItem("access");

                if (!token) {
                    navigate("/");
                    return;
                }

                const response = await API.get("orders/my-orders/", {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });

                setOrders(response.data);
            } catch (err) {
                console.error(
                    "Orders loading error:",
                    err.response?.data || err.message
                );

                setError("Unable to load your orders. Please try again.");
            } finally {
                setLoading(false);
            }
        };

        fetchOrders();
    }, [navigate]);

    return (
        <div>
            <nav className="navbar">
                <div className="logo">ShopSmart</div>

                <div className="nav-links">
                    <Link to="/home">Home</Link>
                    <Link to="/products">Products</Link>
                    <Link to="/cart">Cart</Link>
                    <Link to="/orders">My Orders</Link>
                </div>
            </nav>

            <div className="page-container">
                <h1>My Orders</h1>
                <p>Track and manage your purchases.</p>

                {loading && <p>Loading your orders...</p>}

                {error && (
                    <p style={{ color: "red" }}>{error}</p>
                )}

                {!loading && !error && orders.length === 0 && (
                    <div className="card">
                        <h2>No orders yet!</h2>
                        <p>Your purchases will appear here.</p>
                        <Link to="/products">
                            <button>Explore Products</button>
                        </Link>
                    </div>
                )}

                {!loading && orders.map((order) => (
                    <div
                        className="card"
                        key={order.id}
                        style={{ marginBottom: "20px" }}
                    >
                        <h2>Order #{order.id}</h2>

                        <p>
                            Order Date:{" "}
                            {new Date(order.created_at).toLocaleDateString("en-IN")}
                        </p>

                        <p>
                            Order Status:{" "}
                            <strong>{order.status}</strong>
                        </p>

                        <h3>Shipping Details</h3>
                        <p>{order.shipping_name}</p>
                        <p>{order.shipping_phone}</p>
                        <p>
                            {order.shipping_address}, {order.shipping_city},
                            {" "}{order.shipping_state} - {order.shipping_postal_code}
                        </p>

                        <h3 style={{ marginTop: "20px" }}>
                            Ordered Products
                        </h3>

                        {order.shop_orders?.map((shopOrder) => (
                            <div
                                key={shopOrder.id}
                                style={{
                                    borderTop: "1px solid #ddd",
                                    padding: "12px 0",
                                }}
                            >
                                <h4>Shop: {shopOrder.shop_name}</h4>

                                <p>
                                    Shop Order Status: {shopOrder.status}
                                </p>

                                {shopOrder.items.map((item) => (
                                    <div key={item.id}>
                                        <p>
                                            {item.product_name} × {item.quantity}
                                        </p>

                                        <p>
                                            Unit Price: ₹
                                            {Number(item.unit_price).toFixed(2)}
                                        </p>

                                        <p>
                                            Subtotal: ₹
                                            {Number(item.subtotal).toFixed(2)}
                                        </p>
                                    </div>
                                ))}

                                <p>
                                    Shop Subtotal: ₹
                                    {Number(shopOrder.subtotal).toFixed(2)}
                                </p>
                            </div>
                        ))}

                        <h2 className="price">
                            Total: ₹
                            {Number(order.total_amount).toFixed(2)}
                        </h2>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default Orders;
