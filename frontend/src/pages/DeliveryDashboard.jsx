
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import API from "../api/axios";

function DeliveryDashboard() {
    const [deliveries, setDeliveries] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [message, setMessage] = useState("");

    const fetchDeliveries = async () => {
        try {
            const response = await API.get("delivery/my-deliveries/");
            setDeliveries(response.data);
        } catch (err) {
            setError(
                err.response?.data?.detail ||
                "Unable to load deliveries."
            );
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchDeliveries();
    }, []);

    const updateDelivery = async (id, action) => {
        try {
            await API.post(`delivery/${id}/${action}/`);

            setMessage(
                action === "pickup"
                    ? "Order picked up successfully!"
                    : action === "out-for-delivery"
                        ? "Order is now out for delivery!"
                        : "Order delivered successfully!"
            );

            setError("");
            fetchDeliveries();
        } catch (err) {
            setMessage("");
            setError(
                err.response?.data?.detail ||
                "Unable to update delivery status."
            );
        }
    };

    const handleLogout = () => {
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        window.location.href = "/";
    };

    return (
        <div>
            <nav className="navbar">
                <div className="logo">ShopSmart</div>

                <div className="nav-links">
                    <Link to="/delivery">Dashboard</Link>
                    <button onClick={handleLogout}>Logout</button>
                </div>
            </nav>

            <div className="page-container">
                <h1>Delivery Dashboard</h1>
                <p>Manage your assigned deliveries.</p>

                {message && (
                    <p style={{ color: "green" }}>{message}</p>
                )}

                {error && (
                    <p style={{ color: "red" }}>{error}</p>
                )}

                {loading ? (
                    <h3>Loading deliveries...</h3>
                ) : deliveries.length === 0 ? (
                    <div className="card">
                        <h3>No deliveries assigned</h3>
                        <p>New delivery assignments will appear here.</p>
                    </div>
                ) : (
                    deliveries.map(delivery => (
                        <div
                            className="card"
                            key={delivery.id}
                            style={{ marginBottom: "25px" }}
                        >
                            <h2>Delivery #{delivery.id}</h2>

                            <p>
                                <strong>Order ID:</strong>{" "}
                                #{delivery.order_id}
                            </p>

                            <p>
                                <strong>Shop:</strong>{" "}
                                {delivery.shop_name}
                            </p>

                            <p>
                                <strong>Customer:</strong>{" "}
                                {delivery.customer_name}
                            </p>

                            <p>
                                <strong>Phone:</strong>{" "}
                                {delivery.customer_phone}
                            </p>

                            <p>
                                <strong>Address:</strong>{" "}
                                {delivery.shipping_address},{" "}
                                {delivery.shipping_city},{" "}
                                {delivery.shipping_state} -{" "}
                                {delivery.shipping_postal_code}
                            </p>

                            <p>
                                <strong>Status:</strong>{" "}
                                {delivery.status}
                            </p>

                            <h3>Ordered Products</h3>

                            {delivery.items.map((item, index) => (
                                <div
                                    key={index}
                                    style={{
                                        borderBottom: "1px solid #ddd",
                                        padding: "10px 0",
                                    }}
                                >
                                    <p>
                                        <strong>{item.product_name}</strong>
                                    </p>
                                    <p>Quantity: {item.quantity}</p>
                                    <p>Price: ₹{item.unit_price}</p>
                                </div>
                            ))}

                            {delivery.status === "ASSIGNED" && (
                                <button
                                    onClick={() =>
                                        updateDelivery(delivery.id, "pickup")
                                    }
                                >
                                    Pick Up Order
                                </button>
                            )}

                            {delivery.status === "PICKED_UP" && (
                                <button
                                    onClick={() =>
                                        updateDelivery(
                                            delivery.id,
                                            "out-for-delivery"
                                        )
                                    }
                                >
                                    Start Delivery
                                </button>
                            )}

                            {delivery.status === "OUT_FOR_DELIVERY" && (
                                <button
                                    onClick={() =>
                                        updateDelivery(
                                            delivery.id,
                                            "delivered"
                                        )
                                    }
                                >
                                    Mark as Delivered
                                </button>
                            )}
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}

export default DeliveryDashboard;
