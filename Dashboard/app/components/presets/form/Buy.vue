<template>
  <div
    class="min-h-screen w-full flex items-center justify-center bg-(--surface-secondary) p-4"
  >
    <Card class="w-full max-w-[700px]">
      <CardHeader
        class="border-b border-(--border-color) bg-(--surface-secondary)/30 pb-6"
      >
        <div class="flex items-center justify-between">
          <div>
            <CardTitle class="text-xl">Secure Checkout</CardTitle>
            <CardDescription class="mt-1">
              Complete your purchase in a few simple steps
            </CardDescription>
          </div>
          <div class="text-right">
            <p class="text-sm text-(--hint-text)">Total Amount</p>
            <p class="text-2xl font-bold text-(--label-text)">$129.00</p>
          </div>
        </div>
      </CardHeader>

      <CardContent class="px-8 pt-6">
        <Form class="space-y-6" @submit="handlePurchase">
          <div class="space-y-4">
            <h4
              class="text-sm font-semibold text-(--label-text) uppercase tracking-wider flex items-center gap-2"
            >
              <Icon name="mdi:account-outline" class="h-4 w-4" />
              Contact Information
            </h4>

            <Grid :cols="2" gap="4">
              <Input
                id="name"
                v-model="form.name"
                label="Full Name"
                type="text"
                name="name"
                autocomplete="name"
                placeholder="John Doe"
                icon-left="mdi:account"
                required
              />
              <Input
                id="email"
                v-model="form.email"
                label="Email Address"
                type="email"
                name="email"
                autocomplete="email"
                placeholder="john@example.com"
                icon-left="mdi:email-outline"
                required
              />
            </Grid>
            <Input
              id="tel"
              v-model="form.tel"
              v-model:prefix-value="form.countryCode"
              label="Phone Number"
              type="tel"
              name="phone"
              autocomplete="tel-national"
              placeholder="(555) 123-4567"
              :prefix-options="phoneCodes"
              prefix-searchable
              required
            />
          </div>

          <div class="h-px bg-(--border-color)" />

          <div class="space-y-4">
            <h4
              class="text-sm font-semibold text-(--label-text) uppercase tracking-wider flex items-center gap-2"
            >
              <Icon name="mdi:truck-delivery-outline" class="h-4 w-4" />
              Shipping Address
            </h4>

            <Input
              id="address-line1"
              v-model="form.streetAddress"
              label="Address Line 1"
              name="address-line1"
              autocomplete="shipping address-line1"
              placeholder="Address Line 1"
              icon-left="mdi:map-marker-outline"
              required
            />
            <Grid :cols="2" gap="4">
              <GridItem>
                <Input
                  id="address-line2"
                  v-model="form.city"
                  label="Address Line 2"
                  name="address-line2"
                  autocomplete="shipping address-line2"
                  placeholder="Address Line 2"
                  required
                />
              </GridItem>
              <GridItem>
                <Input
                  id="address-line3"
                  v-model="form.city"
                  label="Address Line 3"
                  name="address-line3"
                  autocomplete="shipping address-line3"
                  placeholder="Address Line 3"
                />
              </GridItem>
            </Grid>

            <Grid :cols="2" gap="4">
              <GridItem>
                <Input
                  id="city"
                  v-model="form.city"
                  label="City"
                  name="city"
                  autocomplete="shipping address-level2"
                  placeholder="New York"
                  required
                />
              </GridItem>

              <GridItem>
                <Input
                  id="state"
                  v-model="form.state"
                  label="State / Province"
                  name="state"
                  autocomplete="shipping address-level1"
                  placeholder="NY"
                />
              </GridItem>
            </Grid>

            <Grid :cols="2" gap="4">
              <GridItem>
                <CustomSelect
                  id="country"
                  v-model="form.country"
                  label="Country"
                  name="country"
                  autocomplete="shipping country"
                  placeholder="United States"
                  :options="countries"
                  searchable
                  hide-scrollbar
                  required
                />
              </GridItem>
              <GridItem>
                <Input
                  id="postal-code"
                  v-model="form.postalCode"
                  label="Postal Code"
                  name="postal-code"
                  autocomplete="shipping postal-code"
                  placeholder="10001"
                  required
                />
              </GridItem>
            </Grid>
          </div>

          <div class="h-px bg-(--border-color)" />

          <div class="space-y-4">
            <h4
              class="text-sm font-semibold text-(--label-text) uppercase tracking-wider flex items-center gap-2"
            >
              <Icon name="mdi:credit-card-outline" class="h-4 w-4" />
              Payment Information
            </h4>

            <Input
              id="cc-name"
              v-model="form.cardName"
              label="Cardholder Name"
              name="cc-name"
              autocomplete="cc-name"
              placeholder="John Doe"
              icon-left="mdi:account-credit-card"
              required
            />

            <Input
              id="cc-number"
              v-model="form.cardNumber"
              label="Card Number"
              name="cc-number"
              type="text"
              inputmode="numeric"
              autocomplete="cc-number"
              placeholder="1234 5678 9012 3456"
              icon-left="mdi:credit-card-outline"
              :max="19"
              required
              @input="formatCardNumber"
            />

            <Grid :cols="3" flow="col" gap="4">
              <GridItem>
                <Input
                  id="cc-exp-month"
                  v-model="form.expMonth"
                  label="Exp Month"
                  name="cc-exp-month"
                  type="text"
                  inputmode="numeric"
                  autocomplete="cc-exp-month"
                  placeholder="MM"
                  icon-left="mdi:calendar"
                  :max="2"
                  required
                />
              </GridItem>
              <GridItem>
                <Input
                  id="cc-exp-year"
                  v-model="form.expYear"
                  label="Exp Year"
                  name="cc-exp-year"
                  type="text"
                  inputmode="numeric"
                  autocomplete="cc-exp-year"
                  placeholder="YY"
                  icon-left="mdi:calendar"
                  :max="2"
                  required
                />
              </GridItem>

              <GridItem>
                <Input
                  id="cc-csc"
                  v-model="form.cvc"
                  label="CVV / CVC"
                  name="cc-csc"
                  inputmode="numeric"
                  autocomplete="cc-csc"
                  placeholder="123"
                  icon-left="mdi:lock-outline"
                  :maxlength="4"
                  required
                />
              </GridItem>
            </Grid>
          </div>

          <div class="h-px bg-(--border-color)" />

          <div
            class="flex items-center justify-between py-3 rounded-xl bg-(--surface-secondary)/50 px-4 border border-(--border-color)"
          >
            <div class="flex items-center gap-3">
              <Icon
                name="mdi:file-document-outline"
                class="h-5 w-5 text-(--icon-color)"
              />
              <span class="text-sm font-medium text-(--label-text)"
                >Billing address same as shipping</span
              >
            </div>
            <Switch v-model="form.sameBilling" size="sm" />
          </div>

          <div v-if="!form.sameBilling" class="space-y-4">
            <h4
              class="text-sm font-semibold text-(--label-text) uppercase tracking-wider flex items-center gap-2"
            >
              <Icon name="mdi:receipt-text-outline" class="h-4 w-4" />
              Billing Address
            </h4>

            <Input
              id="billing-address-line1"
              v-model="form.streetAddress"
              label="Address Line 1"
              name="address-line1"
              autocomplete="billing address-line1"
              placeholder="Address Line 1"
              icon-left="mdi:map-marker-outline"
              required
            />
            <Grid :cols="2" gap="4">
              <GridItem>
                <Input
                  id="billing-address-line2"
                  v-model="form.city"
                  label="Address Line 2"
                  name="address-line2"
                  autocomplete="billing address-line2"
                  placeholder="Address Line 2"
                  required
                />
              </GridItem>
              <GridItem>
                <Input
                  id="billing-address-line3"
                  v-model="form.city"
                  label="Address Line 3"
                  name="address-line3"
                  autocomplete="billing address-line3"
                  placeholder="Address Line 3"
                />
              </GridItem>
            </Grid>

            <Grid :cols="2" gap="4">
              <Input
                id="billing-city"
                v-model="form.billingCity"
                label="City"
                name="billing-city"
                autocomplete="billing address-level2"
                placeholder="Los Angeles"
                required
              />

              <Input
                id="billing-state"
                v-model="form.billingState"
                label="State / Province"
                name="billing-state"
                autocomplete="billing address-level1"
                placeholder="CA"
                required
              />
            </Grid>

            <Grid :cols="2" gap="4">
              <CustomSelect
                id="billing-country"
                v-model="form.billingCountry"
                label="Country"
                name="billing-country"
                autocomplete="billing country"
                placeholder="United States"
                :options="countries"
                searchable
                hide-scrollbar
              />

              <Input
                id="billing-postal-code"
                v-model="form.billingPostalCode"
                label="Postal Code"
                name="billing-postal-code"
                autocomplete="billing postal-code"
                placeholder="90001"
                required
              />
            </Grid>
          </div>

          <div class="space-y-2">
            <label
              for="order-notes"
              class="block text-sm font-medium text-(--label-text)"
            >
              Order Notes (Optional)
            </label>
            <Textarea
              id="order-notes"
              v-model="form.orderNotes"
              name="order-notes"
              rows="3"
              placeholder="Any special instructions for your order..."
            />
          </div>

          <Button
            type="submit"
            variant="solid"
            color="primary"
            block
            size="lg"
            class="h-14 mt-6 text-base font-semibold shadow-lg shadow-(--btn-primary-bg)/20"
            :loading="isProcessing"
            icon-left="mdi:lock"
          >
            Complete Purchase - $129.00
          </Button>
        </Form>
      </CardContent>

      <CardFooter
        class="flex flex-col items-center gap-3 border-t border-(--border-color) bg-(--surface-secondary)/30 py-5"
      >
        <p class="text-xs text-(--hint-text) text-center pt-2">
          Your payment information is encrypted and secure
        </p>
      </CardFooter>
    </Card>
  </div>
