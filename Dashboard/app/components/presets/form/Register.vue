<template>
  <div
    class="min-h-screen w-full flex items-center justify-center bg-(--surface-secondary) p-4"
  >
    <Card class="w-full max-w-[520px]">
      <CardHeader class="text-center pb-8">
        <div class="flex justify-center mb-5">
          <div
            class="h-14 w-14 rounded-2xl bg-(--btn-primary-bg) flex items-center justify-center text-white shadow-xl shadow-(--btn-primary-bg)/20"
          >
            <Icon name="mdi:account-plus" class="h-8 w-8" />
          </div>
        </div>
        <CardTitle class="text-2xl">Create Account</CardTitle>
        <CardDescription class="mt-2 text-base">
          Join us today! Enter your details below.
        </CardDescription>
      </CardHeader>

      <CardContent class="px-8">
        <Form class="space-y-5" @submit="handleRegister">
          <Grid :cols="2" gap="4">
            <GridItem>
              <Input
                id="firstName"
                v-model="form.firstName"
                label="First Name"
                placeholder="John"
                autocomplete="given-name"
                required
                icon-left="mdi:account"
              />
            </GridItem>
            <GridItem>
              <Input
                id="lastName"
                v-model="form.lastName"
                label="Last Name"
                placeholder="Doe"
                autocomplete="family-name"
                required
                icon-left="mdi:account-outline"
              />
            </GridItem>
          </Grid>

          <Input
            id="email"
            v-model="form.email"
            :error="formErrors.emailInvalid"
            label="Email Address"
            type="email"
            autocomplete="username"
            placeholder="john@example.com"
            required
            icon-left="mdi:email"
          />

          <Grid :cols="2" gap="4">
            <GridItem>
              <Input
                v-model="form.password"
                label="Password"
                type="password"
                placeholder="••••••••"
                autocomplete="new-password"
                required
                icon-left="mdi:lock"
              />
            </GridItem>
            <GridItem>
              <Input
                v-model="form.confirmPassword"
                :error="formErrors.passwordMismatch"
                label="Confirm"
                type="password"
                autocomplete="new-password"
                placeholder="••••••••"
                required
                icon-left="mdi:lock-check"
              />
            </GridItem>
          </Grid>

          <Grid :cols="2" gap="4">
            <GridItem>
              <Input
                id="bday"
                v-model="form.dob"
                type="custom-date"
                label="Date of Birth"
                autocomplete="bday"
                placeholder="MM/DD/YYYY"
                icon-left="mdi:cake-variant"
              />
            </GridItem>

            <GridItem>
              <CustomSelect
                v-model="form.role"
                label="Role"
                placeholder="Select role"
                :options="roleOptions"
                icon-left="mdi:briefcase"
                block
                clearable
              />
            </GridItem>
          </Grid>

          <div class="pt-2">
            <Switch
              v-model="form.agreed"
              label="I agree to the Terms & Privacy Policy"
              label-position="right"
              size="md"
            />
            <p
              v-if="formErrors.agreed"
              class="text-xs text-(--input-error-text) mt-1 ml-12"
            >
              {{ formErrors.agreed }}
            </p>
          </div>

          <Button
            type="submit"
            variant="solid"
            color="primary"
            block
            size="lg"
            class="h-12 text-base shadow-lg shadow-(--btn-primary-bg)/20 mt-4"
            :loading="isLoading"
          >
            Create Account
          </Button>
        </Form>
      </CardContent>

      <CardFooter
        class="flex justify-center border-t border-(--border-color) bg-(--surface-secondary)/30 py-6 mt-2"
      >
        <p class="text-sm text-(--hint-text) pt-2">
          Already have an account?
          <CustomLink
            to="/login"
            variant="primary"
            size="sm"
            weight="semibold"
            class="ml-1"
          >
            Sign in
          </CustomLink>
        </p>
      </CardFooter>
    </Card>
  </div>
</template>

<script setup lang="ts">
const isLoading = ref(false);

const form = reactive({
  firstName: "",
  lastName: "",
  email: "",
  password: "",
  confirmPassword: "",
  dob: null as Date | null,
  role: "",
  agreed: false,
});

const formErrors = reactive({
  passwordMismatch: "",
  agreed: "",
  emailInvalid: "",
  firstName: "",
  lastName: "",
});

const roleOptions = [
  { label: "Developer", value: "dev", icon: "mdi:code-tags" },
  { label: "Designer", value: "design", icon: "mdi:palette" },
  { label: "Manager", value: "manager", icon: "mdi:account-tie" },
  { label: "Other", value: "other", icon: "mdi:help-circle" },
];

const handleRegister = async () => {
  if (form.password !== form.confirmPassword) {
    formErrors.passwordMismatch = "Passwords do not match.";
    return;
  }
  formErrors.passwordMismatch = "";
  if (!form.agreed) {
    formErrors.agreed = "You must agree to the Terms & Privacy Policy.";
    return;
  }
  formErrors.agreed = "";
  if (!form.email.includes("@")) {
    formErrors.emailInvalid = "Please enter a valid email address.";
    return;
  }
  formErrors.emailInvalid = "";
  if (!form.firstName) {
    formErrors.firstName = "Please enter your first name.";
    return;
  }
  formErrors.firstName = "";
  if (!form.lastName) {
    formErrors.lastName = "Please enter your last name.";
    return;
  }
  formErrors.lastName = "";

  isLoading.value = true;

  setTimeout(() => {
    console.log("Registered User:", form);
    isLoading.value = false;
    alert("Account created successfully!");
  }, 1500);
};
</script>
