<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";

import api from "../services/api";
import { logout } from "../services/authService";

const router = useRouter();

const loading = ref(true);
const error = ref("");

const stats = ref({
    total_students: 0,
    total_companies: 0,
    total_jobs: 0,
    total_applications: 0
});

const companies = ref([]);
const students = ref([]);
const jobs = ref([]);
const applications = ref([]);

const companySearch = ref("");
const studentSearch = ref("");

const selectedCompany = ref(null);

async function loadDashboard() {
    loading.value = true;
    error.value = "";

    try {
        await loadStats();
        await loadCompanies();
        await loadStudents();
        await loadJobs();
        await loadApplications();
    } catch (err) {
        console.error(err);

        error.value =
            err.response?.data?.message ||
            "Failed to load admin dashboard.";
    } finally {
        loading.value = false;
    }
}

async function loadStats() {
    const response = await api.get(
        "/api/admin/dashboard"
    );

    stats.value = response.data.stats;
}

async function loadCompanies() {
    const response = await api.get(
        "/api/admin/companies",
        {
            params: {
                search: companySearch.value
            }
        }
    );

    companies.value = response.data.companies;
}

async function searchCompanies() {
    try {
        await loadCompanies();
    } catch (err) {
        console.error(err);
    }
}

async function approveCompany(company) {
    try {
        await api.put(
            `/api/admin/company/${company.id}/approve`
        );

        await loadCompanies();
        await loadStats();
    } catch (err) {
        alert(
            err.response?.data?.message ||
            "Failed to approve company."
        );
    }
}

async function revokeCompanyApproval(company) {
    if (!confirm(
        `Revoke approval for ${company.name}?`
    )) {
        return;
    }

    try {
        await api.put(
            `/api/admin/company/${company.id}/revoke`
        );

        await loadCompanies();
        await loadStats();
    } catch (err) {
        alert(
            err.response?.data?.message ||
            "Failed to revoke company approval."
        );
    }
}

async function deactivateCompany(company) {
    if (!confirm(
        `Deactivate ${company.name}?`
    )) {
        return;
    }

    try {
        await api.put(
            `/api/admin/company/${company.id}/deactivate`
        );

        await loadCompanies();
        await loadJobs();
    } catch (err) {
        alert(
            err.response?.data?.message ||
            "Failed to deactivate company."
        );
    }
}

async function activateCompany(company) {
    try {
        await api.put(
            `/api/admin/company/${company.id}/activate`
        );

        await loadCompanies();
    } catch (err) {
        alert(
            err.response?.data?.message ||
            "Failed to activate company."
        );
    }
}

function viewCompanyDetails(company) {
    selectedCompany.value = company;
}

function closeCompanyDetails() {
    selectedCompany.value = null;
}

async function loadStudents() {
    const response = await api.get(
        "/api/admin/students",
        {
            params: {
                search: studentSearch.value
            }
        }
    );

    students.value = response.data.students;
}

async function searchStudents() {
    try {
        await loadStudents();
    } catch (err) {
        console.error(err);
    }
}

async function deactivateStudent(student) {
    if (!confirm(
        `Blacklist ${student.name}?`
    )) {
        return;
    }

    try {
        await api.put(
            `/api/admin/student/${student.id}/deactivate`
        );

        await loadStudents();
    } catch (err) {
        alert(
            err.response?.data?.message ||
            "Failed to blacklist student."
        );
    }
}

async function activateStudent(student) {
    try {
        await api.put(
            `/api/admin/student/${student.id}/activate`
        );

        await loadStudents();
    } catch (err) {
        alert(
            err.response?.data?.message ||
            "Failed to activate student."
        );
    }
}

async function loadJobs() {
    const response = await api.get(
        "/api/admin/jobs"
    );

    jobs.value = response.data.jobs;
}

async function approveJob(job) {
    try {
        await api.put(
            `/api/admin/job/${job.id}/approve`
        );

        await loadJobs();
    } catch (err) {
        alert(
            err.response?.data?.message ||
            "Failed to approve job."
        );
    }
}

