<template>
  <div
    class="min-h-screen w-full flex items-center justify-center bg-(--surface-secondary) p-4"
  >
    <Card class="w-full max-w-[420px]">
      <CardHeader class="text-center pb-8">
        <div class="flex justify-center mb-5">
          <div
            class="h-14 w-14 rounded-2xl bg-(--btn-primary-bg) flex items-center justify-center text-white shadow-xl shadow-(--btn-primary-bg)/20"
          >
            <Icon name="mdi:shield-lock" class="h-8 w-8" />
          </div>
        </div>
        <CardTitle class="text-2xl">Hydralis Access</CardTitle>
        <CardDescription class="mt-2 text-base">
          Sign in to access protected pages
        </CardDescription>
      </CardHeader>

      <CardContent class="px-8">
        <Form class="space-y-5" @submit="handleLogin">
          <Input
            id="username"
            v-model="form.username"
            label="Username"
            type="text"
            placeholder="Enter username"
            autocomplete="username"
            required
            icon-left="mdi:account"
            :error="formErrors.username"
          />

          <Input
            id="password"
            v-model="form.password"
            label="Password"
            type="password"
            placeholder="••••••••"
            autocomplete="current-password"
            required
            icon-left="mdi:lock"
            :error="formErrors.password"
          />

          <p v-if="authError" class="text-sm text-(--input-error-text)">
            {{ authError }}
          </p>

          <Button
            type="submit"
            variant="solid"
            color="primary"
            block
            size="lg"
            class="h-12 text-base shadow-lg shadow-(--btn-primary-bg)/20 mt-2"
            :loading="isLoading"
          >
            Sign In
          </Button>
        </Form>
      </CardContent>

      <CardFooter
        class="flex justify-center border-t border-(--border-color) bg-(--surface-secondary)/30 py-6"
      >
        <p class="text-sm text-(--label-text)">
          Don't have an account? Go to hydralis and ask for a beer!
        </p>
      </CardFooter>
    </Card>
  </div>
</template>

<script setup lang="ts">
import {
  INTERNAL_AUTH_COOKIE,
  isValidInternalCredentials,
  sanitizeRedirectPath,
} from "~/utils/internalAuth";

const route = useRoute();
const sessionCookie = useCookie<string | null>(INTERNAL_AUTH_COOKIE, {
  path: "/",
  sameSite: "lax",
  maxAge: 60 * 60 * 24,
});

const isLoading = ref(false);
const authError = ref("");

const form = reactive({
  username: "",
  password: "",
});

const formErrors = reactive({
  username: "",
  password: "",
});

const redirectPath = computed(() => sanitizeRedirectPath(route.query.redirect));

const handleLogin = async () => {
  formErrors.username = "";
  formErrors.password = "";
  authError.value = "";

  if (!form.username.trim()) {
    formErrors.username = "Username is required.";
  }

  if (!form.password) {
    formErrors.password = "Password is required.";
  }

  if (formErrors.username || formErrors.password) {
    return;
  }

  isLoading.value = true;

  const isValid = isValidInternalCredentials(form.username, form.password);

  if (!isValid) {
    authError.value = "Invalid username or password.";
    isLoading.value = false;
    return;
  }

  sessionCookie.value = form.username.trim();
  await navigateTo(redirectPath.value);
  isLoading.value = false;
};
</script>
