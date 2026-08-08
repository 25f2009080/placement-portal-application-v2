<script setup>
import { useRouter } from "vue-router";
import LogoutButton from "../components/LogoutButton.vue";
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

        <hr>

        <div v-if="!authenticated">
            <h3>Welcome!</h3>

            <p>Please login or create a new account to continue.</p>

            <button @click="$router.push('/login')">
                Login
            </button>

            <button @click="$router.push('/register')">
                Register
            </button>
        </div>

        <div v-else>
            <h3>Welcome, {{ user.username }}!</h3>

            <p><strong>Role:</strong> {{ user.role }}</p>

            <button @click="goToDashboard">
                Go to Dashboard
            </button>

            <LogoutButton />
        </div>
    </div>
</template>