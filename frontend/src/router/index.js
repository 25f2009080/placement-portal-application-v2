import { createRouter, createWebHistory } from "vue-router";

import HomeView from "../views/HomeView.vue";
import LoginView from "../views/LoginView.vue";
import RegisterView from "../views/RegisterView.vue";

import AdminDashboard from "../views/AdminDashboard.vue";
import CompanyDashboard from "../views/CompanyDashboard.vue";
import StudentDashboard from "../views/StudentDashboard.vue";

import NotFound from "../views/NotFound.vue";

import {
    isAuthenticated,
    getCurrentUser,
    logout,
} from "../services/authService";

const routes = [
    {
        path: "/",
        component: HomeView,
    },

    {
        path: "/login",
        component: LoginView,
    },

    {
        path: "/register",
        component: RegisterView,
    },

    {
        path: "/admin",
        component: AdminDashboard,
        meta: {
            requiresAuth: true,
            role: "admin",
        },
    },

    {
        path: "/company",
        component: CompanyDashboard,
        meta: {
            requiresAuth: true,
            role: "company",
        },
    },

    {
        path: "/student",
        component: StudentDashboard,
        meta: {
            requiresAuth: true,
            role: "student",
        },
    },

    {
        path: "/:pathMatch(.*)*",
        component: NotFound,
    },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

router.beforeEach((to, from, next) => {
    const authenticated = isAuthenticated();
    const user = getCurrentUser();

    if (authenticated && !user) {
        logout();
        return next("/login");
    }

    if (to.meta.requiresAuth && !authenticated) {
        return next("/login");
    }

    if (
        authenticated &&
        (to.path === "/login" || to.path === "/register")
    ) {
        switch (user.role) {
            case "admin":
                return next("/admin");

            case "company":
                return next("/company");

            case "student":
                return next("/student");

            default:
                return next("/");
        }
    }

    if (
        authenticated &&
        to.meta.role &&
        user.role !== to.meta.role
    ) {
        switch (user.role) {
            case "admin":
                return next("/admin");

            case "company":
                return next("/company");

            case "student":
                return next("/student");

            default:
                return next("/");
        }
    }

    next();
});

export default router;