async function rejectJob(job) {
    if (!confirm(
        `Reject "${job.title}"?`
    )) {
        return;
    }

    try {
        await api.put(
            `/api/admin/job/${job.id}/reject`
        );

        await loadJobs();
    } catch (err) {
        alert(
            err.response?.data?.message ||
            "Failed to reject job."
        );
    }
}

async function deactivateJob(job) {
    if (!confirm(
        `Deactivate "${job.title}"?`
    )) {
        return;
    }

    try {
        await api.put(
            `/api/admin/job/${job.id}/deactivate`
        );

        await loadJobs();
    } catch (err) {
        alert(
            err.response?.data?.message ||
            "Failed to deactivate job."
        );
    }
}

async function activateJob(job) {
    try {
        await api.put(
            `/api/admin/job/${job.id}/activate`
        );

        await loadJobs();
    } catch (err) {
        alert(
            err.response?.data?.message ||
            "Failed to activate job."
        );
    }
}

function getJobStatusClass(status) {
    if (status === "Active") {
        return "bg-success-subtle text-success-emphasis";
    }

    if (status === "Pending") {
        return "bg-warning-subtle text-warning-emphasis";
    }

    if (status === "Rejected") {
        return "bg-danger-subtle text-danger-emphasis";
    }

    if (status === "Closed") {
        return "bg-secondary-subtle text-secondary-emphasis";
    }

    return "bg-danger-subtle text-danger-emphasis";
}

function getApplicationStatusClass(status) {
    if (status === "Applied") {
        return "bg-primary-subtle text-primary-emphasis";
    }

    if (status === "Shortlisted") {
        return "bg-info-subtle text-info-emphasis";
    }

    if (
        status === "Offer" ||
        status === "Placed" ||
        status === "Selected"
    ) {
        return "bg-success-subtle text-success-emphasis";
    }

    if (status === "Rejected") {
        return "bg-danger-subtle text-danger-emphasis";
    }

    return "bg-secondary-subtle text-secondary-emphasis";
}

async function loadApplications() {
    const response = await api.get(
        "/api/admin/applications"
    );

    applications.value = response.data.applications;
}

function formatDate(date) {
    if (!date) {
        return "-";
    }

    return new Date(date).toLocaleString();
}

function handleLogout() {
    logout();
    router.push("/login");
}

onMounted(() => {
    loadDashboard();
});
</script>

