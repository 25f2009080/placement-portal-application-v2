<script setup>
import { ref, onMounted } from "vue";
import api from "../services/api";

const user = ref(null);

onMounted(async () => {
    try {
        const response = await api.get("/api/profile");
        user.value = response.data;
    } catch (err) {
        console.error(err);
    }
});
</script>

<template>
    <div>
        <h1>Student Dashboard</h1>

        <pre>{{ user }}</pre>
    </div>
</template>