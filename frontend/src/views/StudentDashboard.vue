<script setup>
import { ref, onMounted } from "vue";
import LogoutButton from "../components/LogoutButton.vue";
import api from "../services/api";

const student = ref(null);
const jobs = ref([]);
const applications = ref([]);

const loading = ref(true);
const jobsLoading = ref(false);
const applicationsLoading = ref(false);
const saving = ref(false);

const errorMessage = ref("");
const successMessage = ref("");

const isEditing = ref(false);

const search = ref("");
const companySearch = ref("");
const skillsSearch = ref("");
const applyingJobId = ref(null);

const resumeFile = ref(null);
const resumeUploading = ref(false);
const resumeInput = ref(null);

/* CSV EXPORT */
const exportLoading = ref(false);
const exportStatus = ref("");
const exportTaskId = ref(null);
let exportPollTimer = null;

const editForm = ref({
    name: "",
    department: "",
    phone: "",
    cgpa: "",
    skills: "",
    education: "",
    experience: ""
});


const loadProfile = async () => {
    loading.value = true;
    errorMessage.value = "";

    try {
        const response = await api.get("/api/student/profile");

        student.value = response.data.student;

        editForm.value = {
            name: student.value.name || "",
            department: student.value.department || "",
            phone: student.value.phone || "",
            cgpa: student.value.cgpa ?? "",
            skills: student.value.skills || "",
            education: student.value.education || "",
            experience: student.value.experience || ""
        };

    } catch (error) {
        errorMessage.value =
            error.response?.data?.message ||
            "Failed to load student profile.";
    } finally {
        loading.value = false;
    }
};


const loadJobs = async () => {
    jobsLoading.value = true;
    errorMessage.value = "";

    try {
        const params = {};

        if (search.value.trim()) {
            params.search = search.value.trim();
        }

        if (companySearch.value.trim()) {
            params.company = companySearch.value.trim();
        }

        if (skillsSearch.value.trim()) {
            params.skills = skillsSearch.value.trim();
        }

        const response = await api.get(
            "/api/student/jobs",
            { params }
        );

        jobs.value = response.data.jobs;

    } catch (error) {
        errorMessage.value =
            error.response?.data?.message ||
            "Failed to load jobs.";
    } finally {
        jobsLoading.value = false;
    }
};


const loadApplications = async () => {
    applicationsLoading.value = true;
    errorMessage.value = "";

    try {
        const response = await api.get(
            "/api/student/applications"
        );

        applications.value = response.data.applications;

    } catch (error) {
        errorMessage.value =
            error.response?.data?.message ||
            "Failed to load applications.";
    } finally {
        applicationsLoading.value = false;
    }
};


const applyForJob = async (job) => {
    if (!job.can_apply) {
        return;
    }

    applyingJobId.value = job.id;
    errorMessage.value = "";
    successMessage.value = "";

    try {
        const response = await api.post(
            `/api/student/jobs/${job.id}/apply`
        );

        successMessage.value =
            response.data.message ||
            "Application submitted successfully.";

        await loadJobs();
        await loadApplications();

    } catch (error) {
        errorMessage.value =
            error.response?.data?.message ||
            "Failed to submit application.";
    } finally {
        applyingJobId.value = null;
    }
};


const selectResume = (event) => {
    const file = event.target.files[0];

    if (!file) {
        resumeFile.value = null;
        return;
    }

    const allowedExtensions = ["pdf", "doc", "docx"];

    const extension = file.name
        .split(".")
        .pop()
        .toLowerCase();

    if (!allowedExtensions.includes(extension)) {
        errorMessage.value =
            "Only PDF, DOC and DOCX files are allowed.";

        event.target.value = "";
        resumeFile.value = null;
        return;
    }

    if (file.size > 5 * 1024 * 1024) {
        errorMessage.value =
            "Resume must be smaller than 5 MB.";

        event.target.value = "";
        resumeFile.value = null;
        return;
    }

    errorMessage.value = "";
    resumeFile.value = file;
};


const uploadResume = async () => {
    if (!resumeFile.value) {
        errorMessage.value =
            "Please select a resume first.";
        return;
    }

    resumeUploading.value = true;
    errorMessage.value = "";
    successMessage.value = "";

    const formData = new FormData();

    formData.append(
        "resume",
        resumeFile.value
    );

    try {
        const response = await api.post(
            "/api/student/profile/resume",
            formData
        );

        successMessage.value =
            response.data.message ||
            "Resume uploaded successfully.";

        resumeFile.value = null;

        if (resumeInput.value) {
            resumeInput.value.value = "";
        }

        await loadProfile();

    } catch (error) {

        if (error.response?.status === 413) {
            errorMessage.value =
                "Resume is too large. Maximum size is 5 MB.";
        } else {
            errorMessage.value =
                error.response?.data?.message ||
                "Failed to upload resume.";
        }

    } finally {
        resumeUploading.value = false;
    }
};


