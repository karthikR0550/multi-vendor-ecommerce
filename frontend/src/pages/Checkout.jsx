import { useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../api/axios";

function Checkout() {
    const navigate = useNavigate();

    const [form, setForm] = useState({
        shipping_name: "",
        shipping_phone: "",
        shipping_address: "",
        shipping_city: "",
        shipping_state: "",
        shipping_postal_code: "",
    });

    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const getAuthConfig = () => {
        const token = localStorage.getItem("access");

        return {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        };
    };

    const handleChange = (e) => {
        setForm({
            ...form,
            [e.target.name]: e.target.value,
        });
    };

    const loadRazorpay = () => {
        return new Promise((resolve) => {
            if (window.Razorpay) {
                resolve(true);
                return;
            }

            const script = document.createElement("script");

            script.src =
                "https://checkout.razorpay.com/v1/checkout.js";

            script.onload = () => resolve(true);
            script.onerror = () => resolve(false);

            document.body.appendChild(script);
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        setLoading(true);
        setError("");

        try {
            const loaded = await loadRazorpay();

            if (!loaded) {
                throw new Error(
                    "Unable to load Razorpay. Please try again."
                );
            }

            // Step 1: Create Razorpay order
            const response = await API.post(
                "payments/create-order/",
                {},
                getAuthConfig()
            );

            const paymentData = response.data;

            // Step 2: Configure Razorpay checkout
            const options = {
                key: paymentData.key_id,
                amount: paymentData.amount,
                currency: paymentData.currency,
                name: "ShopSmart",
                description: "Purchase Payment",
                order_id: paymentData.razorpay_order_id,

                handler: async function (paymentResponse) {
                    try {
                        setLoading(true);
                        setError("");

                        // Step 3: Verify payment and create order
                        const verifyResponse = await API.post(
                            "payments/verify/",
                            {
                                ...paymentResponse,
                                ...form,
                            },
                            getAuthConfig()
                        );

                        alert(
                            "Payment successful! Your order has been placed."
                        );

                        navigate("/orders");
                    } catch (err) {
                        console.error(
                            "Payment verification error:",
                            err.response?.data || err.message
                        );

                        setError(
                            err.response?.data?.detail ||
                            "Payment verification failed. Contact support if money was deducted."
                        );

                        setLoading(false);
                    }
                },

                prefill: {
                    name: form.shipping_name,
                    contact: form.shipping_phone,
                },

                theme: {
                    color: "#3399cc",
                },

                modal: {
                    ondismiss: function () {
                        setLoading(false);
                    },
                },
            };

            const razorpay = new window.Razorpay(options);

            razorpay.on("payment.failed", function (response) {
                console.error(
                    "Payment failed:",
                    response.error
                );

                setError(
                    response.error?.description ||
                    "Payment failed. Please try again."
                );

                setLoading(false);
            });

            razorpay.open();

            setLoading(false);

        } catch (err) {
            console.error(
                "Checkout error:",
                err.response?.data || err.message
            );

            setError(
                err.response?.data?.detail ||
                err.message ||
                "Unable to proceed with payment."
            );

            setLoading(false);
        }
    };

    return (
        <div className="form-container">
            <h2>Checkout</h2>

            <p>Enter your shipping details.</p>

            {error && (
                <p style={{ color: "red" }}>
                    {error}
                </p>
            )}

            <form onSubmit={handleSubmit}>

                <input
                    name="shipping_name"
                    placeholder="Full Name"
                    value={form.shipping_name}
                    onChange={handleChange}
                    required
                />

                <input
                    name="shipping_phone"
                    placeholder="Phone Number"
                    value={form.shipping_phone}
                    onChange={handleChange}
                    required
                />

                <input
                    name="shipping_address"
                    placeholder="Address"
                    value={form.shipping_address}
                    onChange={handleChange}
                    required
                />

                <input
                    name="shipping_city"
                    placeholder="City"
                    value={form.shipping_city}
                    onChange={handleChange}
                    required
                />

                <input
                    name="shipping_state"
                    placeholder="State"
                    value={form.shipping_state}
                    onChange={handleChange}
                    required
                />

                <input
                    name="shipping_postal_code"
                    placeholder="Postal Code"
                    value={form.shipping_postal_code}
                    onChange={handleChange}
                    required
                />

                <button
                    type="submit"
                    disabled={loading}
                >
                    {loading
                        ? "Processing..."
                        : "Proceed to Payment"}
                </button>

            </form>
        </div>
    );
}

export default Checkout;