
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import API from "../api/axios";

function AdminDashboard() {
    const navigate = useNavigate();

    const [shops, setShops] = useState([]);
    const [products, setProducts] = useState([]);
    const [packedOrders, setPackedOrders] = useState([]);
    const [deliveryPersons, setDeliveryPersons] = useState([]);
    const [selectedPersons, setSelectedPersons] = useState({});

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [message, setMessage] = useState("");

    const handleLogout = () => {
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        navigate("/");
    };

    // FETCH DASHBOARD DATA
    const fetchDashboard = async () => {
        try {
            const [
                shopResponse,
                productResponse,
                packedResponse,
                deliveryResponse,
            ] = await Promise.all([
                API.get("shops/admin/pending/"),
                API.get("products/admin/pending/"),
                API.get("delivery/admin/packed-orders/"),
                API.get("delivery/admin/delivery-persons/"),
            ]);

            setShops(
                Array.isArray(shopResponse.data)
                    ? shopResponse.data
                    : shopResponse.data.results || []
            );

            setProducts(
                Array.isArray(productResponse.data)
                    ? productResponse.data
                    : productResponse.data.results || []
            );

            setPackedOrders(packedResponse.data);
            setDeliveryPersons(deliveryResponse.data);

        } catch (err) {
            console.error("Admin Dashboard Error:", err);

            setError(
                "API: " + (err.config?.url || "Unknown") +
                " | Status: " + (err.response?.status || "No response") +
                " | Error: " + JSON.stringify(
                    err.response?.data || err.message
                )
            );
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchDashboard();
    }, []);

    // APPROVE SHOP
    const handleShopApprove = async (id) => {
        try {
            await API.post(`shops/admin/${id}/approve/`);

            setShops(shops.filter(shop => shop.id !== id));
            setMessage("Shop approved successfully!");
        } catch (err) {
            setMessage(
                err.response?.data?.detail ||
                "Unable to approve shop."
            );
        }
    };

    // REJECT SHOP
    const handleShopReject = async (id) => {
        const reason = window.prompt(
            "Enter the reason for rejecting this shop:"
        );

        if (reason === null) return;

        if (!reason.trim()) {
            setMessage("Please enter a rejection reason.");
            return;
        }

        try {
            await API.post(`shops/admin/${id}/reject/`, {
                reason: reason.trim(),
            });

            setShops(shops.filter(shop => shop.id !== id));
            setMessage("Shop rejected successfully!");
        } catch (err) {
            setMessage(
                err.response?.data?.detail ||
                "Unable to reject shop."
            );
        }
    };

    // APPROVE PRODUCT
    const handleProductApprove = async (id) => {
        try {
            await API.post(`products/admin/${id}/approve/`);

            setProducts(
                products.filter(product => product.id !== id)
            );

            setMessage("Product approved successfully!");
        } catch (err) {
            setMessage(
                err.response?.data?.detail ||
                "Unable to approve product."
            );
        }
    };

    // REJECT PRODUCT
    const handleProductReject = async (id) => {
        const reason = window.prompt(
            "Enter the reason for rejecting this product:"
        );

        if (reason === null) return;

        if (!reason.trim()) {
            setMessage("Please enter a rejection reason.");
            return;
        }

        try {
            await API.post(`products/admin/${id}/reject/`, {
                reason: reason.trim(),
            });

            setProducts(
                products.filter(product => product.id !== id)
            );

            setMessage("Product rejected successfully!");
        } catch (err) {
            setMessage(
                err.response?.data?.detail ||
                "Unable to reject product."
            );
        }
    };

    // ASSIGN DELIVERY PERSON
    const handleAssignDelivery = async (shopOrderId) => {
        const deliveryPersonId = selectedPersons[shopOrderId];

        if (!deliveryPersonId) {
            setMessage("Please select a delivery person.");
            return;
        }

        try {
            await API.post("delivery/admin/assign/", {
                shop_order: shopOrderId,
                delivery_person: deliveryPersonId,
            });

            setMessage("Delivery assigned successfully!");

            setPackedOrders(
                packedOrders.filter(
                    order => order.id !== shopOrderId
                )
            );

            setSelectedPersons(prev => {
                const updated = { ...prev };
                delete updated[shopOrderId];
                return updated;
            });

        } catch (err) {
            setMessage(
                err.response?.data?.detail ||
                err.response?.data?.shop_order?.[0] ||
                "Unable to assign delivery."
            );
        }
    };

    // LOADING
    if (loading) {
        return (
            <div className="page-container">
                <h2>Loading Admin Dashboard...</h2>
            </div>
        );
    }

    // ERROR
    if (error) {
        return (
            <div className="page-container">
                <h2>Dashboard Error</h2>
                <p>{error}</p>
                <Link to="/admin">Back to dashboard</Link>
            </div>
        );
    }

    return (
        <div>
            <nav className="navbar">
                <div className="logo">ShopSmart Admin</div>

                <div className="nav-links">
                    <Link to="/admin">Dashboard</Link>
                    <button onClick={handleLogout}>Logout</button>
                </div>
            </nav>

            <div className="page-container">
                <h1>Admin Dashboard</h1>
                <p>Manage your marketplace activities.</p>

                {message && (
                    <p style={{ color: "green" }}>{message}</p>
                )}

                {/* DELIVERY MANAGEMENT */}
                <div className="card" style={{ marginTop: "30px" }}>
                    <h2>Delivery Management</h2>
                    <p>Assign packed orders to available delivery persons.</p>

                    <h3>Orders Waiting for Delivery</h3>

                    {packedOrders.length === 0 ? (
                        <p>No packed orders waiting for delivery.</p>
                    ) : (
                        packedOrders.map(order => (
                            <div
                                key={order.id}
                                style={{
                                    borderBottom: "1px solid #ddd",
                                    padding: "20px 0",
                                }}
                            >
                                <h3>Shop Order #{order.id}</h3>

                                <p>Order ID: #{order.order_id}</p>
                                <p>Shop: {order.shop__name}</p>
                                <p>Customer: {order.order__shipping_name}</p>
                                <p>Subtotal: ₹{order.subtotal}</p>
                                <p>Status: {order.status}</p>

                                <select
                                    value={selectedPersons[order.id] || ""}
                                    onChange={(e) =>
                                        setSelectedPersons(prev => ({
                                            ...prev,
                                            [order.id]: e.target.value,
                                        }))
                                    }
                                >
                                    <option value="">
                                        Select Delivery Person
                                    </option>

                                    {deliveryPersons.map(person => (
                                        <option
                                            key={person.id}
                                            value={person.id}
                                        >
                                            {person.username}
                                        </option>
                                    ))}
                                </select>

                                <button
                                    onClick={() =>
                                        handleAssignDelivery(order.id)
                                    }
                                >
                                    Assign Delivery
                                </button>
                            </div>
                        ))
                    )}
                </div>

                {/* DASHBOARD COUNTS */}
                <div className="dashboard-grid">
                    <div className="card">
                        <h2>Pending Shops</h2>
                        <h1>{shops.length}</h1>
                    </div>

                    <div className="card">
                        <h2>Pending Products</h2>
                        <h1>{products.length}</h1>
                    </div>
                </div>

                {/* SHOP MANAGEMENT */}
                <div className="card" style={{ marginTop: "30px" }}>
                    <h2>Shop Management</h2>
                    <p>Review and approve shop registration requests.</p>

                    {shops.length === 0 ? (
                        <p>No pending shop applications.</p>
                    ) : (
                        shops.map(shop => (
                            <div
                                key={shop.id}
                                style={{
                                    borderBottom: "1px solid #ddd",
                                    padding: "20px 0",
                                }}
                            >
                                <h3>{shop.name}</h3>
                                <p>Owner: {shop.owner}</p>
                                <p>Email: {shop.email}</p>
                                <p>Phone: {shop.phone}</p>
                                <p>
                                    Location: {shop.city}, {shop.state}
                                </p>
                                <p>Description: {shop.description}</p>
                                <p>Status: {shop.status}</p>

                                <button onClick={() => handleShopApprove(shop.id)}>
                                    Approve
                                </button>

                                <button onClick={() => handleShopReject(shop.id)}>
                                    Reject
                                </button>
                            </div>
                        ))
                    )}
                </div>

                {/* PRODUCT MANAGEMENT */}
                <div className="card" style={{ marginTop: "20px" }}>
                    <h2>Product Management</h2>
                    <p>Review products submitted by shop owners.</p>

                    {products.length === 0 ? (
                        <p>No pending products.</p>
                    ) : (
                        products.map(product => (
                            <div
                                key={product.id}
                                style={{
                                    borderBottom: "1px solid #ddd",
                                    padding: "20px 0",
                                }}
                            >
                                <h3>{product.name}</h3>
                                <p>Shop: {product.shop}</p>
                                <p>Category: {product.category}</p>
                                <p>Price: ₹{product.price}</p>
                                <p>Stock: {product.stock}</p>
                                <p>Description: {product.description}</p>
                                <p>Status: {product.status}</p>

                                <button
                                    onClick={() => handleProductApprove(product.id)}
                                >
                                    Approve
                                </button>

                                <button
                                    onClick={() => handleProductReject(product.id)}
                                >
                                    Reject
                                </button>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
}

export default AdminDashboard;