const viewResume = async () => {
    errorMessage.value = "";

    try {
        const response = await api.get(
            "/api/student/profile/resume",
            {
                responseType: "blob"
            }
        );

        const fileURL = URL.createObjectURL(
            response.data
        );

        window.open(fileURL, "_blank");

        setTimeout(() => {
            URL.revokeObjectURL(fileURL);
        }, 60000);

    } catch (error) {
        errorMessage.value =
            error.response?.data?.message ||
            "Failed to open resume.";
    }
};


const viewOfferLetter = async (application) => {
    errorMessage.value = "";

    try {
        const response = await api.get(
            `/api/student/applications/${application.id}/offer-letter`,
            {
                responseType: "blob"
            }
        );

        const fileURL = URL.createObjectURL(
            response.data
        );

        window.open(fileURL, "_blank");

        setTimeout(() => {
            URL.revokeObjectURL(fileURL);
        }, 60000);

    } catch (error) {
        errorMessage.value =
            error.response?.data?.message ||
            "Failed to open offer letter.";
    }
};


const clearSearch = () => {
    search.value = "";
    companySearch.value = "";
    skillsSearch.value = "";

    loadJobs();
};


const startEditing = () => {
    successMessage.value = "";
    errorMessage.value = "";

    editForm.value = {
        name: student.value.name || "",
        department: student.value.department || "",
        phone: student.value.phone || "",
        cgpa: student.value.cgpa ?? "",
        skills: student.value.skills || "",
        education: student.value.education || "",
        experience: student.value.experience || ""
    };

    isEditing.value = true;
};


const cancelEditing = () => {
    isEditing.value = false;
    errorMessage.value = "";
};


const saveProfile = async () => {
    saving.value = true;
    errorMessage.value = "";
    successMessage.value = "";

    try {
        const response = await api.put(
            "/api/student/profile",
            {
                name: editForm.value.name,
                department: editForm.value.department,
                phone: editForm.value.phone,
                cgpa: editForm.value.cgpa,
                skills: editForm.value.skills,
                education: editForm.value.education,
                experience: editForm.value.experience
            }
        );

        student.value = response.data.student;

        editForm.value = {
            name: student.value.name || "",
            department: student.value.department || "",
            phone: student.value.phone || "",
            cgpa: student.value.cgpa ?? "",
            skills: student.value.skills || "",
            education: student.value.education || "",
            experience: student.value.experience || ""
        };

        isEditing.value = false;
        successMessage.value = "Profile updated successfully.";

    } catch (error) {
        errorMessage.value =
            error.response?.data?.message ||
            "Failed to update profile.";
    } finally {
        saving.value = false;
    }
};


const getStatusClass = (status) => {
    switch (status) {
        case "Applied":
            return "status-applied";

        case "Shortlisted":
            return "status-shortlisted";

        case "Interview":
            return "status-interview";

        case "Offer":
            return "status-offer";

        case "Placed":
            return "status-placed";

        case "Rejected":
            return "status-rejected";

        default:
            return "status-default";
    }
};


const formatUTCDateTime = (value) => {
    if (!value) {
        return "-";
    }

    const utcValue =
        value.endsWith("Z") ? value : `${value}Z`;

    const date = new Date(utcValue);

    if (isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleString("en-IN", {
        dateStyle: "medium",
        timeStyle: "short"
    });
};


const formatLocalDateTime = (value) => {
    if (!value) {
        return "-";
    }

    const date = new Date(value);

    if (isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleString("en-IN", {
        dateStyle: "medium",
        timeStyle: "short"
    });
};


/* =========================
   CSV EXPORT
   ========================= */

const startExport = async () => {
    exportLoading.value = true;
    exportStatus.value = "Starting export...";
    errorMessage.value = "";
    successMessage.value = "";

    try {
        const response = await api.post(
            "/api/student/export-history"
        );

        exportTaskId.value = response.data.task_id;

        exportStatus.value =
            "Export started. Preparing your CSV...";

        pollExportStatus();

    } catch (error) {
        exportLoading.value = false;
        exportStatus.value = "";

        errorMessage.value =
            error.response?.data?.message ||
            "Failed to start CSV export.";
    }
};


const pollExportStatus = () => {
    if (exportPollTimer) {
        clearTimeout(exportPollTimer);
    }

    exportPollTimer = setTimeout(
        checkExportStatus,
        1000
    );
};


const checkExportStatus = async () => {
    if (!exportTaskId.value) {
        return;
    }

    try {
        const response = await api.get(
            `/api/student/export-history/status/${exportTaskId.value}`
        );

        const status = response.data.status;

        if (
            status === "PENDING" ||
            status === "STARTED"
        ) {
            exportStatus.value =
                "Export is still being prepared...";

            pollExportStatus();
            return;
        }

        if (status === "SUCCESS") {

            exportStatus.value =
                "Export completed. Downloading...";

            await downloadExport();

            exportLoading.value = false;

            exportStatus.value =
                "CSV export completed successfully.";

            successMessage.value =
                `Export completed. ${response.data.records || 0} records exported.`;

            return;
        }

        exportLoading.value = false;
        exportStatus.value = "";

        errorMessage.value =
            response.data.message ||
            "CSV export failed.";

    } catch (error) {
        exportLoading.value = false;
        exportStatus.value = "";

        errorMessage.value =
            error.response?.data?.message ||
            "Failed to check export status.";
    }
};


const downloadExport = async () => {

    const response = await api.get(
        `/api/student/export-history/download/${exportTaskId.value}`,
        {
            responseType: "blob"
        }
    );

    const blob = new Blob(
        [response.data],
        {
            type: "text/csv"
        }
    );

    const url = window.URL.createObjectURL(blob);

    const link = document.createElement("a");

    link.href = url;

    const disposition =
        response.headers["content-disposition"];

    if (disposition) {
        const filenameMatch =
            disposition.match(
                /filename="?([^"]+)"?/
            );

        if (filenameMatch) {
            link.download = filenameMatch[1];
        }
    }

    if (!link.download) {
        link.download = "application_history.csv";
    }

    document.body.appendChild(link);

    link.click();

    document.body.removeChild(link);

    window.URL.revokeObjectURL(url);
};


