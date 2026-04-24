<template>
  <div>
    <NavigationMenu class="px-6 h-14 max-w-screen">
      <template #left>
        <a href="/" class="flex items-center cursor-pointer">
          <span class="font-semibold text-lg tracking-tight text-(--label-text)"
            >Beer</span
          >
        </a>
      </template>

      <div class="hidden md:block">
        <NavigationMenuList>
          <NavigationMenuItem value="home">
            <template #trigger>
              <NavigationMenuTrigger>Plugins</NavigationMenuTrigger>
            </template>
            <template #content>
              <NavigationMenuContent>
                <ul
                  class="grid gap-3 p-2 w-[400px] md:w-[500px] lg:w-[600px] lg:grid-cols-[.8fr_1fr]"
                >
                  <li class="row-span-3">
                    <NavigationMenuLink
                      href="/"
                      class="flex h-full w-full select-none flex-col justify-end rounded-xl bg-linear-to-b from-blue-500 to-blue-700 p-6 no-underline outline-none shadow-lg"
                    >
                      <div class="mt-4 mb-2 text-xl font-bold text-white">
                        Beer
                      </div>
                      <p class="text-sm leading-tight text-white/90">
                        Explore our collection of powerful plugins to enhance
                        your spigot server.
                      </p>
                    </NavigationMenuLink>
                  </li>
                  <NavigationMenuListItem href="#intro" title="Introduction">
                    Get started with Beer and learn the basics.
                  </NavigationMenuListItem>
                  <NavigationMenuListItem href="#install" title="Installation">
                    Step-by-step guide to install our plugins.
                  </NavigationMenuListItem>
                  <NavigationMenuListItem href="#design" title="Design System">
                    Learn about our design principles and components.
                  </NavigationMenuListItem>
                </ul>
              </NavigationMenuContent>
            </template>
          </NavigationMenuItem>

          <NavigationMenuItem value="components">
            <template #trigger>
              <NavigationMenuTrigger>Features</NavigationMenuTrigger>
            </template>
            <template #content>
              <NavigationMenuContent>
                <ul
                  class="grid w-[400px] gap-2 p-2 md:w-[500px] md:grid-cols-2"
                >
                  <NavigationMenuListItem href="#analytics" title="Analytics">
                    Gain insights with in-depth analytics tools.
                  </NavigationMenuListItem>
                  <NavigationMenuListItem href="#automation" title="Automation">
                    Streamline your workflows with powerful automation.
                  </NavigationMenuListItem>
                  <NavigationMenuListItem href="#security" title="Security">
                    Keep your data safe with top-notch security features.
                  </NavigationMenuListItem>
                  <NavigationMenuListItem
                    href="#collaboration"
                    title="Collaboration"
                  >
                    Enhance teamwork with seamless collaboration tools.
                  </NavigationMenuListItem>
                </ul>
              </NavigationMenuContent>
            </template>
          </NavigationMenuItem>

          <NavigationMenuItem value="resources">
            <template #trigger>
              <NavigationMenuTrigger>Resources</NavigationMenuTrigger>
            </template>
            <template #content>
              <NavigationMenuContent>
                <ul class="grid w-[300px] gap-2 p-2">
                  <NavigationMenuListItem href="#blog" title="Blog">
                    Latest updates and articles.
                  </NavigationMenuListItem>
                  <NavigationMenuListItem href="#community" title="Community">
                    Join our discord and forums.
                  </NavigationMenuListItem>
                </ul>
              </NavigationMenuContent>
            </template>
          </NavigationMenuItem>

          <NavigationMenuItem>
            <NavigationMenuLink
              href="#pricing"
              class="text-[13px] font-medium px-3 py-2 text-(--label-text) hover:text-blue-500 transition-colors"
            >
              Pricing
            </NavigationMenuLink>
          </NavigationMenuItem>
        </NavigationMenuList>
      </div>

      <template #right>
        <div class="flex items-center gap-3">
          <MobileNavigationMenu v-model="mobileMenuOpen" class="md:hidden">
            <MobileNavigationMenuList>
              <MobileNavigationMenuDropdown
                title="Plugins"
                :default-open="true"
              >
                <MobileNavigationMenuItem>
                  <MobileNavigationMenuLink href="#intro" :in-dropdown="true">
                    Introduction
                  </MobileNavigationMenuLink>
                </MobileNavigationMenuItem>
                <MobileNavigationMenuItem>
                  <MobileNavigationMenuLink href="#install" :in-dropdown="true">
                    Installation
                  </MobileNavigationMenuLink>
                </MobileNavigationMenuItem>
                <MobileNavigationMenuItem>
                  <MobileNavigationMenuLink href="#design" :in-dropdown="true">
                    Design System
                  </MobileNavigationMenuLink>
                </MobileNavigationMenuItem>
              </MobileNavigationMenuDropdown>

              <MobileNavigationMenuDropdown title="Features">
                <MobileNavigationMenuItem>
                  <MobileNavigationMenuLink
                    href="#analytics"
                    :in-dropdown="true"
                  >
                    Analytics
                  </MobileNavigationMenuLink>
                </MobileNavigationMenuItem>
                <MobileNavigationMenuItem>
                  <MobileNavigationMenuLink
                    href="#automation"
                    :in-dropdown="true"
                  >
                    Automation
                  </MobileNavigationMenuLink>
                </MobileNavigationMenuItem>
                <MobileNavigationMenuItem>
                  <MobileNavigationMenuLink
                    href="#security"
                    :in-dropdown="true"
                  >
                    Security
                  </MobileNavigationMenuLink>
                </MobileNavigationMenuItem>
                <MobileNavigationMenuItem>
                  <MobileNavigationMenuLink
                    href="#collaboration"
                    :in-dropdown="true"
                  >
                    Collaboration
                  </MobileNavigationMenuLink>
                </MobileNavigationMenuItem>
              </MobileNavigationMenuDropdown>

              <MobileNavigationMenuDropdown title="Resources">
                <MobileNavigationMenuItem>
                  <MobileNavigationMenuLink href="#blog" :in-dropdown="true">
                    Blog
                  </MobileNavigationMenuLink>
                </MobileNavigationMenuItem>
                <MobileNavigationMenuItem>
                  <MobileNavigationMenuLink
                    href="#community"
                    :in-dropdown="true"
                  >
                    Community
                  </MobileNavigationMenuLink>
                </MobileNavigationMenuItem>
              </MobileNavigationMenuDropdown>

              <MobileNavigationMenuItem>
                <MobileNavigationMenuLink href="#pricing">
                  Pricing
                </MobileNavigationMenuLink>
              </MobileNavigationMenuItem>
            </MobileNavigationMenuList>
          </MobileNavigationMenu>

          <div class="hidden md:block">
            <Button
              size="sm"
              class="rounded-full px-5 bg-(--label-text) text-(--input-bg) hover:bg-[color-mix(in_srgb,var(--label-text)_90%,transparent)] shadow-md"
            >
              Download
            </Button>
          </div>
        </div>
      </template>
    </NavigationMenu>

    <div class="p-8">
      <h1 class="text-4xl font-bold text-primary mb-4">Beer</h1>
      <p class="mb-6">{{ $t("welcome") }}</p>

      <div class="mb-4">
        <Button color="primary" @click="isModalOpen = true">Open Modal</Button>
        <Modal v-model="isModalOpen" title="My Awesome Modal" size="lg">
          <p>
            This is the modal content. You can put any HTML or components here.
          </p>
          <p class="mt-4">
            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non
            risus. Suspendisse lectus tortor, dignissim sit amet, adipiscing
            nec, ultricies sed, dolor. Cras elementum ultrices diam. Maecenas
            ligula massa, varius a, semper congue, euismod non, mi.
          </p>

          <template #footer="{ close }">
            <Button variant="outline" color="secondary" @click="close">
              Cancel
            </Button>
            <Button color="primary" @click="close">Awesome!</Button>
          </template>
        </Modal>
      </div>

      <div class="flex flex-wrap gap-3 mb-4">
        <ClientOnly>
          <Button color="primary" @click="changeMode">
            Theme: {{ $colorMode.value }}
          </Button>
        </ClientOnly>
        <Button
          v-for="lang in availableLocales"
          :key="lang.code"
          color="primary"
          variant="outline"
          @click="setLocale(lang.code)"
        >
          {{ lang.name }}
        </Button>

        <CustomLink to="/login">
          <Button color="primary" variant="outline" href="/login">
            Login Form
          </Button>
        </CustomLink>
        <CustomLink to="/register">
          <Button color="primary" variant="outline" href="/register">
            Register Form
          </Button>
        </CustomLink>
        <CustomLink to="/buy">
          <Button color="primary" variant="outline" href="/buy">
            Buy Form
          </Button>
        </CustomLink>
        <CustomLink to="/contact">
          <Button color="primary" variant="outline" href="/contact">
            Contact Form
          </Button>
        </CustomLink>
      </div>

      <Button variant="ghost" color="primary" icon-left="mdi:eye">
        Outline
      </Button>
      <Button
        variant="solid"
        class="bg-primary"
        size="sm"
        icon-left="mdi:check"
      >
        Small Primary
      </Button>
      <Button variant="solid" color="secondary" icon-right="mdi:arrow-right">
        Solid Secondary
      </Button>
      <Button variant="outline" color="success" :loading="true">
        Loading
      </Button>
      <Button variant="solid" color="danger" size="lg" :block="true">
        Large Block Danger
      </Button>

      <div class="mt-8 space-y-6 max-w-2xl">
        <h2 class="text-2xl font-bold">Color Picker Component</h2>

        <ClientOnly>
          <ColorPicker v-model="color" label="Pick a Color" />
        </ClientOnly>

        <p class="mt-2">Selected Color: {{ color }}</p>
      </div>

      <div class="mt-8 space-y-6 max-w-2xl">
        <h2 class="text-2xl font-bold">Input Components</h2>

        <div class="space-y-4">
          <Input
            v-model="formData.text"
            label="Text Input"
            placeholder="Enter your name"
            hint="This is a standard text input"
          />

          <Input
            v-model="formData.email"
            type="email"
            label="Email"
            placeholder="your@email.com"
            icon-left="mdi:email"
            :required="true"
          />

          <Input
            v-model="formData.password"
            type="password"
            label="Password"
            placeholder="Enter password"
            icon-left="mdi:lock"
            :clearable="true"
          />

          <Input
            v-model="formData.search"
            type="search"
            label="Search"
            placeholder="Search..."
            icon-left="mdi:magnify"
            :clearable="true"
            :loading="searching"
          />

          <Input
            v-model="formData.number"
            type="number"
            label="Number"
            placeholder="0"
            :min="0"
            :max="100"
            :step="5"
          />

          <Input
            v-model="formData.url"
            type="url"
            label="Website"
            placeholder="https://example.com"
            icon-left="mdi:web"
          />

          <Input
            v-model="formData.tel"
            type="tel"
            label="Phone"
            placeholder="+1 234 567 890"
            icon-left="mdi:phone"
          />

          <Input v-model="formData.date" type="date" label="Date" />

          <Input v-model="formData.time" type="time" label="Time" />

          <Input v-model="formData.color" type="color" label="Color Picker" />

          <Input
            v-model="formData.customColor"
            type="custom-color"
            label="Custom Color Picker"
            placeholder="#ff0000"
            :clearable="true"
          />

          <Input
            v-model="formData.errorExample"
            label="With Error"
            placeholder="This has an error"
            error="This field is required"
          />

          <Input
            v-model="formData.disabled"
            label="Disabled Input"
            placeholder="Cannot edit"
            :disabled="true"
          />

          <Input
            v-model="formData.readonly"
            label="Readonly Input"
            :readonly="true"
          />
        </div>

        <div class="space-y-4">
          <h3 class="text-xl font-semibold">Sizes</h3>
          <Input v-model="formData.small" size="sm" placeholder="Small" />
          <Input v-model="formData.medium" size="md" placeholder="Medium" />
          <Input v-model="formData.large" size="lg" placeholder="Large" />
        </div>

        <div class="space-y-4">
          <h3 class="text-xl font-semibold">Colors</h3>
          <Input
            v-model="formData.colorPrimary"
            color="primary"
            placeholder="Primary"
          />
          <Input
            v-model="formData.colorSecondary"
            color="secondary"
            placeholder="Secondary"
          />
          <Input
            v-model="formData.colorAccent"
            color="accent"
            placeholder="Accent"
          />
          <Input
            v-model="formData.colorSuccess"
            color="success"
            placeholder="Success"
          />
          <Input
            v-model="formData.colorDanger"
            color="danger"
            placeholder="Danger"
          />
        </div>

        <div class="space-y-4">
          <h3 class="text-xl font-semibold">Block Input</h3>
          <Input
            v-model="formData.block"
            placeholder="Full width input"
            :block="true"
          />
        </div>
      </div>

      <div class="mt-8 space-y-4 max-w-2xl">
        <h2 class="text-2xl font-bold">Switch Components</h2>

        <div class="space-y-3">
          <Switch
            v-model="switchStates.basic"
            color="primary"
            label="Basic Switch"
          />
          <Switch
            v-model="switchStates.primary"
            color="primary"
            label="Primary"
          />
          <Switch
            v-model="switchStates.secondary"
            color="secondary"
            label="Secondary"
          />
          <Switch v-model="switchStates.accent" color="accent" label="Accent" />
          <Switch
            v-model="switchStates.success"
            color="success"
            label="Success"
          />
          <Switch v-model="switchStates.danger" color="danger" label="Danger" />
        </div>

        <div class="space-y-3">
          <Switch
            v-model="switchStates.small"
            color="primary"
            size="sm"
            label="Small Size"
          />
          <Switch
            v-model="switchStates.medium"
            color="primary"
            size="md"
            label="Medium Size"
          />
          <Switch
            v-model="switchStates.large"
            color="primary"
            size="lg"
            label="Large Size"
          />
        </div>

        <div class="space-y-3">
          <Switch
            v-model="switchStates.leftLabel"
            color="primary"
            label="Left Label"
            label-position="left"
          />
          <Switch
            v-model="switchStates.required"
            color="primary"
            label="Required Field"
            :required="true"
          />
          <Switch
            v-model="switchStates.disabled"
            color="primary"
            label="Disabled"
            :disabled="true"
          />
        </div>
      </div>

      <div class="mt-8 space-y-4 max-w-2xl">
        <h2 class="text-2xl font-bold">Textarea Components</h2>

        <Textarea
          v-model="formData.textarea"
          label="Description"
          placeholder="Enter your description..."
          hint="Maximum 500 characters"
          :rows="4"
        />

        <Textarea
          v-model="formData.textareaRequired"
          label="Required Textarea"
          placeholder="This field is required"
          :required="true"
          :rows="3"
        />

        <div class="space-y-4">
          <h3 class="text-xl font-semibold">Resize Options</h3>
          <Textarea
            v-model="formData.textareaNone"
            label="No Resize"
            resize="none"
            :rows="3"
          />
          <Textarea
            v-model="formData.textareaVertical"
            label="Vertical Resize"
            resize="vertical"
            :rows="3"
          />
          <Textarea
            v-model="formData.textareaHorizontal"
            label="Horizontal Resize"
            resize="horizontal"
            :rows="3"
          />
          <Textarea
            v-model="formData.textareaBoth"
            label="Both Directions"
            resize="both"
            :rows="3"
          />
        </div>

        <Textarea
          v-model="formData.textareaError"
          label="With Error"
          error="This field has an error"
          :rows="3"
        />

        <Textarea
          v-model="formData.textareaDisabled"
          label="Disabled"
          :disabled="true"
          :rows="3"
        />

        <Textarea
          v-model="formData.textareaReadonly"
          label="Readonly"
          :readonly="true"
          :rows="3"
        />

        <Textarea
          v-model="formData.textareaLoading"
          label="Loading State"
          :loading="true"
          :rows="3"
        />
      </div>

      <div class="mt-8 space-y-4 max-w-2xl">
        <h2 class="text-2xl font-bold">Native Select Components</h2>

        <Select
          v-model="formData.country"
          label="Country"
          placeholder="Select a country"
          :options="countries"
          hint="Choose your country"
        />

        <Select
          v-model="formData.language"
          label="Language"
          :options="languages"
          icon-left="mdi:translate"
          :required="true"
        />

        <div class="grid grid-cols-3 gap-4">
          <Select
            v-model="formData.selectSmall"
            label="Small"
            size="sm"
            :options="['Option 1', 'Option 2', 'Option 3']"
          />
          <Select
            v-model="formData.selectMedium"
            label="Medium"
            size="md"
            :options="['Option 1', 'Option 2', 'Option 3']"
          />
          <Select
            v-model="formData.selectLarge"
            label="Large"
            size="lg"
            :options="['Option 1', 'Option 2', 'Option 3']"
          />
        </div>

        <Select
          v-model="formData.selectError"
          label="With Error"
          :options="['Option 1', 'Option 2']"
          error="Please select a valid option"
        />

        <Select
          v-model="formData.selectDisabled"
          label="Disabled"
          :options="['Option 1', 'Option 2']"
          :disabled="true"
        />

        <Select
          v-model="formData.selectLoading"
          label="Loading"
          :options="['Option 1', 'Option 2']"
          :loading="true"
        />
      </div>

      <div class="mt-8 space-y-4 max-w-2xl">
        <h2 class="text-2xl font-bold">Custom Select Components</h2>

        <CustomSelect
          v-model="formData.customCountry"
          label="Country (Custom)"
          placeholder="Select a country"
          :options="customCountries"
          hint="This is a custom dropdown with icons"
          :clearable="true"
        />

        <CustomSelect
          v-model="formData.customLanguage"
          label="Language (Searchable)"
          :options="customLanguages"
          icon-left="mdi:translate"
          :searchable="true"
          :clearable="true"
          :required="true"
        />

        <div class="grid grid-cols-3 gap-4">
          <CustomSelect
            v-model="formData.customSelectSmall"
            label="Small"
            size="sm"
            :options="customOptions"
            :clearable="true"
          />
          <CustomSelect
            v-model="formData.customSelectMedium"
            label="Medium"
            size="md"
            :options="customOptions"
            :clearable="true"
          />
          <CustomSelect
            v-model="formData.customSelectLarge"
            label="Large"
            size="lg"
            :options="customOptions"
            :clearable="true"
          />
        </div>

        <CustomSelect
          v-model="formData.customSelectColor"
          label="Color Options"
          :options="colorOptions"
          :searchable="true"
          color="accent"
        />

        <CustomSelect
          v-model="formData.customSelectError"
          label="With Error"
          :options="customOptions"
          error="Please select a valid option"
        />

        <CustomSelect
          v-model="formData.customSelectDisabled"
          label="Disabled"
          :options="customOptions"
          :disabled="true"
        />
      </div>

      <div class="mt-8 space-y-4 max-w-2xl">
        <h2 class="text-2xl font-bold">Form with Field Components</h2>

        <Form @submit="handleSubmit">
          <Field
            label="Username"
            hint="Must be at least 3 characters"
            :required="true"
          >
            <template #default="{ id, ariaDescribedby }">
              <Input
                :id="id"
                v-model="formWithFields.username"
                :aria-describedby="ariaDescribedby"
                name="username"
                autocomplete="username"
                placeholder="Enter your username"
              />
            </template>
          </Field>

          <Field
            label="Email Address"
            :error="formErrors.email"
            :required="true"
          >
            <template #default="{ id, ariaDescribedby, ariaInvalid }">
              <Input
                :id="id"
                v-model="formWithFields.email"
                type="email"
                name="email"
                autocomplete="email"
                :aria-describedby="ariaDescribedby"
                :aria-invalid="ariaInvalid"
                icon-left="mdi:email"
                placeholder="your@email.com"
              />
            </template>
          </Field>

          <Field label="Country" hint="Select your country of residence">
            <template #default="{ id, ariaDescribedby }">
              <CustomSelect
                :id="id"
                v-model="formWithFields.country"
                :aria-describedby="ariaDescribedby"
                :options="customCountries"
                placeholder="Choose a country"
                :searchable="true"
                :clearable="true"
              />
            </template>
          </Field>

          <Field label="Bio" hint="Tell us about yourself">
            <template #default="{ id, ariaDescribedby }">
              <Textarea
                :id="id"
                v-model="formWithFields.bio"
                name="bio"
                :aria-describedby="ariaDescribedby"
                placeholder="Write your bio..."
                :rows="4"
              />
            </template>
          </Field>

          <Field>
            <template #default>
              <Switch
                v-model="formWithFields.newsletter"
                label="Subscribe to newsletter"
                color="primary"
              />
            </template>
          </Field>

          <div class="flex gap-3">
            <Button type="submit" color="primary" variant="solid">
              Submit Form
            </Button>
            <Button
              type="button"
              color="secondary"
              variant="outline"
              @click="resetForm"
            >
              Reset
            </Button>
          </div>
        </Form>
      </div>
      <div class="mt-8 space-y-4 max-w-2xl">
        <h2 class="text-2xl font-bold">Cards</h2>

        <Card class="w-[380px]">
          <CardHeader>
            <CardTitle>Notifications</CardTitle>
            <CardDescription>You have 3 unread messages.</CardDescription>
          </CardHeader>
          <CardContent>
            <div
              class="flex items-center gap-4 rounded-xl border border-(--border-color) p-4"
            >
              <div
                class="h-10 w-10 rounded-full bg-blue-500/10 flex items-center justify-center text-blue-500"
              >
                <Icon name="mdi:bell" class="w-5 h-5" />
              </div>
              <div class="flex-1">
                <p class="text-sm font-medium text-(--label-text)">
                  Push Notifications
                </p>
                <p class="text-xs text-(--hint-text)">
                  Send notifications to device.
                </p>
              </div>
            </div>
          </CardContent>
          <CardFooter>
            <Button class="w-full" icon-left="mdi:check"
              >Mark all as read</Button
            >
          </CardFooter>
        </Card>

        <Grid :spacing="4" class="mt-4">
          <Card hover class="w-64">
            <CardHeader class="pb-2">
              <CardDescription>Total Revenue</CardDescription>
              <CardTitle class="text-3xl">$45,231.89</CardTitle>
            </CardHeader>
            <CardContent>
              <div
                class="text-xs text-green-500 flex items-center gap-1 font-medium"
              >
                <Icon name="mdi:trending-up" class="w-3.5 h-3.5" />
                +20.1% from last month
              </div>
            </CardContent>
          </Card>

          <Card hover class="w-64">
            <CardHeader class="pb-2">
              <CardDescription>Active Users</CardDescription>
              <CardTitle class="text-3xl">+2350</CardTitle>
            </CardHeader>
            <CardContent>
              <div class="text-xs text-(--hint-text)">+180 since last hour</div>
            </CardContent>
          </Card>
        </Grid>
      </div>
      <div class="max-h-screen max-w-screen pt-12">
        <div class="space-y-2 mb-6">
          <h2 class="text-2xl font-bold tracking-tight text-(--label-text)">
            Recent Projects
          </h2>
          <p class="text-(--hint-text)">
            Swipe to see what we've been working on.
          </p>
        </div>

        <Carousel loop class="h-full group">
          <CarouselContent>
            <CarouselItem
              v-for="(item, index) in 6"
              :key="index"
              class="basis-1/3"
            >
              <div class="p-1">
                <Card hover class="h-full">
                  <CardHeader>
                    <CardTitle>Project {{ index + 1 }}</CardTitle>
                    <CardDescription>Last updated 2h ago</CardDescription>
                  </CardHeader>
                  <CardContent
                    class="flex aspect-square items-center justify-center p-6"
                  >
                    <span class="text-4xl font-semibold text-(--hint-text)">{{
                      index + 1
                    }}</span>
                  </CardContent>
                  <CardFooter>
                    <Button size="sm" variant="ghost" class="w-full"
                      >View Details</Button
                    >
                  </CardFooter>
                </Card>
              </div>
            </CarouselItem>
          </CarouselContent>

          <CarouselPrevious />
          <CarouselNext />
        </Carousel>
      </div>
      <div class="mt-8 space-y-4 max-w-2xl">
        <h2 class="text-2xl font-bold">Tooltips</h2>
        <Tooltip trigger="click" :close-delay="1200" text="Added to Library">
          <Button variant="ghost" size="sm">
            <Icon name="mdi:plus" class="w-6 h-6 text-(--icon-color)" />
          </Button>
        </Tooltip>

        <Tooltip side="top" :delay="500">
          <Button
            variant="ghost"
            size="sm"
            class="w-full bg-primary hover:bg-primary/80"
            >Save Changes</Button
          >
          <template #content>
            <div class="flex items-center gap-3">
              <span>Save</span>
              <span
                class="flex items-center justify-center h-4 px-1.5 rounded border border-(--border-color) bg-(--surface-primary) font-mono text-[10px] text-(--hint-text)"
              >
                ⌘S
              </span>
            </div>
          </template>
        </Tooltip>
      </div>
      <Grid :spacing="6" items-start>
        <GridItem :xs="12" :md="4" :lg="3">
          <Card class="h-[500px] p-4"> Sidebar Content </Card>
        </GridItem>

        <GridItem :xs="12" :md="8" :lg="9">
          <Grid :spacing="4">
            <GridItem :xs="12" :sm="6" :lg="4">
              <Card>Stat 1</Card>
            </GridItem>
            <GridItem :xs="12" :sm="6" :lg="4">
              <Card>Stat 2</Card>
            </GridItem>
            <GridItem :xs="12" :sm="12" :lg="4">
              <Card>Stat 3</Card>
            </GridItem>

            <GridItem :xs="12" :lg="'full'">
              <Card class="h-64">Chart Area</Card>
            </GridItem>
          </Grid>
        </GridItem>
      </Grid>
      <div class="mt-8 space-y-4 max-w-2xl">
        <Input
          v-model="formData.date"
          type="custom-date"
          placeholder="Select a date"
          label="Select a date"
          enable-time
        />
      </div>
    </div>
    <div
      class="flex h-screen w-full bg-(--surface-secondary) border-t border-(--border-color) mt-12"
    >
      <Sidebar>
        <SidebarHeader>
          <span class="text-xl font-bold text-primary font-mono"> Beer </span>
          <template #icon>
            <div
              class="h-8 w-8 rounded-lg bg-primary flex items-center justify-center text-white font-bold text-lg"
            >
              D
            </div>
          </template>
        </SidebarHeader>

        <SidebarContent>
          <div
            v-if="!isCollapsed"
            class="mb-2 px-3 text-xs font-semibold uppercase text-(--hint-text) tracking-wider"
          >
            Main
          </div>
          <SidebarItem icon="mdi:view-dashboard" label="Dashboard" />
          <SidebarItem icon="mdi:chart-bar" label="Analytics" />
          <SidebarItem icon="mdi:account-group" label="Customers" />

          <div v-if="isCollapsed" class="mt-auto flex justify-center py-2">
            <Button
              variant="ghost"
              size="sm"
              icon-left="mdi:chevron-right"
              @click="toggleCollapse"
            />
          </div>
        </SidebarContent>

        <SidebarFooter>
          <div v-if="isCollapsed" class="flex justify-center">
            <Icon name="mdi:account" class="h-5 w-5 text-(--icon-color)" />
          </div>
          <div v-else class="flex items-center gap-3 p-3">
            <div class="h-9 w-9 rounded-full bg-(--border-color)"></div>
            <div><p class="text-sm">Jane Doe</p></div>
          </div>
        </SidebarFooter>
      </Sidebar>

      <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
        <header
          class="md:hidden flex items-center border-b border-(--border-color) bg-(--surface-primary) px-4 h-16 shrink-0"
        >
          <Button variant="ghost" size="sm" @click="toggleMobile">
            <Icon name="mdi:menu" class="h-6 w-6" />
          </Button>
          <span class="ml-4 font-bold text-(--label-text)">Dashboard</span>
        </header>

        <main class="flex-1 overflow-auto p-4 md:p-6">
          <div
            class="bg-white/5 p-4 rounded-lg border border-dashed border-(--border-color)"
          >
            <p class="text-center text-(--hint-text)">Dashboard Content Area</p>
          </div>
          <TableExample class="mt-6 overflow-x-auto" />
          <DataSimulation class="mt-6" />
          <DataGridExample class="mt-6" />
          <Grid :cols="3" :gap="6" class="mb-8">
            <div class="bg-(--surface-secondary) p-4 rounded">Col 1</div>
            <div class="bg-(--surface-secondary) p-4 rounded">Col 2</div>
            <div class="bg-(--surface-secondary) p-4 rounded">Col 3</div>
          </Grid>

          <Grid :cols="3" :rows="4" flow="col" :gap="4">
            <div
              v-for="i in 12"
              :key="i"
              class="h-12 bg-(--btn-primary-bg) text-white flex items-center justify-center rounded"
            >
              Item {{ i }}
            </div>
          </Grid>

          <div class="h-8"></div>

          <Grid :cols="4" :gap="4">
            <GridItem span="full" class="bg-primary text-white p-4 rounded">
              Header (Span Full)
            </GridItem>

            <GridItem
              :row-span="2"
              class="bg-(--surface-secondary) p-4 rounded"
            >
              Sidebar (Row Span 2)
            </GridItem>

            <GridItem
              :span="3"
              :row-span="2"
              class="bg-(--surface-secondary) p-4 rounded h-32"
            >
              Main Content
            </GridItem>

            <GridItem span="full" class="bg-(--surface-secondary) p-4 rounded">
              Footer
            </GridItem>
          </Grid>
        </main>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: "auth",
});

