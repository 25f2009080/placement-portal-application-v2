<script setup>
import { useRouter } from "vue-router";
import LogoutButton from "../components/LogoutButton.vue";
import {
    isAuthenticated,
    getCurrentUser,
} from "../services/authService";

const router = useRouter();

const authenticated = isAuthenticated();
const user = getCurrentUser();

function goToDashboard() {
    switch (user.role) {
        case "admin":
            router.push("/admin");
            break;

        case "company":
            router.push("/company");
            break;

        default:
            router.push("/student");
    }
}
</script>

<template>
    <div class="min-vh-100 bg-light">
        <nav class="navbar navbar-expand-lg bg-white border-bottom shadow-sm">
            <div class="container">
                <router-link
                    to="/"
                    class="navbar-brand fw-bold text-primary fs-4"
                >
                    Placement Portal
                </router-link>

                <div class="d-flex align-items-center gap-2">
                    <template v-if="!authenticated">
                        <router-link
                            to="/login"
                            class="btn btn-outline-primary px-4"
                        >
                            Login
                        </router-link>

                        <router-link
                            to="/register"
                            class="btn btn-primary px-4"
                        >
                            Register
                        </router-link>
                    </template>

                    <template v-else>
                        <button
                            class="btn btn-primary px-4"
                            @click="goToDashboard"
                        >
                            Dashboard
                        </button>

                        <LogoutButton />
                    </template>
                </div>
            </div>
        </nav>

        <main>
            <section class="py-5">
                <div class="container py-lg-5">
                    <div class="row align-items-center g-5">
                        <div class="col-lg-7">
                            <span
                                class="badge bg-primary-subtle text-primary px-3 py-2 mb-3"
                            >
                                Placement Management System
                            </span>

                            <h1 class="display-3 fw-bold text-dark mb-4">
                                Connecting
                                <span class="text-primary">
                                    Students & Companies
                                </span>
                            </h1>

                            <p class="lead text-secondary mb-4">
                                A centralized platform for managing placement
                                drives, applications, interviews and final
                                placements efficiently.
                            </p>

                            <div class="d-flex flex-wrap gap-3">
                                <template v-if="!authenticated">
                                    <router-link
                                        to="/login"
                                        class="btn btn-primary btn-lg px-4"
                                    >
                                        Get Started
                                    </router-link>

                                    <router-link
                                        to="/register"
                                        class="btn btn-outline-secondary btn-lg px-4"
                                    >
                                        Create Account
                                    </router-link>
                                </template>

                                <button
                                    v-else
                                    class="btn btn-primary btn-lg px-4"
                                    @click="goToDashboard"
                                >
                                    Go to Dashboard
                                </button>
                            </div>
                        </div>

                        <div class="col-lg-5">
                            <div class="card border-0 shadow-lg rounded-4">
                                <div class="card-body p-4 p-lg-5">
                                    <h3 class="fw-bold mb-4">
                                        One Platform, Three Roles
                                    </h3>

                                    <div class="d-flex gap-3 mb-4">
                                        <div
                                            class="bg-primary-subtle text-primary rounded-3 p-3"
                                        >
                                            <span class="fw-bold fs-5">S</span>
                                        </div>

                                        <div>
                                            <h5 class="fw-bold mb-1">
                                                Students
                                            </h5>
                                            <p class="text-secondary mb-0">
                                                Find drives, apply for jobs and
                                                track applications.
                                            </p>
                                        </div>
                                    </div>

                                    <div class="d-flex gap-3 mb-4">
                                        <div
                                            class="bg-success-subtle text-success rounded-3 p-3"
                                        >
                                            <span class="fw-bold fs-5">C</span>
                                        </div>

                                        <div>
                                            <h5 class="fw-bold mb-1">
                                                Companies
                                            </h5>
                                            <p class="text-secondary mb-0">
                                                Create drives, manage
                                                applicants and placements.
                                            </p>
                                        </div>
                                    </div>

                                    <div class="d-flex gap-3">
                                        <div
                                            class="bg-dark-subtle text-dark rounded-3 p-3"
                                        >
                                            <span class="fw-bold fs-5">A</span>
                                        </div>

                                        <div>
                                            <h5 class="fw-bold mb-1">
                                                Administrators
                                            </h5>
                                            <p class="text-secondary mb-0">
                                                Manage users, companies, jobs
                                                and placement activities.
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <section class="bg-white py-5 border-top">
                <div class="container py-4">
                    <div class="text-center mb-5">
                        <h2 class="fw-bold">Everything in One Place</h2>
                        <p class="text-secondary">
                            Manage the complete placement lifecycle through a
                            single platform.
                        </p>
                    </div>

                    <div class="row g-4">
                        <div class="col-md-4">
                            <div class="card h-100 border-0 shadow-sm rounded-4">
                                <div class="card-body p-4">
                                    <h4 class="fw-bold mb-3">
                                        Placement Drives
                                    </h4>
                                    <p class="text-secondary mb-0">
                                        Companies can create placement
                                        opportunities with eligibility,
                                        skills, salary and deadline details.
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div class="col-md-4">
                            <div class="card h-100 border-0 shadow-sm rounded-4">
                                <div class="card-body p-4">
                                    <h4 class="fw-bold mb-3">
                                        Application Tracking
                                    </h4>
                                    <p class="text-secondary mb-0">
                                        Students can monitor applications,
                                        interviews and placement status from
                                        their dashboard.
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div class="col-md-4">
                            <div class="card h-100 border-0 shadow-sm rounded-4">
                                <div class="card-body p-4">
                                    <h4 class="fw-bold mb-3">
                                        Automated Processing
                                    </h4>
                                    <p class="text-secondary mb-0">
                                        Background tasks handle interview
                                        reminders and application-history
                                        reports efficiently.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <footer class="bg-dark text-white py-4">
                <div class="container text-center">
                    <p class="mb-1 fw-semibold">
                        Placement Portal
                    </p>
                    <small class="text-white-50">
                        A centralized platform for placement management
                    </small>
                </div>
            </footer>
        </main>
    </div>
</template>