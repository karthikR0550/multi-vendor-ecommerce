
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import API from "../api/axios";

function VendorOrders() {
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [message, setMessage] = useState("");

    const fetchOrders = async () => {
        try {
            const response = await API.get("orders/shop/");
            setOrders(response.data);
        } catch (err) {
            setError(
                err.response?.data?.detail ||
                "Unable to load shop orders."
            );
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchOrders();
    }, []);

    const updateOrderStatus = async (id, action) => {
        try {
            await API.post(`orders/shop/${id}/${action}/`);

            setMessage(
                action === "accept"
                    ? "Order accepted successfully!"
                    : "Order marked as packed successfully!"
            );

            setError("");
            fetchOrders();
        } catch (err) {
            setMessage("");
            setError(
                err.response?.data?.detail ||
                "Unable to update order status."
            );
        }
    };

    return (
        <div>
            <nav className="navbar">
                <div className="logo">ShopSmart</div>

                <div className="nav-links">
                    <Link to="/vendor">Dashboard</Link>
                    <Link to="/vendor/add-product">Add Product</Link>
                </div>
            </nav>

            <div className="page-container">
                <h1>Shop Orders</h1>
                <p>View and manage orders placed by customers.</p>

                {message && (
                    <p style={{ color: "green" }}>{message}</p>
                )}

                {error && (
                    <p style={{ color: "red" }}>{error}</p>
                )}

                {loading ? (
                    <h3>Loading orders...</h3>
                ) : orders.length === 0 ? (
                    <div className="card">
                        <h3>No orders found</h3>
                        <p>You haven't received any orders yet.</p>
                    </div>
                ) : (
                    orders.map(order => (
                        <div
                            className="card"
                            key={order.id}
                            style={{ marginBottom: "25px" }}
                        >
                            <h2>Order #{order.order_id || order.id}</h2>

                            <p>
                                <strong>Customer:</strong>{" "}
                                {order.customer_name}
                            </p>

                            <p>
                                <strong>Phone:</strong>{" "}
                                {order.customer_phone}
                            </p>

                            <p>
                                <strong>Delivery Address:</strong>{" "}
                                {order.shipping_address},{" "}
                                {order.shipping_city},{" "}
                                {order.shipping_state} -{" "}
                                {order.shipping_postal_code}
                            </p>

                            <p>
                                <strong>Order Date:</strong>{" "}
                                {new Date(order.created_at).toLocaleString()}
                            </p>

                            <p>
                                <strong>Status:</strong>{" "}
                                {order.status}
                            </p>

                            <h3>Products</h3>

                            {order.items.map(item => (
                                <div
                                    key={item.id}
                                    style={{
                                        borderBottom: "1px solid #ddd",
                                        padding: "10px 0",
                                    }}
                                >
                                    <p>
                                        <strong>{item.product_name}</strong>
                                    </p>

                                    <p>Price: ₹{item.unit_price}</p>
                                    <p>Quantity: {item.quantity}</p>
                                    <p>Subtotal: ₹{item.subtotal}</p>
                                </div>
                            ))}

                            <h3>
                                Shop Subtotal: ₹{order.subtotal}
                            </h3>

                            {order.status === "PENDING" && (
                                <button
                                    onClick={() =>
                                        updateOrderStatus(order.id, "accept")
                                    }
                                >
                                    Accept Order
                                </button>
                            )}

                            {order.status === "ACCEPTED" && (
                                <button
                                    onClick={() =>
                                        updateOrderStatus(order.id, "pack")
                                    }
                                >
                                    Mark as Packed
                                </button>
                            )}
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}

export default VendorOrders;
