export type PlanTier = "starter" | "operations" | "enterprise";

export interface SubscriptionPlan {
  tier: PlanTier;
  name: string;
  price: number;
  currency: string;
  period: "month";
  features: string[];
  limits: { alerts: number; locations: number; sensors: number; users: number };
}

export const useSubscription = () => {
  const currentTier = useState<PlanTier>("current-tier", () => "operations");

  const plans: SubscriptionPlan[] = [
    {
      tier: "starter",
      name: "Starter",
      price: 0,
      currency: "EUR",
      period: "month",
      features: ["Dispatcher console", "Citizen app", "CAP export", "5 safe locations", "Basic templates", "Email support"],
      limits: { alerts: 10, locations: 5, sensors: 0, users: 2 },
    },
    {
      tier: "operations",
      name: "Operations Plus",
      price: 29,
      currency: "EUR",
      period: "month",
      features: ["Everything in Starter", "Sensor integration", "Advanced reporting", "Multilingual templates", "Audit logs", "Priority support", "Up to 50 safe locations", "Copernicus data feed"],
      limits: { alerts: 100, locations: 50, sensors: 25, users: 10 },
    },
    {
      tier: "enterprise",
      name: "Enterprise / Critical Site",
      price: 99,
      currency: "EUR",
      period: "month",
      features: ["Everything in Operations", "Custom SLA", "Integration support", "Role customization", "Multi-site operations", "Galileo GNSS priority", "Unlimited safe locations", "Dedicated account manager", "White-label option"],
      limits: { alerts: -1, locations: -1, sensors: -1, users: -1 },
    },
  ];

  const currentPlan = computed(() => plans.find((p) => p.tier === currentTier.value)!);

  const usage = useState("subscription-usage", () => ({
    alertsSent: 47,
    locationsConfigured: 7,
    sensorsConnected: 12,
    activeUsers: 4,
  }));

  const changeTier = (tier: PlanTier) => { currentTier.value = tier; };

  return { currentTier, plans, currentPlan, usage, changeTier };
};
