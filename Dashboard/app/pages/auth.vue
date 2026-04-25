<template>
  <div class="min-h-screen w-full flex items-center justify-center bg-(--surface-secondary) p-4">
    <Card class="w-full max-w-[420px]">
      <CardHeader class="text-center pb-8">
        <div class="flex justify-center mb-5">
          <div class="h-14 w-14 rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center text-white shadow-xl shadow-blue-500/20">
            <Icon name="mdi:water-alert" class="h-8 w-8" />
          </div>
        </div>
        <CardTitle class="text-2xl">Hydralis Access</CardTitle>
        <CardDescription class="mt-2 text-base">
          Sign in to the flood monitoring dashboard
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

          <div>
            <label class="text-sm font-medium text-(--label-text) mb-2 block">Role</label>
            <div class="grid grid-cols-3 gap-2">
              <button
                v-for="role in roles"
                :key="role.value"
                type="button"
                class="flex flex-col items-center gap-1.5 p-3 rounded-xl border transition-all duration-200 cursor-pointer"
                :class="form.role === role.value
                  ? 'border-blue-500 bg-blue-500/10 shadow-sm'
                  : 'border-(--border-color) bg-(--surface-secondary)/50 hover:border-(--border-color) hover:bg-(--surface-secondary)'"
                @click="form.role = role.value"
              >
                <Icon :name="role.icon" class="h-5 w-5" :class="form.role === role.value ? 'text-blue-500' : 'text-(--icon-color)'" />
                <span class="text-xs font-medium" :class="form.role === role.value ? 'text-blue-500' : 'text-(--label-text)'">{{ role.label }}</span>
              </button>
            </div>
          </div>

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

      <CardFooter class="flex justify-center border-t border-(--border-color) bg-(--surface-secondary)/30 py-6">
        <p class="text-sm text-(--label-text)">
          Hydralis — Flood Early Warning Platform
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

const { setRole } = useRole();

const isLoading = ref(false);
const authError = ref("");

const form = reactive({
  username: "",
  password: "",
  role: "dispatcher" as "dispatcher" | "industrial" | "admin",
});

const formErrors = reactive({
  username: "",
  password: "",
});

const roles = [
  { value: "dispatcher", label: "Dispatcher", icon: "mdi:shield-alert" },
  { value: "industrial", label: "Industrial", icon: "mdi:factory" },
  { value: "admin", label: "Admin", icon: "mdi:cog" },
];

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
  setRole(form.role);

  const target = redirectPath.value === "/" ? "/dashboard" : redirectPath.value;
  await navigateTo(target);
  isLoading.value = false;
};
</script>
