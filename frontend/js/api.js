const API_BASE_URL = 'http://localhost:8000'; // Cambiar por la URL real en producción

const api = {
    async fetch(endpoint, options = {}) {
        const token = localStorage.getItem('access_token');
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers
        });

        if (response.status === 401) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('user_id');
            window.location.href = '/index.html';
            return;
        }

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ocurrió un error inesperado');
        }

        return response.json();
    },

    async upload(endpoint, formData) {
        const token = localStorage.getItem('access_token');
        const headers = {};
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            body: formData,
            headers
        });

        if (response.status === 401) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('user_id');
            window.location.href = '/index.html';
            return;
        }

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Error al subir el archivo');
        }

        return response.json();
    },

    auth: {
        login: (username, password) => {
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);
            return fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData
            }).then(async res => {
                if (!res.ok) {
                    const error = await res.json();
                    throw new Error(error.detail || 'Credenciales incorrectas');
                }
                return res.json();
            });
        }
    },

    alumnos: {
        listar: () => api.fetch('/alumnos/'),
        crear: (data) => api.fetch('/alumnos/', { method: 'POST', body: JSON.stringify(data) }),
        editar: (id, data) => api.fetch(`/alumnos/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
        eliminar: (id) => api.fetch(`/alumnos/${id}`, { method: 'DELETE' }),
        observar: (id, comentario) => api.fetch(`/alumnos/${id}/observar?comentario=${encodeURIComponent(comentario)}`, { method: 'POST' }),
        aprobar: (id) => api.fetch(`/alumnos/${id}/aprobar`, { method: 'POST' }),
        obtener: (id) => api.fetch(`/alumnos/${id}`)
    },

    documentos: {
        subir: (alumnoId, tipo, file) => {
            const formData = new FormData();
            formData.append('file', file);
            return api.upload(`/documentos/${alumnoId}?tipo=${tipo}`, formData);
        },
        listarPorAlumno: (alumnoId) => api.fetch(`/documentos/alumno/${alumnoId}`)
    },

    usuarios: {
        listar: () => api.fetch('/usuarios/'),
        crear: (data) => api.fetch('/usuarios/', { method: 'POST', body: JSON.stringify(data) })
    },

    historial: {
        listar: () => api.fetch('/historial/')
    },

    escuelas: {
        listar: () => api.fetch('/escuelas/')
    },

    observar: async (id, motivo) => {
        return fetch(`${API_BASE_URL}/alumnos/${id}/observar`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${localStorage.getItem("access_token")}`
            },
            body: JSON.stringify({ motivo })
        }).then(res => {
            if (!res.ok) throw new Error("Error al observar alumno");
            return res.json();
        });
    }
};