</template>

<script setup lang="ts">
const isProcessing = ref(false);

const form = reactive({
  name: "",
  email: "",
  tel: "",
  countryCode: "+1",

  streetAddress: "",
  city: "",
  state: "",
  country: "us",
  postalCode: "",

  cardName: "",
  cardNumber: "",
  expMonth: "",
  expYear: "",
  cvc: "",

  sameBilling: true,
  billingStreetAddress: "",
  billingCity: "",
  billingState: "",
  billingCountry: "us",
  billingPostalCode: "",

  orderNotes: "",
});

const countries = [
  { label: "United States", value: "us", icon: "circle-flags:us" },
  { label: "United Kingdom", value: "uk", icon: "circle-flags:uk" },
  { label: "Canada", value: "ca", icon: "circle-flags:ca" },
  { label: "Australia", value: "au", icon: "circle-flags:au" },
  { label: "Germany", value: "de", icon: "circle-flags:de" },
  { label: "France", value: "fr", icon: "circle-flags:fr" },
  { label: "Spain", value: "es", icon: "circle-flags:es" },
  { label: "Italy", value: "it", icon: "circle-flags:it" },
  { label: "Romania", value: "ro", icon: "circle-flags:ro" },
  { label: "Japan", value: "jp", icon: "circle-flags:jp" },
  { label: "China", value: "cn", icon: "circle-flags:cn" },
  { label: "India", value: "in", icon: "circle-flags:in" },
  { label: "Brazil", value: "br", icon: "circle-flags:br" },
  { label: "Mexico", value: "mx", icon: "circle-flags:mx" },
  { label: "Netherlands", value: "nl", icon: "circle-flags:nl" },
  { label: "Sweden", value: "se", icon: "circle-flags:se" },
  { label: "Norway", value: "no", icon: "circle-flags:no" },
  { label: "Poland", value: "pl", icon: "circle-flags:pl" },
  { label: "Belgium", value: "be", icon: "circle-flags:be" },
  { label: "Switzerland", value: "ch", icon: "circle-flags:ch" },
];