<template>
    <div class="admin-dashboard min-vh-100">

        <nav class="navbar navbar-dark bg-dark shadow-sm">
            <div class="container-fluid px-3 px-lg-4">
                <div class="d-flex align-items-center gap-3">
                    <div class="dashboard-logo">
                        <i class="bi bi-grid-1x2-fill"></i>
                    </div>

                    <div>
                        <div class="navbar-brand mb-0 fw-semibold">
                            Placement Portal
                        </div>

                        <div class="navbar-subtitle">
                            Administration
                        </div>
                    </div>
                </div>

                <button
                    class="btn btn-outline-light btn-sm px-3"
                    @click="handleLogout"
                >
                    <i class="bi bi-box-arrow-right me-1"></i>
                    Logout
                </button>
            </div>
        </nav>

        <main class="container-fluid px-3 px-lg-4 py-4">

            <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-end gap-3 mb-4">
                <div>
                    <div class="text-uppercase small fw-semibold text-primary mb-1">
                        Administration
                    </div>

                    <h1 class="display-6 fw-bold mb-1">
                        Admin Dashboard
                    </h1>

                    <p class="text-secondary mb-0">
                        Manage students, companies, job postings and applications.
                    </p>
                </div>

                <button
                    class="btn btn-light border shadow-sm"
                    @click="loadDashboard"
                    :disabled="loading"
                >
                    <i class="bi bi-arrow-clockwise me-1"></i>
                    Refresh
                </button>
            </div>

            <div
                v-if="error"
                class="alert alert-danger d-flex align-items-center gap-2 shadow-sm"
                role="alert"
            >
                <i class="bi bi-exclamation-triangle-fill"></i>
                <div>{{ error }}</div>
            </div>

            <div
                v-if="loading"
                class="card border-0 shadow-sm"
            >
                <div class="card-body py-5 text-center">
                    <div
                        class="spinner-border text-primary mb-3"
                        role="status"
                    ></div>

                    <div class="fw-semibold">
                        Loading dashboard...
                    </div>

                    <div class="text-secondary small mt-1">
                        Fetching the latest portal information.
                    </div>
                </div>
            </div>

            <template v-else>

                <div class="row g-3 mb-4">

                    <div class="col-12 col-sm-6 col-xl-3">
                        <div class="card stat-card border-0 shadow-sm h-100">
                            <div class="card-body p-4">
                                <div class="d-flex justify-content-between align-items-start">
                                    <div>
                                        <div class="text-secondary small fw-semibold">
                                            TOTAL STUDENTS
                                        </div>

                                        <div class="display-6 fw-bold mt-2">
                                            {{ stats.total_students }}
                                        </div>
                                    </div>

                                    <div class="stat-icon bg-primary-subtle text-primary">
                                        <i class="bi bi-mortarboard-fill"></i>
                                    </div>
                                </div>

                                <div class="small text-secondary mt-3">
                                    Registered students
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="col-12 col-sm-6 col-xl-3">
                        <div class="card stat-card border-0 shadow-sm h-100">
                            <div class="card-body p-4">
                                <div class="d-flex justify-content-between align-items-start">
                                    <div>
                                        <div class="text-secondary small fw-semibold">
                                            TOTAL COMPANIES
                                        </div>

                                        <div class="display-6 fw-bold mt-2">
                                            {{ stats.total_companies }}
                                        </div>
                                    </div>

                                    <div class="stat-icon bg-success-subtle text-success">
                                        <i class="bi bi-buildings-fill"></i>
                                    </div>
                                </div>

                                <div class="small text-secondary mt-3">
                                    Registered companies
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="col-12 col-sm-6 col-xl-3">
                        <div class="card stat-card border-0 shadow-sm h-100">
                            <div class="card-body p-4">
                                <div class="d-flex justify-content-between align-items-start">
                                    <div>
                                        <div class="text-secondary small fw-semibold">
                                            JOB POSTINGS
                                        </div>

                                        <div class="display-6 fw-bold mt-2">
                                            {{ stats.total_jobs }}
                                        </div>
                                    </div>

                                    <div class="stat-icon bg-warning-subtle text-warning">
                                        <i class="bi bi-briefcase-fill"></i>
                                    </div>
                                </div>

                                <div class="small text-secondary mt-3">
                                    Placement opportunities
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="col-12 col-sm-6 col-xl-3">
                        <div class="card stat-card border-0 shadow-sm h-100">
                            <div class="card-body p-4">
                                <div class="d-flex justify-content-between align-items-start">
                                    <div>
                                        <div class="text-secondary small fw-semibold">
                                            APPLICATIONS
                                        </div>

                                        <div class="display-6 fw-bold mt-2">
                                            {{ stats.total_applications }}
                                        </div>
                                    </div>

                                    <div class="stat-icon bg-info-subtle text-info">
                                        <i class="bi bi-file-earmark-text-fill"></i>
                                    </div>
                                </div>

                                <div class="small text-secondary mt-3">
                                    Submitted applications
                                </div>
                            </div>
                        </div>
                    </div>

                </div>

                <section class="card dashboard-section border-0 shadow-sm mb-4">

                    <div class="card-header bg-white border-0 p-4">
                        <div class="d-flex flex-column flex-lg-row justify-content-between gap-3">
                            <div>
                                <div class="d-flex align-items-center gap-2 mb-1">
                                    <i class="bi bi-buildings text-primary"></i>
                                    <h2 class="h5 fw-bold mb-0">
                                        Companies
                                    </h2>
                                </div>

                                <p class="text-secondary small mb-0">
                                    Review and manage registered companies.
                                </p>
                            </div>

                            <div class="search-box">
                                <i class="bi bi-search"></i>

                                <input
                                    v-model="companySearch"
                                    @input="searchCompanies"
                                    type="text"
                                    class="form-control"
                                    placeholder="Search name or industry"
                                >
                            </div>
                        </div>
                    </div>

                    <div
                        v-if="companies.length === 0"
                        class="card-body pt-0"
                    >
                        <div class="empty-state">
                            <i class="bi bi-buildings"></i>
                            <div class="fw-semibold mt-2">
                                No companies found
                            </div>
                            <div class="small text-secondary">
                                Try a different search term.
                            </div>
                        </div>
                    </div>

                    <div
                        v-else
                        class="table-responsive"
                    >
                        <table class="table table-hover align-middle mb-0">
                            <thead class="table-light">
                                <tr>
                                    <th class="ps-4">Company ID</th>
                                    <th>Name</th>
                                    <th>Industry</th>
                                    <th>Location</th>
                                    <th>Status</th>
                                    <th class="text-end pe-4">Actions</th>
                                </tr>
                            </thead>

                            <tbody>
                                <tr
                                    v-for="company in companies"
                                    :key="company.id"
                                >
                                    <td class="ps-4">
                                        <span class="font-monospace small">
                                            {{ company.company_id }}
                                        </span>
                                    </td>

                                    <td>
                                        <div class="fw-semibold">
                                            {{ company.name }}
                                        </div>
                                    </td>

                                    <td>
                                        <span class="text-secondary">
                                            {{ company.industry || "-" }}
                                        </span>
                                    </td>

                                    <td>
                                        {{ company.location || "-" }}
                                    </td>

                                    <td>
                                        <span
                                            v-if="!company.is_active"
                                            class="badge rounded-pill bg-danger-subtle text-danger-emphasis"
                                        >
                                            Deactivated
                                        </span>

                                        <span
                                            v-else-if="!company.approved"
                                            class="badge rounded-pill bg-warning-subtle text-warning-emphasis"
                                        >
                                            Pending
                                        </span>

                                        <span
                                            v-else
                                            class="badge rounded-pill bg-success-subtle text-success-emphasis"
                                        >
                                            Approved
                                        </span>
                                    </td>

                                    <td class="text-end pe-4">
                                        <div class="d-flex flex-wrap justify-content-end gap-1">

                                            <button
                                                class="btn btn-sm btn-outline-primary"
                                                @click="viewCompanyDetails(company)"
                                            >
                                                <i class="bi bi-eye me-1"></i>
                                                Details
                                            </button>

                                            <button
                                                v-if="!company.approved"
                                                class="btn btn-sm btn-success"
                                                @click="approveCompany(company)"
                                            >
                                                <i class="bi bi-check-lg me-1"></i>
                                                Approve
                                            </button>

                                            <button
                                                v-else
                                                class="btn btn-sm btn-outline-warning"
                                                @click="revokeCompanyApproval(company)"
                                            >
                                                <i class="bi bi-arrow-counterclockwise me-1"></i>
                                                Revoke
                                            </button>

                                            <button
                                                v-if="company.is_active"
                                                class="btn btn-sm btn-outline-danger"
                                                @click="deactivateCompany(company)"
                                            >
                                                <i class="bi bi-person-x me-1"></i>
                                                Deactivate
                                            </button>

                                            <button
                                                v-else
                                                class="btn btn-sm btn-outline-success"
                                                @click="activateCompany(company)"
                                            >
                                                <i class="bi bi-person-check me-1"></i>
                                                Activate
                                            </button>

                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                </section>

                <section class="card dashboard-section border-0 shadow-sm mb-4">

                    <div class="card-header bg-white border-0 p-4">
                        <div class="d-flex flex-column flex-lg-row justify-content-between gap-3">
                            <div>
                                <div class="d-flex align-items-center gap-2 mb-1">
                                    <i class="bi bi-mortarboard text-primary"></i>
                                    <h2 class="h5 fw-bold mb-0">
                                        Students
                                    </h2>
                                </div>

                                <p class="text-secondary small mb-0">
                                    Search and manage student accounts.
                                </p>
                            </div>

                            <div class="search-box">
                                <i class="bi bi-search"></i>

                                <input
                                    v-model="studentSearch"
                                    @input="searchStudents"
                                    type="text"
                                    class="form-control"
                                    placeholder="Search name, ID or contact"
                                >
                            </div>
                        </div>
                    </div>

                    <div
                        v-if="students.length === 0"
                        class="card-body pt-0"
                    >
                        <div class="empty-state">
                            <i class="bi bi-people"></i>
                            <div class="fw-semibold mt-2">
                                No students found
                            </div>
                            <div class="small text-secondary">
                                Try a different search term.
                            </div>
                        </div>
                    </div>

                    <div
                        v-else
                        class="table-responsive"
                    >
                        <table class="table table-hover align-middle mb-0">
                            <thead class="table-light">
                                <tr>
                                    <th class="ps-4">Student ID</th>
                                    <th>Name</th>
                                    <th>Department</th>
                                    <th>Contact</th>
                                    <th>CGPA</th>
                                    <th>Status</th>
                                    <th class="text-end pe-4">Action</th>
                                </tr>
                            </thead>

                            <tbody>
                                <tr
                                    v-for="student in students"
                                    :key="student.id"
                                >
                                    <td class="ps-4">
                                        <span class="font-monospace small">
                                            {{ student.student_id }}
                                        </span>
                                    </td>

                                    <td>
                                        <div class="fw-semibold">
                                            {{ student.name }}
                                        </div>
                                    </td>

                                    <td>
                                        {{ student.department || "-" }}
                                    </td>

                                    <td>
                                        {{ student.phone || "-" }}
                                    </td>

                                    <td>
                                        <span class="fw-semibold">
                                            {{ student.cgpa ?? "-" }}
                                        </span>
                                    </td>

                                    <td>
                                        <span
                                            v-if="student.is_active"
                                            class="badge rounded-pill bg-success-subtle text-success-emphasis"
                                        >
                                            Active
                                        </span>

                                        <span
                                            v-else
                                            class="badge rounded-pill bg-danger-subtle text-danger-emphasis"
                                        >
                                            Blacklisted
                                        </span>
                                    </td>

                                    <td class="text-end pe-4">
                                        <button
                                            v-if="student.is_active"
                                            class="btn btn-sm btn-outline-danger"
                                            @click="deactivateStudent(student)"
                                        >
                                            <i class="bi bi-person-x me-1"></i>
                                            Blacklist
                                        </button>

                                        <button
                                            v-else
                                            class="btn btn-sm btn-outline-success"
                                            @click="activateStudent(student)"
                                        >
                                            <i class="bi bi-person-check me-1"></i>
                                            Activate
                                        </button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                </section>

                <section class="card dashboard-section border-0 shadow-sm mb-4">

                    <div class="card-header bg-white border-0 p-4">
                        <div>
                            <div class="d-flex align-items-center gap-2 mb-1">
                                <i class="bi bi-briefcase text-primary"></i>

                                <h2 class="h5 fw-bold mb-0">
                                    Job Postings
                                </h2>
                            </div>

                            <p class="text-secondary small mb-0">
                                Review, approve and manage placement drives.
                            </p>
                        </div>
                    </div>

                    <div
                        v-if="jobs.length === 0"
                        class="card-body pt-0"
                    >
                        <div class="empty-state">
                            <i class="bi bi-briefcase"></i>

                            <div class="fw-semibold mt-2">
                                No job postings found
                            </div>
                        </div>
                    </div>

                    <div
                        v-else
                        class="table-responsive"
                    >
                        <table class="table table-hover align-middle mb-0">
                            <thead class="table-light">
                                <tr>
                                    <th class="ps-4">Title</th>
                                    <th>Company</th>
                                    <th>Location</th>
                                    <th>Deadline</th>
                                    <th>Applications</th>
                                    <th>Status</th>
                                    <th class="text-end pe-4">Actions</th>
                                </tr>
                            </thead>

                            <tbody>
                                <tr
                                    v-for="job in jobs"
                                    :key="job.id"
                                >
                                    <td class="ps-4">
                                        <div class="fw-semibold">
                                            {{ job.title }}
                                        </div>
                                    </td>

                                    <td>
                                        {{ job.company?.name || "-" }}
                                    </td>

                                    <td>
                                        {{ job.location || "-" }}
                                    </td>

                                    <td>
                                        <span class="small">
                                            {{ job.deadline || "-" }}
                                        </span>
                                    </td>

                                    <td>
                                        <span class="badge bg-light text-dark border">
                                            {{ job.application_count }}
                                        </span>
                                    </td>

                                    <td>
                                        <span
                                            class="badge rounded-pill"
                                            :class="getJobStatusClass(job.status)"
                                        >
                                            {{ job.status }}
                                        </span>
                                    </td>

                                    <td class="text-end pe-4">
                                        <div class="d-flex flex-wrap justify-content-end gap-1">

                                            <button
                                                v-if="job.status === 'Pending'"
                                                class="btn btn-sm btn-success"
                                                @click="approveJob(job)"
                                            >
                                                <i class="bi bi-check-lg me-1"></i>
                                                Approve
                                            </button>

                                            <button
                                                v-if="job.status === 'Pending'"
                                                class="btn btn-sm btn-outline-danger"
                                                @click="rejectJob(job)"
                                            >
                                                <i class="bi bi-x-lg me-1"></i>
                                                Reject
                                            </button>

                                            <button
                                                v-if="
                                                    job.status !== 'Inactive' &&
                                                    job.status !== 'Rejected'
                                                "
                                                class="btn btn-sm btn-outline-danger"
                                                @click="deactivateJob(job)"
                                            >
                                                <i class="bi bi-pause-circle me-1"></i>
                                                Deactivate
                                            </button>

                                            <button
                                                v-if="job.status === 'Inactive'"
                                                class="btn btn-sm btn-outline-success"
                                                @click="activateJob(job)"
                                            >
                                                <i class="bi bi-play-circle me-1"></i>
                                                Reactivate
                                            </button>

                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                </section>

                <section class="card dashboard-section border-0 shadow-sm mb-4">

                    <div class="card-header bg-white border-0 p-4">
                        <div class="d-flex align-items-center gap-2 mb-1">
                            <i class="bi bi-file-earmark-text text-primary"></i>

                            <h2 class="h5 fw-bold mb-0">
                                Applications
                            </h2>
                        </div>

                        <p class="text-secondary small mb-0">
                            Overview of applications submitted through the portal.
                        </p>
                    </div>

                    <div
                        v-if="applications.length === 0"
                        class="card-body pt-0"
                    >
                        <div class="empty-state">
                            <i class="bi bi-inbox"></i>

                            <div class="fw-semibold mt-2">
                                No applications found
                            </div>
                        </div>
                    </div>

                    <div
                        v-else
                        class="table-responsive"
                    >
                        <table class="table table-hover align-middle mb-0">
                            <thead class="table-light">
                                <tr>
                                    <th class="ps-4">Student</th>
                                    <th>Student ID</th>
                                    <th>Job</th>
                                    <th>Company</th>
                                    <th>Status</th>
                                    <th class="pe-4">Applied At</th>
                                </tr>
                            </thead>

                            <tbody>
                                <tr
                                    v-for="application in applications"
                                    :key="application.id"
                                >
                                    <td class="ps-4">
                                        <div class="fw-semibold">
                                            {{ application.student?.name || "-" }}
                                        </div>
                                    </td>

                                    <td>
                                        <span class="font-monospace small">
                                            {{ application.student?.student_id || "-" }}
                                        </span>
                                    </td>

                                    <td>
                                        {{ application.job?.title || "-" }}
                                    </td>

                                    <td>
                                        {{ application.job?.company || "-" }}
                                    </td>

                                    <td>
                                        <span
                                            class="badge rounded-pill"
                                            :class="getApplicationStatusClass(application.status)"
                                        >
                                            {{ application.status }}
                                        </span>
                                    </td>

                                    <td class="pe-4">
                                        <span class="small text-secondary">
                                            {{ formatDate(application.applied_at) }}
                                        </span>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                </section>

            </template>

        </main>

        <div
            v-if="selectedCompany"
            class="modal-backdrop-custom"
            @click.self="closeCompanyDetails"
        >
            <div class="company-modal shadow-lg">

                <div class="modal-header-custom">
                    <div class="d-flex align-items-center gap-3">
                        <div class="company-modal-icon">
                            <i class="bi bi-building"></i>
                        </div>

                        <div>
                            <div class="small text-secondary">
                                Company Profile
                            </div>

                            <h2 class="h5 fw-bold mb-0">
                                {{ selectedCompany.name }}
                            </h2>
                        </div>
                    </div>

                    <button
                        class="btn btn-sm btn-light border rounded-circle close-modal-btn"
                        @click="closeCompanyDetails"
                        aria-label="Close"
                    >
                        <i class="bi bi-x-lg"></i>
                    </button>
                </div>

                <div class="modal-body-custom">

                    <div class="row g-3">

                        <div class="col-md-6">
                            <div class="detail-box">
                                <div class="detail-label">
                                    Company ID
                                </div>

                                <div class="detail-value font-monospace">
                                    {{ selectedCompany.company_id }}
                                </div>
                            </div>
                        </div>

                        <div class="col-md-6">
                            <div class="detail-box">
                                <div class="detail-label">
                                    Industry
                                </div>

                                <div class="detail-value">
                                    {{ selectedCompany.industry || "-" }}
                                </div>
                            </div>
                        </div>

                        <div class="col-md-6">
                            <div class="detail-box">
                                <div class="detail-label">
                                    Location
                                </div>

                                <div class="detail-value">
                                    {{ selectedCompany.location || "-" }}
                                </div>
                            </div>
                        </div>

                        <div class="col-md-6">
                            <div class="detail-box">
                                <div class="detail-label">
                                    Website
                                </div>

                                <div class="detail-value">
                                    <a
                                        v-if="selectedCompany.website"
                                        :href="selectedCompany.website"
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        class="text-decoration-none"
                                    >
                                        {{ selectedCompany.website }}
                                        <i class="bi bi-box-arrow-up-right ms-1"></i>
                                    </a>

                                    <span v-else>-</span>
                                </div>
                            </div>
                        </div>

                        <div class="col-12">
                            <div class="detail-box">
                                <div class="detail-label">
                                    Description
                                </div>

                                <div class="detail-value">
                                    {{ selectedCompany.description || "No description provided." }}
                                </div>
                            </div>
                        </div>

                        <div class="col-12">
                            <div class="section-divider">
                                <span>
                                    <i class="bi bi-person-badge me-2"></i>
                                    HR Contact
                                </span>
                            </div>
                        </div>

                        <div class="col-md-6">
                            <div class="detail-box">
                                <div class="detail-label">
                                    HR Name
                                </div>

                                <div class="detail-value">
                                    {{ selectedCompany.hr_name || "-" }}
                                </div>
                            </div>
                        </div>

                        <div class="col-md-6">
                            <div class="detail-box">
                                <div class="detail-label">
                                    HR Email
                                </div>

                                <div class="detail-value">
                                    <a
                                        v-if="selectedCompany.hr_email"
                                        :href="`mailto:${selectedCompany.hr_email}`"
                                        class="text-decoration-none"
                                    >
                                        {{ selectedCompany.hr_email }}
                                    </a>

                                    <span v-else>-</span>
                                </div>
                            </div>
                        </div>

                        <div class="col-12">
                            <div class="detail-box d-flex align-items-center justify-content-between gap-3">
                                <div>
                                    <div class="detail-label">
                                        Account Status
                                    </div>

                                    <div class="small text-secondary">
                                        Current company approval and activity state
                                    </div>
                                </div>

                                <span
                                    v-if="!selectedCompany.is_active"
                                    class="badge rounded-pill bg-danger-subtle text-danger-emphasis px-3 py-2"
                                >
                                    Deactivated
                                </span>

                                <span
                                    v-else-if="!selectedCompany.approved"
                                    class="badge rounded-pill bg-warning-subtle text-warning-emphasis px-3 py-2"
                                >
                                    Pending Approval
                                </span>

                                <span
                                    v-else
                                    class="badge rounded-pill bg-success-subtle text-success-emphasis px-3 py-2"
                                >
                                    Approved & Active
                                </span>
                            </div>
                        </div>

                    </div>

                </div>

                <div class="modal-footer-custom">
                    <button
                        class="btn btn-secondary"
                        @click="closeCompanyDetails"
                    >
                        Close
                    </button>
                </div>

            </div>
        </div>

    </div>
