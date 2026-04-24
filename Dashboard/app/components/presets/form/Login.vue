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
            <Icon name="mdi:login" class="h-8 w-8" />
          </div>
        </div>
        <CardTitle class="text-2xl">Welcome back</CardTitle>
        <CardDescription class="mt-2 text-base">
          Please sign in to your account
        </CardDescription>
      </CardHeader>

      <CardContent class="px-8">
        <Form class="space-y-5" @submit="handleLogin">
          <Input
            id="email"
            v-model="form.email"
            label="Email"
            type="email"
            placeholder="john@example.com"
            autocomplete="email"
            required
            icon-left="mdi:email"
            :error="formErrors.email"
          />

          <div class="flex flex-col gap-1.5">
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
            <div class="flex justify-end">
              <CustomLink
                to="/"
                variant="muted"
                weight="normal"
                class="text-xs"
              >
                Forgot password?
              </CustomLink>
            </div>
          </div>

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
        <p class="text-sm text-(--hint-text) pt-2">
          Don't have an account?
          <CustomLink
            to="/register"
            variant="primary"
            size="sm"
            weight="semibold"
            class="ml-1"
          >
            Sign up
          </CustomLink>
        </p>
      </CardFooter>
    </Card>
  </div>
</template>

<script setup lang="ts">
const isLoading = ref(false);

const form = reactive({
  email: "",
  password: "",
});

const formErrors = reactive({
  email: "",
  password: "",
});

const handleLogin = async () => {
  formErrors.email = "";
  formErrors.password = "";

  if (!form.email || !form.email.includes("@")) {
    formErrors.email = "Please enter a valid email address.";
    return;
  }
  if (!form.password || form.password.length < 6) {
    formErrors.password = "Password must be at least 6 characters.";
    return;
  }

  isLoading.value = true;

  setTimeout(() => {
    console.log("Logging in with:", form);
    isLoading.value = false;
    alert("Logged in successfully!");
  }, 1500);
};
</script>