const phoneCodes = [
  { label: "+1 (US)", value: "+1", icon: "circle-flags:us" },
  { label: "+44 (UK)", value: "+44", icon: "circle-flags:uk" },
  { label: "+1 (CA)", value: "+1", icon: "circle-flags:ca" },
  { label: "+61 (AU)", value: "+61", icon: "circle-flags:au" },
  { label: "+49 (DE)", value: "+49", icon: "circle-flags:de" },
  { label: "+33 (FR)", value: "+33", icon: "circle-flags:fr" },
  { label: "+34 (ES)", value: "+34", icon: "circle-flags:es" },
  { label: "+39 (IT)", value: "+39", icon: "circle-flags:it" },
  { label: "+40 (RO)", value: "+40", icon: "circle-flags:ro" },
  { label: "+81 (JP)", value: "+81", icon: "circle-flags:jp" },
  { label: "+86 (CN)", value: "+86", icon: "circle-flags:cn" },
];

const formatCardNumber = (event: Event) => {
  const input = event.target as HTMLInputElement;
  const value = input.value.replace(/\s/g, "");
  const formattedValue = value.match(/.{1,4}/g)?.join(" ") || value;
  form.cardNumber = formattedValue;
};

const handlePurchase = async (e: Event) => {
  e.preventDefault();
  isProcessing.value = true;

  setTimeout(() => {
    console.log("Order Placed:", {
      ...form,
      billing: form.sameBilling
        ? {
            streetAddress: form.streetAddress,
            city: form.city,
            state: form.state,
            country: form.country,
            postalCode: form.postalCode,
          }
        : {
            streetAddress: form.billingStreetAddress,
            city: form.billingCity,
            state: form.billingState,
            country: form.billingCountry,
            postalCode: form.billingPostalCode,
          },
    });
    isProcessing.value = false;
  }, 2000);
};
</script>