</template>

<style scoped>
.admin-dashboard {
    background: #f5f7fb;
    color: #212529;
}

.dashboard-logo {
    width: 38px;
    height: 38px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.12);
    color: #fff;
}

.navbar-subtitle {
    color: rgba(255, 255, 255, 0.65);
    font-size: 0.72rem;
    line-height: 1;
}

.stat-card {
    transition:
        transform 0.2s ease,
        box-shadow 0.2s ease;
}

.stat-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 0.75rem 1.5rem rgba(0, 0, 0, 0.08) !important;
}

.stat-icon {
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 12px;
    font-size: 1.25rem;
}

.dashboard-section {
    overflow: hidden;
}

.dashboard-section .table {
    font-size: 0.9rem;
}

.dashboard-section .table th {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #6c757d;
    white-space: nowrap;
}

.dashboard-section .table td {
    padding-top: 0.95rem;
    padding-bottom: 0.95rem;
}

.search-box {
    position: relative;
    width: min(100%, 340px);
}

.search-box i {
    position: absolute;
    left: 0.9rem;
    top: 50%;
    transform: translateY(-50%);
    color: #6c757d;
    z-index: 2;
}

.search-box .form-control {
    padding-left: 2.5rem;
    min-height: 42px;
}

.empty-state {
    min-height: 180px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #adb5bd;
    text-align: center;
}

