const auth = {

    // =========================
    // LOGIN
    // =========================
    async login(username, password) {
        try {
            const data = await api.auth.login(username, password);

            // Guardar token
            localStorage.setItem("access_token", data.access_token);

            // Decodificar JWT
            const payload = JSON.parse(atob(data.access_token.split(".")[1]));
            localStorage.setItem("user_id", payload.sub);

            // Intentar obtener rol (JWT o respuesta)
            let role = payload.rol || payload.role || data.rol || data.role || null;

            if (role) {
                localStorage.setItem("user_role", role.toLowerCase());
            } else {
                // Si no hay rol, limpiar
                localStorage.removeItem("user_role");
            }

            // Redirigir (ruta absoluta para evitar errores)
            window.location.href = "/pages/dashboard.html";

        } catch (error) {
            alert("Error al iniciar sesión: " + error.message);
        }
    },

    // =========================
    // LOGOUT
    // =========================
    logout() {
        localStorage.removeItem("access_token");
        localStorage.removeItem("user_id");
        localStorage.removeItem("user_role");

        window.location.href = "/index.html";
    },

    // =========================
    // AUTH CHECK
    // =========================
    isAuthenticated() {
        return !!localStorage.getItem("access_token");
    },

    checkAuth() {
        const path = window.location.pathname;

        const isLoginPage =
            path === "/" ||
            path.endsWith("index.html");

        if (!this.isAuthenticated() && !isLoginPage) {
            window.location.href = "/index.html";
        }
    },

    // =========================
    // USER DATA
    // =========================
    getUserId() {
        return localStorage.getItem("user_id");
    },

    async getUserRole() {
        // 1. Cache local
        let cached = localStorage.getItem("user_role");

        if (cached && cached !== "null" && cached !== "undefined") {
            return cached.toLowerCase();
        }

        // 2. Intentar desde JWT
        const token = localStorage.getItem("access_token");

        if (token) {
            try {
                const payload = JSON.parse(atob(token.split(".")[1]));
                let role = payload.rol || payload.role || null;

                if (role) {
                    role = role.toLowerCase();
                    localStorage.setItem("user_role", role);
                    return role;
                }
            } catch (e) {
                console.warn("Error decodificando JWT");
            }
        }

        // 3. No hay rol disponible
        return "desconocido";
    },

    // =========================
    // PROTECCIÓN DE RUTAS
    // =========================
    async requireRole(allowedRoles = []) {
        if (!this.isAuthenticated()) {
            window.location.href = "/index.html";
            return false;
        }

        const role = await this.getUserRole();

        if (!allowedRoles.includes(role)) {
            window.location.href = "/pages/dashboard.html";
            return false;
        }

        return true;
    }
};


// =========================
// AUTO-CHECK GLOBAL
// =========================
if (
    !window.location.pathname.endsWith("index.html") &&
    window.location.pathname !== "/"
) {
    auth.checkAuth();
}