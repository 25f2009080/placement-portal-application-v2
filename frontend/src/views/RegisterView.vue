<script setup>
import { ref } from "vue";

import StudentRegisterForm from "../components/StudentRegisterForm.vue";
import CompanyRegisterForm from "../components/CompanyRegisterForm.vue";

const selected = ref(null);
</script>

<template>
    <div>
        <h1>Register</h1>

        <div v-if="!selected">
            <button @click="selected = 'student'">
                Register as Student
            </button>

            <button @click="selected = 'company'">
                Register as Company
            </button>
        </div>

        <StudentRegisterForm
            v-if="selected === 'student'"
        />

        <CompanyRegisterForm
            v-if="selected === 'company'"
        />
    </div>
</template>