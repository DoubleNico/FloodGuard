<template>
  <div
    class="min-h-screen w-full flex items-center justify-center bg-(--surface-secondary) p-4"
  >
    <Card class="w-full max-w-[600px]">
      <CardHeader class="text-center pb-8">
        <div class="flex justify-center mb-5">
          <div
            class="h-14 w-14 rounded-2xl bg-(--btn-primary-bg) flex items-center justify-center text-white shadow-xl shadow-(--btn-primary-bg)/20"
          >
            <Icon name="mdi:email-outline" class="h-8 w-8" />
          </div>
        </div>
        <CardTitle class="text-2xl">Get in touch</CardTitle>
        <CardDescription class="mt-2 text-base">
          We'd love to hear from you. Please fill out this form.
        </CardDescription>
      </CardHeader>

      <CardContent class="px-8">
        <Form class="space-y-5" @submit="handleSubmit">
          <Grid :cols="2" gap="4">
            <GridItem>
              <Input
                id="firstName"
                v-model="form.firstName"
                label="First name"
                autocomplete="given-name"
                placeholder="John"
                required
                icon-left="mdi:account"
              />
            </GridItem>
            <GridItem>
              <Input
                id="lastName"
                v-model="form.lastName"
                label="Last name"
                autocomplete="family-name"
                placeholder="Doe"
                required
                icon-left="mdi:account-outline"
              />
            </GridItem>
          </Grid>

          <Input
            id="email"
            v-model="form.email"
            label="Email"
            type="email"
            placeholder="john@example.com"
            required
            icon-left="mdi:email"
            :error="errors.email"
          />

          <CustomSelect
            v-model="form.topic"
            label="Topic"
            placeholder="Select a topic"
            :options="topicOptions"
            icon-left="mdi:format-list-bulleted"
            required
          />

          <Textarea
            id="message"
            v-model="form.message"
            label="Message"
            placeholder="Tell us how we can help..."
            :rows="5"
            required
            resize="vertical"
          />

          <div class="flex items-center justify-between pt-2">
            <Switch
              v-model="form.sendCopy"
              label="Send me a copy of this message"
              label-position="right"
              size="sm"
            />
          </div>

          <Button
            type="submit"
            variant="solid"
            color="primary"
            block
            size="lg"
            class="h-12 text-base shadow-lg shadow-(--btn-primary-bg)/20 mt-4"
            :loading="isLoading"
            icon-right="mdi:send"
          >
            Send Message
          </Button>
        </Form>
      </CardContent>

      <CardFooter
        class="flex justify-center border-t border-(--border-color) bg-(--surface-secondary)/30 py-6 mt-2"
      >
        <p class="text-sm text-(--hint-text) pt-2">
          Need immediate help?
          <CustomLink
            to="/"
            variant="primary"
            size="sm"
            weight="semibold"
            class="ml-1"
          >
            Visit our Help Center
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
  topic: "",
  message: "",
  sendCopy: false,
});

const errors = reactive({
  email: "",
});

const topicOptions = [
  {
    label: "General Inquiry",
    value: "general",
    icon: "mdi:information-outline",
  },
  { label: "Technical Support", value: "support", icon: "mdi:wrench" },
  { label: "Billing & Account", value: "billing", icon: "mdi:credit-card" },
  { label: "Partnerships", value: "partners", icon: "mdi:handshake" },
];

const handleSubmit = async () => {
  errors.email = "";

  if (!form.email.includes("@")) {
    errors.email = "Please enter a valid email address.";
    return;
  }

  if (!form.topic) {
    alert("Please select a topic.");
    return;
  }

  isLoading.value = true;

  setTimeout(() => {
    console.log("Message sent:", form);
    isLoading.value = false;
    alert("Message sent successfully! We'll get back to you soon.");
  }, 1500);
};
</script>