.empty-state > i {
    font-size: 2.2rem;
}

.modal-backdrop-custom {
    position: fixed;
    inset: 0;
    z-index: 1055;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
    background: rgba(15, 23, 42, 0.62);
    backdrop-filter: blur(3px);
}

.company-modal {
    width: 100%;
    max-width: 720px;
    max-height: 90vh;
    overflow-y: auto;
    background: #fff;
    border-radius: 16px;
}

.modal-header-custom {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    padding: 1.25rem 1.5rem;
    border-bottom: 1px solid #e9ecef;
}

.company-modal-icon {
    width: 46px;
    height: 46px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 12px;
    background: #e7f1ff;
    color: #0d6efd;
    font-size: 1.2rem;
}

.close-modal-btn {
    width: 34px;
    height: 34px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.modal-body-custom {
    padding: 1.5rem;
}

.detail-box {
    height: 100%;
    padding: 1rem;
    border: 1px solid #e9ecef;
    border-radius: 12px;
    background: #f8f9fa;
}

.detail-label {
    margin-bottom: 0.3rem;
    color: #6c757d;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

.detail-value {
    color: #212529;
    line-height: 1.5;
    overflow-wrap: anywhere;
}

.section-divider {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin: 0.25rem 0;
    color: #495057;
    font-size: 0.85rem;
    font-weight: 700;
}

.section-divider::after {
    content: "";
    flex: 1;
    height: 1px;
    background: #dee2e6;
}

.modal-footer-custom {
    display: flex;
    justify-content: flex-end;
    padding: 1rem 1.5rem;
    border-top: 1px solid #e9ecef;
}

@media (max-width: 767.98px) {
    .navbar-brand {
        font-size: 0.95rem;
    }

    .dashboard-section .table {
        min-width: 900px;
    }

    .search-box {
        width: 100%;
    }

    .modal-header-custom,
    .modal-footer-custom {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .modal-body-custom {
        padding: 1rem;
    }
}
</style>