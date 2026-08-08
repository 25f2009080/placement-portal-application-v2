<script setup>
import LogoutButton from "../components/LogoutButton.vue";
import { getCurrentUser } from "../services/authService";

const user = getCurrentUser();
</script>

<template>
    <div>
        <h1>Admin Dashboard</h1>

        <h3>Welcome, {{ user.username }}</h3>

        <p>Role: {{ user.role }}</p>

        <LogoutButton />
    </div>
</template>