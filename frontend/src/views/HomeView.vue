<script setup>
import { ref, onMounted } from "vue";
import api from "../services/api";

const message = ref("Connecting...");

onMounted(async () => {
    try {
        const response = await api.get("/api/test");
        message.value = response.data.message;
    } catch (error) {
        message.value = "Connection failed!";
        console.error(error);
    }
});
</script>

<template>
    <div>
        <h1>Placement Portal</h1>
        <p>{{ message }}</p>
    </div>
</template>