useHead({
  title: "Beer Studios",
  meta: [
    {
      name: "viewport",
      content:
        "width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=no, shrink-to-fit=no",
    },
    {
      name: "description",
      content: "Beer website",
    },
  ],
});

const { isCollapsed, toggleMobile, toggleCollapse } = useSidebar();

const isModalOpen = ref(false);

const { locale, locales, setLocale } = useI18n();
const availableLocales = computed(() => {
  return locales.value.filter((i: { code: string }) => i.code !== locale.value);
});

const colorMode = useColorMode();

const mobileMenuOpen = ref(false);

const changeMode = () => {
  if (colorMode.value === "light") colorMode.preference = "dark";
  else if (colorMode.value === "dark") colorMode.preference = "contrast";
  else if (colorMode.value === "contrast") colorMode.preference = "christmas";
  else if (colorMode.value === "christmas") colorMode.preference = "light";
};

const color = ref("#441A1A");

const switchStates = ref({
  basic: false,
  primary: true,
  secondary: false,
  accent: true,
  success: false,
  danger: true,
  small: false,
  medium: true,
  large: false,
  leftLabel: true,
  required: false,
  disabled: true,
});

const formData = ref({
  text: "",
  email: "",
  password: "",
  search: "",
  number: 0,
  url: "",
  tel: "",
  date: "",
  time: "",
  color: "#3B82F6",
  errorExample: "",
  disabled: "This is disabled",
  readonly: "This is readonly",
  small: "",
  medium: "",
  large: "",
  colorPrimary: "",
  colorSecondary: "",
  colorAccent: "",
  colorSuccess: "",
  colorDanger: "",
  block: "",
  textarea: "",
  textareaRequired: "",
  textareaNone: "",
  textareaVertical: "",
  textareaHorizontal: "",
  textareaBoth: "",
  textareaError: "",
  textareaDisabled: "This is disabled",
  textareaReadonly: "This is readonly",
  textareaLoading: "",
  country: "",
  language: "",
  selectSmall: "",
  selectMedium: "",
  selectLarge: "",
  selectError: "",
  selectDisabled: "Option 1",
  selectLoading: "",
  customCountry: "",
  customLanguage: "",
  customSelectSmall: "",
  customSelectMedium: "",
  customSelectLarge: "",
  customSelectColor: "",
  customSelectError: "",
  customColor: "#ff0000",
  customSelectDisabled: "option1",
});

