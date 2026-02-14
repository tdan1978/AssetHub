<template>
  <div class="login-page login-bg">
    <form class="login" @submit.prevent="onLogin">
      <h2 class="title">
        <img class="logo" :src="logoUrl" alt="AssetHub" />
        AssetHub
      </h2>
      <p class="login-text">Login</p>

      <div class="logindiv">
        <input
          v-model="username"
          class="username loginInput"
          id="username"
          type="text"
          required
        />
        <label for="username">Username</label>
        <User class="login-icon" />
      </div>

      <div class="logindiv">
        <input
          v-model="password"
          class="password loginInput"
          id="password"
          type="password"
          required
        />
        <label for="password">Password</label>
        <KeyRound class="login-icon" />
      </div>

      <button class="loginButton" type="submit">登录</button>

      <Alert v-if="error" variant="destructive" class="login-alert">
        <AlertTitle>登录失败</AlertTitle>
        <AlertDescription>{{ error }}</AlertDescription>
      </Alert>
    </form>

    <div class="footer">
      Product by <img class="itlogo" :src="logoUrl" alt="" /> 2026 AssetHub Contributors
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useAuthStore } from "../stores/auth";
import { useRouter } from "vue-router";
import { Alert, AlertDescription, AlertTitle } from "../components/ui/alert";
import { KeyRound, User } from "lucide-vue-next";
import logoUrl from "../assets/logo.png";

const username = ref("");
const password = ref("");
const auth = useAuthStore();
const router = useRouter();
const error = ref("");

const onLogin = async () => {
  error.value = "";
  try {
    await auth.login(username.value, password.value);
    router.push("/");
  } catch (err) {
    error.value = "登录失败，请检查账号密码或后端服务。";
  }
};
</script>

<style scoped>
.login-bg {
  background-image: url("../assets/login_background.png");
}

.login-page {
  min-height: 100vh;
  background-size: cover;
  background-repeat: no-repeat;
  background-attachment: fixed;
  background-position: bottom;
  margin: 0;
  position: relative;
}

.login {
  width: 300px;
  height: 340px;
  margin: auto;
  position: absolute;
  top: 50%;
  left: 50%;
  margin-top: -190px;
  margin-left: -150px;
  backdrop-filter: blur(10px);
  border-radius: 20px;
  text-align: center;
  padding: 20px;
  box-shadow: 0 0 15px #1e1e1e66, inset 0 0 0 0.5px #ffffff7d;
  background-color: #fff2;
}

.logindiv {
  position: relative;
  width: 200px;
  margin: 26px auto 0;
}

.loginInput {
  width: 100%;
  height: 30px;
  border: 0px;
  background-color: transparent;
  border-bottom: 0.5px solid #2d2d2d;
  margin-top: 16px;
  outline: 0ch;
  padding-right: 22px;
  color: #203f00;
}

.loginButton {
  width: 200px;
  height: 30px;
  background-color: #2d2d2d;
  border: 0px;
  margin-top: 60px;
  border-radius: 10px;
  color: #ffffff;
}

.logindiv label {
  position: absolute;
  z-index: 99;
  top: 6px;
  left: 0;
  transition: 0.5s;
  color: #203f00;
}

.title {
  font-size: 24px;
  position: absolute;
  margin-top: -90px;
  width: 100%;
  font-weight: 700;
  color: #203f00;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.loginInput:focus + label,
.loginInput:valid + label {
  top: -10px;
  font-size: 11px;
}

.footer {
  position: absolute;
  bottom: 30px;
  font-size: 12px;
  zoom: 0.7;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: #203f00;
  white-space: nowrap;
}

.itlogo {
  height: 16px;
  vertical-align: bottom;
}

.logo {
  width: 36px;
  vertical-align: middle;
}

.login-icon {
  position: absolute;
  right: 0;
  top: 22px;
  width: 14px;
  height: 14px;
}

.login-alert {
  margin-top: 12px;
  text-align: left;
}
</style>
.login-text {
  color: #203f00;
}



