<script setup>
import { ref, onMounted } from "vue";
import LogoutButton from "../components/LogoutButton.vue";
import api from "../services/api";

const student = ref(null);

const loading = ref(true);
const saving = ref(false);

const errorMessage = ref("");
const successMessage = ref("");

const isEditing = ref(false);

const editForm = ref({
    name: "",
    department: "",
    phone: "",
    cgpa: "",
    skills: "",
    education: ""
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
            education: student.value.education || ""
        };

    } catch (error) {
        errorMessage.value =
            error.response?.data?.message ||
            "Failed to load student profile.";
    } finally {
        loading.value = false;
    }
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
        education: student.value.education || ""
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
                education: editForm.value.education
            }
        );

        student.value = response.data.student;

        editForm.value = {
            name: student.value.name || "",
            department: student.value.department || "",
            phone: student.value.phone || "",
            cgpa: student.value.cgpa ?? "",
            skills: student.value.skills || "",
            education: student.value.education || ""
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


onMounted(() => {
    loadProfile();
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


        <div v-if="loading" class="message">
            Loading profile...
        </div>


        <div v-else>

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
                        <label>Resume</label>

                        <p v-if="student.resume">
                            Resume uploaded
                        </p>

                        <p v-else>
                            No resume uploaded
                        </p>
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

        </div>

    </div>
</template>


<style scoped>

.dashboard {
    max-width: 1100px;
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

.profile-section {
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

.edit-button,
.save-button,
.cancel-button {
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

.edit-button:hover,
.save-button:hover,
.cancel-button:hover {
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

.message {
    padding: 20px;
    text-align: center;
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

@media (max-width: 700px) {

    .profile-grid,
    .form-grid {
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
}

</style>