onMounted(async () => {
    await loadProfile();
    await loadJobs();
    await loadApplications();
});
</script>


<template>
    <div class="dashboard">

        <div class="header">

            <div>
                <h1>Student Dashboard</h1>

                <p v-if="student">
                    Welcome, {{ student.name }}!
                </p>
            </div>

            <LogoutButton />

        </div>



        <div
            v-if="errorMessage"
            class="error-message"
        >
            {{ errorMessage }}
        </div>

        <div
            v-if="successMessage"
            class="success-message"
        >
            {{ successMessage }}
        </div>



        <div
            v-if="loading"
            class="message"
        >
            Loading profile...
        </div>


        <div v-else>

            <div
                v-if="student && !isEditing"
                class="profile-section"
            >

                <div class="section-header">

                    <h2>My Profile</h2>

                    <button
                        class="edit-button"
                        @click="startEditing"
                    >
                        Edit Profile
                    </button>

                </div>


                <div class="profile-grid">

                    <div class="profile-item">
                        <label>Student ID</label>
                        <p>{{ student.student_id || "-" }}</p>
                    </div>


                    <div class="profile-item">
                        <label>Name</label>
                        <p>{{ student.name || "-" }}</p>
                    </div>


                    <div class="profile-item">
                        <label>Department</label>
                        <p>{{ student.department || "-" }}</p>
                    </div>


                    <div class="profile-item">
                        <label>Email</label>
                        <p>{{ student.email || "-" }}</p>
                    </div>


                    <div class="profile-item">
                        <label>Phone</label>
                        <p>{{ student.phone || "-" }}</p>
                    </div>


                    <div class="profile-item">
                        <label>CGPA</label>
                        <p>{{ student.cgpa ?? "-" }}</p>
                    </div>


                    <div class="profile-item full-width">
                        <label>Skills</label>
                        <p>{{ student.skills || "-" }}</p>
                    </div>


                    <div class="profile-item full-width">
                        <label>Education</label>
                        <p>{{ student.education || "-" }}</p>
                    </div>

                    <div class="profile-item full-width">
                        <label>Experience</label>
                        <p>{{ student.experience || "No experience needed" }}</p>
                    </div>


                    <div class="profile-item full-width">

                        <label>Resume</label>

                        <div
                            v-if="student.resume"
                            class="resume-status uploaded"
                        >
                            <div class="resume-current">

                                <span>
                                    Resume uploaded
                                </span>

                                <button
                                    type="button"
                                    class="view-resume-button"
                                    @click="viewResume"
                                >
                                    View Resume
                                </button>

                            </div>
                        </div>

                        <div
                            v-else
                            class="resume-status not-uploaded"
                        >
                            <span>
                                No resume uploaded
                            </span>
                        </div>


                        <div class="resume-upload">

                            <input
                                ref="resumeInput"
                                type="file"
                                accept=".pdf,.doc,.docx"
                                @change="selectResume"
                            />


                            <p
                                v-if="resumeFile"
                                class="selected-file"
                            >
                                Selected:
                                {{ resumeFile.name }}
                            </p>


                            <button
                                type="button"
                                class="resume-upload-button"
                                @click="uploadResume"
                                :disabled="
                                    !resumeFile ||
                                    resumeUploading
                                "
                            >
                                {{
                                    resumeUploading
                                        ? "Uploading..."
                                        : student.resume
                                            ? "Update Resume"
                                            : "Upload Resume"
                                }}
                            </button>


                            <small>
                                PDF, DOC or DOCX — maximum 5 MB
                            </small>

                        </div>

                    </div>

                </div>

            </div>



            <div
                v-if="student && isEditing"
                class="profile-section"
            >

                <div class="section-header">

                    <h2>Edit Profile</h2>

                </div>


                <form @submit.prevent="saveProfile">

                    <div class="form-grid">

                        <div class="form-group">

                            <label>Student ID</label>

                            <input
                                :value="student.student_id"
                                type="text"
                                disabled
                            />

                        </div>


                        <div class="form-group">

                            <label>Email</label>

                            <input
                                :value="student.email"
                                type="email"
                                disabled
                            />

                        </div>


                        <div class="form-group">

                            <label>Name</label>

                            <input
                                v-model="editForm.name"
                                type="text"
                                required
                            />

                        </div>


                        <div class="form-group">

                            <label>Department</label>

                            <input
                                v-model="editForm.department"
                                type="text"
                                required
                            />

                        </div>


                        <div class="form-group">

                            <label>Phone</label>

                            <input
                                v-model="editForm.phone"
                                type="text"
                                required
                            />

                        </div>


                        <div class="form-group">

                            <label>CGPA</label>

                            <input
                                v-model="editForm.cgpa"
                                type="number"
                                min="0"
                                max="10"
                                step="0.01"
                                required
                            />

                        </div>


                        <div class="form-group full-width">

                            <label>Skills</label>

                            <textarea
                                v-model="editForm.skills"
                                rows="3"
                                placeholder="Example: Python, C, SQL, Vue"
                            ></textarea>

                        </div>


                        <div class="form-group full-width">

                            <label>Education</label>

                            <textarea
                                v-model="editForm.education"
                                rows="3"
                                placeholder="Enter your educational details"
                            ></textarea>

                        </div>


                        <div class="form-group full-width">

                            <label>Experience</label>

                            <textarea
                                v-model="editForm.experience"
                                rows="4"
                                placeholder="Experience Summary"
                            ></textarea>

                        </div>

                    </div>


                    <div class="form-actions">

                        <button
                            type="submit"
                            class="save-button"
                            :disabled="saving"
                        >
                            {{ saving ? "Saving..." : "Save Changes" }}
                        </button>

                        <button
                            type="button"
                            class="cancel-button"
                            @click="cancelEditing"
                            :disabled="saving"
                        >
                            Cancel
                        </button>

                    </div>

                </form>

            </div>


            <div class="jobs-section">

                <div class="section-header">

                    <h2>Placement Drives</h2>

                </div>


                <div class="search-panel">

                    <div class="search-field">

                        <label>Search</label>

                        <input
                            v-model="search"
                            type="text"
                            placeholder="Company, position or skill"
                            @keyup.enter="loadJobs"
                        />

                    </div>


                    <div class="search-field">

                        <label>Company</label>

                        <input
                            v-model="companySearch"
                            type="text"
                            placeholder="Company name"
                            @keyup.enter="loadJobs"
                        />

                    </div>


                    <div class="search-field">

                        <label>Required Skills</label>

                        <input
                            v-model="skillsSearch"
                            type="text"
                            placeholder="Example: Python"
                            @keyup.enter="loadJobs"
                        />

                    </div>


                    <div class="search-actions">

                        <button
                            class="search-button"
                            @click="loadJobs"
                        >
                            Search
                        </button>


                        <button
                            class="reset-button"
                            @click="clearSearch"
                        >
                            Reset
                        </button>

                    </div>

                </div>



                <div
                    v-if="jobsLoading"
                    class="message"
                >
                    Loading placement drives...
                </div>



                <div
                    v-else-if="jobs.length === 0"
                    class="empty-message"
                >
                    No placement drives found.
                </div>



                <div
                    v-else
                    class="jobs-grid"
                >

                    <div
                        v-for="job in jobs"
                        :key="job.id"
                        class="job-card"
                    >

                        <div class="job-header">

                            <div>

                                <h3>
                                    {{ job.title }}
                                </h3>

                                <p class="company-name">
                                    {{ job.company.name }}
                                </p>

                            </div>


                            <span class="status-badge">
                                {{ job.status }}
                            </span>

                        </div>


                        <div class="job-details">

                            <div>
                                <strong>Location:</strong>
                                {{ job.location || "-" }}
                            </div>


                            <div>
                                <strong>Salary:</strong>

                                <span v-if="job.salary !== null">
                                    ₹{{ job.salary }}
                                </span>

                                <span v-else>
                                    Not specified
                                </span>

                            </div>


                            <div>
                                <strong>Experience:</strong>
                                {{ job.experience || "-" }}
                            </div>


                            <div>
                                <strong>Minimum CGPA:</strong>
                                {{ job.min_cgpa ?? "No minimum" }}
                            </div>


                            <div>
                                <strong>Deadline:</strong>
                                {{ job.deadline }}
                            </div>


                            <div>
                                <strong>Applications:</strong>

                                {{ job.application_count }}

                                <span v-if="job.application_limit">
                                    / {{ job.application_limit }}
                                </span>

                                <span v-else>
                                    / Unlimited
                                </span>

                            </div>

                        </div>


                        <div class="job-description">

                            <strong>Description</strong>

                            <p>
                                {{ job.description || "-" }}
                            </p>

                        </div>


                        <div class="job-info">

                            <strong>Required Skills</strong>

                            <p>
                                {{ job.skills_required || "-" }}
                            </p>

                        </div>


                        <div class="job-info">

                            <strong>Benefits</strong>

                            <p>
                                {{ job.benefits || "-" }}
                            </p>

                        </div>


                        <div class="company-info">

                            <strong>Company</strong>

                            <p>
                                {{ job.company.name }}
                            </p>


                            <p v-if="job.company.industry">
                                Industry:
                                {{ job.company.industry }}
                            </p>


                            <p v-if="job.company.location">
                                Location:
                                {{ job.company.location }}
                            </p>

                        </div>



                        <div class="application-state">

                            <div
                                v-if="job.already_applied"
                                class="state already-applied"
                            >
                                Already Applied
                            </div>


                            <div
                                v-else-if="!job.cgpa_eligible"
                                class="state not-eligible"
                            >
                                CGPA requirement not met
                            </div>


                            <div
                                v-else-if="job.application_limit_reached"
                                class="state limit-reached"
                            >
                                Application limit reached
                            </div>


                            <div
                                v-else
                                class="apply-section"
                            >

                                <div class="state eligible">
                                    You are Eligible to apply
                                </div>


                                <button
                                    class="apply-button"
                                    @click="applyForJob(job)"
                                    :disabled="applyingJobId === job.id"
                                >
                                    {{
                                        applyingJobId === job.id
                                            ? "Applying..."
                                            : "Apply now"
                                    }}
                                </button>

                            </div>

                        </div>

                    </div>

                </div>

            </div>


            <div class="applications-section">

                <div class="section-header">

                    <h2>My Applications</h2>

                    <button
                        class="export-button"
                        @click="startExport"
                        :disabled="exportLoading"
                    >
                        {{
                            exportLoading
                                ? "Exporting..."
                                : "Export Application History"
                        }}
                    </button>

                </div>

                <p
                    v-if="exportStatus"
                    class="export-status"
                >
                    {{ exportStatus }}
                </p>


                <div
                    v-if="applicationsLoading"
                    class="message"
                >
                    Loading applications...
                </div>


                <div
                    v-else-if="applications.length === 0"
                    class="empty-message"
                >
                    You have not applied for any jobs yet.
                </div>


                <div
                    v-else
                    class="applications-list"
                >

                    <div
                        v-for="application in applications"
                        :key="application.id"
                        class="application-card"
                    >

                        <div class="application-header">

                            <div>

                                <h3>
                                    {{ application.job.title }}
                                </h3>


                                <p class="company-name">
                                    {{
                                        application.company
                                            ? application.company.name
                                            : "Company unavailable"
                                    }}
                                </p>

                            </div>


                            <span
                                class="application-status"
                                :class="
                                    getStatusClass(
                                        application.status
                                    )
                                "
                            >
                                {{ application.status }}
                            </span>

                        </div>


                        <div class="application-details">

                            <div>

                                <strong>Location:</strong>

                                {{
                                    application.job.location || "-"
                                }}

                            </div>


                            <div>

                                <strong>Salary:</strong>

                                <span
                                    v-if="
                                        application.job.salary !== null
                                    "
                                >
                                    ₹{{ application.job.salary }}
                                </span>

                                <span v-else>
                                    Not specified
                                </span>

                            </div>


                            <div>

                                <strong>Experience:</strong>

                                {{
                                    application.job.experience || "-"
                                }}

                            </div>


                            <div>

                                <strong>Applied On:</strong>

                                {{
                                    formatUTCDateTime(
                                        application.applied_at
                                    )
                                }}

                            </div>


                            <div>

                                <strong>Last Updated:</strong>

                                {{
                                    formatUTCDateTime(
                                        application.updated_at
                                    )
                                }}

                            </div>


                            <div>

                                <strong>Job Deadline:</strong>

                                {{
                                    application.job.deadline || "-"
                                }}

                            </div>

                        </div>


                        <div
                            v-if="application.company"
                            class="application-info"
                        >

                            <h4>Company Information</h4>


                            <p>
                                <strong>Name:</strong>
                                {{ application.company.name }}
                            </p>


                            <p
                                v-if="application.company.industry"
                            >
                                <strong>Industry:</strong>
                                {{ application.company.industry }}
                            </p>


                            <p
                                v-if="application.company.location"
                            >
                                <strong>Location:</strong>
                                {{ application.company.location }}
                            </p>


                            <p
                                v-if="application.company.website"
                            >
                                <strong>Website:</strong>

                                {{ application.company.website }}
                            </p>

                        </div>


                        <div
                            v-if="application.remarks"
                            class="application-info feedback"
                        >

                            <h4>Company Feedback</h4>

                            <p>
                                {{ application.remarks }}
                            </p>

                        </div>



                        <div
                            v-if="
                                application.interview &&
                                application.interview.datetime
                            "
                            class="interview-section"
                        >

                            <h4>Interview Schedule</h4>


                            <div class="interview-details">

                                <div>

                                    <strong>
                                        Date & Time:
                                    </strong>

                                    {{
                                        formatLocalDateTime(
                                            application.interview
                                                .datetime
                                        )
                                    }}

                                </div>


                                <div
                                    v-if="
                                        application.interview.mode
                                    "
                                >

                                    <strong>Mode:</strong>

                                    {{
                                        application.interview.mode
                                    }}

                                </div>


                                <div
                                    v-if="
                                        application.interview.location
                                    "
                                >

                                    <strong>
                                        Location / Link:
                                    </strong>

                                    {{
                                        application.interview.location
                                    }}

                                </div>


                                <div
                                    v-if="
                                        application.interview.notes
                                    "
                                >

                                    <strong>Notes:</strong>

                                    {{
                                        application.interview.notes
                                    }}

                                </div>

                            </div>

                        </div>


                        <div
                            v-else-if="
                                application.status ===
                                'Shortlisted'
                            "
                            class="waiting-message"
                        >
                            Interview has not been scheduled yet.
                        </div>


                        <div
                            v-if="
                                application.status ===
                                'Offer'
                            "
                            class="result-message selected-result"
                        >

                            <strong>
                                🎉 Offer Received!
                            </strong>

                            <p>
                                You have received an offer for this
                                placement opportunity.
                            </p>

                            <div
                                v-if="
                                    application.placement &&
                                    application.placement.offer_letter
                                "
                                class="offer-letter-section"
                            >
                                <strong>Offer Letter</strong>

                                <p>
                                    Your offer letter is available.
                                </p>

                                <button
                                    type="button"
                                    class="view-offer-letter-button"
                                    @click="
                                        viewOfferLetter(application)
                                    "
                                >
                                    View Offer Letter
                                </button>
                            </div>

                        </div>


                        <div
                            v-if="
                                application.status ===
                                'Placed'
                            "
                            class="result-message placed-result"
                        >

                            <strong>
                                🎉 Congratulations! You are Placed.
                            </strong>

                            <p>
                                Your placement has been confirmed.
                            </p>

                            <div
                                v-if="application.placement"
                                class="placement-details"
                            >

                                <p>
                                    <strong>Position:</strong>
                                    {{ application.placement.position || "-" }}
                                </p>

                                <p>
                                    <strong>Salary:</strong>
                                    <span
                                        v-if="application.placement.salary !== null"
                                    >
                                        ₹{{ application.placement.salary }}
                                    </span>
                                    <span v-else>
                                        Not specified
                                    </span>
                                </p>

                                <p
                                    v-if="application.placement.joining_date"
                                >
                                    <strong>Joining Date:</strong>
                                    {{ application.placement.joining_date }}
                                </p>

                                <div
                                    v-if="
                                        application.placement.offer_letter
                                    "
                                    class="offer-letter-section"
                                >
                                    <strong>Offer Letter</strong>

                                    <p>
                                        Your offer letter is available.
                                    </p>

                                    <button
                                        type="button"
                                        class="view-offer-letter-button"
                                        @click="
                                            viewOfferLetter(application)
                                        "
                                    >
                                        View Offer Letter
                                    </button>

                                </div>

                            </div>

                        </div>


                        <div
                            v-if="
                                application.status ===
                                'Rejected'
                            "
                            class="result-message rejected-result"
                        >

                            <strong>
                                Application Rejected
                            </strong>

                            <p>
                                Your application was not selected
                                for this opportunity.
                            </p>

                        </div>


                        <div
                            v-if="
                                application.status ===
                                'Interview'
                            "
                            class="waiting-message interview-status-message"
                        >
                            Your interview has been scheduled. Please
                            attend the interview at the scheduled date
                            and time.
                        </div>


                        <div
                            v-if="
                                application.status ===
                                'Applied'
                            "
                            class="waiting-message"
                        >
                            Your application is currently under
                            review by the company.
                        </div>


                        <div
                            v-if="
                                application.status ===
                                'Shortlisted'
                            "
                            class="waiting-message shortlisted-message"
                        >
                            You have been shortlisted. Please check
                            the interview details above.
                        </div>

                    </div>

                </div>

            </div>

        </div>

    </div>
