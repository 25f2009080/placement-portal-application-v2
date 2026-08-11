<script setup>
import { ref } from "vue";

import StudentRegisterForm from "../components/StudentRegisterForm.vue";
import CompanyRegisterForm from "../components/CompanyRegisterForm.vue";

const selected = ref(null);
</script>

<template>
    <div class="min-vh-100 bg-light py-5">
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-lg-10 col-xl-9">
                    <div class="text-center mb-4">
                        <router-link
                            to="/"
                            class="text-decoration-none"
                        >
                            <h2 class="fw-bold text-primary mb-2">
                                Placement Portal
                            </h2>
                        </router-link>

                        <p class="text-secondary mb-0">
                            Create your account and get started
                        </p>
                    </div>

                    <div class="card border-0 shadow-lg rounded-4">
                        <div class="card-body p-4 p-md-5">

                            <template v-if="!selected">
                                <div class="text-center mb-5">
                                    <h2 class="fw-bold mb-2">
                                        Create an Account
                                    </h2>

                                    <p class="text-secondary mb-0">
                                        Select the account type you want to
                                        create.
                                    </p>
                                </div>

                                <div class="row g-4 justify-content-center">
                                    <div class="col-md-6">
                                        <button
                                            type="button"
                                            class="card w-100 h-100 border-2 rounded-4 text-start bg-white"
                                            @click="selected = 'student'"
                                        >
                                            <div class="card-body p-4 p-lg-5">
                                                <div
                                                    class="d-flex align-items-center justify-content-center bg-primary-subtle text-primary rounded-4 mb-4"
                                                    style="width: 64px; height: 64px;"
                                                >
                                                    <span
                                                        class="fw-bold fs-3"
                                                    >
                                                        S
                                                    </span>
                                                </div>

                                                <h3 class="fw-bold mb-2">
                                                    Student
                                                </h3>

                                                <p class="text-secondary mb-4">
                                                    Create a student profile,
                                                    upload your resume and
                                                    apply for placement
                                                    opportunities.
                                                </p>

                                                <span
                                                    class="text-primary fw-semibold"
                                                >
                                                    Register as Student →
                                                </span>
                                            </div>
                                        </button>
                                    </div>

                                    <div class="col-md-6">
                                        <button
                                            type="button"
                                            class="card w-100 h-100 border-2 rounded-4 text-start bg-white"
                                            @click="selected = 'company'"
                                        >
                                            <div class="card-body p-4 p-lg-5">
                                                <div
                                                    class="d-flex align-items-center justify-content-center bg-success-subtle text-success rounded-4 mb-4"
                                                    style="width: 64px; height: 64px;"
                                                >
                                                    <span
                                                        class="fw-bold fs-3"
                                                    >
                                                        C
                                                    </span>
                                                </div>

                                                <h3 class="fw-bold mb-2">
                                                    Company
                                                </h3>

                                                <p class="text-secondary mb-4">
                                                    Register your organization,
                                                    create placement drives
                                                    and manage applicants.
                                                </p>

                                                <span
                                                    class="text-success fw-semibold"
                                                >
                                                    Register as Company →
                                                </span>
                                            </div>
                                        </button>
                                    </div>
                                </div>
                            </template>

                            <template v-else>
                                <div class="registration-top">
                                    <button
                                        type="button"
                                        class="btn btn-outline-secondary"
                                        @click="selected = null"
                                    >
                                        ← Back
                                    </button>

                                    <span
                                        class="badge rounded-pill px-3 py-2"
                                        :class="
                                            selected === 'student'
                                                ? 'bg-primary'
                                                : 'bg-success'
                                        "
                                    >
                                        {{
                                            selected === "student"
                                                ? "Student Registration"
                                                : "Company Registration"
                                        }}
                                    </span>
                                </div>

                                <hr class="my-4">

                                <div class="registration-title text-center">
                                    <h2 class="fw-bold mb-2">
                                        {{
                                            selected === "student"
                                                ? "Student Registration"
                                                : "Company Registration"
                                        }}
                                    </h2>

                                    <p class="text-secondary mb-0">
                                        {{
                                            selected === "student"
                                                ? "Enter your details to create your student account."
                                                : "Enter your organization details to create your company account."
                                        }}
                                    </p>
                                </div>

                                <div class="registration-content">
                                    <StudentRegisterForm
                                        v-if="selected === 'student'"
                                    />

                                    <CompanyRegisterForm
                                        v-if="selected === 'company'"
                                    />
                                </div>
                            </template>

                        </div>
                    </div>

                    <div class="text-center mt-4">
                        <p class="text-secondary mb-2">
                            Already have an account?
                        </p>

                        <router-link
                            to="/login"
                            class="fw-semibold text-primary text-decoration-none"
                        >
                            Login here
                        </router-link>

                        <span class="mx-2 text-secondary">•</span>

                        <router-link
                            to="/"
                            class="text-secondary text-decoration-none"
                        >
                            Home
                        </router-link>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.registration-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.registration-top .btn {
    padding: 0.55rem 1.1rem;
    border-radius: 0.6rem;
}

.registration-top .badge {
    font-size: 0.95rem;
}

.registration-title {
    margin-bottom: 2.5rem;
}

.registration-title h2 {
    font-size: 2rem;
}

.registration-content {
    width: 100%;
    max-width: 100%;
    padding: 0 0.25rem;
}

@media (max-width: 768px) {
    .registration-top {
        gap: 1rem;
    }

    .registration-title h2 {
        font-size: 1.6rem;
    }

    .registration-title {
        margin-bottom: 2rem;
    }
}
</style>