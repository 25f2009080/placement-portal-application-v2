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

        await Promise.all([
            loadStats(),
            loadCompanies(),
            loadStudents(),
            loadJobs(),
            loadApplications()
        ]);

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

async function viewCompanyDetails(company) {
    selectedCompany.value = company;
}

async function closeCompanyDetails() {
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

    if (!confirm(
        `Reactivate "${job.title}"?`
    )) {
        return;
    }

    try {

        await api.put(
            `/api/admin/job/${job.id}/activate`
        );

        await loadJobs();

    } catch (err) {

        alert(
            err.response?.data?.message ||
            "Failed to reactivate job."
        );
    }
}


function getJobStatusClass(status) {

    if (status === "Active") {
        return "active";
    }

    if (status === "Pending") {
        return "pending";
    }

    return "inactive";
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
    <div class="admin-dashboard">

        <div class="header">
            <div>
                <h1>Admin Dashboard</h1>
                <p>Manage students, companies, jobs and applications.</p>
            </div>

            <button class="logout-btn" @click="handleLogout">
                Logout
            </button>
        </div>


        <div v-if="error" class="error">
            {{ error }}
        </div>


        <div v-if="loading" class="loading">
            Loading dashboard...
        </div>


        <div v-else>


            <div class="stats-grid">

                <div class="stat-card">
                    <h3>{{ stats.total_students }}</h3>
                    <p>Total Students</p>
                </div>

                <div class="stat-card">
                    <h3>{{ stats.total_companies }}</h3>
                    <p>Total Companies</p>
                </div>

                <div class="stat-card">
                    <h3>{{ stats.total_jobs }}</h3>
                    <p>Total Job Postings</p>
                </div>

                <div class="stat-card">
                    <h3>{{ stats.total_applications }}</h3>
                    <p>Total Applications</p>
                </div>

            </div>



            <section class="section">

                <div class="section-header">
                    <h2>Companies</h2>

                    <input
                        v-model="companySearch"
                        @input="searchCompanies"
                        type="text"
                        placeholder="Search by name or industry"
                    />
                </div>

                <div v-if="companies.length === 0" class="empty">
                    No companies found.
                </div>

                <div v-else class="table-container">

                    <table>
                        <thead>
                            <tr>
                                <th>Company ID</th>
                                <th>Name</th>
                                <th>Industry</th>
                                <th>Location</th>
                                <th>Status</th>
                                <th>Action</th>
                            </tr>
                        </thead>

                        <tbody>
                            <tr
                                v-for="company in companies"
                                :key="company.id"
                            >
                                <td>{{ company.company_id }}</td>
                                <td>{{ company.name }}</td>
                                <td>{{ company.industry }}</td>
                                <td>{{ company.location }}</td>

                                <td>
                                    <span
                                        v-if="!company.is_active"
                                        class="status inactive"
                                    >
                                        Deactivated
                                    </span>

                                    <span
                                        v-else-if="!company.approved"
                                        class="status pending"
                                    >
                                        Pending
                                    </span>

                                    <span
                                        v-else
                                        class="status active"
                                    >
                                        Approved
                                    </span>
                                </td>

                                <td>

                                    <button
                                        class="action-btn details"
                                        @click="viewCompanyDetails(company)"
                                    >
                                        View Details
                                    </button>

                                    <button
                                        v-if="!company.approved"
                                        class="action-btn approve"
                                        @click="approveCompany(company)"
                                    >
                                        Approve
                                    </button>

                                    <button
                                        v-else
                                        class="action-btn warning"
                                        @click="revokeCompanyApproval(company)"
                                    >
                                        Revoke Approval
                                    </button>

                                    <button
                                        v-if="company.is_active"
                                        class="action-btn danger"
                                        @click="deactivateCompany(company)"
                                    >
                                        Deactivate
                                    </button>

                                    <button
                                        v-else
                                        class="action-btn activate"
                                        @click="activateCompany(company)"
                                    >
                                        Activate
                                    </button>

                                </td>
                            </tr>
                        </tbody>
                    </table>

                </div>

            </section>



            <section class="section">

                <div class="section-header">
                    <h2>Students</h2>

                    <input
                        v-model="studentSearch"
                        @input="searchStudents"
                        type="text"
                        placeholder="Search by name, ID or contact"
                    />
                </div>

                <div v-if="students.length === 0" class="empty">
                    No students found.
                </div>

                <div v-else class="table-container">

                    <table>
                        <thead>
                            <tr>
                                <th>Student ID</th>
                                <th>Name</th>
                                <th>Department</th>
                                <th>Contact</th>
                                <th>CGPA</th>
                                <th>Status</th>
                                <th>Action</th>
                            </tr>
                        </thead>

                        <tbody>
                            <tr
                                v-for="student in students"
                                :key="student.id"
                            >
                                <td>{{ student.student_id }}</td>
                                <td>{{ student.name }}</td>
                                <td>{{ student.department }}</td>
                                <td>{{ student.phone }}</td>
                                <td>{{ student.cgpa ?? "-" }}</td>

                                <td>
                                    <span
                                        v-if="student.is_active"
                                        class="status active"
                                    >
                                        Active
                                    </span>

                                    <span
                                        v-else
                                        class="status inactive"
                                    >
                                        Blacklisted
                                    </span>
                                </td>

                                <td>

                                    <button
                                        v-if="student.is_active"
                                        class="action-btn danger"
                                        @click="deactivateStudent(student)"
                                    >
                                        Blacklist
                                    </button>

                                    <button
                                        v-else
                                        class="action-btn activate"
                                        @click="activateStudent(student)"
                                    >
                                        Activate
                                    </button>

                                </td>
                            </tr>
                        </tbody>
                    </table>

                </div>

            </section>



            <section class="section">

                <div class="section-header">
                    <h2>Job Postings</h2>
                </div>

                <div v-if="jobs.length === 0" class="empty">
                    No job postings found.
                </div>

                <div v-else class="table-container">

                    <table>
                        <thead>
                            <tr>
                                <th>Title</th>
                                <th>Company</th>
                                <th>Location</th>
                                <th>Deadline</th>
                                <th>Applications</th>
                                <th>Status</th>
                                <th>Action</th>
                            </tr>
                        </thead>

                        <tbody>
                            <tr
                                v-for="job in jobs"
                                :key="job.id"
                            >
                                <td>{{ job.title }}</td>

                                <td>
                                    {{ job.company?.name || "-" }}
                                </td>

                                <td>{{ job.location }}</td>

                                <td>{{ job.deadline }}</td>

                                <td>{{ job.application_count }}</td>

                                <td>
                                    <span
                                        class="status"
                                        :class="getJobStatusClass(job.status)"
                                    >
                                        {{ job.status }}
                                    </span>
                                </td>

                                <td>

                                    <button
                                        v-if="job.status === 'Pending'"
                                        class="action-btn approve"
                                        @click="approveJob(job)"
                                    >
                                        Approve
                                    </button>

                                    <button
                                        v-if="job.status === 'Pending'"
                                        class="action-btn danger"
                                        @click="rejectJob(job)"
                                    >
                                        Reject
                                    </button>

                                    <button
                                        v-if="
                                            job.status !== 'Inactive' &&
                                            job.status !== 'Rejected'
                                        "
                                        class="action-btn danger"
                                        @click="deactivateJob(job)"
                                    >
                                        Deactivate
                                    </button>

                                    <button
                                        v-if="job.status === 'Inactive'"
                                        class="action-btn activate"
                                        @click="activateJob(job)"
                                    >
                                        Reactivate
                                    </button>

                                </td>
                            </tr>
                        </tbody>
                    </table>

                </div>

            </section>



            <section class="section">

                <div class="section-header">
                    <h2>Applications</h2>
                </div>

                <div v-if="applications.length === 0" class="empty">
                    No applications found.
                </div>

                <div v-else class="table-container">

                    <table>
                        <thead>
                            <tr>
                                <th>Student</th>
                                <th>Student ID</th>
                                <th>Job</th>
                                <th>Company</th>
                                <th>Status</th>
                                <th>Applied At</th>
                            </tr>
                        </thead>

                        <tbody>
                            <tr
                                v-for="application in applications"
                                :key="application.id"
                            >
                                <td>
                                    {{ application.student?.name || "-" }}
                                </td>

                                <td>
                                    {{ application.student?.student_id || "-" }}
                                </td>

                                <td>
                                    {{ application.job?.title || "-" }}
                                </td>

                                <td>
                                    {{ application.job?.company || "-" }}
                                </td>

                                <td>
                                    {{ application.status }}
                                </td>

                                <td>
                                    {{ formatDate(application.applied_at) }}
                                </td>
                            </tr>
                        </tbody>
                    </table>

                </div>

            </section>

        </div>

    </div>

    <div
    v-if="selectedCompany"
    class="details-overlay"
    @click.self="closeCompanyDetails"
>

    <div class="details-card">

        <div class="details-header">
            <h2>Company Details</h2>

            <button
                class="close-btn"
                @click="closeCompanyDetails"
            >
                ×
            </button>
        </div>


        <div class="details-content">

            <div class="detail-row">
                <strong>Company ID:</strong>
                <span>{{ selectedCompany.company_id }}</span>
            </div>

            <div class="detail-row">
                <strong>Company Name:</strong>
                <span>{{ selectedCompany.name }}</span>
            </div>

            <div class="detail-row">
                <strong>Industry:</strong>
                <span>{{ selectedCompany.industry }}</span>
            </div>

            <div class="detail-row">
                <strong>Location:</strong>
                <span>{{ selectedCompany.location }}</span>
            </div>

            <div class="detail-row">
                <strong>Website:</strong>

                <span v-if="selectedCompany.website">
                    <a
                        :href="selectedCompany.website"
                        target="_blank"
                    >
                        {{ selectedCompany.website }}
                    </a>
                </span>

                <span v-else>
                    -
                </span>
            </div>

            <div class="detail-row">
                <strong>Description:</strong>
                <span>
                    {{ selectedCompany.description || "-" }}
                </span>
            </div>


            <hr>


            <h3>HR Contact</h3>

            <div class="detail-row">
                <strong>HR Name:</strong>
                <span>{{ selectedCompany.hr_name }}</span>
            </div>

            <div class="detail-row">
                <strong>HR Email:</strong>

                <span>
                    <a
                        :href="`mailto:${selectedCompany.hr_email}`"
                    >
                        {{ selectedCompany.hr_email }}
                    </a>
                </span>
            </div>


            <hr>


            <div class="detail-row">
                <strong>Status:</strong>

                <span
                    v-if="!selectedCompany.is_active"
                    class="status inactive"
                >
                    Deactivated
                </span>

                <span
                    v-else-if="!selectedCompany.approved"
                    class="status pending"
                >
                    Pending Approval
                </span>

                <span
                    v-else
                    class="status active"
                >
                    Approved & Active
                </span>
            </div>

        </div>


        <div class="details-footer">

            <button
                class="action-btn"
                @click="closeCompanyDetails"
            >
                Close
            </button>

        </div>

    </div>

    </div>

</template>



<style scoped>

.admin-dashboard {
    max-width: 1400px;
    margin: 0 auto;
    padding: 30px;
    font-family: Arial, sans-serif;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
}

.header h1 {
    margin: 0;
}

.header p {
    color: #666;
}

.logout-btn {
    padding: 10px 18px;
    border: none;
    border-radius: 6px;
    background: #333;
    color: white;
    cursor: pointer;
}

.logout-btn:hover {
    background: #111;
}

.error {
    padding: 12px;
    margin-bottom: 20px;
    background: #ffe0e0;
    color: #a00000;
    border-radius: 6px;
}

.loading {
    text-align: center;
    padding: 30px;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
    margin-bottom: 40px;
}

.stat-card {
    padding: 25px;
    background: white;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    text-align: center;
}

.stat-card h3 {
    font-size: 32px;
    margin: 0 0 8px;
}

.stat-card p {
    margin: 0;
    color: #666;
}

.section {
    margin-bottom: 40px;
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.section-header input {
    width: 300px;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 6px;
}

.table-container {
    overflow-x: auto;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

table {
    width: 100%;
    border-collapse: collapse;
}

th,
td {
    padding: 12px;
    border-bottom: 1px solid #eee;
    text-align: left;
}

th {
    background: #f5f5f5;
}

.action-btn {
    border: none;
    padding: 7px 12px;
    margin: 2px;
    border-radius: 5px;
    cursor: pointer;
}

.approve {
    background: #198754;
    color: white;
}

.activate {
    background: #0d6efd;
    color: white;
}

.danger {
    background: #dc3545;
    color: white;
}

.warning {
    background: #ffc107;
    color: #212529;
}

.status {
    display: inline-block;
    padding: 5px 9px;
    border-radius: 5px;
    font-size: 13px;
}

.active {
    background: #d1e7dd;
    color: #0f5132;
}

.pending {
    background: #fff3cd;
    color: #664d03;
}

.inactive {
    background: #f8d7da;
    color: #842029;
}

.empty {
    padding: 20px;
    text-align: center;
    color: #777;
    background: #f8f8f8;
}

.details {
    background: #6f42c1;
    color: white;
}

.details-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);

    display: flex;
    justify-content: center;
    align-items: center;

    z-index: 1000;
}

.details-card {
    width: 600px;
    max-width: 90%;
    max-height: 85vh;

    overflow-y: auto;

    background: white;
    border-radius: 10px;

    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
}

.details-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    padding: 20px;

    border-bottom: 1px solid #eee;
}

.details-header h2 {
    margin: 0;
}

.close-btn {
    border: none;
    background: transparent;

    font-size: 28px;
    cursor: pointer;

    color: #555;
}

.close-btn:hover {
    color: #000;
}

.details-content {
    padding: 20px;
}

.detail-row {
    display: grid;
    grid-template-columns: 150px 1fr;
    gap: 15px;

    padding: 10px 0;

    border-bottom: 1px solid #f0f0f0;
}

.detail-row strong {
    color: #555;
}

.details-content h3 {
    margin-top: 10px;
}

.details-content hr {
    border: none;
    border-top: 1px solid #ddd;
    margin: 20px 0;
}

.details-footer {
    padding: 15px 20px;

    border-top: 1px solid #eee;

    text-align: right;
}

@media (max-width: 900px) {

    .stats-grid {
        grid-template-columns: repeat(2, 1fr);
    }

    .section-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }

    .section-header input {
        width: 100%;
    }
}

@media (max-width: 500px) {

    .stats-grid {
        grid-template-columns: 1fr;
    }

    .admin-dashboard {
        padding: 15px;
    }
}

</style>