</template>


<style scoped>

.dashboard {
    max-width: 1200px;
    margin: 0 auto;
    padding: 30px;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
}

.header h1 {
    margin-bottom: 5px;
}

.header p {
    margin: 0;
    color: #666;
}

.profile-section,
.jobs-section,
.applications-section {
    background: #ffffff;
    border: 1px solid #ddd;
    border-radius: 10px;
    padding: 25px;
    margin-bottom: 25px;
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
}

.section-header h2 {
    margin: 0;
}

.profile-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
}

.profile-item {
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;
}

.profile-item.full-width {
    grid-column: span 2;
}

.profile-item label {
    display: block;
    font-weight: bold;
    margin-bottom: 7px;
}

.profile-item p {
    margin: 0;
    color: #444;
    white-space: pre-wrap;
}

.resume-status {
    padding: 10px;
    border-radius: 6px;
    margin-top: 5px;
}

.resume-status.uploaded {
    background: #d1e7dd;
    color: #0f5132;
}

.resume-status.not-uploaded {
    background: #fff3cd;
    color: #664d03;
}


.edit-button,
.save-button,
.cancel-button,
.search-button,
.reset-button {
    border: none;
    border-radius: 6px;
    padding: 10px 18px;
    cursor: pointer;
    font-size: 14px;
}

