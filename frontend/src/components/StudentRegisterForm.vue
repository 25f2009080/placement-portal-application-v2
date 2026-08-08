<script setup>
import { ref } from "vue";
import { registerStudent } from "../services/auth";
import { useRouter } from "vue-router";

const router = useRouter();

const error = ref("");
const success = ref("");

const form = ref({
    username: "",
    email: "",
    password: "",
    student_id: "",
    name: "",
    department: "",
    phone: "",
    cgpa: ""
});

const register = async () => {
    error.value = "";
    success.value = "";

    try {
        const response = await registerStudent(form.value);

        success.value = response.data.message;

        setTimeout(() => {
            router.push("/login");
        }, 1500);

    } catch (err) {
        error.value =
            err.response?.data?.message || "Registration failed";
    }
};
</script>

<template>

<h2>Student Registration</h2>

<input v-model="form.username" placeholder="Username">

<input v-model="form.email" placeholder="Email">

<input
type="password"
v-model="form.password"
placeholder="Password">

<input
v-model="form.student_id"
placeholder="Student ID">

<input
v-model="form.name"
placeholder="Name">

<input
v-model="form.department"
placeholder="Department">

<input
v-model="form.phone"
placeholder="Phone">

<div>
    <label for="cgpa">CGPA</label>

    <input
        id="cgpa"
        v-model="form.cgpa"
        type="number"
        min="0"
        max="10"
        step="0.01"
        required
    />
</div>

<br><br>

<button @click="register">

Register

</button>

<p style="color:green">{{ success }}</p>
<p style="color:red">{{ error }}</p>

</template>