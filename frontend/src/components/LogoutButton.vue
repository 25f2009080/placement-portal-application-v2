<script setup>
import { useRouter } from "vue-router";

const router = useRouter();

function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");

    router.push("/login");
}
</script>

<template>
    <button @click="logout">
        Logout
    </button>
</template>