.edit-button {
    background: #0d6efd;
    color: white;
}

.save-button {
    background: #198754;
    color: white;
}

.cancel-button {
    background: #6c757d;
    color: white;
}

.search-button {
    background: #0d6efd;
    color: white;
}

.reset-button {
    background: #6c757d;
    color: white;
}

.edit-button:hover,
.save-button:hover,
.cancel-button:hover,
.search-button:hover,
.reset-button:hover {
    opacity: 0.9;
}

.edit-button:disabled,
.save-button:disabled,
.cancel-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}


.form-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
}

.form-group {
    display: flex;
    flex-direction: column;
}

.form-group.full-width {
    grid-column: span 2;
}

.form-group label {
    font-weight: bold;
    margin-bottom: 7px;
}

.form-group input,
.form-group textarea {
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 6px;
    font-size: 14px;
    font-family: inherit;
}

.form-group input:disabled {
    background: #e9ecef;
    cursor: not-allowed;
}

.form-actions {
    display: flex;
    gap: 10px;
    margin-top: 25px;
}


.search-panel {
    display: grid;
    grid-template-columns: 1.5fr 1fr 1fr auto;
    gap: 15px;
    align-items: end;
    background: #f8f9fa;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 25px;
}

.search-field {
    display: flex;
    flex-direction: column;
}