const formWithFields = ref({
  username: "",
  email: "",
  country: "",
  bio: "",
  newsletter: false,
});

const formErrors = ref({
  email: "",
});

const countries = [
  { label: "United States", value: "us" },
  { label: "United Kingdom", value: "uk" },
  { label: "Canada", value: "ca" },
  { label: "Australia", value: "au" },
  { label: "Germany", value: "de" },
  { label: "France", value: "fr" },
  { label: "Spain", value: "es" },
  { label: "Italy", value: "it" },
];

const languages = [
  "English",
  "Spanish",
  "French",
  "German",
  "Italian",
  "Portuguese",
  "Russian",
  "Chinese",
  "Japanese",
];

const customCountries = [
  { label: "United States", value: "us", icon: "circle-flags:us" },
  { label: "United Kingdom", value: "uk", icon: "circle-flags:uk" },
  { label: "Canada", value: "ca", icon: "circle-flags:ca" },
  { label: "Australia", value: "au", icon: "circle-flags:au" },
  { label: "Germany", value: "de", icon: "circle-flags:de" },
  { label: "France", value: "fr", icon: "circle-flags:fr" },
  { label: "Spain", value: "es", icon: "circle-flags:es" },
  { label: "Italy", value: "it", icon: "circle-flags:it" },
];

