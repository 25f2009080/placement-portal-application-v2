<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { login } from "../services/auth";

const router = useRouter();

const username = ref("");
const password = ref("");
const error = ref("");

const handleLogin = async () => {
    error.value = "";

    try {
        const response = await login({
            username: username.value,
            password: password.value,
        });

        localStorage.setItem("token", response.data.access_token);

        localStorage.setItem(
            "user",
            JSON.stringify(response.data.user)
        );

        const role = response.data.user.role;

        if (role === "admin") {
            router.push("/admin");
        } else if (role === "company") {
            router.push("/company");
        } else {
            router.push("/student");
        }
    } catch (err) {
        error.value =
            err.response?.data?.message || "Login failed";
    }
};
</script>

<template>
    <div class="min-vh-100 bg-light d-flex align-items-center py-5">
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-sm-10 col-md-7 col-lg-5 col-xl-4">
                    <div class="text-center mb-4">
                        <router-link
                            to="/"
                            class="text-decoration-none"
                        >
                            <h2 class="fw-bold text-primary mb-2">
                                Placement Portal
                            </h2>
                        </router-link>

                        <p class="text-secondary mb-0">
                            Sign in to continue to your dashboard
                        </p>
                    </div>

                    <div class="card border-0 shadow-lg rounded-4">
                        <div class="card-body p-4 p-md-5">
                            <h3 class="fw-bold text-dark mb-1">
                                Welcome back
                            </h3>

                            <p class="text-secondary mb-4">
                                Enter your credentials to sign in.
                            </p>

                            <form @submit.prevent="handleLogin">
                                <div class="mb-3">
                                    <label
                                        for="username"
                                        class="form-label fw-semibold"
                                    >
                                        Username
                                    </label>

                                    <input
                                        id="username"
                                        v-model="username"
                                        type="text"
                                        class="form-control form-control-lg"
                                        placeholder="Enter your username"
                                        autocomplete="username"
                                        required
                                    />
                                </div>

                                <div class="mb-4">
                                    <label
                                        for="password"
                                        class="form-label fw-semibold"
                                    >
                                        Password
                                    </label>

                                    <input
                                        id="password"
                                        v-model="password"
                                        type="password"
                                        class="form-control form-control-lg"
                                        placeholder="Enter your password"
                                        autocomplete="current-password"
                                        required
                                    />
                                </div>

                                <div
                                    v-if="error"
                                    class="alert alert-danger"
                                    role="alert"
                                >
                                    {{ error }}
                                </div>

                                <button
                                    type="submit"
                                    class="btn btn-primary btn-lg w-100"
                                >
                                    Login
                                </button>
                            </form>

                            <div class="text-center mt-4">
                                <p class="text-secondary mb-2">
                                    New to the Placement Portal?
                                </p>

                                <router-link
                                    to="/register"
                                    class="fw-semibold text-primary text-decoration-none"
                                >
                                    Create an account
                                </router-link>
                            </div>
                        </div>
                    </div>

                    <div class="text-center mt-4">
                        <router-link
                            to="/"
                            class="text-secondary text-decoration-none"
                        >
                            ← Back to Home
                        </router-link>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>