.search-field label {
    font-weight: bold;
    margin-bottom: 7px;
}

.search-field input {
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 6px;
}

.search-actions {
    display: flex;
    gap: 8px;
}


.jobs-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
}

.job-card {
    border: 1px solid #ddd;
    border-radius: 10px;
    padding: 20px;
    background: #fff;
}

.job-header {
    display: flex;
    justify-content: space-between;
    gap: 15px;
    margin-bottom: 20px;
}

.job-header h3 {
    margin: 0 0 5px;
}

.company-name {
    margin: 0;
    font-weight: bold;
    color: #555;
}

.status-badge {
    background: #198754;
    color: white;
    padding: 5px 10px;
    border-radius: 15px;
    font-size: 12px;
    height: fit-content;
}

.job-details {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-bottom: 20px;
}

.job-description,
.job-info,
.company-info {
    margin-bottom: 18px;
}

.job-description p,
.job-info p,
.company-info p {
    margin: 6px 0 0;
    white-space: pre-wrap;
}

.company-info {
    padding-top: 15px;
    border-top: 1px solid #eee;
}



.application-state {
    margin-top: 20px;
}

.state {
    padding: 10px;
    border-radius: 6px;
    text-align: center;
    font-weight: bold;
}

.already-applied {
    background: #cff4fc;
    color: #055160;
}

