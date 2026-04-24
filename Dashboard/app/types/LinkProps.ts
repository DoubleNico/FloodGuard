import type { HTMLAttributes } from "vue";

export interface LinkProps extends /* @vue-ignore */ HTMLAttributes {
  to: string | object;

  target?: string;

  /**
   * @default 'primary'
   */
  variant?:
    | "primary"
    | "secondary"
    | "accent"
    | "success"
    | "danger"
    | "default"
    | "muted";

  size?: "xs" | "sm" | "md" | "base" | "lg" | "xl";

  /**
   * @default true
   */
  underline?: boolean;

  /**
   * @default 'medium'
   */
  weight?: "normal" | "medium" | "semibold" | "bold";
}
