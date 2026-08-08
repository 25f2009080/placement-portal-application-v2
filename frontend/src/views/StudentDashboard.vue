<script setup>
import LogoutButton from "../components/LogoutButton.vue";
import { getCurrentUser } from "../services/authService";

const user = getCurrentUser();
</script>

<template>
    <div>
        <h1>Student Dashboard</h1>

        <h3>Welcome, {{ user.username }}!</h3>

        <p><strong>Email:</strong> {{ user.email }}</p>

        <p><strong>Role:</strong> {{ user.role }}</p>

        <LogoutButton />
    </div>
</template>