.not-eligible {
    background: #f8d7da;
    color: #842029;
}

.limit-reached {
    background: #fff3cd;
    color: #664d03;
}

.eligible {
    background: #d1e7dd;
    color: #0f5132;
}

.apply-section {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.apply-button {
    width: 100%;
    padding: 11px;
    border: none;
    border-radius: 6px;
    background: #0d6efd;
    color: white;
    font-size: 15px;
    font-weight: bold;
    cursor: pointer;
}

.apply-button:hover {
    opacity: 0.9;
}

.apply-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}


.applications-list {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.application-card {
    border: 1px solid #ddd;
    border-radius: 10px;
    padding: 20px;
    background: #fff;
}

.application-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 15px;
    margin-bottom: 20px;
}

.application-header h3 {
    margin: 0 0 5px;
}

.application-status {
    padding: 7px 14px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: bold;
    white-space: nowrap;
}

.status-applied {
    background: #cff4fc;
    color: #055160;
}

.status-shortlisted {
    background: #fff3cd;
    color: #664d03;
}

.status-interview {
    background: #e7f1ff;
    color: #084298;
}

.status-offer {
    background: #d1e7dd;
    color: #0f5132;
}

.status-placed {
    background: #198754;
    color: #ffffff;
}

.status-rejected {
    background: #f8d7da;
    color: #842029;
}