const customLanguages = [
  { label: "English", value: "en", icon: "mdi:web" },
  { label: "Spanish", value: "es", icon: "mdi:web" },
  { label: "French", value: "fr", icon: "mdi:web" },
  { label: "German", value: "de", icon: "mdi:web" },
  { label: "Italian", value: "it", icon: "mdi:web" },
  { label: "Portuguese", value: "pt", icon: "mdi:web" },
  { label: "Russian", value: "ru", icon: "mdi:web" },
  { label: "Chinese", value: "zh", icon: "mdi:web" },
  { label: "Japanese", value: "ja", icon: "mdi:web" },
];

const customOptions = [
  { label: "Option 1", value: "option1" },
  { label: "Option 2", value: "option2" },
  { label: "Option 3", value: "option3" },
  { label: "Disabled Option", value: "disabled", disabled: true },
];

const colorOptions = [
  { label: "Red", value: "red", icon: "mdi:circle", disabled: false },
  { label: "Blue", value: "blue", icon: "mdi:circle" },
  { label: "Green", value: "green", icon: "mdi:circle" },
  { label: "Yellow", value: "yellow", icon: "mdi:circle" },
  { label: "Purple", value: "purple", icon: "mdi:circle" },
];

const searching = ref(false);

const handleSubmit = (event: Event) => {
  event.preventDefault();

  if (!formWithFields.value.email.includes("@")) {
    formErrors.value.email = "Please enter a valid email address";
    return;
  }

  formErrors.value.email = "";
  console.log("Form submitted:", formWithFields.value);
  alert("Form submitted successfully!");
};

const resetForm = () => {
  formWithFields.value = {
    username: "",
    email: "",
    country: "",
    bio: "",
    newsletter: false,
  };
  formErrors.value = {
    email: "",
  };
};
</script>

<style scoped>
h1 {
  font-family: MonteCarlo;
}
</style>
