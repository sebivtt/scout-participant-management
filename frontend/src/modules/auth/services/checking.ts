import axios from "axios"
const BASE_URL = import.meta.env.VITE_APP_API

export default {
  async usernameCheck(username: string) {
    return axios.post(`${BASE_URL}/auth/check-username/`, { username })
  },
  async emailCheck(email: string) {
    return axios.post(`${BASE_URL}/auth/check-email/`, { email })
  },
  async passwordCheck(password: string) {
    return axios.post(`${BASE_URL}/auth/check-password/`, { password })
  },
  async zipCodeCheck(zipCode: string) {
    return axios.post(`${BASE_URL}/basic/check-zip-code/`, { zipCode })
  },
  async personCheck(regId: any, person: any) {
    return axios.post(`${BASE_URL}/event/registration/${regId}/check-person/`, person)
  },
  // Für neue Anmeldungen: Die Anmeldung gibt es noch nicht, deshalb prüft
  // das Backend über die Veranstaltung (Issue #19).
  async personCheckForEvent(eventId: string, person: Record<string, unknown>) {
    return axios.post(`${BASE_URL}/event/event/${eventId}/check-person/`, person)
  },
}
