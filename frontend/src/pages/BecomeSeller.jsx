
import { useState } from "react";
import { Link } from "react-router-dom";
import API from "../api/axios";

function BecomeSeller() {
    const [form, setForm] = useState({
        name: "",
        description: "",
        phone: "",
        email: "",
        address: "",
        city: "",
        state: "",
        postal_code: "",
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
            const token = localStorage.getItem("access");

            await API.post("shops/apply/", form, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });

            setMessage(
                "Shop application submitted successfully! Please wait for admin approval."
            );
        } catch (err) {
            const data = err.response?.data;
            setError(
                typeof data === "string"
                    ? data
                    : data
                        ? JSON.stringify(data)
                        : "Something went wrong. Please try again."
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="page-container">
            <h1>Become a Seller</h1>
            <p>Enter your shop details to apply for a seller account.</p>

            {message && <p style={{ color: "green" }}>{message}</p>}
            {error && <p style={{ color: "red" }}>{error}</p>}

            <form onSubmit={handleSubmit} className="card">
                <input name="name" placeholder="Shop Name" value={form.name}
                    onChange={handleChange} required />

                <textarea name="description" placeholder="Shop Description"
                    value={form.description} onChange={handleChange} />

                <input name="phone" placeholder="Phone Number" value={form.phone}
                    onChange={handleChange} required />

                <input name="email" type="email" placeholder="Email Address"
                    value={form.email} onChange={handleChange} required />

                <textarea name="address" placeholder="Full Address"
                    value={form.address} onChange={handleChange} required />

                <input name="city" placeholder="City" value={form.city}
                    onChange={handleChange} required />

                <input name="state" placeholder="State" value={form.state}
                    onChange={handleChange} required />

                <input name="postal_code" placeholder="Postal Code"
                    value={form.postal_code} onChange={handleChange} required />

                <button type="submit" disabled={loading}>
                    {loading ? "Submitting..." : "Submit Application"}
                </button>
            </form>

            <p>
                <Link to="/home">Back to Home</Link>
            </p>
        </div>
    );
}

export default BecomeSeller;
