import axios from 'axios';


const apiClient = axios.create({
    baseURL: process.env.NEXT_PUBLIC_BACKEND_URL,
    withCredentials: true, // Ensure cookies are included in requests
    headers: {
      "Content-Type": "application/json",
    },
  })

export default apiClient