.status-default {
    background: #e2e3e5;
    color: #41464b;
}

.application-details {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;
    margin-bottom: 20px;
}

.application-info {
    padding: 15px 0;
    border-top: 1px solid #eee;
}

.application-info h4,
.interview-section h4 {
    margin: 0 0 10px;
}

.application-info p {
    margin: 5px 0;
}

.feedback {
    background: #fff3cd;
    padding: 15px;
    border-radius: 8px;
    border-top: none;
    margin-bottom: 15px;
}

.interview-section {
    margin-top: 15px;
    padding: 15px;
    background: #e7f1ff;
    border-radius: 8px;
}

.interview-details {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.waiting-message {
    margin-top: 15px;
    padding: 12px;
    background: #f8f9fa;
    border-radius: 6px;
    color: #555;
}

.shortlisted-message {
    background: #fff3cd;
    color: #664d03;
}

.result-message {
    margin-top: 15px;
    padding: 12px;
    border-radius: 6px;
}

.result-message strong {
    display: block;
    margin-bottom: 5px;
}

.result-message p {
    margin: 0;
}

.offer-result {
    background: #d1e7dd;
    color: #0f5132;
}

.placed-result {
    background: #198754;
    color: #ffffff;
}

.placement-details {
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid rgba(255, 255, 255, 0.35);
}

.placement-details p {
    margin: 6px 0;
}

.rejected-result {
    background: #f8d7da;
    color: #842029;
}


/* CSV EXPORT */

.export-button {
    border: none;
    border-radius: 6px;
    padding: 10px 18px;
    background: #198754;
    color: white;
    cursor: pointer;
    font-size: 14px;
    font-weight: bold;
}

.export-button:hover {
    opacity: 0.9;
}

.export-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.export-status {
    margin: 0 0 20px;
    padding: 10px 14px;
    background: #e7f1ff;
    color: #084298;
    border-radius: 6px;
}


.message {
    padding: 20px;
    text-align: center;
}

.empty-message {
    padding: 30px;
    text-align: center;
    color: #666;
    background: #f8f9fa;
    border-radius: 8px;
}

.error-message {
    background: #f8d7da;
    color: #842029;
    border: 1px solid #f5c2c7;
    padding: 12px;
    border-radius: 6px;
    margin-bottom: 20px;
}

.success-message {
    background: #d1e7dd;
    color: #0f5132;
    border: 1px solid #badbcc;
    padding: 12px;
    border-radius: 6px;
    margin-bottom: 20px;
}

.resume-current {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 15px;
    flex-wrap: wrap;
}

.view-resume-button {
    display: inline-block;
    padding: 8px 14px;
    background: #0d6efd;
    color: white;
    text-decoration: none;
    border-radius: 6px;
    font-size: 13px;
}

.view-resume-button:hover {
    opacity: 0.9;
}

.resume-upload {
    margin-top: 15px;
    padding-top: 15px;
    border-top: 1px solid #ddd;
}

.resume-upload input[type="file"] {
    display: block;
    width: 100%;
    margin-bottom: 10px;
}

.selected-file {
    margin: 8px 0;
    color: #555;
    font-size: 14px;
    word-break: break-word;
}

.resume-upload-button {
    border: none;
    border-radius: 6px;
    padding: 9px 16px;
    background: #198754;
    color: white;
    cursor: pointer;
    font-size: 14px;
    margin-right: 10px;
}

.resume-upload-button:hover {
    opacity: 0.9;
}

.resume-upload-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.resume-upload small {
    color: #666;
}

.offer-letter-section {
    margin-top: 15px;
    padding-top: 15px;
    border-top: 1px solid #badbcc;
}

.offer-letter-section p {
    margin: 6px 0 10px;
}

.view-offer-letter-button {
    border: none;
    border-radius: 6px;
    padding: 9px 16px;
    background: #0d6efd;
    color: white;
    cursor: pointer;
    font-size: 14px;
}

.view-offer-letter-button:hover {
    opacity: 0.9;
}


@media (max-width: 900px) {

    .jobs-grid {
        grid-template-columns: 1fr;
    }

    .search-panel {
        grid-template-columns: 1fr 1fr;
    }

    .application-details {
        grid-template-columns: 1fr;
    }

    .application-header {
        flex-direction: column;
    }
}


@media (max-width: 700px) {

    .profile-grid,
    .form-grid,
    .search-panel {
        grid-template-columns: 1fr;
    }

    .profile-item.full-width,
    .form-group.full-width {
        grid-column: span 1;
    }

    .header {
        flex-direction: column;
        align-items: flex-start;
        gap: 15px;
    }

    .job-details {
        grid-template-columns: 1fr;
    }

    .search-actions {
        width: 100%;
    }

    .search-actions button {
        flex: 1;
    }

    .section-header {
        flex-wrap: wrap;
        gap: 10px;
    }
}

</style>