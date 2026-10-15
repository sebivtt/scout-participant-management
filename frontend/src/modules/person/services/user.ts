import axios from "axios";
const BASE_URL = import.meta.env.VITE_APP_API;
const SERVICE = 'keycloak/members'

export default {
  fetchAll(params: any) {
    return axios.get(`${BASE_URL}/${SERVICE}/`, {
      params: params,
    });
  },

  fetchById(id: any) {
    return axios.get(`${BASE_URL}/${SERVICE}/${id}/`);
  },
};
