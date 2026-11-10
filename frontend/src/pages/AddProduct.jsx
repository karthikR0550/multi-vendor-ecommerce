
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import API from "../api/axios";

function AddProduct() {
    const navigate = useNavigate();

    const [form, setForm] = useState({
        name: "",
        description: "",
        price: "",
        category: "",
        stock: "",
    });

    const [message, setMessage] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        setForm({
            ...form,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        setMessage("");
        setError("");
        setLoading(true);

        try {
            const response = await API.post(
                "products/create/",
                {
                    ...form,
                    price: Number(form.price),
                    stock: Number(form.stock || 0),
                }
            );

            setMessage(
                `Product "${response.data.name}" submitted successfully! Awaiting admin approval.`
            );

            setForm({
                name: "",
                description: "",
                price: "",
                category: "",
                stock: "",
            });

        } catch (err) {
            const data = err.response?.data;

            setError(
                typeof data === "string"
                    ? data
                    : data
                        ? JSON.stringify(data)
                        : "Unable to add product. Please try again."
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <nav className="navbar">
                <div className="logo">ShopSmart</div>

                <div className="nav-links">
                    <Link to="/home">Home</Link>
                    <Link to="/vendor">Dashboard</Link>
                    <Link to="/vendor/add-product">Add Product</Link>
                    <Link to="/">Logout</Link>
                </div>
            </nav>

            <div className="page-container">
                <div className="form-container">
                    <h1>Add New Product</h1>
                    <p>Enter your product details below.</p>

                    {message && (
                        <p style={{ color: "green" }}>{message}</p>
                    )}

                    {error && (
                        <p style={{ color: "red" }}>{error}</p>
                    )}

                    <form onSubmit={handleSubmit}>
                        <label>Product Name</label>
                        <input
                            type="text"
                            name="name"
                            placeholder="Enter product name"
                            value={form.name}
                            onChange={handleChange}
                            required
                        />

                        <label>Description</label>
                        <textarea
                            name="description"
                            rows="4"
                            placeholder="Describe your product"
                            value={form.description}
                            onChange={handleChange}
                            required
                        />

                        <label>Price (₹)</label>
                        <input
                            type="number"
                            name="price"
                            placeholder="Enter price"
                            min="0.01"
                            step="0.01"
                            value={form.price}
                            onChange={handleChange}
                            required
                        />

                        <label>Category</label>
                        <select
                            name="category"
                            value={form.category}
                            onChange={handleChange}
                            required
                        >
                            <option value="">Select category</option>
                            <option value="Electronics">Electronics</option>
                            <option value="Fashion">Fashion</option>
                            <option value="Home & Living">Home & Living</option>
                            <option value="Sports">Sports</option>
                        </select>

                        <label>Stock Quantity</label>
                        <input
                            type="number"
                            name="stock"
                            placeholder="Enter stock quantity"
                            min="0"
                            value={form.stock}
                            onChange={handleChange}
                            required
                        />

                        <button type="submit" disabled={loading}>
                            {loading ? "Submitting..." : "Add Product"}
                        </button>
                    </form>

                    <p style={{ marginTop: "20px" }}>
                        <Link to="/vendor">
                            Back to Dashboard
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
}

export default AddProduct;
