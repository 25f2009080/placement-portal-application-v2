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
    <div>
        <h1>Login</h1>

        <input
            v-model="username"
            placeholder="Username"
        />

        <br><br>

        <input
            v-model="password"
            type="password"
            placeholder="Password"
        />

        <br><br>

        <button @click="handleLogin">
            Login
        </button>

        <br><br>

        <p>
            New user?
            <router-link to="/register">
                Register here
            </router-link>
        </p>

        <p style="color:red">
            {{ error }}
        </p>
    </div>
</template>