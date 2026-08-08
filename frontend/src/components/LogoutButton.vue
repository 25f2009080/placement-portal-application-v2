<script setup>
import { useRouter } from "vue-router";
import { logout } from "../services/authService";

const router = useRouter();

function handleLogout() {
    logout();
    router.push("/login");
}
</script>

<template>
    <button @click="handleLogout">
        Logout
    </button>
</template>