<script setup>
import { useRouter } from "vue-router";
import {
    isAuthenticated,
    getCurrentUser,
    logout,
} from "../services/authService";

const router = useRouter();

const authenticated = isAuthenticated();
const user = getCurrentUser();

function goToDashboard() {
    switch (user.role) {
        case "admin":
            router.push("/admin");
            break;

        case "company":
            router.push("/company");
            break;

        default:
            router.push("/student");
    }
}

function handleLogout() {
    logout();
    router.push("/login");
}
</script>

<template>
    <div>
        <h1>Placement Portal</h1>

        <p>
            A placement management system for Students,
            Companies and Administrators.
        </p>

        <div v-if="!authenticated">
            <button @click="$router.push('/login')">
                Login
            </button>

            <button @click="$router.push('/register')">
                Register
            </button>
        </div>

        <div v-else>
            <h3>Welcome, {{ user.username }}!</h3>

            <p>Role: {{ user.role }}</p>

            <button @click="goToDashboard">
                Go to Dashboard
            </button>

            <button @click="handleLogout">
                Logout
            </button>
        </div>
    </div>
</template>