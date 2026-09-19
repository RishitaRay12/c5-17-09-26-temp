import api from "./api";

export interface LoginData {
  username: string;
  password: string;
}

export const loginUser = async (data: LoginData) => {
  const formData = new URLSearchParams();
  formData.set("username", data.username);
  formData.set("password", data.password);

  const response = await api.post("/users/login", formData, {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });
  return response.data;
};