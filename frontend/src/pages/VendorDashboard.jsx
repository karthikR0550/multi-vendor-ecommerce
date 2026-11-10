
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import API from "../api/axios";

function VendorDashboard() {
    const navigate = useNavigate();
    const [shop, setShop] = useState(null);
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [editingId, setEditingId] = useState(null);
    const [statusFilter, setStatusFilter] = useState("ALL");

    const [editForm, setEditForm] = useState({
        name: "",
        description: "",
        category: "",
        price: "",
        stock: "",
    });

    const [message, setMessage] = useState("");
    const handleLogout = () => {
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");

        navigate("/");
    };
    const fetchDashboard = async () => {
        try {
            const [shopResponse, productResponse] =
                await Promise.all([
                    API.get("shops/my-shop/"),
                    API.get("products/my-products/"),
                ]);

            setShop(shopResponse.data);
            setProducts(productResponse.data);
        } catch (err) {
            setError(
                err.response?.data?.detail ||
                "Unable to load dashboard."
            );
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchDashboard();
    }, []);

    const handleEdit = (product) => {
        setEditingId(product.id);

        setEditForm({
            name: product.name,
            description: product.description,
            category: product.category,
            price: product.price,
            stock: product.stock,
        });

        setMessage("");
    };

    const handleEditChange = (e) => {
        setEditForm({
            ...editForm,
            [e.target.name]: e.target.value,
        });
    };

    const handleUpdate = async (id) => {
        try {
            const response = await API.patch(
                `products/my-products/${id}/`,
                {
                    ...editForm,
                    price: Number(editForm.price),
                    stock: Number(editForm.stock),
                }
            );

            setProducts(products.map(product =>
                product.id === id ? response.data : product
            ));

            setEditingId(null);
            setMessage("Product updated successfully!");
        } catch (err) {
            setMessage(
                err.response?.data?.detail ||
                "Unable to update product."
            );
        }
    };

    const handleDelete = async (id) => {
        const confirmDelete = window.confirm(
            "Are you sure you want to delete this product?"
        );

        if (!confirmDelete) return;

        try {
            await API.delete(`products/my-products/${id}/`);

            setProducts(products.filter(
                product => product.id !== id
            ));

            setMessage("Product deleted successfully!");
        } catch (err) {
            setMessage(
                err.response?.data?.detail ||
                "Unable to delete product."
            );
        }
    };

    if (loading) {
        return (
            <div className="page-container">
                <h2>Loading dashboard...</h2>
            </div>
        );
    }

    if (error) {
        return (
            <div className="page-container">
                <h2>Dashboard Error</h2>
                <p>{error}</p>
                <Link to="/home">Back to dashboard</Link>
            </div>
        );
    }

    const approvedProducts = products.filter(
        product => product.status === "APPROVED"
    );

    const pendingProducts = products.filter(
        product => product.status === "PENDING"
    );

    const rejectedProducts = products.filter(
        product => product.status === "REJECTED"
    );

    const filteredProducts = products.filter(product =>
        statusFilter === "ALL" || product.status === statusFilter
    );

    return (
        <div>
            <nav className="navbar">
                <div className="logo">ShopSmart</div>

                <div className="nav-links">

                    <Link to="/vendor">Dashboard</Link>
                    <Link to="/vendor/add-product">Add Product</Link>
                    <Link to="/vendor/orders">Orders</Link>
                    <button onClick={handleLogout}>Logout</button>
                </div>
            </nav>

            <div className="page-container">
                <h1>Shop Owner Dashboard</h1>
                <p>Welcome to your shop management dashboard.</p>

                <div className="card">
                    <h2>{shop.name}</h2>
                    <p>Shop Status: <strong>{shop.status}</strong></p>
                    <p>Location: {shop.city}, {shop.state}</p>
                </div>

                <div className="dashboard-grid">
                    <div className="card">
                        <h2>Total Products</h2>
                        <h1>{products.length}</h1>
                    </div>

                    <div className="card">
                        <h2>Approved</h2>
                        <h1>{approvedProducts.length}</h1>
                    </div>

                    <div className="card">
                        <h2>Pending</h2>
                        <h1>{pendingProducts.length}</h1>
                    </div>

                    <div className="card">
                        <h2>Rejected</h2>
                        <h1>{rejectedProducts.length}</h1>
                    </div>
                </div>

                <div className="card" style={{ marginTop: "30px" }}>
                    <h2>Product Management</h2>
                    <Link to="/vendor/add-product">
                        <button>Add New Product</button>
                    </Link>
                </div>

                <div className="card" style={{ marginTop: "20px" }}>
                    <h2>My Products</h2>

                    {message && <p>{message}</p>}

                    <label>Filter by Status: </label>

                    <select
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value)}
                    >
                        <option value="ALL">All Products</option>
                        <option value="APPROVED">Approved</option>
                        <option value="PENDING">Pending</option>
                        <option value="REJECTED">Rejected</option>
                    </select>

                    {filteredProducts.length === 0 ? (
                        <p>No products found for this status.</p>
                    ) : (
                        filteredProducts.map(product => (
                            <div
                                key={product.id}
                                style={{
                                    borderBottom: "1px solid #ddd",
                                    padding: "20px 0",
                                }}
                            >
                                {editingId === product.id ? (
                                    <div>
                                        <h3>Edit Product</h3>

                                        <label>Product Name</label>
                                        <input
                                            name="name"
                                            value={editForm.name}
                                            onChange={handleEditChange}
                                        />

                                        <label>Description</label>
                                        <textarea
                                            name="description"
                                            value={editForm.description}
                                            onChange={handleEditChange}
                                        />

                                        <label>Category</label>
                                        <input
                                            name="category"
                                            value={editForm.category}
                                            onChange={handleEditChange}
                                        />

                                        <label>Price</label>
                                        <input
                                            type="number"
                                            name="price"
                                            min="0.01"
                                            step="0.01"
                                            value={editForm.price}
                                            onChange={handleEditChange}
                                        />

                                        <label>Stock</label>
                                        <input
                                            type="number"
                                            name="stock"
                                            min="0"
                                            value={editForm.stock}
                                            onChange={handleEditChange}
                                        />

                                        <button
                                            onClick={() => handleUpdate(product.id)}
                                        >
                                            Save Changes
                                        </button>

                                        <button
                                            onClick={() => setEditingId(null)}
                                        >
                                            Cancel
                                        </button>
                                    </div>
                                ) : (
                                    <div>
                                        <h3>{product.name}</h3>
                                        <p>Category: {product.category}</p>
                                        <p>Price: ₹{product.price}</p>
                                        <p>Stock: {product.stock}</p>
                                        <p>
                                            Status: <strong>{product.status}</strong>
                                        </p>

                                        {product.status === "REJECTED" && (
                                            <p style={{ color: "red" }}>
                                                Rejection Reason: {
                                                    product.rejection_reason ||
                                                    "No reason provided"
                                                }
                                            </p>
                                        )}

                                        <button
                                            onClick={() => handleEdit(product)}
                                        >
                                            Edit
                                        </button>

                                        <button
                                            onClick={() => handleDelete(product.id)}
                                        >
                                            Delete
                                        </button>
                                    </div>
                                )}
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
}

export default VendorDashboard;
