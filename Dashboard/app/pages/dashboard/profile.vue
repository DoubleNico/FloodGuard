<template>
  <div class="space-y-6 max-w-[800px] mx-auto">
    <div>
      <h1 class="text-2xl font-bold text-(--label-text) tracking-tight">Profile</h1>
      <p class="text-sm text-(--hint-text) mt-1">Manage your personal information</p>
    </div>

    <Card class="p-6">
      <h2 class="text-lg font-semibold text-(--label-text) mb-4">Personal Details</h2>
      <div class="space-y-4">
        <Input v-model="profile.name" label="Full Name" placeholder="Your name" />
        <Input v-model="profile.email" type="email" label="Email Address" placeholder="Your email" />
        <Input v-model="profile.phone" label="Phone Number" placeholder="Your phone number" />
        
        <div class="pt-4 flex justify-end">
          <Button color="primary" @click="saveProfile" :disabled="isSaving">
            {{ isSaving ? 'Saving...' : 'Save Changes' }}
          </Button>
        </div>
      </div>
    </Card>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: "dashboard", middleware: "auth" });

const profile = reactive({
  name: "Andrei Ionescu",
  email: "andrei@example.com",
  phone: "+40 700 000 000",
});

const isSaving = ref(false);

const saveProfile = async () => {
  isSaving.value = true;
  await new Promise(resolve => setTimeout(resolve, 800));
  isSaving.value = false;
  alert("Profile updated successfully!");
};
</script>
