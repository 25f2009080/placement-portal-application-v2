<script setup>
import { ref } from "vue";
import { registerCompany } from "../services/auth";
import { useRouter } from "vue-router";

const form = ref({
    username: "",
    email: "",
    password: "",
    name: "",
    industry: "",
    location: "",
    website: "",
    description: "",
    hr_name: "",
    hr_email: "",
});

const router = useRouter();

const error = ref("");
const success = ref("");

const register = async () => {
    error.value = "";
    success.value = "";

    try {
        const response = await registerCompany(form.value);

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

<h2>Company Registration</h2>

<input v-model="form.username" placeholder="Username">

<input v-model="form.email" placeholder="Email">

<input
type="password"
v-model="form.password"
placeholder="Password">

<input
v-model="form.name"
placeholder="Company Name">

<input
v-model="form.industry"
placeholder="Industry">

<input
v-model="form.location"
placeholder="Location">

<input
v-model="form.website"
placeholder="Website">

<textarea
v-model="form.description"
placeholder="Description"/>

<input
v-model="form.hr_name"
placeholder="HR Name">

<input
v-model="form.hr_email"
placeholder="HR Email">

<br><br>

<button @click="register">

Register

</button>

<p style="color:green">{{ success }}</p>
<p style="color:red">{{ error }}</p>

</template>